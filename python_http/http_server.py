import copy
import logging
import re
import sys
import time
import uuid
from hashlib import md5
from string import Template

from settings import Settings
from tcp_server import TCPServer

logger = logging.getLogger()


class HTTPServer(TCPServer):
    def __init__(self, host="localhost", port=8080, root_package="./webroot"):
        super().__init__(host=host, port=port)
        self.root_package = root_package
        self.opaque = uuid.uuid4().hex

    data = b"HTTP/1.1 200 OK\nContent-Type: text/plain\nContent-Length: 12\n\nHello world!"
    response_line = Template("HTTP/1.1 $status_code $message\r\n")

    headers = {
        "Server": "python-html-server",
        "Content-Type": "text/html"
    }
    empty_line = b"\r\n\r\n"
    status_codes = {
        200: "OK",
        400: "Bad request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Server error"
    }

    @staticmethod
    def md5sum(data):
        md_hash = md5()
        md_hash.update(data.encode("utf-8"))
        return md_hash.hexdigest()

    def calc_ha1(self, username="test", realm="auth", password="test"):
        return self.md5sum(f'{username}:{realm}:{password}')

    def check_auth(self, data, method_type, uri):
        is_authorized = "Authorization" in data
        headers = copy.deepcopy(self.headers)
        nonce = self.md5sum(str(time.time()))
        realm = "auth"
        if uri in Settings.admin_resources or uri in Settings.admin_login_resources:
            realm = "admin"
        if method_type not in Settings.need_auth_methods:
            return self.http_response(data=b"Method type " +
                                           method_type.encode("utf-8") +
                                           b" is not allowed for " +
                                           uri.encode("utf-8"), status_code=400, headers=headers), None
        headers["WWW-Authenticate"] = f'Digest realm="{realm}", ' \
                                      f'nonce="{nonce}", ' \
                                      f'opaque="{self.opaque}", ' \
                                      f'algorithm=MD5, qop="auth"'
        if not is_authorized:
            return self.http_response(data=b"Authorize please!", status_code=401, headers=headers), None

        auth_data = data["Authorization"]
        matches = re.compile("Digest \s+ (.*)", re.I + re.X).match(auth_data)
        if not matches:
            return self.http_response(data=b"Reauthorize please!", status_code=401, headers=headers), None

        vals = re.compile(", \s*", re.I + re.X).split(matches.group(1))
        auth_data = {}

        pat = re.compile('(\S+?) \s* = \s* ("?) (.*) \\2', re.X)
        for val in vals:
            ms = pat.match(val)
            if not ms:
                return self.http_response(data=b"Reauthorize please!", status_code=401, headers=headers), None
            auth_data[ms.group(1)] = ms.group(3)

        if auth_data["opaque"] != self.opaque:
            return self.http_response(data=b"Reauthorize please!", status_code=401,
                                      headers=headers), auth_data["username"]

        if uri in Settings.login_resources and "auth" not in auth_data["realm"]:
            return self.http_response(data=b"Reauthorize please!", status_code=401, headers=headers), None
        elif uri in Settings.admin_login_resources and "admin" not in auth_data["realm"]:
            return self.http_response(data=b"Reauthorize please!", status_code=401, headers=headers), None

        # ha1 = self.calc_ha1(auth_data["username"])
        ha1 = Htdigest().read(auth_data["username"], auth_data["realm"])
        ha2 = self.md5sum(f"{method_type}:{uri}")
        my_resp = self.md5sum(f"{ha1}:{auth_data['nonce']}:{auth_data['nc']}:{auth_data['cnonce']}:{auth_data['qop']}:{ha2}")

        if my_resp != auth_data['response']:
            logger.info(f"Wrong password. Auth failed for user {auth_data['username']} with realm {auth_data['realm']}")
            return self.http_response(data=b"Auth_failed!", status_code=401,
                                      headers=headers, send_data=True), auth_data["username"]
        if auth_data["realm"] == "auth":
            if uri in Settings.admin_resources or uri in Settings.admin_login_resources:
                return self.http_response(data=uri.encode("utf-8") + b" forbidden with auth only rights!",
                                          status_code=403), auth_data["username"]
        return None, auth_data["username"]

    def parse_request(self, request):
        lines = request.split(b"\r\n")
        request_line = lines[0]
        if not request_line:
            return None

        words = request_line.split(b" ")
        data = lines[1:]
        headers, body = data[:data.index(b'')], data[data.index(b'') + 1:]
        body = [el.decode("utf-8") for el in body]
        headers = [el.decode("utf-8") for el in headers]
        headers = {s[:s.find(":")]: s[s.find(":") + 2:] for s in headers}
        # print(f"headers={headers}")
        # print(f"body={body}")

        method_type = words[0].decode("utf-8")
        uri = words[1].decode("utf-8")
        http = words[2].decode("utf-8")
        logger.info(f"{method_type} {uri} {http}")
        if method_type == "GET":
            return self.do_get(headers, uri)
        if method_type == "POST":
            return self.do_post(uri, headers, body)
        else:
            return self.http_response(data=b"Method type " +
                                           method_type.encode("utf-8") +
                                           b" is not allowed for " +
                                           uri.encode("utf-8"), status_code=400, headers=headers), None

    def handle_request(self, request):
        data = self.parse_request(request)
        return data

    def http_response(self, data=b"", status_code=200, page=None, send_data=True, headers=None):
        headers = self.headers if headers is None else headers
        response = self.response_line.substitute(status_code=status_code, message=self.status_codes[status_code])
        response += "\r\n".join(f"{key}: {value}" for key, value in headers.items())
        response = response.encode("utf-8")
        if send_data:
            response += self.empty_line
            if page:
                response += page
            else:
                body = b"""<html><body><h1>""" + data + b"""</h1></body></html>"""
                response += body
        logger.info(f"{status_code} {len(data)}")
        return response

    def do_get(self, headers, uri):
        if uri in Settings.need_auth:
            res, user = self.check_auth(headers, "GET", uri)
            if res:
                return res
            try:
                with open(self.root_package + uri, "rb") as f:
                    data = f.read()
                    return self.http_response(page=data, status_code=200)
            except FileNotFoundError:
                data = b"This is " + uri.encode("utf-8") + b" page. Enable with auth only. User: " + \
                       user.encode("utf-8")
                if user in Settings.admins:
                    data = b"This is " + uri.encode("utf-8") + b" page. This page for admins only. User: " + \
                           user.encode("utf-8")
                return self.http_response(data=data, status_code=200)
        else:
            if uri in Settings.login_resources or uri in Settings.admin_login_resources:
                res, user = self.check_auth(headers, "GET", uri)
                if res:
                    return res
                role = b"admin" if uri in Settings.admin_login_resources else b"auth"
                data = b"You authorized as user: " + user.encode("utf-8") + b" with role: " + role
                return self.http_response(data=data, status_code=200)
            try:
                with open(self.root_package + uri, "rb") as f:
                    data = f.read()
                    return self.http_response(page=data, status_code=200)
            except FileNotFoundError:
                return self.http_response(data=uri.encode("utf-8") + b" not found!", status_code=404)

    def do_post(self, uri, headers, body=None):
        if uri in Settings.need_auth:
            res, user = self.check_auth(headers, "POST", uri)
            if res:
                return res
        data = b"You did POST on " + uri.encode("utf-8")
        return self.http_response(data=data, status_code=200)


class Htdigest:
    htdigest_file = "/usr/local/sbin/.htdigest"
    # admin admin1
    # user user1

    def create(self, username, realm, password):
        with open(file=self.htdigest_file, mode="a") as f:
            f.write(f"{username}:{realm}:{HTTPServer.md5sum(f'{username}:{realm}:{password}')}")
            return True

    def read(self, username, realm):
        with open(file=self.htdigest_file) as f:
            data = f.readlines()
            for d in data:
                parts = d.strip("\n").strip("\r").split(":")
                if parts[0] == username and ":".join(parts[1:-1]) == realm:
                    return parts[-1]
            return 0


if __name__ == "__main__":
    logging.basicConfig(filename="/var/log/digitalauthweb/digitalauthweb.log", level=logging.DEBUG,
                        format="%(asctime)s %(message)s")
    argv = sys.argv
    if len(argv) != 3:
        raise Exception
    in_port = int(argv[1])
    in_root_package = argv[2]
    http_server = HTTPServer(port=in_port, root_package=in_root_package)
    # Htdigest().create("user2", http_server.realm, "user2")
    # Htdigest().create("test", http_server.realm, "test")
    http_server.start()
