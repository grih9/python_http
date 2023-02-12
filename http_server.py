import copy
from string import Template

from tcp_server import TCPServer


class HTTPServer(TCPServer):
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
        403: "Forbidden",
        404: "Not Found",
        500: "Server error"
    }

    @classmethod
    def parse_request(cls, request):
        lines = request.split(b"\r\n")
        print(lines)
        request_line = lines[0]
        if not request_line:
            return cls.http_response(data=b"Bad request", status_code=400)

        words = request_line.split(b" ")
        print(words)
        method_type = words[0]
        print(method_type)
        # print(uri)
        # print(http)
        return cls.http_response(data=b"Hello world!", status_code=200)

    def handle_request(self, request):
        data = self.parse_request(request)
        print(data)
        return data.encode("utf-8")

    @classmethod
    def http_response(cls, data, status_code):
        response = cls.response_line.substitute(status_code=status_code, message=cls.status_codes[status_code])
        response += "\r\n".join(f"{key}: {value}" for key, value in cls.headers.items())
        response += cls.empty_line
        body = b"""<html><body><h1>""" + data + b"""</h1></body></html>"""
        response += body.decode("utf-8")

        return response

    def do_get(self, uri):
        pass

    def do_post(self, uri, body=None):
        pass


if __name__ == '__main__':
    http_server = HTTPServer()
    http_server.start()