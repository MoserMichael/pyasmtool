* [Python bytecode explained](#s1)
  * [Overview of the python bytecode](#s1-1)
  * [Disassembling of python code](#s1-2)
  * [learning by looking at disassembled code](#s1-3)
      * [learning about expression evaluation](#s1-3-1)
      * [learning about function calls](#s1-3-2)
      * [learning about loops](#s1-3-3)


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

Here is a [reference](https://docs.python.org/3/library/dis.html#python-bytecode-instructions) of the instructions, as part of the [dis](https://docs.python.org/3/library/dis.html) module from the python standard library. I was suprised to learn, that many bytecode instructions changed in minor releases of the runtime! If you are upgrading the python interpreter, then you probably should also delete all \_\_pycache\_\_ folders, these folders hold the binary files that hold the compiled bytecode instructions, but you can't be sure that these will work after an upgrade!



## <a id='s1-2' />Disassembling of python code

You can examine the pyhon bytecode of a function by means of a dissassembler, as part of the python standard library you have the [dis](https://docs.python.org/3/library/dis.html) package, that can show you the bytecode of a python function.

I have written a disassembler that is producing a combined listing for a given python function, this means that you have a line of the python source code, followed by the python bytecode instructions that this source line translates into; I hope that this combined listing will make it much easier to comprehend, what the byte code instructions mean. I think that this will illustrate the concepts, that were explained in the previous section.

Let's look at an example:

(There is one limitation, the tool can't be used, if running python code compiled from a string by means of the [compile](https://docs.python.org/3/library/functions.html#compile) and [exec](https://docs.python.org/3/library/functions.html#exec) built-in functions, here it is impossible to find the source code of a line, while running the program)



## <a id='s1-3' />learning by looking at disassembled code

We will now learn about the python bytecode, while looking at disassembled example functions


### <a id='s1-3-1' />learning about expression evaluation


__Source:__

```python
import prettydiasm

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

print( "prettydiasm.prettydis(calculator, show_opcode_as_links=True):", prettydiasm.prettydis(calculator, show_opcode_as_links=True) )


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
> prettydiasm.prettydis(calculator, show_opcode_as_links=True): None
</pre>


### <a id='s1-3-2' />learning about function calls


__Source:__

```python
import prettydiasm

def fac(arg_n=7):
    if arg_n == 1:
        return arg_n
    return arg_n * fac(arg_n - 1)

print( "prettydiasm.prettydis(fac, show_opcode_as_links=True):", prettydiasm.prettydis(fac, show_opcode_as_links=True) )

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
> prettydiasm.prettydis(fac, show_opcode_as_links=True): None
</pre>


### <a id='s1-3-3' />learning about loops


__Source:__

```python
import prettydiasm

def fac_iter(arg_n: int) -> int:
    res = 1
    for cur_n in range(1,arg_n):
        res *= cur_n
    return res

print( "prettydiasm.prettydis(fac, show_opcode_as_links=True):", prettydiasm.prettydis(fac_iter, show_opcode_as_links=True) )



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
> prettydiasm.prettydis(fac, show_opcode_as_links=True): None
</pre>


