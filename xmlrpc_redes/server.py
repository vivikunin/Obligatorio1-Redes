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
                print("Cliente conectado desde {}:{}".format(address[0], address[1]))
                t = threading.Thread(target=self.atenderCliente, args=(client,))
                t.start()
        except KeyboardInterrupt:
            print("Cerrando conexión...")
            self.master.close()

if __name__ == "__main__":        
        server1 = server("localhost", 8000)
        server2 = server("localhost", 8001)

        def suma(a, b):
            return int(int(a) + int(b)), "Se sumo con exito"

        def concat(a, b):
            return a + b

        def find(a, b):
            return a.find(b)

        def div(a,b):
            return a/b
        
        def funcion_muy_complicada(lista, dicc, numero, texto, bandera, fecha):
                #while True:
                """
                Ejecuta una serie de operaciones complejas sobre los parámetros recibidos.
                - lista: lista de enteros
                - dicc: diccionario con claves string y valores enteros
                - numero: entero
                - texto: string
                - bandera: booleano
                - fecha: objeto datetime
                """
                print(lista, dicc, numero, texto, bandera, fecha)
                try:
                    # 1. Filtra la lista usando el número y suma los elementos filtrados
                    filtrados = [x for x in lista if x % numero == 0]
                    suma_filtrados = sum(filtrados)

                    # 2. Crea una nueva lista combinando los valores del diccionario y la suma anterior
                    nueva_lista = list(dicc.values()) + [suma_filtrados]

                    # 3. Manipula el texto: lo invierte, lo pone en mayúsculas y reemplaza vocales por "*"
                    texto_modificado = texto[::-1].upper()
                    for vocal in "AEIOU":
                        texto_modificado = texto_modificado.replace(vocal, "*")

                    # 4. Si la bandera es True, calcula el producto de todos los valores, si no, su promedio
                    if bandera:
                        producto = 1
                        for val in nueva_lista:
                            producto *= val if val != 0 else 1  # Evita multiplicar por cero
                        resultado = producto
                    else:
                        resultado = sum(nueva_lista) / len(nueva_lista) if nueva_lista else 0

                    # 5. Devuelve un diccionario con todos los resultados
                    # 6. Usa la fecha para calcular días desde hoy
                    from datetime import datetime
                    hoy = datetime.now()
                    dias_desde_fecha = (hoy - fecha).days if isinstance(fecha, datetime) else None
                    return {
                        "suma_filtrados": suma_filtrados,
                        "texto_modificado": texto_modificado,
                        "resultado_final": resultado,
                        "elementos_filtrados": filtrados,
                        "nueva_lista": nueva_lista,
                        "dias_desde_fecha": dias_desde_fecha,
                        "fecha_recibida": fecha.strftime('%Y-%m-%d %H:%M:%S') if hasattr(fecha, 'strftime') else str(fecha)
                    }
                except Exception as e:
                    return {"error": str(e)}

        def gradient_descent(a, b, c, x0, lr, epochs):
            """
            Descenso por gradiente para f(x) = ax^2 + bx + c
            - a, b, c: coeficientes de la función
            - x0: valor inicial de x
            - lr: tasa de aprendizaje
            - epochs: cantidad de iteraciones
            Devuelve el valor mínimo encontrado y la lista de valores de x en cada paso.
            """
            x = float(x0)
            history = [x]
            for _ in range(int(epochs)):
                grad = 2 * a * x + b  # Derivada de f(x)
                x = x - lr * grad
                history.append(x)
            return {
                "minimo_aproximado": x,
                "historial_x": history
            }

        def estadisticas_lista(lista):
            """
            Recibe una lista de números y devuelve un diccionario con estadísticas básicas.
            """
            if not lista:
                return {"error": "Lista vacía"}
            return {
                "min": min(lista),
                "max": max(lista),
                "promedio": sum(lista) / len(lista),
                "cantidad": len(lista),
                "pares": [x for x in lista if x % 2 == 0],
                "impares": [x for x in lista if x % 2 != 0]
            }

        server1.add_method(suma)
        server1.add_method(concat)
        server1.add_method(find)
        server1.add_method(div)
        server2.add_method(funcion_muy_complicada)
        server2.add_method(gradient_descent)
        server2.add_method(estadisticas_lista)

        server2.add_method(suma)

        import threading
        #### ESTO ES PARA QUE LOS SERVIDORES CORRAN EN HILOS SEPARADOS ####
        threading.Thread(target=server1.serve, daemon=True).start()
        threading.Thread(target=server2.serve, daemon=True).start()
        input("Servidores corriendo. Presiona Enter para salir...\n")

