* [Python bytecode explained](#s1)
  * [Overview of the python bytecode](#s1-1)
  * [Disassembling of python code](#s1-2)
  * [learning by looking at disassembled code](#s1-3)
      * [learning about expression evaluation](#s1-3-1)
      * [learning about function calls](#s1-3-2)
      * [learning about loops](#s1-3-3)
      * [learning about classes](#s1-3-4)
      * [learning about dictionaries](#s1-3-5)
      * [learning about lists](#s1-3-6)


# <a id='s1' />Python bytecode explained

Python is an interpreted language; When a program is run, the python interpreter is first parsing your code and checking for any syntax errors, then it is translating the source code into a series of bytecode instructions; these bytecode instructions are then run by the python interpreter. This text is explaining some of the features of the python bytecode.

This article looks at [cpython](https://github.com/python/cpython), which is the reference implementation of the python interpreter. Most people are probably running cpython (that's what you get with 
```brew install python3``` on the Mac). If you are talking about the latest and greatest versions of python, then use of the CPython interpreter is implicitly assumed. However there is a drawback, CPython doesn't have a just in time compiler right now, instead the interpreter is running the bytecode instructions directly.

There is a competing python runtime [PyPy](https://www.pypy.org/). This one does have a just in time compiler that translates the bytecode into machine code on the fly, while running your programm. PyPy is therefore several times faster than CPython in most benchmark tests. However it is normally playing catch up with CPython, and is normally a few minor versions behind the CPython release cycle.

This article is focusing on CPython.



## <a id='s1-1' />Overview of the python bytecode

The byte code deals with two entities, a memory store that keeps functions and data items, and a stack used for evaluating expression (the stack is maintained separately per each function object)
The python interpreter works as a [stack machine](https://en.wikipedia.org/wiki/Stack\_machine) when it evaluates the bytecode instructions. This means that values are moved from a main memory store to the stack, where the expression is evaluated, then the result is moved back to the main memory store.

The purpose of some the bytecode instructions is to populate the stack, some example instructions:
- THE [LOAD\_CONST](https://docs.python.org/3/library/dis.html#opcode-LOAD\_CONST) instructions takes a constant and pushes its value to the stack.
- The [LOAD\_FAST](https://docs.python.org/3/library/dis.html#opcode-LOAD\_FAST) instruction takes a variable and pushes a reference to this variable to the stack

Other bytecode instructions serve the purpose of evaluating expressions. These instructions pop one or several values of a stack, perform some operation on the obtained values (like adding them) and push the result back to the stack. Some example instructions:
- [BINARY\_ADD](https://docs.python.org/3/library/dis.html#opcode-BINARY\_ADD) pops two values off the stack, and pushes the sum of these values back to the stack.
- [UNARY\_NEGATE](https://docs.python.org/3/library/dis.html#opcode-UNARY\_NEGATIVE) pops the top entry from the stack, and pushes the negated numeric value back to it.

There are instructions used to implement control flow
- [JUMP\_ABSOLUTE](https://docs.python.org/3/library/dis.html#opcode-JUMP\_ABSOLUTE) transfers control to a given bytecode instruction
- [JUMP\_IF\_TRUE\_OR\_POP](https://docs.python.org/3/library/dis.html#opcode-JUMP\_IF\_TRUE\_OR\_POP) conditional jump if top of stack has True value, in this case the top element of the stack is left unchanged, if the top of the stack is False then pop the value off the stack.

A very important bytecode sequence is the function call sequence.
- Here the lowest position on the stack must be a function object, this is put onto the stack by the [LOAD\_GLOBAL](https://docs.python.org/3/library/dis.html#opcode-LOAD\_GLOBAL) opcode,

- Next on the stack come the arguments of the function call
- The next instruction is a function call opcode [CALL\_FUNCTION](https://docs.python.org/3/library/dis.html#opcode-CALL\_FUNCTION); This opcode comes with a parameter that specifies the number of parameters / number of stack entries that will be passed to the function call; these parameters will be poped off the stack, the return value of the function call will be pushed onto the stack.

Here is a [reference](https://docs.python.org/3/library/dis.html#python-bytecode-instructions) of the instructions, as part of the [dis](https://docs.python.org/3/library/dis.html) module from the python standard library. I was suprised to learn, that many bytecode instructions changed in minor releases of the runtime! If you are upgrading or downgrading the python interpreter, then you probably should also delete all \_\_pycache\_\_ folders, these folders hold the binary files that hold the compiled bytecode instructions, but you can't be sure that these will work after a version change!



## <a id='s1-2' />Disassembling of python code

You can examine the pyhon bytecode of a function by means of a dissassembler, as part of the python standard library you have the [dis](https://docs.python.org/3/library/dis.html) package, that can show you the bytecode of a python function.

I have written a disassembler that is producing a combined listing for a given python function, this means that you have a line of the python source code, followed by the python bytecode instructions that this source line translates into; I hope that this combined listing will make it much easier to comprehend the meaning of each lineof code and how it translates into the byte code instructions. I think that this will illustrate the concepts, that were explained in the previous section.

Let's look at an example:

(Note: there is one limitation, the tool can't be used, if running python code compiled from a string by means of the [compile](https://docs.python.org/3/library/functions.html#compile) and [exec](https://docs.python.org/3/library/functions.html#exec) built-in functions, here it is impossible to find the source code of a line, while running the program)



## <a id='s1-3' />learning by looking at disassembled code

We will now learn about the python bytecode, while looking at disassembled example functions


### <a id='s1-3-1' />learning about expression evaluation

The calc function receives the name of the operation and two argument numbers, it switches on the type of the requested operation and performs the requested arithmetic operation on the other two arguments. This is an example function that is evaluating some expression, and then returning a value back to the caller of the function.

Note some difference betwen the python bytecode and the mnemonics of an assembly language - on most CPU's you have a stack that is shared between function calls performed for a given operating system thread. However the python interpreter works differently, you have a Frame object per function, this frame object has a seperate stack used to evaluating the bytecode of that function. The frame objects are chained together and form a seperate stack ordered by the sequence of calling each function. Note that the python bytecode is therefore closely related to how the cpython interpreter is working.

Why should the python runtime maintain a separate stack, just for the purpose of evaluating an expression? One possible reason would be to simplify generators and asynchronous calls, here you need to switch often between co-routines, and it is easier to do so, if each activation record/frame has its own stack to begin with. You can learn more about the cooperative multitasking features of python in [this lesson](https://github.com/MoserMichael/python-obj-system/blob/master/gen-iterator.md)

Please examine the following example and bytecode listing; you can see the patterns exlained in the previous section: evaluation of an expression is loading the arguments to the evaluating stack, then performing an operation on the values in the stack, the result is moved back to main memory via a store instruction.


__Source:__

```python
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


```

__Result:__
<pre>
> File path: /Users/michaelmo/mystuff/pyasmtools/calc.py 
> 
> calc.py:3 def calculator(op, num_one, num_two):
> 
> calc.py:4 	    if op == 1:
> 
>   4           0 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (op)
>               2 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     1 (1)
>               4 <a href="https://docs.python.org/3/library/dis.html#opcode-COMPARE_OP">COMPARE_OP</a>     2 (==)
>               6 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_FALSE">POP_JUMP_IF_FALSE</a>    16
> 
> calc.py:5 	        return num_one + num_two
> 
>   5           8 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (num_one)
>              10 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     2 (num_two)
>              12 <a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_ADD">BINARY_ADD</a>
>              14 <a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE">RETURN_VALUE</a>
> 
> calc.py:6 	    elif op == 2:
> 
>   6     >>   16 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (op)
>              18 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     2 (2)
>              20 <a href="https://docs.python.org/3/library/dis.html#opcode-COMPARE_OP">COMPARE_OP</a>     2 (==)
>              22 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_FALSE">POP_JUMP_IF_FALSE</a>    32
> 
> calc.py:7 	        return num_one - num_two
> 
>   7          24 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (num_one)
>              26 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     2 (num_two)
>              28 <a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_SUBTRACT">BINARY_SUBTRACT</a>
>              30 <a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE">RETURN_VALUE</a>
> 
> calc.py:8 	    elif op == 3:
> 
>   8     >>   32 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (op)
>              34 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     3 (3)
>              36 <a href="https://docs.python.org/3/library/dis.html#opcode-COMPARE_OP">COMPARE_OP</a>     2 (==)
>              38 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_FALSE">POP_JUMP_IF_FALSE</a>    48
> 
> calc.py:9 	        return num_one * num_two
> 
>   9          40 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (num_one)
>              42 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     2 (num_two)
>              44 <a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_MULTIPLY">BINARY_MULTIPLY</a>
>              46 <a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE">RETURN_VALUE</a>
> 
> calc.py:10 	    elif op == 4:
> 
>  10     >>   48 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (op)
>              50 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     4 (4)
>              52 <a href="https://docs.python.org/3/library/dis.html#opcode-COMPARE_OP">COMPARE_OP</a>     2 (==)
>              54 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_FALSE">POP_JUMP_IF_FALSE</a>    64
> 
> calc.py:11 	        return num_one / num_two
> 
>  11          56 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (num_one)
>              58 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     2 (num_two)
>              60 <a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_TRUE_DIVIDE">BINARY_TRUE_DIVIDE</a>
>              62 <a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE">RETURN_VALUE</a>
> 
> calc.py:13 	        raise ValueError("Invalid operation")
> 
>  13     >>   64 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL">LOAD_GLOBAL</a>     0 (ValueError)
>              66 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     5 ('Invalid operation')
>              68 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION">CALL_FUNCTION</a>     1
>              70 <a href="https://docs.python.org/3/library/dis.html#opcode-RAISE_VARARGS">RAISE_VARARGS</a>     1
>              72 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     0 (None)
>              74 <a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE">RETURN_VALUE</a>
> pyasmtools.prettydis(calculator, show_opcode_as_links=True): None
</pre>


### <a id='s1-3-2' />learning about function calls

The next example has a recursive function with one positional argument, the function computes the factorial on the argument, recursively. 
Note that first on the stack is variable of type Function that is to be invoked. Next the function parameter is computed and pushed onto the stack, finally the 
<a href="https://docs.python.org/3/library/dis.html#opcode-CALL\_FUNCTION">CALL\_FUNCTION</a> opocde is perfoming the call, this instruction also has the number of arguments of the call.


__Source:__

```python
import pyasmtools 

def fac(arg_n=7):
    if arg_n == 1:
        return arg_n
    return arg_n * fac(arg_n - 1)

print( "pyasmtools.prettydis(fac, show_opcode_as_links=True):", pyasmtools.prettydis(fac, show_opcode_as_links=True) )

```

__Result:__
<pre>
> File path: /Users/michaelmo/mystuff/pyasmtools/fac_rec.py 
> 
> fac_rec.py:3 def fac(arg_n = 7):
> 
> fac_rec.py:4 	    if arg_n == 1:
> 
>   4           0 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (arg_n)
>               2 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     1 (1)
>               4 <a href="https://docs.python.org/3/library/dis.html#opcode-COMPARE_OP">COMPARE_OP</a>     2 (==)
>               6 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_FALSE">POP_JUMP_IF_FALSE</a>    12
> 
> fac_rec.py:5 	        return arg_n
> 
>   5           8 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (arg_n)
>              10 <a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE">RETURN_VALUE</a>
> 
> fac_rec.py:6 	    return arg_n * fac(arg_n - 1)
> 
>   6     >>   12 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (arg_n)
>              14 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL">LOAD_GLOBAL</a>     0 (fac)
>              16 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (arg_n)
>              18 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     1 (1)
>              20 <a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_SUBTRACT">BINARY_SUBTRACT</a>
>              22 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION">CALL_FUNCTION</a>     1
>              24 <a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_MULTIPLY">BINARY_MULTIPLY</a>
>              26 <a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE">RETURN_VALUE</a>
> pyasmtools.prettydis(fac, show_opcode_as_links=True): None
</pre>


### <a id='s1-3-3' />learning about loops


__Source:__

```python
import pyasmtools 

def fac_iter(arg_n: int) -> int:
    res = 1
    for cur_n in range(1,arg_n):
        res *= cur_n
    return res

print( "pyasmtools.prettydis(fac, show_opcode_as_links=True):", pyasmtools.prettydis(fac_iter, show_opcode_as_links=True) )



```

__Result:__
<pre>
> File path: /Users/michaelmo/mystuff/pyasmtools/fac_iter.py 
> 
> fac_iter.py:3 def fac_iter(arg_n: int) -> int:
> 
> fac_iter.py:4 	    res = 1
> 
>   4           0 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     1 (1)
>               2 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     1 (res)
> 
> fac_iter.py:5 	    for cur_n in range(1,arg_n):
> 
>   5           4 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL">LOAD_GLOBAL</a>     0 (range)
>               6 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     1 (1)
>               8 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (arg_n)
>              10 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION">CALL_FUNCTION</a>     2
>              12 <a href="https://docs.python.org/3/library/dis.html#opcode-GET_ITER">GET_ITER</a>
>         >>   14 <a href="https://docs.python.org/3/library/dis.html#opcode-FOR_ITER">FOR_ITER</a>    12 (to 28)
>              16 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     2 (cur_n)
> 
> fac_iter.py:6 	        res *= cur_n
> 
>   6          18 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (res)
>              20 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     2 (cur_n)
>              22 <a href="https://docs.python.org/3/library/dis.html#opcode-INPLACE_MULTIPLY">INPLACE_MULTIPLY</a>
>              24 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     1 (res)
>              26 <a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE">JUMP_ABSOLUTE</a>    14
> 
> fac_iter.py:7 	    return res
> 
>   7     >>   28 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (res)
>              30 <a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE">RETURN_VALUE</a>
> pyasmtools.prettydis(fac, show_opcode_as_links=True): None
</pre>


### <a id='s1-3-4' />learning about classes


__Source:__

```python
import pyasmtools

class Hello:
    def __init__(self, greeting):
        self.greeting = greeting

    def show(self):
        print(self.greeting)


hello_obj = Hello("hello world")
hello_obj.show()
print( "pyasmtools.prettydis(hello_obj.show, show_opcode_as_links=True):", pyasmtools.prettydis(hello_obj.show, show_opcode_as_links=True) )


```

__Result:__
<pre>
> hello world
> File path: /Users/michaelmo/mystuff/pyasmtools/obj_call.py 
> 
> obj_call.py:7 def Hello.show(self):
> 
> obj_call.py:8 	        print(self.greeting)
> 
>   8           0 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL">LOAD_GLOBAL</a>     0 (print)
>               2 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (self)
>               4 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_ATTR">LOAD_ATTR</a>     1 (greeting)
>               6 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION">CALL_FUNCTION</a>     1
>               8 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP">POP_TOP</a>
>              10 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     0 (None)
>              12 <a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE">RETURN_VALUE</a>
> pyasmtools.prettydis(hello_obj.show, show_opcode_as_links=True): None
</pre>


### <a id='s1-3-5' />learning about dictionaries


__Source:__

```python
#!/usr/bin/env python3

import pyasmtools 

def compute_historgram(file_name):
    with open(file_name,'r') as file:
        text = file.read()

        histo = {}
        for ch in text:
            if not ch in histo:
                histo[ch] = 1
            else:
                histo[ch] += 1

        for ch in histo.keys():
            print("char:", repr(ch), "frequency:", histo[ch])

#compute_historgram(__file__)
print( "pyasmtools.prettydis(compute_historgram, show_opcode_as_links=True):", pyasmtools.prettydis(compute_historgram, show_opcode_as_links=True) )


```

__Result:__
<pre>
> File path: /Users/michaelmo/mystuff/pyasmtools/histo.py 
> 
> histo.py:5 def compute_historgram(file_name):
> 
> histo.py:6 	    with open(file_name,'r') as file:
> 
>   6           0 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL">LOAD_GLOBAL</a>     0 (open)
>               2 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (file_name)
>               4 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     1 ('r')
>               6 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION">CALL_FUNCTION</a>     2
>               8 <a href="https://docs.python.org/3/library/dis.html#opcode-SETUP_WITH">SETUP_WITH</a>   108 (to 118)
>              10 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     1 (file)
> 
> histo.py:7 	        text = file.read()
> 
>   7          12 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (file)
>              14 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_METHOD">LOAD_METHOD</a>     1 (read)
>              16 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_METHOD">CALL_METHOD</a>     0
>              18 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     2 (text)
> 
> histo.py:9 	        histo = {}
> 
>   9          20 <a href="https://docs.python.org/3/library/dis.html#opcode-BUILD_MAP">BUILD_MAP</a>     0
>              22 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     3 (histo)
> 
> histo.py:10 	        for ch in text:
> 
>  10          24 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     2 (text)
>              26 <a href="https://docs.python.org/3/library/dis.html#opcode-GET_ITER">GET_ITER</a>
>         >>   28 <a href="https://docs.python.org/3/library/dis.html#opcode-FOR_ITER">FOR_ITER</a>    38 (to 68)
>              30 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     4 (ch)
> 
> histo.py:11 	            if not ch in histo:
> 
>  11          32 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     4 (ch)
>              34 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     3 (histo)
>              36 <a href="https://docs.python.org/3/library/dis.html#opcode-CONTAINS_OP">CONTAINS_OP</a>     1
>              38 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_FALSE">POP_JUMP_IF_FALSE</a>    50
> 
> histo.py:12 	                histo[ch] = 1
> 
>  12          40 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     2 (1)
>              42 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     3 (histo)
>              44 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     4 (ch)
>              46 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_SUBSCR">STORE_SUBSCR</a>
>              48 <a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE">JUMP_ABSOLUTE</a>    28
> 
> histo.py:14 	                histo[ch] += 1
> 
>  14     >>   50 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     3 (histo)
>              52 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     4 (ch)
>              54 <a href="https://docs.python.org/3/library/dis.html#opcode-DUP_TOP_TWO">DUP_TOP_TWO</a>
>              56 <a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_SUBSCR">BINARY_SUBSCR</a>
>              58 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     2 (1)
>              60 <a href="https://docs.python.org/3/library/dis.html#opcode-INPLACE_ADD">INPLACE_ADD</a>
>              62 <a href="https://docs.python.org/3/library/dis.html#opcode-ROT_THREE">ROT_THREE</a>
>              64 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_SUBSCR">STORE_SUBSCR</a>
>              66 <a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE">JUMP_ABSOLUTE</a>    28
> 
> histo.py:16 	        for ch in histo.keys():
> 
>  16     >>   68 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     3 (histo)
>              70 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_METHOD">LOAD_METHOD</a>     2 (keys)
>              72 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_METHOD">CALL_METHOD</a>     0
>              74 <a href="https://docs.python.org/3/library/dis.html#opcode-GET_ITER">GET_ITER</a>
>         >>   76 <a href="https://docs.python.org/3/library/dis.html#opcode-FOR_ITER">FOR_ITER</a>    26 (to 104)
>              78 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     4 (ch)
> 
> histo.py:17 	            print("char:", repr(ch), "frequency:", histo[ch])
> 
>  17          80 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL">LOAD_GLOBAL</a>     3 (print)
>              82 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     3 ('char:')
>              84 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL">LOAD_GLOBAL</a>     4 (repr)
>              86 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     4 (ch)
>              88 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION">CALL_FUNCTION</a>     1
>              90 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     4 ('frequency:')
>              92 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     3 (histo)
>              94 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     4 (ch)
>              96 <a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_SUBSCR">BINARY_SUBSCR</a>
>              98 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION">CALL_FUNCTION</a>     4
>             100 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP">POP_TOP</a>
>             102 <a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE">JUMP_ABSOLUTE</a>    76
>         >>  104 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_BLOCK">POP_BLOCK</a>
>             106 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     0 (None)
>             108 <a href="https://docs.python.org/3/library/dis.html#opcode-DUP_TOP">DUP_TOP</a>
>             110 <a href="https://docs.python.org/3/library/dis.html#opcode-DUP_TOP">DUP_TOP</a>
>             112 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION">CALL_FUNCTION</a>     3
>             114 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP">POP_TOP</a>
>             116 <a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_FORWARD">JUMP_FORWARD</a>    16 (to 134)
>         >>  118 <a href="https://docs.python.org/3/library/dis.html#opcode-WITH_EXCEPT_START">WITH_EXCEPT_START</a>
>             120 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_TRUE">POP_JUMP_IF_TRUE</a>   124
>             122 <a href="https://docs.python.org/3/library/dis.html#opcode-RERAISE">RERAISE</a>
>         >>  124 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP">POP_TOP</a>
>             126 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP">POP_TOP</a>
>             128 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP">POP_TOP</a>
>             130 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_EXCEPT">POP_EXCEPT</a>
>             132 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP">POP_TOP</a>
>         >>  134 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     0 (None)
>             136 <a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE">RETURN_VALUE</a>
> pyasmtools.prettydis(compute_historgram, show_opcode_as_links=True): None
</pre>


### <a id='s1-3-6' />learning about lists


__Source:__

```python
#!/usr/bin/env python3

import random
import pyasmtools


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
print( "pyasmtools.prettydis(shuffle, show_opcode_as_links=True):", pyasmtools.prettydis(shuffle, show_opcode_as_links=True) )


```

__Result:__
<pre>
> File path: /Users/michaelmo/mystuff/pyasmtools/shuffle.py 
> 
> shuffle.py:7 def shuffle(arr_size):
> 
> shuffle.py:8 	    arr=[]
> 
>   8           0 <a href="https://docs.python.org/3/library/dis.html#opcode-BUILD_LIST">BUILD_LIST</a>     0
>               2 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     1 (arr)
> 
> shuffle.py:9 	    for num in range(1,arr_size+1):
> 
>   9           4 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL">LOAD_GLOBAL</a>     0 (range)
>               6 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     1 (1)
>               8 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (arr_size)
>              10 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     1 (1)
>              12 <a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_ADD">BINARY_ADD</a>
>              14 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION">CALL_FUNCTION</a>     2
>              16 <a href="https://docs.python.org/3/library/dis.html#opcode-GET_ITER">GET_ITER</a>
>         >>   18 <a href="https://docs.python.org/3/library/dis.html#opcode-FOR_ITER">FOR_ITER</a>    14 (to 34)
>              20 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     2 (num)
> 
> shuffle.py:10 	        arr.append(num)
> 
>  10          22 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (arr)
>              24 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_METHOD">LOAD_METHOD</a>     1 (append)
>              26 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     2 (num)
>              28 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_METHOD">CALL_METHOD</a>     1
>              30 <a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP">POP_TOP</a>
>              32 <a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE">JUMP_ABSOLUTE</a>    18
> 
> shuffle.py:12 	    for nun in range(0, arr_size):
> 
>  12     >>   34 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL">LOAD_GLOBAL</a>     0 (range)
>              36 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     2 (0)
>              38 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (arr_size)
>              40 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION">CALL_FUNCTION</a>     2
>              42 <a href="https://docs.python.org/3/library/dis.html#opcode-GET_ITER">GET_ITER</a>
>         >>   44 <a href="https://docs.python.org/3/library/dis.html#opcode-FOR_ITER">FOR_ITER</a>    44 (to 90)
>              46 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     3 (nun)
> 
> shuffle.py:13 	        idx = random.randint(1,arr_size)
> 
>  13          48 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL">LOAD_GLOBAL</a>     2 (random)
>              50 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_METHOD">LOAD_METHOD</a>     3 (randint)
>              52 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     1 (1)
>              54 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     0 (arr_size)
>              56 <a href="https://docs.python.org/3/library/dis.html#opcode-CALL_METHOD">CALL_METHOD</a>     2
>              58 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     4 (idx)
> 
> shuffle.py:14 	        tmp = arr[0]
> 
>  14          60 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (arr)
>              62 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     2 (0)
>              64 <a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_SUBSCR">BINARY_SUBSCR</a>
>              66 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST">STORE_FAST</a>     5 (tmp)
> 
> shuffle.py:15 	        arr[0] = arr[idx]
> 
>  15          68 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (arr)
>              70 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     4 (idx)
>              72 <a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_SUBSCR">BINARY_SUBSCR</a>
>              74 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (arr)
>              76 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST">LOAD_CONST</a>     2 (0)
>              78 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_SUBSCR">STORE_SUBSCR</a>
> 
> shuffle.py:16 	        arr[idx] = tmp
> 
>  16          80 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     5 (tmp)
>              82 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (arr)
>              84 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     4 (idx)
>              86 <a href="https://docs.python.org/3/library/dis.html#opcode-STORE_SUBSCR">STORE_SUBSCR</a>
>              88 <a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE">JUMP_ABSOLUTE</a>    44
> 
> shuffle.py:18 	    return arr
> 
>  18     >>   90 <a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST">LOAD_FAST</a>     1 (arr)
>              92 <a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE">RETURN_VALUE</a>
> pyasmtools.prettydis(shuffle, show_opcode_as_links=True): None
</pre>


