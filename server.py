#!/usr/bin/env python
# -*- coding: utf-8 -*-

import BaseHTTPServer
import SimpleHTTPServer
from SocketServer import ThreadingMixIn
from StringIO import StringIO

from classifier import prepare_model


class HTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass


class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_PUT(self):
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)
        prediction = model.predict_single(data)
        if prediction == 1:
            self.send_response(221)
        else:
            self.send_response(220)
        self.send_header("Content-Type", "text/plain");
        self.send_header("Content-Length", 1)
        self.end_headers()

        self.wfile.write("%d" % prediction)


def test(HandlerClass=RequestHandler,
         ServerClass=HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass, protocol="HTTP/1.0")


if __name__ == '__main__':
    model = prepare_model()
    test()


