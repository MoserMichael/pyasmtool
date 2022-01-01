#!/usr/bin/env python3

from mdpyformat import *

header_md("python bytecode explained", nesting=1)

header_md("Introduction to bytecode", nesting=2)

print_md("""
Python is an interpreted language; When a program is run, the python interpreter is first parsing your code and checking for any syntax errors, then it is translating the source code into a series of bytecode instructions; these bytecode instructions are then run by the python interpreter. This text is explaining some of the features of the python bytecode.

The byte code deals with two entities, a memory store that keeps functions and data items, and a stack used for evaluating expression.
The python interpreter works as a [stack machine](https://en.wikipedia.org/wiki/Stack_machine) when it executes the byte code; 

The purpose of some the bytecode instructions is to populate the stack,
- THE [LOAD_CONST](https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST) instructions takes a constant and pushes its value to the stack.
- The [LOAD_FAST](https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST) instruction takes a variable and pushes a reference to this variable to the stack

Other bytecode instructions pop one or several values of a stack, perform some operation on them (like adding them) and push the result back to it,
- [BINARY_ADD](https://docs.python.org/3/library/dis.html#opcode-BINARY_ADD) pops two values off the stack, and pushes the sum of these values back to the stack.
- [UNARY_NEGATE](https://docs.python.org/3/library/dis.html#opcode-UNARY_NEGATIVE) pops the top entry from the stack, and pushes the negated numeric value back to it.

A very important sequence is the function call sequence.
- The lowest position on the stack must be a function object, this is put onto the stack by the [LOAD_GLOBAL](https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL) opcode,
- next come the arguments of the function call
- the next instruction is a function call opcode [CALL_FUNCTION](https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION); This opcode comes with a parameter that specifies the number of parameters / number of stack entries that will be passed to the function call; these parameters will be poped off the stack, the return value of the function call will be pushed onto the stack.

Here is a [reference](https://docs.python.org/3/library/dis.html#python-bytecode-instructions) of the instructions.
""")

header_md("Disassembling of python code", nesting=2)

print_md("""
You can examine the pyhon bytecode of a function by means of a dissassembler, as part of the python standard library you have the [dis](https://docs.python.org/3/library/dis.html) package, that can show you the bytecode of a python function.

I have written a disassembler that is producing a combined lising for a given python function, this means that you have a line of the python source code, followed by the python bytecode instructions that this source line translates into; I hope that this combined listing will make it much easier to comprehend, what the byte code instructions mean. I think that this will illustrate the conecpts, that were explained in the previous section.

Let's look at an example:
(There is one limitation, the tool can't be used, if running python code by means of the [exec](https://docs.python.org/3/library/functions.html#exec) built-in function) 

""")

header_md("learning by looking at disassembled code", nesting=2)

print_md("""
We will now learn about the python bytecode, while looking at disassembled example functions
""")

header_md("learning about expression evaluation", nesting=3)

run_and_quote("calc.py", command="python3", line_prefix="> ")

header_md("learning about function calls", nesting=3)

run_and_quote("fac_rec.py", command="python3", line_prefix="> ")

header_md("learning about loops", nesting=3)

run_and_quote("fac_iter.py", command="python3", line_prefix="> ")
