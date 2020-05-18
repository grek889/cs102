import asyncore
import asynchat
import datetime
import socket
import multiprocessin
import logging
import mimetypes
import os
from mimetypes import guess_type
import urllib
import argparse
from time import strftime, gmtime

def url_normalize(path):
    if path.startswith("/"):
        path = path[1:]
    if path.startswith("."):
        path = "/" + path
    while "../" in path:
        p1 = path.find("/..")
        p2 = path.rfind("/", 0, p1)
        if p2 != -1:
            path = path[:p2] + path[p1+3:]
        else:
            path = path.replace("/..", "", 1)
    path = path.replace("/./", "/")
    path = path.replace("/.", "")
    path = path.replace("%20", " ")
    if "?" in path:
        num = path.index("?")
        path = path[:num]
    return path

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)s] %(message)s'
    )
log = logging

responses = {
    200: ('OK', 'Request fulfilled, document follows'),
    400: ('Bad Request',
        'Bad request syntax or unsupported method'),
    403: ('Forbidden',
        'Request forbidden -- authorization will not help'),
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed',
        'Specified method is invalid for this resource.'),
}

class FileProducer(object):
    def __init__(self, file, chunk_size=4096):
        self.file = file
        self.chunk_size = chunk_size

    def more(self):
        if self.file:
            data = self.file.read(self.chunk_size)
            if data:
                return data
            self.file.close()
            self.file = None
        return ""

class AsyncServer(asyncore.dispatcher):

    def __init__(self, host="127.0.0.1", port=9000):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self, sock, addr):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print('Incoming connection from %s' % repr(addr))
            handler = AsyncHTTPRequestHandler(sock)


class AsyncHTTPRequestHandler(asynchat.async_chat):
    def __init__(self, sock):
        asynchat.async_chat.__init__(self, sock=sock)
        self.data = None
        self.method = None
        self.request = None
        self.file_type = ""
        self.path = ""
        self.query = None
        self.protocol = None
        self.sock = sock
        self.headers = {}
        self.response_body = ()
        self.response_headers = {}
        self.set_terminator(b"\r\n\r\n")

    def collect_incoming_data(self, data):
        data_parsed = data.decode('utf-8')
        if self.data is not None:
            self.parse_request()
        self.data = data_parsed
        self.ibuffer.append(data)

    def found_terminator(self):
        self.parse_request()

    def parse_request(self):
        if not self.request:
            self.request = {}
            self.data_list = self.data.split('\r\n')

            self.parse_headers()

            if not self.res_good:
                self.send_error(400, responses[400])
                self.shutdown = 1

        self.handle_request()

    def parse_headers(self):
        headers = self.data.split('\r\n')
        try:
            self.headers = dict([(i.split(':')[0], i.split(':')[1][1:]) for i in headers[1:]])
            self.method = headers[0].split()[0]
            self.query = headers[0].split()[1]
            self.protocol = headers[0].split()[2]
        except:
            return False
        return True

    def handle_request(self):
        method_name = 'do_' + self.method
        if not hasattr(self, method_name):
            self.send_error(405)
            self.handle_close()
            return
        handler = getattr(self, method_name)
        handler()

    def send_header(self, keyword, value):
        self.response_headers[keyword] = value

    def send_error(self, code, message=None):
        try:
            short_msg, long_msg = self.responses[code]
        except KeyError:
            short_msg, long_msg = '???', '???'
        if message is None:
            message = short_msg

        self.send_response(code, message)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Connection", "close")
        self.end_headers()

    def send_response(self, code, message):
        self.push("HTTP/1.1 {} {}\r\n".format(code, message).encode())

    def end_headers(self):
        self.push("\r\n".encode())

    def date_time_string(self):
        now = datetime.now()
        return now.strftime("%c")

    def send_head(self):
        self.send_header("Server", self.server_name)
        self.send_header("Date", self.date_time_string())
        self.send_header("Content-Length", self.content_len)
        self.send_header("Content-Type", self.file_type)
        self.send_header("Connection", "Closed")
        self.end_headers()

    def translate_path(self, path):
        query = 'files'
        query += path
        index_key = False
        image_key = False
        if query[-1] == '/':
            query += 'index.html'
            index_key = True
        query = url_normalize(query)
        if '?' in query:
            query = query[:query.find('?')]
        query = query.replace('%20', ' ')
        _, extension = os.path.splitext(query)
        return query, extension, index_key, image_key

    def do_GET(self):
        if self.path == '':
            self.path = 'index.html'
        try:
            f = open(self.path)
            f.close()
            self.file_type, _ = guess_type(self.path)
            self.content_len = os.path.getsize(self.path)
            # log.debug(f'CONTENT_LEN {uri}: {self.content_len}')
            self.send_response(code=200, message=responses[200][1])
            self.send_head()
            self.send_file()
        except FileNotFoundError:
            self.send_error(code=404, message=responses[404][1])
        except PermissionError:
            self.send_error(code=403, message=responses[403][1])
        self.handle_close()

    def do_HEAD(self):
        if self.path == '':
            self.path = 'index.html'
        try:
            self.file_type, _ = guess_type(self.path)
            self.content_len = os.path.getsize(self.path)
            self.send_response(code=200, message=responses[200][1])
            self.send_head()
        except FileNotFoundError:
            self.send_error(code=404, message=responses[404][1])
        except PermissionError:
            self.send_error(code=403, message=responses[403][1])
        self.handle_close()

    responses = {
        200: ('OK', 'Request fulfilled, document follows'),
        400: ('Bad Request',
            'Bad request syntax or unsupported method'),
        403: ('Forbidden',
            'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
            'Specified method is invalid for this resource.'),
    }

def parse_args():
    parser = argparse.ArgumentParser("Simple asynchronous web-server")
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9000)
    parser.add_argument("--log", dest="loglevel", default="info")
    parser.add_argument("--logfile", dest="logfile", default=None)
    parser.add_argument("-w", dest="nworkers", type=int, default=1)
    parser.add_argument("-r", dest="document_root", default=".")
    return parser.parse_args()


def run():
    server = AsyncServer(host=args.host, port=args.port)
    asyncore.loop()


if __name__ == "main":
    args = parse_args()

    logging.basicConfig(
        filename=args.logfile,
        level=getattr(logging, args.loglevel.upper()),
        format="%(name)s: %(process)d %(message)s")
    log = logging.getLogger(__name__)

    DOCUMENT_ROOT = args.document_root
    for _ in range(args.nworkers):
        p = multiprocessin.Process(target=run)
        p.start()