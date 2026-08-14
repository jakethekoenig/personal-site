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

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

# Start the server
with ReusableTCPServer(("", PORT), handler_object) as my_server:
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        pass
