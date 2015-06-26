import os
import http.server
import socketserver
import socket
from threading import Thread

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    #def server_bind(self):
    #    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #    self.socket.bind(self.server_address)


class FileServer(object):
    def __init__(self, port, root=os.path.abspath(os.curdir), run=False):
        if isinstance(port, str):
            port = int(port)

        self.root = root
        self.port = port
        self.handler = http.server.SimpleHTTPRequestHandler
        self.httpd = None

        if run:
            self.run()

    def run(self):
        os.chdir(self.root)
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = Server(('localhost', self.port), self.handler, True)
        #self.httpd.allow_reuse_address = True
        #self.httpd.server_bind()
        #self.httpd.server_activate()
        print('{0} active on port {1} ({2})'.format(self.__class__.__name__, self.port, self.root))

        th = Thread(target=self.httpd.handle_request, args=(), daemon=True)
        th.start()

    def close(self):
        self.httpd.server_close()