import pyasmtools 

def fac_iter(arg_n: int) -> int:
    res = 1
    for cur_n in range(1,arg_n):
        res *= cur_n
    return res

print( "pyasmtools.prettydis(fac, show_opcode_as_links=True):", pyasmtools.prettydis(fac_iter, show_opcode_as_links=True) )


