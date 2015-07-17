import argparse
import os
import http.server
import socketserver
import socket
from threading import Thread

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


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

    def run(self, forever=False):
        os.chdir(self.root)
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = Server(('localhost', self.port), self.handler, True)
        print('{0} active on port {1} ({2})'.format(self.__class__.__name__, self.port, self.root))
        if not forever:
            self.httpd.handle_request()
        else:
            self.httpd.serve_forever()
        self.close()

    def close(self):
        self.httpd.server_close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--root', default=os.path.abspath(os.curdir), help='Path to files')
    parser.add_argument('-p', '--port', type=int, default=8888, help='TCP port')
    parser.add_argument('-s', '--single', action='store_false')
    args = parser.parse_args()

    fileserver = FileServer(args.port, args.root)
    fileserver.run(forever=args.single)


if __name__ == '__main__':
    main()

