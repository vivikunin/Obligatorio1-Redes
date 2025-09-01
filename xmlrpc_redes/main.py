from server import *

if __name__ == "__main__":

    server = server("localhost", 8000)

    def suma(a, b):
        return int(int(a) + int(b)), "Se sumo con exito"

    def concat(a, b):
        return a + b

    def find(a, b):
        return a.find(b)
    
    def div(a,b):
        return a/b

    server.add_method(suma)
    server.add_method(concat)
    server.add_method(find)
    server.add_method(div)
    server.serve()

