#!/usr/bin/env python3

import random
import prettydiasm


def shuffle(arr_size):
    arr=[]
    for num in range(1,arr_size+1):
        arr.append(num)

    for nun in range(0, arr_size):
        idx = random.randint(1,arr_size)
        tmp = arr[0]
        arr[0] = arr[idx]
        arr[idx] = tmp

    return arr

#print(shuffle(7))        
print( "prettydiasm.prettydis(shuffle, show_opcode_as_links=True):", prettydiasm.prettydis(shuffle, show_opcode_as_links=True) )

