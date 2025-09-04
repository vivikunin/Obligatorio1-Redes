from client import *

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
            
