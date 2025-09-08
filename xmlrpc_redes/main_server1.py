from server import *

if __name__ == "__main__":

    #inicialización del server
    server1 = server("0.0.0.0", 8000)

    ##defincición de las funciones que implementan
    def suma(a, b):
        return int(int(a) + int(b)), "Se sumo con exito"

    def concat(a, b):
        return a + b

    def find(a, b):
        return a.find(b)

    def div(a,b):
        return a/b
    
    def refran():
        return "Entre fantasmas no nos pisamos la sábana - Nicolas Alberro 2025"

    def echo(text):
        return text

    #Agregar los métodos a cada server
    server1.add_method(suma)
    server1.add_method(concat)
    server1.add_method(find)
    server1.add_method(div)
    server1.add_method(refran)
    server1.add_method(echo)

    server1.serve()
   