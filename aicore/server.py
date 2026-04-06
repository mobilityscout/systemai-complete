from http.server import BaseHTTPRequestHandler, HTTPServer
import json, sys, os

sys.path.append("/root/aicore")
from workspace.api import handle

DOC_PATH = "/root/aicore/doc"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # ROOT UI
        if self.path == "/":
            with open("/root/aicore/workspace/ui.html") as f:
                html = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
            return

        # DOC FILE SERVE
        if self.path.startswith("/doc/"):
            file_path = os.path.join(DOC_PATH, self.path.replace("/doc/", ""))

            if os.path.isfile(file_path):
                with open(file_path, "r") as f:
                    content = f.read()

                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(content.encode())
                return
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"file not found")
                return

        # API FALLBACK
        path = self.path.split("?")[0].strip("/")
        path = "/" + path if path else "/"

        result = handle(path)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 50000), Handler).serve_forever()
