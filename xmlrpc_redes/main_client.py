import time
from client import *

if __name__ == "__main__":
    try:

        #suma con parámetros correctos
        cliente = client('150.150.0.2', 8000)
        response = cliente.suma(1,3)
        if response != None:
            print("Respuesta del servidor:", response)

        #suma con parámetros incorrectos
        cliente = client('150.150.0.2', 8000)
        response = cliente.suma(177)
        if response != None:
            print("Respuesta del servidor:", response)

        #Prueba de funcion_muy_complicada para probar correcto manejo de todos los parámetros
        import datetime
        cliente = client("150.150.0.2", 8001)
        # Parámetros de ejemplo para cada tipo XML-RPC
        ejemplo_entero = 42
        ejemplo_doble = 3.14
        ejemplo_binario = b"prueba binaria"
        ejemplo_booleano = True
        ejemplo_texto = "Redes de computadoras"
        ejemplo_fecha = datetime.datetime(2023, 10, 5, 15, 30)
        ejemplo_lista = [1, 2, 3, 4]
        ejemplo_dicc = {"clave1": "valor1", "clave2": 123}

        try:
            resultado = cliente.funcion_muy_complicada(
                ejemplo_entero,
                ejemplo_doble,
                ejemplo_binario,
                ejemplo_booleano,
                ejemplo_texto,
                ejemplo_fecha,
                ejemplo_lista,
                ejemplo_dicc
            )
            print("Resultado funcion_muy_complicada:", resultado)
        except Exception as e:
            print("Error:", e)

        #prueba de manejo de parámetros de lista
        cliente = client("150.150.0.2", 8001)
        lista = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        try:
            resultado = cliente.estadisticas_lista(lista)
            print("Resultado estadisticas_lista:", resultado)
        except Exception as e:
            print("Error:", e)

        #prueba de gradient descent correcto
        cliente = client("100.100.0.2", 8001)
        # Parámetros: a, b, c, x0, lr, epochs
        try:
            resultado = cliente.gradient_descent(1, -2, 1, 0, 0.1, 10)
            print("Resultado gradient_descent:", resultado)
        except Exception as e:
            print("Error:", e)

        #prueba de método inexistente
        cliente = client("150.150.0.2", 8001)
        # Parámetros: a, b, c, x0, lr, epochs
        try:
            resultado = cliente.metodo_inexistente(1, -2, 1, 0, 0.1, 10)
            if resultado != None:
                print("Resultado metodo_inexistente:", resultado)
        except Exception as e:
            print("Error:", e)

        #prueba de error interno de ejecucion
        cliente = client("150.150.0.2", 8001)
        try:
            resultado = cliente.funcion_con_error_interno()
            if resultado != None:
                print("Resultado error interno:", resultado)
        except Exception as e:
            print("Error:", e)

        #prueba de otros errores
        cliente = client("150.150.0.2", 8001)
        time.sleep(6)
        try:
            resultado = cliente.funcion_otro_error()
            if resultado is not None:
                print("Resultado prueba otro error:", resultado)
        except Exception as e:
            print("Error:", e)
    except KeyboardInterrupt:
            print("Cerrando conexión...")
            cliente.close()

      #PODRÍAMOS ELIMINAR      
"""cliente = client("localhost", 8001)

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
        """
""" cliente = client("localhost", 8001)
        try:
            import base64
            data = b"Hola, esto es binario!"
            resultado = cliente.echo_base64("123")
            if resultado is not None:
                print(resultado)
        except Exception as e:
            print("Error:", e)"""