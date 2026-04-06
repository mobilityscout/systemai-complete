#!/usr/bin/env python3
"""
systemai_server.py - REST API Server

Flask server on port 8000 providing:
- Endpoints for all 227 modules
- WebSocket live updates via SSE (Server-Sent Events, no extra deps)
- Health check endpoint
- Dashboard UI
"""

import json
import logging
import queue
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Ensure repo root is on path
REPO_ROOT = Path(__file__).parent.resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from flask import Flask, Response, jsonify, request, stream_with_context

from systemai_orchestrator import SystemAIOrchestrator

logger = logging.getLogger(__name__)

PORT = 8000

# ---------------------------------------------------------------------------
# SSE event bus (for live updates)
# ---------------------------------------------------------------------------


class EventBus:
    """Simple in-process broadcast bus for SSE subscribers."""

    def __init__(self):
        self._subscribers: list[queue.Queue] = []
        self._lock = threading.Lock()

    def subscribe(self) -> queue.Queue:
        q: queue.Queue = queue.Queue(maxsize=100)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        with self._lock:
            self._subscribers = [s for s in self._subscribers if s is not q]

    def publish(self, data: dict) -> None:
        payload = f"data: {json.dumps(data)}\n\n"
        with self._lock:
            for q in list(self._subscribers):
                try:
                    q.put_nowait(payload)
                except queue.Full:
                    pass  # slow consumer – drop event


_event_bus = EventBus()


