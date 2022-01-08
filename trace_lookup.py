#!/usr/bin/env python3

import prettytrace
import prettydiasm


def swap_list(arg_list):
    tmp = arg_list[0]
    arg_list[0] = arg_list[1]
    arg_list[1] = tmp

def swap_dict(arg_dict):
    tmp = arg_dict['first']
    arg_dict['first'] = arg_dict['second']
    arg_dict['second'] = tmp

#prettydiasm.prettydis(swap_list)
#prettydiasm.prettydis(swap_dict)

swap_list = prettytrace.TraceMe(swap_list)
swap_dict = prettytrace.TraceMe(swap_dict)
    
arg_list=[1,2]
swap_list(arg_list)
print(arg_list)

arg_dict={ 'first': 'a',
           'second': 'b' }
swap_dict(arg_dict)
print(arg_dict)

