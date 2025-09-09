from server import *

if __name__ == "__main__":

    #inicialización del server
    server2 = server("0.0.0.0", 8001)
    
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

    def estadisticas_lista(lista, nombrelista):
        """
        Recibe una lista de números con su nombre y devuelve un diccionario con estadísticas básicas.
        """
        if not lista:
            return {"error": f"La lista '{nombrelista}' está vacía"}
        return {
            "min": min(lista),
            "max": max(lista),
            "promedio": sum(lista) / len(lista),
            "cantidad": len(lista),
            "pares": [x for x in lista if x % 2 == 0],
            "impares": [x for x in lista if x % 2 != 0]
        }
    ##defincición de las funciones que implementan
    def suma(a, b):
        return int(int(a) + int(b)), "Se sumo con exito"

    #funcion con error interno de ejecucion
    def funcion_con_error_interno():
        raise RuntimeError("Error interno forzado para prueba")

    #funcion con otro error
    def funcion_otro_error():
        raise ValueError("Error inesperado para prueba de faultCode 5")

    def metodo_lento():
        import time
        time.sleep(10)
        return "Método lento completado"
    
    def edad_persona(nombre, edad):
        return f"{nombre} tiene {edad} años"

    #Agregar los métodos al server
    server2.add_method(funcion_muy_complicada)
    server2.add_method(gradient_descent)
    server2.add_method(estadisticas_lista)
    server2.add_method(edad_persona)
    server2.add_method(funcion_con_error_interno)
    server2.add_method(funcion_otro_error)
    server2.add_method(metodo_lento)
    server2.add_method(suma)

    server2.serve()

 