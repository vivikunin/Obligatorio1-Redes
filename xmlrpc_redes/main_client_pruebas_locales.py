import time
from client import *

if __name__ == "__main__":
    try:
        print("Prueba metodo lento: timeout durante la ejecución del método")
        cliente = client("localhost", 8001)
        try:
            resultado = cliente.metodo_lento()
            if resultado is not None:
                print("Resultado prueba metodo lento:", resultado)
        except Exception as e:
            print("Error:", e)
        print()

        print("Suma con parámetros correctos")
        cliente = client('localhost', 8000)
        response = cliente.suma(1,3)
        if response != None:
            print("Respuesta del servidor:", response)
        print()

        print("Suma con parámetros incorrectos")
        cliente = client('localhost', 8000)
        response = cliente.suma(177)
        if response != None:
            print("Respuesta del servidor:", response)
        print()

        print("Division entre 0")
        cliente = client('localhost', 8000)
        response = cliente.div(1, 0)
        if response != None:
            print("Respuesta del servidor:", response)
        print()

        print("prueba de método echo con un string corto")
        cliente = client('localhost', 8000)
        try:
            resultado = cliente.echo("echo")
            print("Echo recibido:", resultado)
        except Exception as e:
            print("Error en echo:", e)
        print()

        print("prueba de método echo con un string largo")
        cliente = client('localhost', 8000)
        texto_largo = "palabra " * 20000  # Genera un string de 20.000 palabras
        try:
            resultado = cliente.echo(texto_largo)
            if resultado==texto_largo:
                print("Echo recibido correctamente")
            else:
                print("Echo recibido incorrectamente")
        except Exception as e:
            print("Error en echo:", e)
        print()

        print("prueba de método sin parámetros y que retorna un único valor")
        cliente = client('localhost', 8000)
        try:
            response = cliente.refran()
            if response != None:
                print("Respuesta del servidor:", response)
        except Exception as e:
            print("Error en refran:", e)
        print()

        print("prueba de método con parámetros entero y string y que retorna un único valor")
        cliente = client('localhost', 8001)
        try:
            response = cliente.edad_persona("Juan", 30)
            if response != None:
                print("Respuesta del servidor:", response)
        except Exception as e:
            print("Error en edad_persona:", e)
        print()

        print("Prueba de funcion_muy_complicada para probar correcto manejo de todos los parámetros")
        import datetime
        cliente = client("localhost", 8001)
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
        print()

        print("prueba de manejo de parámetros de lista")
        cliente = client("localhost", 8001)
        lista = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        try:
            resultado = cliente.estadisticas_lista(lista, "prueba")
            print("Resultado estadisticas_lista:", resultado)
        except Exception as e:
            print("Error:", e)
        print()

        print("prueba de gradient descent correcto")
        cliente = client("localhost", 8001)
        # Parámetros: a, b, c, x0, lr, epochs
        try:
            resultado = cliente.gradient_descent(1, -2, 1, 0, 0.1, 10)
            print("Resultado gradient_descent:", resultado)
        except Exception as e:
            print("Error:", e)
        print()

        print("prueba de llamada a método inexistente")
        cliente = client("localhost", 8001)
        try:
            resultado = cliente.metodo_inexistente(1, -2, 1, 0, 0.1, 10)
            if resultado != None:
                print("Resultado metodo_inexistente:", resultado)
        except Exception as e:
            print("Error:", e)
        print()

        print("prueba de método con error interno de ejecucion")
        cliente = client("localhost", 8001)
        try:
            resultado = cliente.funcion_con_error_interno()
            if resultado != None:
                print("Resultado error interno:", resultado)
        except Exception as e:
            print("Error:", e)
        print()     
       
        print("Prueba de timeout antes de enviar el pedido")
        cliente = client("localhost", 8001)
        time.sleep(10)
        try:
            resultado = cliente.funcion_otro_error()
            if resultado is not None:
                print("Resultado prueba otro error:", resultado)
        except Exception as e:
            print("Error:", e)
        print()

            
    except KeyboardInterrupt:
        print("Cerrando conexión...")
        cliente.close()
    except Exception as e:
        print("Error en la conexión:", e)
        cliente.close()

