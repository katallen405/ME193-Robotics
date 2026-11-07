"""Serve AnnaCode on localhost with caching switched off.

    python3 serve.py          # http://localhost:8000/
    python3 serve.py 8001     # pick another port

Plain `python3 -m http.server` works too, but it lets the browser cache files, and
PyScript fetches its .py files itself, so after you switch branches or edit a file the
page can keep running the old code (a hard reload does not always fix it). This server
tells the browser never to keep a copy. It only listens on this computer.
"""
import http.server
import os
import sys


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), NoCacheHandler) as server:
        print(f"AnnaCode on http://localhost:{port}/   (builder)")
        print(f"                http://localhost:{port}/trainer.html   (trainer)")
        print("Ctrl-C to stop.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
