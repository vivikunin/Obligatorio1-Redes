import time
from client import *

if __name__ == "__main__":
    try:

        #prueba metodo lento
        cliente = client("150.150.0.2", 800)
        try:
            resultado = cliente.sumar(1, 2)
            if resultado is not None:
                print("Resultado suma:", resultado)
        except Exception as e:
            print("Error:", e)

    except KeyboardInterrupt:
            print("Cerrando conexión...")
            cliente.close()