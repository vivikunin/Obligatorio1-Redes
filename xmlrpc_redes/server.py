import socket
import threading
import xml.etree.ElementTree as ET
import http_utils

class server:
    
    def atenderCliente(self, client):
        data = client.recv(1024) 
        info = http_utils.parse_http_response(data)
        response = self.stub(info[3])
        "loop para mandar"
        client.send(http_utils.build_http_response(response))

    def __init__(self, ip, puerto): 
        self.master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.master.bind((ip, puerto))
        self.master.listen()
        self.serve()
        
 


    def stub(self, data):
        root = ET.fromstring(data)
        method = root.find('methodName').text
        "poner try"
        params = [v[0].text for v in root.findall('params/param/value')]
        if method in self.methods:
            try:
                retorno = self.methods[method](*params)
            except Exception as e:
                #ver tipo error
                #construir body xml 
            response = http_utils.build_http_response(f"<error>{str(e)}</error>")
            client.sendall(response)

        else:
            #error que no esta definido el metodo previamente

    def add_method(self,proc1):
        self.methods[proc1.__name__] = proc1
    

    def serve(self): 
       while True:
            client, address = self.master.accept()
            t = threading.Thread(target=self.atenderCliente, args=(self, client))
            t.start()