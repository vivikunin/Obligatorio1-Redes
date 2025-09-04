import base64
import datetime
from itertools import repeat
import socket
import threading
import xml.etree.ElementTree as ET
import http_utils

class server:
    def xmlrpc_to_python(self, value_elem):
        # Convierte un elemento <value> XMLRPC en el tipo Python correspondiente
        import xml.etree.ElementTree as ET
        if value_elem is None or len(value_elem) == 0:
            return value_elem.text if value_elem is not None else None
        child = value_elem[0]
        tag = child.tag
        if tag == "int" or tag == "i4":
            return int(child.text)
        elif tag == "double":
            return float(child.text)
        elif tag == "string":
            return child.text
        elif tag == "boolean":
            return child.text == "1"
        elif tag == "dateTime.iso8601":
            from datetime import datetime
            return datetime.strptime(child.text, "%Y%m%dT%H:%M:%S")
        elif tag == "array":
            data = child.find("data")
            return [self.xmlrpc_to_python(val) for val in data.findall("value")]
        elif tag == "struct":
            result = {}
            for member in child.findall("member"):
                name = member.find("name").text
                val = member.find("value")
                result[name] = self.xmlrpc_to_python(val)
            return result
        elif tag == "base64":
            import base64
            return base64.b64decode(child.text)
        else:
            return child.text
        
    def __init__(self, ip, puerto): 
        self.methods = {}
        self.master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.master.bind((ip, puerto))
        self.master.listen()
        print("Servidor escuchando en {}:{}".format(ip, puerto))

    
    def atenderCliente(self, client):
        data = b""
        while b"\r\n\r\n" not in data:
            print("Esperando datos del cliente...")
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
        #Hace el demarshalling del mensaje y arma la respuesta xml.
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
            params = [self.xmlrpc_to_python(v) for v in root.findall('params/param/value')]
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
        #identifica el tipo de dato dentro del mensaje xml en base a las etiquetas
        stack = [(val, None)]
        root_value = None
        import xml.etree.ElementTree as ET
        while stack:
            current, parent = stack.pop()
            value = ET.Element("value")
            if isinstance(current, int):
                tipo = ET.SubElement(value, "int")
                tipo.text = str(current)
            elif isinstance(current, float):
                tipo = ET.SubElement(value, "double")
                tipo.text = str(current)
            elif isinstance(current, str):
                tipo = ET.SubElement(value, "string")
                tipo.text = current
            elif isinstance(current, bool):
                tipo = ET.SubElement(value, "boolean")
                tipo.text = "1" if current else "0"
            elif isinstance(current, datetime.datetime):
                tipo = ET.SubElement(value, "dateTime.iso8601")
                tipo.text = current.strftime("%Y%m%dT%H:%M:%S")
            elif isinstance(current, list):
                array = ET.SubElement(value, "array")
                data = ET.SubElement(array, "data")
                for item in current:
                    data.append(self.definir_value(item))
            elif isinstance(current, dict):
                struct = ET.SubElement(value, "struct")
                for k, v in current.items():
                    member = ET.SubElement(struct, "member")
                    name = ET.SubElement(member, "name")
                    name.text = k
                    member.append(self.definir_value(v))
            else:
                tipo = ET.SubElement(value, "string")
                tipo.text = str(current)
            if parent is None:
                root_value = value
        return root_value

    def build_xmlrpc_response(self, retorno, error=0, faultString=""):
        #construye la respuesta xml-rcp
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
        # Agrega un nuevo método al servidor
        self.methods[proc1.__name__] = proc1
    
    def serve(self): 
        #método bloqueante para que el servidor acepte pedidos
        try:
            while True:
                client, address = self.master.accept()
                print("Cliente conectado desde {}:{}".format(address[0], address[1]))
                t = threading.Thread(target=self.atenderCliente, args=(client,))
                t.start()
        except KeyboardInterrupt:
            print("Cerrando conexión...")
            self.master.close()
