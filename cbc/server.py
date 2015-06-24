import os
import http.server
import socketserver


class FileServer(object):
    def __init__(self, port, root=os.path.abspath(os.curdir), run=False):
        if isinstance(port, str):
            port = int(port)

        self.root = root
        self.port = port
        self.handler = http.server.SimpleHTTPRequestHandler

        if run:
            self.run()

    def run(self):
        os.chdir(self.root)
        httpd = socketserver.TCPServer(("", self.port), self.handler)
        print("{0} active on port {1}".format(self.__class__.__name__, self.port))
        httpd.handle_request()