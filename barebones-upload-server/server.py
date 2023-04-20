from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

from os import mkdir

class FancyHTTPRequesHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        with open("index.html", "rb") as fp:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            try:
                self.wfile.write(fp.read())
            except BrokenPipeError:
                # from my understanding some browsers will assume this resource is
                # unmodified and simply close the connection
                ...

        print(f"\nRequest headers:\n{self.headers}")

    def do_POST(self):
        if self.path != "/upload-image":
            print("Invalid POST request")

        # this was hardcoded inspecting examples, so it might break anytime :D

        content_length = int(self.headers["Content-Length"])
        content_type = self.headers["Content-Type"]
        # we are inspecting the followin bytestring
        # "Content-Type': multipart/form-data; boundary=..."
        boundary = content_type.split("=")[1].encode()
        content = self.rfile.read(content_length)

        # get the image offset within body
        image_start = content.find(b"\r\n\r\n")
        image_end = content.find(b"--" + boundary + b"--")

        # getting content disposition information at the top of the body, expected bytestring
        # "Content-Disposition: form-data; name="file"; filename="something.jpg""
        meta_data = content[:image_start].split(b"\r\n")

        for item in meta_data:
            if b"Content-Disposition" in item:
                content_disp_header = item.split(b"; ")
                break
        
        for k_v in content_disp_header:
            if b"filename" in k_v:
                filename = k_v.split(b"=")[1][1:-1].decode("utf-8")
        
        with open("assets/" + filename, "wb+") as fp:
            fp.write(content[image_start + 4:image_end])
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Request received')

        print(f"\nRequest headers:\n{self.headers}")


PORT = 8080

server = HTTPServer(('', PORT), FancyHTTPRequesHandler)
try:
    mkdir("assets")
except FileExistsError:
    ...

print(f"Listening on http://localhost:{PORT}")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nKeyboard interrupt received")

