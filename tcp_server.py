import logging
import socket
from time import sleep

logger = logging.getLogger()


class TCPServer:

    def __init__(self, host="localhost", port=8080):
        self.__socket = None
        self.host = host
        self.port = port

    def start(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        # self.socket.setsockopt()
        self.__socket.bind((self.host, self.port))

        self.__socket.listen(10)

        logger.info(f"Listening on {self.__socket.getsockname()}")
        print(f"Listening on port {self.port}, {self.__socket.getsockname()}")

        while True:
            soc, addr = self.__socket.accept()
            logger.info(f"Connected {addr}")
            print(f"Connected {addr}")
            data = soc.recv(1024)
            response = self.handle_request(data)
            soc.sendall(response)
            soc.close()
            print(f"Closed {addr}")

    def handle_request(self, data):
        return data


if __name__ == '__main__':
    tcp_server = TCPServer()
    tcp_server.start()
