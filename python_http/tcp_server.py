import logging
import socket
from time import sleep

logger = logging.getLogger()


class TCPServer:

    def __init__(self, host="localhost", port=8080):
        self.__socket = None
        self.host = host
        self.port = port

    @staticmethod
    def read_data(soc):
        data = b""
        while True:
            try:
                tmp = soc.recv(1024)
                if not tmp:
                    break
                data += tmp
            except socket.timeout:
                break
        return data

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as self.__socket:
            # self.__socket.setsockopt()
            self.__socket.bind((self.host, self.port))

            self.__socket.listen(10)

            # logger.info(f"Listening on {self.__socket.getsockname()}")
            print(f"Listening on port {self.port}, {self.__socket.getsockname()}")

            while True:
                soc, addr = self.__socket.accept()
                soc.settimeout(2)
                with soc:
                    # logger.info(f"Connected {addr}")
                    print(f"Connected {addr}")
                    data = self.read_data(soc)
                    print(f"Received data {data.decode('utf-8')}")
                    response = self.handle_request(data)
                    soc.sendall(response)
                    print(f"Closed {addr}")

    def handle_request(self, data):
        return data


if __name__ == '__main__':
    tcp_server = TCPServer()
    tcp_server.start()
