import datetime
from itertools import repeat
import socket
import threading
import xml.etree.ElementTree as ET
import http_utils
from client import *

class server:
    def __init__(self, ip, puerto): 
        self.methods = {}
        self.master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.master.bind((ip, puerto))
        self.master.listen()         

    
    def atenderCliente(self, client):
        data = client.recv(1024) 
        info = http_utils.parse_http_response(data)
        response = self.stub(info[3])
        data = http_utils.build_http_response(response)
        total_sent = 0
        while total_sent < len(data):
            remain = client.send(data[total_sent:])
            if remain == 0:
                raise RuntimeError("Socket connection broken")
            total_sent += remain   

    def stub(self, data):
        faultString=""
        faultCode=0
        try:
            root = ET.fromstring(data)
            method = root.find('methodName').text
            if method not in self.methods:
                raise Exception (e=2)
            params = [v[0].text for v in root.findall('params/param/value')]
            retorno = self.methods[method](*params)
        except TypeError:
                faultCode = 3
                faultString = "Error en parámetros del método invocado"
        except RuntimeError:
                faultCode = 4
                faultString = "Error interno en la ejecución del método"
        except Exception as e:
            if e==ET.ParseError:
                faultCode = 1
                faultString = "Error parseo de XML"
            elif e==2:
                faultCode = 2
                faultString = "No existe el método invocado"
            else:
                faultCode = 5
                faultString = f"Otros errores: {str(e)}"
        body = self.build_xmlrpc_response(retorno, faultCode, faultString)
        response = http_utils.build_http_response(body)
        while total_sent < len(response):
            remain = self.client.send(response[total_sent:])
            if remain == 0:
                raise RuntimeError("Socket connection broken")
            total_sent += remain   

    def serialize_value(self, val):
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
                data.append(self.serialize_value(item))
        elif type(val) == dict:
            struct = ET.SubElement(value, "struct")
            for k, v in val.items():
                member = ET.SubElement(struct, "member")
                name = ET.SubElement(member, "name")
                name.text = k
                member.append(self.serialize_value(v))
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
            param.append(self.serialize_value(retorno))
            return ET.tostring(methodResponse, encoding="utf-8", xml_declaration=True)
        else:
            methodResponse = ET.Element("methodResponse")
            fault = ET.SubElement(methodResponse, "fault")
            value = ET.SubElement(fault, "value")
            struct = ET.SubElement(value, "struct")
            member = ET.SubElement(struct, "member")
            name = ET.SubElement(member, "name")
            name.append("faultCode")
            value = ET.SubElement(member, "value")
            value.append(str(error))
            member = ET.SubElement(struct, "member")
            name = ET.SubElement(member, "name")
            name.append("faultString")
            value = ET.SubElement(member, "value")
            value.append(faultString)

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