def _build_app(orchestrator: SystemAIOrchestrator) -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    # ------------------------------------------------------------------
    # Health & status
    # ------------------------------------------------------------------

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()})

    @app.route("/status")
    def status():
        return jsonify(orchestrator.get_status())

    # ------------------------------------------------------------------
    # Module endpoints
    # ------------------------------------------------------------------

    @app.route("/modules")
    def list_modules():
        status_filter = request.args.get("status")
        modules = orchestrator.list_modules(status_filter=status_filter)
        return jsonify({"count": len(modules), "modules": modules})

    @app.route("/modules/<path:module_key>")
    def get_module(module_key: str):
        meta = orchestrator.loader.metadata.get(module_key)
        if meta is None:
            return jsonify({"error": "Module not found", "key": module_key}), 404
        health = orchestrator.monitor.get_module_status(module_key)
        return jsonify({"key": module_key, "metadata": meta, "health": health})

    @app.route("/modules/<path:module_key>/reload", methods=["POST"])
    def reload_module(module_key: str):
        result = orchestrator.reload_module(module_key)
        _event_bus.publish({"event": "module_reloaded", "key": module_key, "result": result})
        return jsonify(result)

    @app.route("/modules/load", methods=["POST"])
    def load_module():
        data = request.get_json(force=True, silent=True) or {}
        path = data.get("path")
        if not path:
            return jsonify({"error": "Missing 'path' in request body"}), 400
        result = orchestrator.load_module(path)
        _event_bus.publish({"event": "module_loaded", "path": path, "result": result})
        return jsonify(result)

    # ------------------------------------------------------------------
    # Health monitor endpoints
    # ------------------------------------------------------------------

    @app.route("/health/modules")
    def health_modules():
        return jsonify(orchestrator.monitor.get_all_statuses())

    @app.route("/health/summary")
    def health_summary():
        return jsonify(orchestrator.monitor.get_summary())

    # ------------------------------------------------------------------
    # WebSocket-style live updates via SSE
    # ------------------------------------------------------------------

    @app.route("/events")
    def sse_stream():
        """
        Server-Sent Events endpoint for live module updates.
        Connect with:  EventSource('/events')
        """
        q = _event_bus.subscribe()

        @stream_with_context
        def generate():
            # Send initial "connected" event
            yield f"data: {json.dumps({'event': 'connected', 'timestamp': datetime.now(timezone.utc).isoformat()})}\n\n"
            try:
                while True:
                    try:
                        payload = q.get(timeout=25)
                        yield payload
                    except queue.Empty:
                        # Heartbeat to keep connection alive
                        yield ": heartbeat\n\n"
            finally:
                _event_bus.unsubscribe(q)

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    # ------------------------------------------------------------------
    # Dashboard UI
    # ------------------------------------------------------------------

    @app.route("/dashboard")
    def dashboard():
        status = orchestrator.get_status()
        modules = orchestrator.list_modules()
        loaded = sum(1 for m in modules if m["status"] == "loaded")
        failed = sum(1 for m in modules if m["status"] == "failed")

        rows = ""
        for m in modules:
            badge = (
                '<span style="color:green">✅ loaded</span>'
                if m["status"] == "loaded"
                else f'<span style="color:red">❌ {m["status"]}</span>'
            )
            rows += f"<tr><td>{m['key']}</td><td>{badge}</td><td>{m.get('load_time_ms', '-')} ms</td></tr>\n"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>SystemAI Dashboard</title>
  <style>
    body {{ font-family: monospace; background:#111; color:#eee; padding:20px; }}
    h1 {{ color:#4af; }}
    .stat {{ display:inline-block; margin:10px 20px 10px 0; padding:12px 20px;
             background:#222; border-radius:6px; font-size:1.2em; }}
    .stat span {{ color:#4af; font-size:1.5em; }}
    table {{ border-collapse:collapse; width:100%; margin-top:20px; }}
    th {{ background:#333; padding:8px; text-align:left; }}
    td {{ padding:6px 8px; border-bottom:1px solid #333; font-size:0.85em; }}
    tr:hover td {{ background:#1a1a2e; }}
    #log {{ height:120px; overflow-y:auto; background:#0d0d0d; padding:10px;
            border:1px solid #333; margin-top:20px; font-size:0.8em; color:#8f8; }}
  </style>
</head>
<body>
  <h1>🤖 SystemAI Live Dashboard</h1>
  <div>
    <div class="stat">Total: <span>{len(modules)}</span></div>
    <div class="stat">Loaded: <span style="color:#4f4">{loaded}</span></div>
    <div class="stat">Failed: <span style="color:#f44">{failed}</span></div>
    <div class="stat">Startup: <span style="font-size:0.9em">{status.get('startup_time','—')}</span></div>
  </div>
  <div id="log">🔌 Connecting to live event stream…</div>
  <table>
    <thead><tr><th>Module</th><th>Status</th><th>Load Time</th></tr></thead>
    <tbody id="tbody">
{rows}
    </tbody>
  </table>
  <script>
    const log = document.getElementById('log');
    const es = new EventSource('/events');
    es.onmessage = (e) => {{
      const data = JSON.parse(e.data);
      log.innerHTML += '<br>' + JSON.stringify(data);
      log.scrollTop = log.scrollHeight;
    }};
    es.onerror = () => {{ log.innerHTML += '<br>⚠️ Stream error – retrying…'; }};
  </script>
</body>
</html>"""
        return Response(html, mimetype="text/html")

    # ------------------------------------------------------------------
    # Catch-all
    # ------------------------------------------------------------------

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "path": request.path}), 404

    return app


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------


def create_server(orchestrator: Optional[SystemAIOrchestrator] = None) -> Flask:
    from systemai_orchestrator import get_orchestrator

    orch = orchestrator or get_orchestrator()
    return _build_app(orch)


def _publish_status_loop(orchestrator: SystemAIOrchestrator) -> None:
    """Background thread that broadcasts health summaries every 10 s."""
    while True:
        time.sleep(10)
        try:
            summary = orchestrator.monitor.get_summary()
            _event_bus.publish({"event": "health_update", "data": summary})
        except Exception:
            pass


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
    )
    from systemai_orchestrator import SystemAIOrchestrator

    orch = SystemAIOrchestrator()
    orch.start()

    # Background SSE publisher
    t = threading.Thread(target=_publish_status_loop, args=(orch,), daemon=True)
    t.start()

    app = _build_app(orch)
    print(f"\n🚀 SystemAI Server running on http://localhost:{PORT}")
    print(f"   Dashboard : http://localhost:{PORT}/dashboard")
    print(f"   Health    : http://localhost:{PORT}/health")
    print(f"   Modules   : http://localhost:{PORT}/modules")
    print(f"   Events    : http://localhost:{PORT}/events\n")
    app.run(host="0.0.0.0", port=PORT, threaded=True)
