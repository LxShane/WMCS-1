import http.server
import socketserver
import os
import sys

# Serve the 'viz' directory
PORT = 3000
DIRECTORY = "viz"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

print(f"Serving Dashboard at http://127.0.0.1:{PORT}/ultimate.html")
print(f"Legacy Dashboard at http://127.0.0.1:{PORT}/dashboard.html")

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
except OSError:
    print(f"Port {PORT} is busy. Try closing other node servers.")
