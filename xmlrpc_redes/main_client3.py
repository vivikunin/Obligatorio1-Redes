import time
from client import *

if __name__ == "__main__":
    try:

        #prueba metodo lento
        cliente = client("150.150.0.2", 8000)
        try:
            resultado = cliente.metodo_lento()
            if resultado is not None:
                print("Resultado prueba metodo lento:", resultado)
        except Exception as e:
            print("Error:", e)

    except KeyboardInterrupt:
            print("Cerrando conexión...")
            cliente.close()