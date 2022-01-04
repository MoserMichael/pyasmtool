#!/usr/bin/env python3

from mdpyformat import *

header_md("Python bytecode explained", nesting=1)

print_md("""
Python is an interpreted language; When a program is run, the python interpreter is first parsing your code and checking for any syntax errors, then it is translating the source code into a series of bytecode instructions; these bytecode instructions are then run by the python interpreter. This text is explaining some of the features of the python bytecode.

This article looks at [cpython](https://github.com/python/cpython), which is the reference implementation of the python interpreter. Most people are probably running cpython (that's what you get with ```brew install python3``` on the Mac). If you are talking about the latest and greatest versions of python, then use of the CPython interpreter is implicitly assumed. However there is a drawback, CPython doesn't have a just in time compiler right now, instead the interpreter is running the bytecode instructions directly.

There is a competing python runtime [PyPy](https://www.pypy.org/). This one does have a just in time compiler that translates the bytecode into machine code on the fly, while running your programm. PyPy is therefore several times faster than CPython in most benchmark tests. However it is normally playing catch up with CPython, and is normally a few minor versions behind the CPython release cycle.

This article is focusing on CPython.

""")        

header_md("Overview of the python bytecode", nesting=2)

print_md("""
The byte code deals with two entities, a memory store that keeps functions and data items, and a stack used for evaluating expression (the stack is maintained separately per each function object)
The python interpreter works as a [stack machine](https://en.wikipedia.org/wiki/Stack_machine) when it evaluates the bytecode instructions. This means that values are moved from a main memory store to the stack, where the expression is evaluated, then the result is moved back to the main memory store.

The purpose of some the bytecode instructions is to populate the stack, some example instructions:
- THE [LOAD_CONST](https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST) instructions takes a constant and pushes its value to the stack.
- The [LOAD_FAST](https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST) instruction takes a variable and pushes a reference to this variable to the stack

Other bytecode instructions serve the purpose of evaluating expressions. These instructions pop one or several values of a stack, perform some operation on the obtained values (like adding them) and push the result back to the stack. Some example instructions:
- [BINARY_ADD](https://docs.python.org/3/library/dis.html#opcode-BINARY_ADD) pops two values off the stack, and pushes the sum of these values back to the stack.
- [UNARY_NEGATE](https://docs.python.org/3/library/dis.html#opcode-UNARY_NEGATIVE) pops the top entry from the stack, and pushes the negated numeric value back to it.

There are instructions used to implement control flow
- [JUMP_ABSOLUTE](https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE) transfers control to a given bytecode instruction
- [JUMP_IF_TRUE_OR_POP](https://docs.python.org/3/library/dis.html#opcode-JUMP_IF_TRUE_OR_POP) conditional jump if top of stack has True value, in this case the top element of the stack is left unchanged, if the top of the stack is False then pop the value off the stack.

A very important bytecode sequence is the function call sequence.
- Here the lowest position on the stack must be a function object, this is put onto the stack by the [LOAD_GLOBAL](https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL) opcode,

- Next on the stack come the arguments of the function call
- The next instruction is a function call opcode [CALL_FUNCTION](https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION); This opcode comes with a parameter that specifies the number of parameters / number of stack entries that will be passed to the function call; these parameters will be poped off the stack, the return value of the function call will be pushed onto the stack.

Here is a [reference](https://docs.python.org/3/library/dis.html#python-bytecode-instructions) of the instructions, as part of the [dis](https://docs.python.org/3/library/dis.html) module from the python standard library. I was suprised to learn, that many bytecode instructions changed in minor releases of the runtime! If you are upgrading or downgrading the python interpreter, then you probably should also delete all __pycache__ folders, these folders hold the binary files that hold the compiled bytecode instructions, but you can't be sure that these will work after a version change!

""")

header_md("Disassembling of python code", nesting=2)

print_md("""
You can examine the pyhon bytecode of a function by means of a dissassembler, as part of the python standard library you have the [dis](https://docs.python.org/3/library/dis.html) package, that can show you the bytecode of a python function.

I have written a disassembler that is producing a combined listing for a given python function, this means that you have a line of the python source code, followed by the python bytecode instructions that this source line translates into; I hope that this combined listing will make it much easier to comprehend the meaning of each lineof code and how it translates into the byte code instructions. I think that this will illustrate the concepts, that were explained in the previous section.

Let's look at an example:

(Note: there is one limitation, the tool can't be used, if running python code compiled from a string by means of the [compile](https://docs.python.org/3/library/functions.html#compile) and [exec](https://docs.python.org/3/library/functions.html#exec) built-in functions, here it is impossible to find the source code of a line, while running the program)

""")

header_md("learning by looking at disassembled code", nesting=2)

print_md("""
We will now learn about the python bytecode, while looking at disassembled example functions
""")

header_md("learning about expression evaluation", nesting=3)

print_md("""
The calc function receives the name of the operation and two argument numbers, it switches on the type of the requested operation and performs the requested arithmetic operation on the other two arguments. This is an example function that is evaluating some expression, and then returning a value back to the caller of the function.

Note some difference betwen the python bytecode and the mnemonics of an assembly language - on most CPU's you have a stack that is shared between function calls performed for a given operating system thread. However the python interpreter works differently, you have a Frame object per function, this frame object has a seperate stack used to evaluating the bytecode of that function. The frame objects are chained together and form a seperate stack ordered by the sequence of calling each function. Note that the python bytecode is therefore closely related to how the cpython interpreter is working.

Why should the python runtime maintain a separate stack, just for the purpose of evaluating an expression? One possible reason would be to simplify generators and asynchronous calls, here you need to switch often between co-routines, and it is easier to do so, if each activation record/frame has its own stack to begin with.

Please examine the following example and bytecode listing; you can see the patterns exlained in the previous section: evaluation of an expression is loading the arguments to the evaluating stack, then performing an operation on the values in the stack, the result is moved back to main memory via a store instruction.
""")        
run_and_quote("calc.py", command="python3", line_prefix="> ")

header_md("learning about function calls", nesting=3)

print_md("""
The next example has a recursive function with one positional argument, the function computes the factorial on the argument, recursively. 
Note that first on the stack is variable of type Function that is to be invoked. Next the function parameter is computed and pushed onto the stack, finally the 
<a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION">CALL_FUNCTION</a> opocde is perfoming the call, this instruction also has the number of arguments of the call.
""")

run_and_quote("fac_rec.py", command="python3", line_prefix="> ")

header_md("learning about loops", nesting=3)

run_and_quote("fac_iter.py", command="python3", line_prefix="> ")
