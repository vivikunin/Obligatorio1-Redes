import socket
import threading
import xml.etree.ElementTree as ET
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
        response = self.stub(info[3])
        client.sendall(http_utils.build_http_response(response))


    def stub(self, data):
        root = ET.fromstring(data)
        method = root.find('methodName').text
        params = [v[0].text for v in root.findall('params/param/value')]
        if method in self.methods:
            try:
                retorno = self.methods[method](*params)
            except Exception as e:
                #ver tipo error
            #construir body xml manito ya sabes
            response = http_utils.build_http_response(f"<error>{str(e)}</error>")
            client.sendall(response)

        else:
            #error que no esta definido el metodo previamente

    def add_method(self,proc1):
        self.methods[proc1.__name__] = proc1
    

        


    def serve(self):
