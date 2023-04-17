from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

class FancyHTTPRequesHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        print(self.headers)
        print(self.client_address)

server = HTTPServer(('', 8080), FancyHTTPRequesHandler)
server.serve_forever()

