import socket
import threading
import http_utils

class server:
    def __init__(self):
        self.master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.master.bind(('localhost', 0)) # confirmar puerto
        self.master.listen(10) # preguntar cantidad
        client, address = self.master.accept()
        t = threading.Thread(target=funcion, args=(client,))
        t.start()

    def funcion(self, client):
        data = client.recv(1024)
        info = http_utils.parse_http_response(data) 