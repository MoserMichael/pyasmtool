#!/usr/bin/env python3

import pyasmtools


def swap_list(arg_list):
    tmp = arg_list[0]
    arg_list[0] = arg_list[1]
    arg_list[1] = tmp

def swap_dict(arg_dict):
    tmp = arg_dict['first']
    arg_dict['first'] = arg_dict['second']
    arg_dict['second'] = tmp

#pyasmtools.prettydis(swap_list)
#pyasmtools.prettydis(swap_dict)

swap_list = pyasmtools.TraceMe(swap_list)
swap_dict = pyasmtools.TraceMe(swap_dict)
    
arg_list=[1,2]
swap_list(arg_list)
print(arg_list)

arg_dict={ 'first': 'a',
           'second': 'b' }
swap_dict(arg_dict)
print(arg_dict)

