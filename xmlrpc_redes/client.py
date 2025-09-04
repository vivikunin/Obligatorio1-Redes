from multiprocessing.dummy.connection import Client
import socket
import sys
import xml.etree.ElementTree as ET
import datetime
import http_utils

class client:

    def __init__(self, address, port):
        self.connect(address, port)

    def connect(self, address, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((address, port))
        print("Conectado al servidor en {}:{}".format(address, port))
        return self
    
    def __getattr__(self, name):
        return lambda *args: self.stub(name, *args)

    def definir_value(self, val):
        import xml.etree.ElementTree as ET
        import base64
        stack = [(val, None)]
        root_value = None
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
            elif isinstance(current, bytes):
                tipo = ET.SubElement(value, "base64")
                tipo.text = base64.b64encode(current).decode("ascii")
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

    def build_xmlrpc_request(self, metodo, params):
        methodCall = ET.Element("methodCall")
        methodName = ET.SubElement(methodCall, "methodName")
        methodName.text = metodo
        params_elem = ET.SubElement(methodCall, "params")
        for param in params:
            param_elem = ET.SubElement(params_elem, "param")
            param_elem.append(self.definir_value(param))
        return ET.tostring(methodCall, encoding="utf-8", xml_declaration=True)

    def stub(self, name, *args):
        # 1. Construir el XML-RPC
        xml = self.build_xmlrpc_request(name, args)
        value_elem = self.enviar_y_recibir(xml)
        return value_elem

    def enviar_y_recibir(self, xml):
        # 2. Enviar la solicitud
        mensaje = http_utils.build_http_post_request("/", "localhost:8000", xml.decode())
        total_sent = 0
        while total_sent < len(mensaje):
            remain = self.sock.send(mensaje[total_sent:].encode('utf-8'))
            if remain == 0:
                raise RuntimeError("Socket connection broken")
            total_sent += remain   
        # 3. Recibir la respuesta completa
        data = b""
        while b"\r\n\r\n" not in data:
            resto = self.sock.recv(1024)
            if not resto:
                break
            data += resto
        # Separa header y body
        header, _, body = data.partition(b"\r\n\r\n")
        header_str = header.decode("utf-8")
        try:
            if "200 OK" not in header_str:
                raise Exception("Respuesta HTTP no exitosa: " + header_str.splitlines()[0])
        except Exception as e:
            print(e)
            self.master.close()
        # Busca Content-Length
        import re
        match = re.search(r"Content-Length: (\d+)", header_str)
        content_length = int(match.group(1)) if match else 0

        # Calcula cuántos bytes faltan del body
        body_bytes = body
        while len(body_bytes) < content_length:
            resto = self.sock.recv(1024)
            if not resto:
                break
            body_bytes += resto

        root = ET.fromstring(body_bytes.decode("utf-8"))
        fault_elem = root.find("fault")
        try:
            if fault_elem is not None:
                fault_value = fault_elem.find("value")
                struct = fault_value.find("struct") if fault_value is not None else None
                if struct is not None:
                    fault_code = None
                    fault_string = None
                    for member in struct.findall("member"):
                        name = member.find("name").text
                        val = member.find("value").text
                        if name == "faultCode":
                            fault_code = val
                        elif name == "faultString":
                            fault_string = val
                    raise Exception(f"XML-RPC Fault {fault_code}: {fault_string}")

            value_elem = root.find(".//value")
            if value_elem is not None:
                value_elem = self.extraer_value(value_elem)
            return value_elem
        except Exception as e:
            print(e)
            
        
    def extraer_value(self, value_elem):
        int_elem = value_elem.find("int")
        if int_elem is not None:
            return int(int_elem.text)
        int_elem = value_elem.find("i4")
        if int_elem is not None:
            return int(int_elem.text)
        double_elem = value_elem.find("double")
        if double_elem is not None:
            return float(double_elem.text)
        string_elem = value_elem.find("string")
        if string_elem is not None:
            return string_elem.text
        boolean_elem = value_elem.find("boolean")
        if boolean_elem is not None:
            return bool(int(boolean_elem.text))
        date_elem = value_elem.find("dateTime.iso8601")
        if date_elem is not None:
            return datetime.datetime.strptime(date_elem.text, "%Y%m%dT%H:%M:%S")
        base64_elem = value_elem.find("base64")
        if base64_elem is not None:
            import base64
            return base64.b64decode(base64_elem.text)
        array_elem = value_elem.find("array")
        if array_elem is not None:
            data_elem = array_elem.find("data")
            return [self.extraer_value(val) for val in data_elem.findall("value")]
        struct_elem = value_elem.find("struct")
        if struct_elem is not None:
            result = {}
            for member in struct_elem.findall("member"):
                name = member.find("name").text
                val = member.find("value")
                result[name] = self.extraer_value(val)
            return result
        return value_elem.text
    
    def close(self):
        if hasattr(self, "sock"):
            self.sock.close()
            print("Socket del cliente cerrado correctamente.")

if __name__ == "__main__":
    try:
        cliente = client("localhost", 8000)
        #response = cliente.suma(1, 2)
        #print("Respuesta del servidor:", response)
        response = cliente.suma(1,3)
        if response != None:
            print("Respuesta del servidor:", response)
        cliente = client("localhost", 8000)
        response = cliente.suma(1,777)
        if response != None:
            print("Respuesta del servidor:", response)

        # Supongamos que la clase se llama Client
        cliente = client("localhost", 8001)

        # Parámetros de ejemplo
        ejemplo_lista = [12, 5, 8, 20, 33]
        ejemplo_dicc = {"a": 3, "b": 7, "c": 1}
        ejemplo_numero = 4
        ejemplo_texto = "Redes de computadoras"
        ejemplo_bandera = True
        ejemplo_fecha = datetime.datetime(2023, 10, 5)

        # Llamada al procedimiento remoto
        try:
            response = cliente.funcion_muy_complicada(
                ejemplo_lista,
                ejemplo_dicc,
                ejemplo_numero,
                ejemplo_texto,
                ejemplo_bandera,
                ejemplo_fecha
            )
            if response is not None:
                print("Respuesta del servidor:", response)
            else:
                print("El servidor no devolvió respuesta.")
        except Exception as e:
            print("Error al invocar el procedimiento remoto:", e)
        
        cliente = client("localhost", 8001)
        lista = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        try:
            resultado = cliente.estadisticas_lista(lista)
            print("Resultado estadisticas_lista:", resultado)
        except Exception as e:
            print("Error:", e)

        cliente = client("localhost", 8001)
        # Parámetros: a, b, c, x0, lr, epochs
        try:
            resultado = cliente.gradient_descent(1, -2, 1, 0, 0.1, 10)
            print("Resultado gradient_descent:", resultado)
        except Exception as e:
            print("Error:", e)

        cliente = client("localhost", 8001)
        try:
            import base64
            data = b"Hola, esto es binario!"
            resultado = cliente.echo_base64("123")
            if resultado is not None:
                print(resultado)
        except Exception as e:
            print("Error:", e)

    except KeyboardInterrupt:
            print("Cerrando conexión...")
            cliente.close()
            
