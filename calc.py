import pyasmtools

def calculator(op, num_one, num_two):
    if op == 1:
        return num_one + num_two
    elif op == 2:
        return num_one - num_two
    elif op == 3:
        return num_one * num_two
    elif op == 4:
        return num_one / num_two
    else:
        raise ValueError("Invalid operation")

print( "pyasmtools.prettydis(calculator, show_opcode_as_links=True):", pyasmtools.prettydis(calculator, show_opcode_as_links=True) )

