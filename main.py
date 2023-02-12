from tcp_server import TCPServer
from tcp_client import TCPClient

server = TCPServer()
server.start()

client = TCPClient()
client.connect("Hello!")
client.connect("I am here!")
