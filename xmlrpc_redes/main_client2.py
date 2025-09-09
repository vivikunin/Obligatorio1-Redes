import time
from client import *

if __name__ == "__main__":
    try:

        #suma con parámetros correctos
        cliente = client('150.150.0.2', 8000)
        response = cliente.suma(1,3)
        if response != None:
            print("Respuesta del servidor:", response)

        #suma con parámetros correctos
        cliente = client('100.100.0.2', 8001)
        response = cliente.suma(1,3)
        if response != None:
            print("Respuesta del servidor:", response)

        #suma con parámetros correctos
        cliente = client('150.150.0.2', 8000)
        response = cliente.suma(1,3)
        if response != None:
            print("Respuesta del servidor:", response)

        #suma con parámetros correctos
        cliente = client('100.100.0.2', 8001)
        response = cliente.suma(1,3)
        if response != None:
            print("Respuesta del servidor:", response)

        #suma con parámetros correctos
        cliente = client('150.150.0.2', 8000)
        response = cliente.suma(1,3)
        if response != None:
            print("Respuesta del servidor:", response)

        #suma con parámetros correctos
        cliente = client('100.100.0.2', 8001)
        response = cliente.suma(1,3)
        if response != None:
            print("Respuesta del servidor:", response)

        #suma con parámetros correctos
        cliente = client('150.150.0.2', 8000)
        response = cliente.suma(1,3)
        if response != None:
            print("Respuesta del servidor:", response)

    except KeyboardInterrupt:
            print("Cerrando conexión...")
            cliente.close()
        

