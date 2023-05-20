import copy
import uuid
from string import Template

from tcp_server import TCPServer


class HTTPServer(TCPServer):
    def __init__(self):
        super().__init__()
        self.realm = f"{self.host}:{self.port}"
        self.nonce = "dcd98b7102dd2f0e8b11d0f600bfb0c093"
        self.opaque = uuid.uuid4().hex

    data = b"HTTP/1.1 200 OK\nContent-Type: text/plain\nContent-Length: 12\n\nHello world!"
    response_line = Template("HTTP/1.1 $status_code $message\r\n")

    headers = {
        "Server": "python-html-server",
        "Content-Type": "text/html"
    }
    empty_line = "\r\n\r\n"
    status_codes = {
        200: "OK",
        400: "Bad request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Server error"
    }

    def check_auth(self, data):
        is_authorized = "Authorization" in data
        if not is_authorized:
            headers = copy.deepcopy(self.headers)
            headers["WWW-Authenticate"] = f'Digest realm="{self.realm}", ' \
                                          f'nonce="{self.nonce}", ' \
                                          f'opaque="{self.opaque}", ' \
                                          f'algorithm=MD5, qop="auth"'
            return self.http_response(data=b"Authorize please!", status_code=401, headers=headers, send_data=False)
        auth_data = data["Authorization"]
        print(f"{auth_data}")

    def parse_request(self, request):
        lines = request.split(b"\r\n")
        request_line = lines[0]
        if not request_line:
            return self.http_response(data=b"Bad request", status_code=400, send_data=False)

        words = request_line.split(b" ")
        data = lines[1:]
        headers, body = data[:data.index(b'')], data[data.index(b'') + 1:]
        body = [el.decode("utf-8") for el in body]
        headers = [el.decode("utf-8") for el in headers]
        headers = {s[:s.find(":")]: s[s.find(":") + 2:] for s in headers}
        print(f"{headers=}")
        print(f"{body=}")

        method_type = words[0].decode("utf-8")
        uri = words[1].decode("utf-8")
        http = words[2].decode("utf-8")
        print(f"{method_type=} {uri=} {http=}")
        self.check_auth(lines)
        return self.http_response(data=b"Hello world!" + uri.encode("utf-8"), status_code=200)

    def handle_request(self, request):
        data = self.parse_request(request)
        print(data)
        return data.encode("utf-8")

    def http_response(self, data, status_code, send_data=True, headers=None):
        headers = self.headers if headers is None else headers
        response = self.response_line.substitute(status_code=status_code, message=self.status_codes[status_code])
        response += "\r\n".join(f"{key}: {value}" for key, value in headers.items())
        if send_data:
            response += self    .empty_line
            body = b"""<html><body><h1>""" + data + b"""</h1></body></html>"""
            response += body.decode("utf-8")

        return response

    def do_get(self, uri):
        pass

    def do_post(self, uri, body=None):
        pass


import sys
import re
from pprint import pprint
from base64 import *
from time import time
import md5

def md5sum(data):
  m = md5.new()
  m.update(data)
  return m.hexdigest()

def calc_ha1(username='test', password="test"):
    return md5sum(f'{username}:secret:{password}')

def check_authorization(env, resp):
    matches = re.compile('Digest \s+ (.*)', re.I + re.X).match(resp)
    if not matches:
        return None

    vals = re.compile(', \s*', re.I + re.X).split(matches.group(1))

    dict = {}

    pat = re.compile('(\S+?) \s* = \s* ("?) (.*) \\2', re.X)
    for val in vals:
        ms = pat.match(val)
        if not ms:
            raise 'ERROR'
        dict[ms.group(1)] = ms.group(3)

    ha1 = calc_ha1(dict['username'])
    ha2 = md5sum(f"{env['REQUEST_METHOD']}:{dict['uri']}")
    myresp = md5sum(f"{ha1}:{dict['nonce']}:{dict['nc']}:{dict['cnonce']}:{dict['qop']}:{ha2}")
    if myresp != dict['response']:
        print >> sys.stderr, "Auth failed!"
        return None

      # TODO: check nonce's timestamp
    cur_nonce = int(time())
    aut_nonce = int(b64decode(dict['nonce']))
    pprint({'cli': aut_nonce, 'srv': cur_nonce}, sys.stderr, 2)
    if cur_nonce - aut_nonce > 10:    # 10sec
        # print >>sys.stderr, "Too old!"
        return False

    return dict['username']

def app(environ, start_response):
  heads = wsgiref.headers.Headers([])

  heads.add_header('Content-Type', 'text/plain')

  auth = environ.get('HTTP_AUTHORIZATION', '')
  state = check_authorization(environ, auth)
  if state:
    start_response('200 OK', heads.items())
    return ['OK!']

  nonce = b64encode(str(int(time())))
  auth_head = 'Digest realm="secret", nonce="%s", algorithm=MD5, qop="auth"' % (nonce)
  if state == False:
    auth_head += ', stale=true'
  heads.add_header('WWW-Authenticate', auth_head)
  start_response('401 Authorization Required', heads.items())

  return ['Hello, World!']

if __name__ == '__main__':
    http_server = HTTPServer()
    http_server.start()
