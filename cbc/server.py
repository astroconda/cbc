import os
import http.server
import socketserver


class FileServer(object):
    def __init__(self, port, root=os.curdir):
        if isinstance(port, str):
            port = int(port)
            
        self.port = port
        self.handler = http.server.SimpleHTTPRequestHandler

    def run(self):
        httpd = socketserver.TCPServer(("", self.port), self.handler)
        print("{0} active on port {1}".format(self.__class__.__name__, self.port))
        httpd.serve_forever()