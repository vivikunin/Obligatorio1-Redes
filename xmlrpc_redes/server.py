import datetime
from itertools import repeat
import socket
import threading
import xml.etree.ElementTree as ET
import http_utils

class server:
    def __init__(self, ip, puerto): 
        self.methods = {}
        self.master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.master.bind((ip, puerto))
        self.master.listen()         

    
    def atenderCliente(self, client):
        data = b""
        while b"\r\n\r\n" not in data:
            resto = client.recv(1024)
            if not resto:
                break
            data += resto

        # Separa header y body
        header, _, body = data.partition(b"\r\n\r\n")
        header_str = header.decode("utf-8")
        # Busca Content-Length
        import re
        match = re.search(r"Content-Length: (\d+)", header_str)
        content_length = int(match.group(1)) if match else 0

        # Calcula cuántos bytes faltan del body
        body_bytes = body
        while len(body_bytes) < content_length:
            resto = client.recv(1024)
            if not resto:
                break
            body_bytes += resto

        # Reconstruye el mensaje completo
        full_message = header + b"\r\n\r\n" + body_bytes

        info = http_utils.parse_http_response(full_message.decode("utf-8"))
        response = self.stub(info[2],client)
        data = http_utils.build_http_response(response)
        total_sent = 0
        while total_sent < len(data):
            remain = client.send(data[total_sent:])
            if remain == 0:
                raise RuntimeError("Socket connection broken")
            total_sent += remain    

    def stub(self, data, client):
        faultString = ""
        faultCode = 0
        retorno = None
        try:
            root = ET.fromstring(data)
            method_elem = root.find('methodName')
            if method_elem is None:
                raise Exception("NO_METHOD")
            method = method_elem.text
            if method not in self.methods:
                raise Exception("NO_METHOD")
            params = [v[0].text for v in root.findall('params/param/value')]
            retorno = self.methods[method](*params)
        except ET.ParseError:
            faultCode = 1
            faultString = "Error parseo de XML"
        except TypeError:
            faultCode = 3
            faultString = "Error en parámetros del metodo invocado"
        except RuntimeError:
            faultCode = 4
            faultString = "Error interno en la ejecución del metodo"
        except Exception as e:
            if str(e) == "NO_METHOD":
                faultCode = 2
                faultString = "No existe el metodo invocado"
            else:
                faultCode = 5
                faultString = f"Otros errores: {str(e)}"
        body = self.build_xmlrpc_response(retorno, faultCode, faultString)
        return body

    def definir_value(self, val):
        value = ET.Element("value")
        if type(val) == int:
            tipo = ET.SubElement(value, "int")
            tipo.text = str(val)
        elif type(val) == float:
            tipo = ET.SubElement(value, "double")
            tipo.text = str(val)
        elif type(val) == str:
            tipo = ET.SubElement(value, "string")
            tipo.text = val
        elif type(val) == bool:
            tipo = ET.SubElement(value, "boolean")
            tipo.text = "1" if val else "0"
        elif type(val) == datetime:
            tipo = ET.SubElement(value, "dateTime.iso8601")
            tipo.text = val.strftime("%Y%m%dT%H:%M:%S")
        elif type(val) == list:
            array = ET.SubElement(value, "array")
            data = ET.SubElement(array, "data")
            for item in val:
                data.append(self.definir_value(item))
        elif type(val) == dict:
            struct = ET.SubElement(value, "struct")
            for k, v in val.items():
                member = ET.SubElement(struct, "member")
                name = ET.SubElement(member, "name")
                name.text = k
                member.append(self.definir_value(v))
        else:
            tipo = ET.SubElement(value, "string")
            tipo.text = str(val)
        return value

    def build_xmlrpc_response(self, retorno, error=0, faultString=""):
        import xml.etree.ElementTree as ET
        from datetime import datetime
        if error == 0:
            methodResponse = ET.Element("methodResponse")
            params = ET.SubElement(methodResponse, "params")
            param = ET.SubElement(params, "param")
            param.append(self.definir_value(retorno))
            return ET.tostring(methodResponse, encoding="utf-8", xml_declaration=True)
        else:
            methodResponse = ET.Element("methodResponse")
            fault = ET.SubElement(methodResponse, "fault")
            value = ET.SubElement(fault, "value")
            struct = ET.SubElement(value, "struct")
            member = ET.SubElement(struct, "member")
            name = ET.SubElement(member, "name")
            name.text = "faultCode"
            value = ET.SubElement(member, "value")
            value.text = str(error)
            member = ET.SubElement(struct, "member")
            name = ET.SubElement(member, "name")
            name.text = "faultString"   
            value = ET.SubElement(member, "value")
            value.text = faultString
            return ET.tostring(methodResponse, encoding="utf-8", xml_declaration=True)

    def add_method(self,proc1):
        self.methods[proc1.__name__] = proc1
    
    def serve(self): 
        try:
            while True:
                client, address = self.master.accept()
                t = threading.Thread(target=self.atenderCliente, args=(client,))
                t.start()
        except KeyboardInterrupt:
            print("Cerrando conexión...")
            self.master.close()

if __name__ == "__main__":        
        server = server("localhost", 8000)

        def suma(a, b):
            return int(int(a) + int(b))

        def concat(a, b):
            return a + b

        def find(a, b):
            return a.find(b)
        
        def div(a,b):
            return a/b

        server.add_method(suma)
        server.add_method(concat)
        server.add_method(find)
        server.add_method(div)
        server.serve()

