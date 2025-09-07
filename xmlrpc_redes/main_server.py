from server import *

if __name__ == "__main__":

    #inicialización de los servers
    server1 = server("0.0.0.0", 8000)
    server2 = server("0.0.0.0", 8001)

    ##defincición de las funciones que implementan
    def suma(a, b):
        return int(int(a) + int(b)), "Se sumo con exito"

    def concat(a, b):
        return a + b

    def find(a, b):
        return a.find(b)

    def div(a,b):
        return a/b
    
    def funcion_muy_complicada(
    entero,          # int
    doble,           # double
    binario,         # base64 (bytes)
    booleano,        # bool
    texto,           # string
    fecha,           # datetime
    lista,           # array (list)
    dicc             # struct (dict)
    ):
        """
        Recibe y retorna un elemento de cada tipo XML-RPC:
        - entero: int
        - doble: float
        - binario: bytes (base64)
        - booleano: bool
        - texto: string
        - fecha: datetime
        - lista: list
        - dicc: dict
        """
        import base64
        from datetime import datetime

        try:
            # Procesos simples para cada tipo
            entero_out = entero + 1
            doble_out = doble * 2.0
            binario_out = base64.b64encode(binario).decode("ascii")  # Retorna como string base64
            booleano_out = not booleano
            texto_out = texto[::-1]
            fecha_out = fecha.strftime('%Y-%m-%d %H:%M:%S') if hasattr(fecha, 'strftime') else str(fecha)
            lista_out = [x for x in lista] + [entero_out]
            dicc_out = {k: v for k, v in dicc.items()}
            dicc_out["nuevo"] = doble_out

            # Retorna todos los tipos en un struct/dict
            return {
                "entero": entero_out,
                "doble": doble_out,
                "binario_base64": binario_out,
                "booleano": booleano_out,
                "texto": texto_out,
                "fecha": fecha_out,
                "lista": lista_out,
                "dicc": dicc_out
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
    #funcion con error interno de ejecucion
    def funcion_con_error_interno():
        raise RuntimeError("Error interno forzado para prueba")

    #funcion con otro error
    def funcion_otro_error():
        raise ValueError("Error inesperado para prueba de faultCode 5")


        
    #Agregar los métodos a cada server
    server1.add_method(suma)
    server1.add_method(concat)
    server1.add_method(find)
    server1.add_method(div)
    server2.add_method(funcion_muy_complicada)
    server2.add_method(gradient_descent)
    server2.add_method(estadisticas_lista)
    server2.add_method(funcion_con_error_interno)
    server2.add_method(funcion_otro_error)

    #Creamos threads para que los servers corran en paralelo
    import threading
    threading.Thread(target=server1.serve, daemon=True).start()
    threading.Thread(target=server2.serve, daemon=True).start()
    while True:
        pass

    #PODRÍAMOS ELIMINAR
    """def funcion_muy_complicada(lista, dicc, numero, texto, bandera, fecha):

        Ejecuta una serie de operaciones sobre los diferentes parámetros recibidos, 
        permitiendo probar enviar y recibir diferentes tipos de parámetros.
        - lista: lista de enteros
        - dicc: diccionario con claves string y valores enteros
        - numero: entero
        - texto: string
        - bandera: booleano
        - fecha: objeto datetime

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
            """

    """def echo_base64(data_bin):
    
        Recibe datos binarios (base64) y los devuelve como string y como binario.
        - data_bin: bytes (el cliente debe enviar un parámetro tipo bytes)
        Devuelve un diccionario con la longitud, el string base64 y los primeros bytes.

        import base64
        base64_str = base64.b64encode(data_bin).decode("ascii")
        return {
            "base64_str": base64_str,
            "longitud": len(data_bin),
            "primeros_10_bytes": list(data_bin[:10])
        }
    """
    #server2.add_method(echo_base64)