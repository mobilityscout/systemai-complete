#!/usr/bin/env python3
"""
systemai_launcher.py - Start Script

Automates the full SystemAI startup sequence:
1. Dependency resolution (installs missing Python packages)
2. Orchestrator initialisation (loads all 227 modules)
3. REST API server startup on port 8000
4. Graceful shutdown on SIGINT / SIGTERM
5. Comprehensive logging
"""

import atexit
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging setup – must happen before any local imports
# ---------------------------------------------------------------------------

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "systemai.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("launcher")

# ---------------------------------------------------------------------------
# Ensure repo root on path
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Required packages
# ---------------------------------------------------------------------------

REQUIRED_PACKAGES = {
    "flask": "flask",
    "psutil": "psutil",
}


def _ensure_dependencies() -> None:
    """Install any missing Python packages from REQUIRED_PACKAGES."""
    missing = []
    for import_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)

    if not missing:
        logger.info("All dependencies satisfied.")
        return

    logger.info("Installing missing packages: %s", missing)
    cmd = [sys.executable, "-m", "pip", "install", "--quiet"] + missing
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("pip install failed:\n%s", result.stderr)
        sys.exit(1)
    logger.info("Packages installed successfully.")


# ---------------------------------------------------------------------------
# Graceful shutdown
# ---------------------------------------------------------------------------

_shutdown_event = threading.Event()
_orchestrator = None
_flask_server = None


def _handle_signal(signum, _frame):
    logger.info("Received signal %s – initiating graceful shutdown...", signum)
    _shutdown_event.set()


def _shutdown() -> None:
    logger.info("Shutting down SystemAI…")
    if _orchestrator:
        try:
            _orchestrator.stop()
        except Exception as exc:
            logger.warning("Error stopping orchestrator: %s", exc)
    logger.info("Shutdown complete. Goodbye 👋")


# ---------------------------------------------------------------------------
# Startup banner
# ---------------------------------------------------------------------------

BANNER = r"""
 ____            _                     _    ___
/ ___| _   _ ___| |_ ___ _ __ ___    / \  |_ _|
\___ \| | | / __| __/ _ \ '_ ` _ \  / _ \  | |
 ___) | |_| \__ \ ||  __/ | | | | |/ ___ \ | |
|____/ \__, |___/\__\___|_| |_| |_/_/   \_\___|
       |___/
"""


def _print_banner(port: int) -> None:
    print(BANNER)
    print("=" * 60)
    print(f"  🚀 SystemAI Live Server  –  http://localhost:{port}")
    print(f"  📊 Dashboard             –  http://localhost:{port}/dashboard")
    print(f"  🩺 Health                –  http://localhost:{port}/health")
    print(f"  📦 Modules               –  http://localhost:{port}/modules")
    print(f"  🔴 Live Events (SSE)     –  http://localhost:{port}/events")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

PORT = int(os.environ.get("SYSTEMAI_PORT", "8000"))


def main() -> None:
    global _orchestrator

    # 1. Resolve dependencies
    logger.info("Step 1/4 - Checking dependencies…")
    _ensure_dependencies()

    # 2. Import heavy modules only after deps are confirmed present
    from systemai_orchestrator import SystemAIOrchestrator
    from systemai_server import _build_app, _publish_status_loop

    # 3. Register shutdown handlers
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)
    atexit.register(_shutdown)

    # 4. Start orchestrator
    logger.info("Step 2/4 - Starting orchestrator…")
    _orchestrator = SystemAIOrchestrator()
    result = _orchestrator.start()
    logger.info(
        "Orchestrator ready: %d loaded, %d failed (total %d).",
        result["loaded"],
        result["failed"],
        result["total"],
    )

    # 5. Build Flask app
    logger.info("Step 3/4 - Building REST API server…")
    app = _build_app(_orchestrator)

    # 6. Start SSE publisher thread
    pub_thread = threading.Thread(
        target=_publish_status_loop, args=(_orchestrator,), daemon=True
    )
    pub_thread.start()

    # 7. Start Flask in a daemon thread so we can watch _shutdown_event
    logger.info("Step 4/4 - Starting HTTP server on port %d…", PORT)
    _print_banner(PORT)

    flask_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=PORT, threaded=True, use_reloader=False),
        daemon=True,
        name="FlaskServer",
    )
    flask_thread.start()

    # 8. Wait for shutdown signal
    try:
        while not _shutdown_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    _shutdown()


if __name__ == "__main__":
    main()
