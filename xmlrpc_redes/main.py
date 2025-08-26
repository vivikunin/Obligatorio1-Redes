from server import *

if __name__ == "__main__":

    server = server("localhost", 5000)

    def suma(a, b):
        return int(int(a) + int(b))

    def concat(a, b):
        return a + b

    def find(a, b):
        return a.find(b)


    server.add_method(suma)
    server.add_method(concat)
    server.add_method(find)
    server.serve()

