import http.server
import socketserver

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        if '.' not in self.path:
            self.send_header("Content-type", "text/html")
        http.server.SimpleHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 8070
my_server = socketserver.TCPServer(("", PORT), handler_object)

my_server.allow_reuse_address = True
# Start the server
my_server.serve_forever()
