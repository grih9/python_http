import copy
import uuid
import time
import subprocess
import re
from string import Template
from hashlib import md5
from tcp_server import TCPServer

NON_SECRET = ["/", "/start", "/go/123"]
SECRET = ["/secret", "/admin"]
SUPER_SECRET = ["/super_secret"]
ROUTES = NON_SECRET + SECRET + SUPER_SECRET

user = ["/secret"]


class Htdigest:
    htdigest_file = ".htdigest"
    # def create(self):
    #     subprocess.run()

    def read(self, username, realm):
        with open(file=self.htdigest_file) as f:
            data = f.readlines()
            for d in data:
                parts = d.split(":")
                if parts[0] == username and ":".join(parts[1:-1]) == realm:
                    return parts[-1]
            return 0


class HTTPServer(TCPServer):
    def __init__(self, host="localhost", port=8080):
        super().__init__(host=host, port=port)
        self.realm = f"{self.host}:{self.port}"
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

    def md5sum(self, data):
        md_hash = md5()
        md_hash.update(data.encode("utf-8"))
        return md_hash.hexdigest()

    def calc_ha1(self, username='test', password="test"):
        # get_password(username)
        return self.md5sum(f'{username}:{self.realm}:{password}')

    def check_auth(self, data, method_type, uri):
        is_authorized = "Authorization" in data
        headers = copy.deepcopy(self.headers)
        nonce = self.md5sum(str(time.time()))
        headers["WWW-Authenticate"] = f'Digest realm="{self.realm}", ' \
                                      f'nonce="{nonce}", ' \
                                      f'opaque="{self.opaque}", ' \
                                      f'algorithm=MD5, qop="auth"'
        if not is_authorized:
            return self.http_response(data=b"Authorize please!", status_code=401, headers=headers, send_data=False)

        auth_data = data["Authorization"]
        matches = re.compile('Digest \s+ (.*)', re.I + re.X).match(auth_data)
        if not matches:
            return self.http_response(data=b"Reauthorize please!", status_code=401, headers=headers, send_data=True)

        vals = re.compile(', \s*', re.I + re.X).split(matches.group(1))
        auth_data = {}

        pat = re.compile('(\S+?) \s* = \s* ("?) (.*) \\2', re.X)
        for val in vals:
            ms = pat.match(val)
            if not ms:
                return self.http_response(data=b"Reauthorize please!", status_code=401, headers=headers, send_data=True)
            auth_data[ms.group(1)] = ms.group(3)

        if auth_data["opaque"] != self.opaque:
            return self.http_response(data=b"Reauthorize please!", status_code=401, headers=headers, send_data=True)

        # ha1 = self.calc_ha1(auth_data["username"])
        ha1 = Htdigest().read(auth_data["username"], auth_data["realm"])
        ha2 = self.md5sum(f"{method_type}:{uri}")
        my_resp = self.md5sum(f"{ha1}:{auth_data['nonce']}:{auth_data['nc']}:{auth_data['cnonce']}:{auth_data['qop']}:{ha2}")

        if my_resp != auth_data['response']:
            return self.http_response(data=b"Auth_failed!", status_code=401, headers=headers, send_data=True)

        if auth_data["uri"] not in user:
            return self.http_response(data=b"Forbidden!", status_code=403, send_data=True)

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
        print(f"headers={headers}")
        print(f"body={body}")

        method_type = words[0].decode("utf-8")
        uri = words[1].decode("utf-8")
        http = words[2].decode("utf-8")
        print(f"method_type={method_type} uri={uri} http={http}")
        if uri in SECRET or uri in SUPER_SECRET:
            res = self.check_auth(headers, method_type, uri)
            if res:
                return res
            return self.http_response(data=b"This is " + uri.encode("utf-8") + b" page", status_code=200)
        elif uri in NON_SECRET:
            return self.http_response(data=b"This is " + uri.encode("utf-8") + b" page", status_code=200)
        else:
            return self.http_response(data=uri.encode("utf-8") + b" not found!", status_code=404)

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


if __name__ == '__main__':
    http_server = HTTPServer(port=8050)
    http_server.start()
