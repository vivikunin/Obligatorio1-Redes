from server import *

if __name__ == "__main__":

    server = server("localhost", 8000)

    def suma(a, b):
        return a + b

    def concat(a, b):
        return a + b

    def find(a, b):
        return a.find(b)

    server.add_method(suma)
    server.add_method(concat)
    server.add_method(find)
    server.serve()

