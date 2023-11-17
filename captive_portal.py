import http.server
from dotenv import load_dotenv
import os

load_dotenv()

INTERFACE_ADDRESS = os.getenv("INTERFACE_ADDRESS")


class RedirectHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header("Location", f"{INTERFACE_ADDRESS}:8000")
        self.end_headers()

    def do_HEAD(self):
        self.send_response(302)
        self.send_header("Location", f"{INTERFACE_ADDRESS}:8000")
        self.end_headers()


if __name__ == "__main__":
    http.server.HTTPServer(("", 80), RedirectHandler).serve_forever()
