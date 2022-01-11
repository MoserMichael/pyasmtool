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

Why should the python runtime maintain a separate stack, just for the purpose of evaluating an expression? One possible reason would be to simplify generators and asynchronous calls, here you need to switch often between co-routines, and it is easier to do so, if each activation record/frame has its own stack to begin with.

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
&gt; File path: /Users/michaelmo/mystuff/pyasmtools/calc.py 
&gt; 
&gt; calc.py:3 def calculator(op, num_one, num_two):
&gt; 
&gt; calc.py:4 	    if op == 1:
&gt; 
&gt;   4           0 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (op)
&gt;               2 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     1 (1)
&gt;               4 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-COMPARE_OP"&gt;COMPARE_OP&lt;/a&gt;     2 (==)
&gt;               6 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_FALSE"&gt;POP_JUMP_IF_FALSE&lt;/a&gt;    16
&gt; 
&gt; calc.py:5 	        return num_one + num_two
&gt; 
&gt;   5           8 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (num_one)
&gt;              10 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     2 (num_two)
&gt;              12 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_ADD"&gt;BINARY_ADD&lt;/a&gt;
&gt;              14 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE"&gt;RETURN_VALUE&lt;/a&gt;
&gt; 
&gt; calc.py:6 	    elif op == 2:
&gt; 
&gt;   6     &gt;&gt;   16 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (op)
&gt;              18 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     2 (2)
&gt;              20 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-COMPARE_OP"&gt;COMPARE_OP&lt;/a&gt;     2 (==)
&gt;              22 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_FALSE"&gt;POP_JUMP_IF_FALSE&lt;/a&gt;    32
&gt; 
&gt; calc.py:7 	        return num_one - num_two
&gt; 
&gt;   7          24 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (num_one)
&gt;              26 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     2 (num_two)
&gt;              28 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_SUBTRACT"&gt;BINARY_SUBTRACT&lt;/a&gt;
&gt;              30 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE"&gt;RETURN_VALUE&lt;/a&gt;
&gt; 
&gt; calc.py:8 	    elif op == 3:
&gt; 
&gt;   8     &gt;&gt;   32 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (op)
&gt;              34 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     3 (3)
&gt;              36 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-COMPARE_OP"&gt;COMPARE_OP&lt;/a&gt;     2 (==)
&gt;              38 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_FALSE"&gt;POP_JUMP_IF_FALSE&lt;/a&gt;    48
&gt; 
&gt; calc.py:9 	        return num_one * num_two
&gt; 
&gt;   9          40 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (num_one)
&gt;              42 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     2 (num_two)
&gt;              44 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_MULTIPLY"&gt;BINARY_MULTIPLY&lt;/a&gt;
&gt;              46 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE"&gt;RETURN_VALUE&lt;/a&gt;
&gt; 
&gt; calc.py:10 	    elif op == 4:
&gt; 
&gt;  10     &gt;&gt;   48 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (op)
&gt;              50 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     4 (4)
&gt;              52 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-COMPARE_OP"&gt;COMPARE_OP&lt;/a&gt;     2 (==)
&gt;              54 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_FALSE"&gt;POP_JUMP_IF_FALSE&lt;/a&gt;    64
&gt; 
&gt; calc.py:11 	        return num_one / num_two
&gt; 
&gt;  11          56 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (num_one)
&gt;              58 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     2 (num_two)
&gt;              60 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_TRUE_DIVIDE"&gt;BINARY_TRUE_DIVIDE&lt;/a&gt;
&gt;              62 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE"&gt;RETURN_VALUE&lt;/a&gt;
&gt; 
&gt; calc.py:13 	        raise ValueError("Invalid operation")
&gt; 
&gt;  13     &gt;&gt;   64 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL"&gt;LOAD_GLOBAL&lt;/a&gt;     0 (ValueError)
&gt;              66 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     5 ('Invalid operation')
&gt;              68 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION"&gt;CALL_FUNCTION&lt;/a&gt;     1
&gt;              70 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RAISE_VARARGS"&gt;RAISE_VARARGS&lt;/a&gt;     1
&gt;              72 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     0 (None)
&gt;              74 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE"&gt;RETURN_VALUE&lt;/a&gt;
&gt; pyasmtools.prettydis(calculator, show_opcode_as_links=True): None
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
&gt; File path: /Users/michaelmo/mystuff/pyasmtools/fac_rec.py 
&gt; 
&gt; fac_rec.py:3 def fac(arg_n = 7):
&gt; 
&gt; fac_rec.py:4 	    if arg_n == 1:
&gt; 
&gt;   4           0 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (arg_n)
&gt;               2 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     1 (1)
&gt;               4 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-COMPARE_OP"&gt;COMPARE_OP&lt;/a&gt;     2 (==)
&gt;               6 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_FALSE"&gt;POP_JUMP_IF_FALSE&lt;/a&gt;    12
&gt; 
&gt; fac_rec.py:5 	        return arg_n
&gt; 
&gt;   5           8 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (arg_n)
&gt;              10 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE"&gt;RETURN_VALUE&lt;/a&gt;
&gt; 
&gt; fac_rec.py:6 	    return arg_n * fac(arg_n - 1)
&gt; 
&gt;   6     &gt;&gt;   12 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (arg_n)
&gt;              14 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL"&gt;LOAD_GLOBAL&lt;/a&gt;     0 (fac)
&gt;              16 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (arg_n)
&gt;              18 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     1 (1)
&gt;              20 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_SUBTRACT"&gt;BINARY_SUBTRACT&lt;/a&gt;
&gt;              22 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION"&gt;CALL_FUNCTION&lt;/a&gt;     1
&gt;              24 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_MULTIPLY"&gt;BINARY_MULTIPLY&lt;/a&gt;
&gt;              26 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE"&gt;RETURN_VALUE&lt;/a&gt;
&gt; pyasmtools.prettydis(fac, show_opcode_as_links=True): None
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
&gt; File path: /Users/michaelmo/mystuff/pyasmtools/fac_iter.py 
&gt; 
&gt; fac_iter.py:3 def fac_iter(arg_n: int) -&gt; int:
&gt; 
&gt; fac_iter.py:4 	    res = 1
&gt; 
&gt;   4           0 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     1 (1)
&gt;               2 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     1 (res)
&gt; 
&gt; fac_iter.py:5 	    for cur_n in range(1,arg_n):
&gt; 
&gt;   5           4 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL"&gt;LOAD_GLOBAL&lt;/a&gt;     0 (range)
&gt;               6 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     1 (1)
&gt;               8 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (arg_n)
&gt;              10 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION"&gt;CALL_FUNCTION&lt;/a&gt;     2
&gt;              12 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-GET_ITER"&gt;GET_ITER&lt;/a&gt;
&gt;         &gt;&gt;   14 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-FOR_ITER"&gt;FOR_ITER&lt;/a&gt;    12 (to 28)
&gt;              16 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     2 (cur_n)
&gt; 
&gt; fac_iter.py:6 	        res *= cur_n
&gt; 
&gt;   6          18 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (res)
&gt;              20 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     2 (cur_n)
&gt;              22 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-INPLACE_MULTIPLY"&gt;INPLACE_MULTIPLY&lt;/a&gt;
&gt;              24 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     1 (res)
&gt;              26 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE"&gt;JUMP_ABSOLUTE&lt;/a&gt;    14
&gt; 
&gt; fac_iter.py:7 	    return res
&gt; 
&gt;   7     &gt;&gt;   28 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (res)
&gt;              30 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE"&gt;RETURN_VALUE&lt;/a&gt;
&gt; pyasmtools.prettydis(fac, show_opcode_as_links=True): None
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
&gt; hello world
&gt; File path: /Users/michaelmo/mystuff/pyasmtools/obj_call.py 
&gt; 
&gt; obj_call.py:7 def Hello.show(self):
&gt; 
&gt; obj_call.py:8 	        print(self.greeting)
&gt; 
&gt;   8           0 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL"&gt;LOAD_GLOBAL&lt;/a&gt;     0 (print)
&gt;               2 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (self)
&gt;               4 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_ATTR"&gt;LOAD_ATTR&lt;/a&gt;     1 (greeting)
&gt;               6 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION"&gt;CALL_FUNCTION&lt;/a&gt;     1
&gt;               8 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP"&gt;POP_TOP&lt;/a&gt;
&gt;              10 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     0 (None)
&gt;              12 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE"&gt;RETURN_VALUE&lt;/a&gt;
&gt; pyasmtools.prettydis(hello_obj.show, show_opcode_as_links=True): None
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
&gt; File path: /Users/michaelmo/mystuff/pyasmtools/histo.py 
&gt; 
&gt; histo.py:5 def compute_historgram(file_name):
&gt; 
&gt; histo.py:6 	    with open(file_name,'r') as file:
&gt; 
&gt;   6           0 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL"&gt;LOAD_GLOBAL&lt;/a&gt;     0 (open)
&gt;               2 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (file_name)
&gt;               4 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     1 ('r')
&gt;               6 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION"&gt;CALL_FUNCTION&lt;/a&gt;     2
&gt;               8 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-SETUP_WITH"&gt;SETUP_WITH&lt;/a&gt;   108 (to 118)
&gt;              10 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     1 (file)
&gt; 
&gt; histo.py:7 	        text = file.read()
&gt; 
&gt;   7          12 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (file)
&gt;              14 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_METHOD"&gt;LOAD_METHOD&lt;/a&gt;     1 (read)
&gt;              16 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_METHOD"&gt;CALL_METHOD&lt;/a&gt;     0
&gt;              18 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     2 (text)
&gt; 
&gt; histo.py:9 	        histo = {}
&gt; 
&gt;   9          20 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BUILD_MAP"&gt;BUILD_MAP&lt;/a&gt;     0
&gt;              22 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     3 (histo)
&gt; 
&gt; histo.py:10 	        for ch in text:
&gt; 
&gt;  10          24 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     2 (text)
&gt;              26 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-GET_ITER"&gt;GET_ITER&lt;/a&gt;
&gt;         &gt;&gt;   28 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-FOR_ITER"&gt;FOR_ITER&lt;/a&gt;    38 (to 68)
&gt;              30 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     4 (ch)
&gt; 
&gt; histo.py:11 	            if not ch in histo:
&gt; 
&gt;  11          32 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     4 (ch)
&gt;              34 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     3 (histo)
&gt;              36 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CONTAINS_OP"&gt;CONTAINS_OP&lt;/a&gt;     1
&gt;              38 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_FALSE"&gt;POP_JUMP_IF_FALSE&lt;/a&gt;    50
&gt; 
&gt; histo.py:12 	                histo[ch] = 1
&gt; 
&gt;  12          40 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     2 (1)
&gt;              42 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     3 (histo)
&gt;              44 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     4 (ch)
&gt;              46 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_SUBSCR"&gt;STORE_SUBSCR&lt;/a&gt;
&gt;              48 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE"&gt;JUMP_ABSOLUTE&lt;/a&gt;    28
&gt; 
&gt; histo.py:14 	                histo[ch] += 1
&gt; 
&gt;  14     &gt;&gt;   50 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     3 (histo)
&gt;              52 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     4 (ch)
&gt;              54 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-DUP_TOP_TWO"&gt;DUP_TOP_TWO&lt;/a&gt;
&gt;              56 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_SUBSCR"&gt;BINARY_SUBSCR&lt;/a&gt;
&gt;              58 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     2 (1)
&gt;              60 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-INPLACE_ADD"&gt;INPLACE_ADD&lt;/a&gt;
&gt;              62 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-ROT_THREE"&gt;ROT_THREE&lt;/a&gt;
&gt;              64 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_SUBSCR"&gt;STORE_SUBSCR&lt;/a&gt;
&gt;              66 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE"&gt;JUMP_ABSOLUTE&lt;/a&gt;    28
&gt; 
&gt; histo.py:16 	        for ch in histo.keys():
&gt; 
&gt;  16     &gt;&gt;   68 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     3 (histo)
&gt;              70 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_METHOD"&gt;LOAD_METHOD&lt;/a&gt;     2 (keys)
&gt;              72 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_METHOD"&gt;CALL_METHOD&lt;/a&gt;     0
&gt;              74 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-GET_ITER"&gt;GET_ITER&lt;/a&gt;
&gt;         &gt;&gt;   76 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-FOR_ITER"&gt;FOR_ITER&lt;/a&gt;    26 (to 104)
&gt;              78 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     4 (ch)
&gt; 
&gt; histo.py:17 	            print("char:", repr(ch), "frequency:", histo[ch])
&gt; 
&gt;  17          80 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL"&gt;LOAD_GLOBAL&lt;/a&gt;     3 (print)
&gt;              82 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     3 ('char:')
&gt;              84 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL"&gt;LOAD_GLOBAL&lt;/a&gt;     4 (repr)
&gt;              86 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     4 (ch)
&gt;              88 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION"&gt;CALL_FUNCTION&lt;/a&gt;     1
&gt;              90 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     4 ('frequency:')
&gt;              92 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     3 (histo)
&gt;              94 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     4 (ch)
&gt;              96 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_SUBSCR"&gt;BINARY_SUBSCR&lt;/a&gt;
&gt;              98 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION"&gt;CALL_FUNCTION&lt;/a&gt;     4
&gt;             100 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP"&gt;POP_TOP&lt;/a&gt;
&gt;             102 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE"&gt;JUMP_ABSOLUTE&lt;/a&gt;    76
&gt;         &gt;&gt;  104 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_BLOCK"&gt;POP_BLOCK&lt;/a&gt;
&gt;             106 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     0 (None)
&gt;             108 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-DUP_TOP"&gt;DUP_TOP&lt;/a&gt;
&gt;             110 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-DUP_TOP"&gt;DUP_TOP&lt;/a&gt;
&gt;             112 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION"&gt;CALL_FUNCTION&lt;/a&gt;     3
&gt;             114 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP"&gt;POP_TOP&lt;/a&gt;
&gt;             116 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_FORWARD"&gt;JUMP_FORWARD&lt;/a&gt;    16 (to 134)
&gt;         &gt;&gt;  118 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-WITH_EXCEPT_START"&gt;WITH_EXCEPT_START&lt;/a&gt;
&gt;             120 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_JUMP_IF_TRUE"&gt;POP_JUMP_IF_TRUE&lt;/a&gt;   124
&gt;             122 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RERAISE"&gt;RERAISE&lt;/a&gt;
&gt;         &gt;&gt;  124 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP"&gt;POP_TOP&lt;/a&gt;
&gt;             126 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP"&gt;POP_TOP&lt;/a&gt;
&gt;             128 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP"&gt;POP_TOP&lt;/a&gt;
&gt;             130 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_EXCEPT"&gt;POP_EXCEPT&lt;/a&gt;
&gt;             132 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP"&gt;POP_TOP&lt;/a&gt;
&gt;         &gt;&gt;  134 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     0 (None)
&gt;             136 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE"&gt;RETURN_VALUE&lt;/a&gt;
&gt; pyasmtools.prettydis(compute_historgram, show_opcode_as_links=True): None
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
&gt; File path: /Users/michaelmo/mystuff/pyasmtools/shuffle.py 
&gt; 
&gt; shuffle.py:7 def shuffle(arr_size):
&gt; 
&gt; shuffle.py:8 	    arr=[]
&gt; 
&gt;   8           0 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BUILD_LIST"&gt;BUILD_LIST&lt;/a&gt;     0
&gt;               2 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     1 (arr)
&gt; 
&gt; shuffle.py:9 	    for num in range(1,arr_size+1):
&gt; 
&gt;   9           4 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL"&gt;LOAD_GLOBAL&lt;/a&gt;     0 (range)
&gt;               6 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     1 (1)
&gt;               8 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (arr_size)
&gt;              10 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     1 (1)
&gt;              12 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_ADD"&gt;BINARY_ADD&lt;/a&gt;
&gt;              14 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION"&gt;CALL_FUNCTION&lt;/a&gt;     2
&gt;              16 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-GET_ITER"&gt;GET_ITER&lt;/a&gt;
&gt;         &gt;&gt;   18 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-FOR_ITER"&gt;FOR_ITER&lt;/a&gt;    14 (to 34)
&gt;              20 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     2 (num)
&gt; 
&gt; shuffle.py:10 	        arr.append(num)
&gt; 
&gt;  10          22 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (arr)
&gt;              24 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_METHOD"&gt;LOAD_METHOD&lt;/a&gt;     1 (append)
&gt;              26 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     2 (num)
&gt;              28 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_METHOD"&gt;CALL_METHOD&lt;/a&gt;     1
&gt;              30 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-POP_TOP"&gt;POP_TOP&lt;/a&gt;
&gt;              32 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE"&gt;JUMP_ABSOLUTE&lt;/a&gt;    18
&gt; 
&gt; shuffle.py:12 	    for nun in range(0, arr_size):
&gt; 
&gt;  12     &gt;&gt;   34 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL"&gt;LOAD_GLOBAL&lt;/a&gt;     0 (range)
&gt;              36 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     2 (0)
&gt;              38 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (arr_size)
&gt;              40 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION"&gt;CALL_FUNCTION&lt;/a&gt;     2
&gt;              42 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-GET_ITER"&gt;GET_ITER&lt;/a&gt;
&gt;         &gt;&gt;   44 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-FOR_ITER"&gt;FOR_ITER&lt;/a&gt;    44 (to 90)
&gt;              46 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     3 (nun)
&gt; 
&gt; shuffle.py:13 	        idx = random.randint(1,arr_size)
&gt; 
&gt;  13          48 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL"&gt;LOAD_GLOBAL&lt;/a&gt;     2 (random)
&gt;              50 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_METHOD"&gt;LOAD_METHOD&lt;/a&gt;     3 (randint)
&gt;              52 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     1 (1)
&gt;              54 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     0 (arr_size)
&gt;              56 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-CALL_METHOD"&gt;CALL_METHOD&lt;/a&gt;     2
&gt;              58 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     4 (idx)
&gt; 
&gt; shuffle.py:14 	        tmp = arr[0]
&gt; 
&gt;  14          60 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (arr)
&gt;              62 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     2 (0)
&gt;              64 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_SUBSCR"&gt;BINARY_SUBSCR&lt;/a&gt;
&gt;              66 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_FAST"&gt;STORE_FAST&lt;/a&gt;     5 (tmp)
&gt; 
&gt; shuffle.py:15 	        arr[0] = arr[idx]
&gt; 
&gt;  15          68 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (arr)
&gt;              70 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     4 (idx)
&gt;              72 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-BINARY_SUBSCR"&gt;BINARY_SUBSCR&lt;/a&gt;
&gt;              74 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (arr)
&gt;              76 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST"&gt;LOAD_CONST&lt;/a&gt;     2 (0)
&gt;              78 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_SUBSCR"&gt;STORE_SUBSCR&lt;/a&gt;
&gt; 
&gt; shuffle.py:16 	        arr[idx] = tmp
&gt; 
&gt;  16          80 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     5 (tmp)
&gt;              82 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (arr)
&gt;              84 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     4 (idx)
&gt;              86 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-STORE_SUBSCR"&gt;STORE_SUBSCR&lt;/a&gt;
&gt;              88 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-JUMP_ABSOLUTE"&gt;JUMP_ABSOLUTE&lt;/a&gt;    44
&gt; 
&gt; shuffle.py:18 	    return arr
&gt; 
&gt;  18     &gt;&gt;   90 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST"&gt;LOAD_FAST&lt;/a&gt;     1 (arr)
&gt;              92 &lt;a href="https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE"&gt;RETURN_VALUE&lt;/a&gt;
&gt; pyasmtools.prettydis(shuffle, show_opcode_as_links=True): None
</pre>


