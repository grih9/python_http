import logging
import socket
from time import sleep

logger = logging.getLogger()


class TCPClient:

    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = port

        self.__socket = None

    def connect(self, msg: str):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as self.__socket:
            self.__socket.connect((self.host, self.port))
            self.__socket.sendall(msg.encode("utf-8"))
            # logger.info("Message sent")
            print("Message sent")
            data = self.__socket.recv(1024)
            # logger.info(f"Received data {data}")
            print(f"Received data {data}")
            sleep(2)


if __name__ == '__main__':
    client = TCPClient()
    counter = 0
    while True:
        counter += 1
        client.connect(f"Hello from client! ({counter})")
