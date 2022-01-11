import pyasmtools

class Hello:
    def __init__(self, greeting):
        self.greeting = greeting

    def show(self):
        print(self.greeting)


hello_obj = Hello("hello world")
hello_obj.show()
print( "pyasmtools.prettydis(hello_obj.show, show_opcode_as_links=True):", pyasmtools.prettydis(hello_obj.show, show_opcode_as_links=True) )

