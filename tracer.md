* [Execution traces in Python](#s1)
  * [Execution traces in the bash shell](#s1-1)
  * [Execution trace in Python](#s1-2)
  * [Let's make a better tracer for python!](#s1-3)
      * [The python tracer in action](#s1-3-1)


# <a id='s1' />Execution traces in Python

This section will examine, how to use our understanding of the Python bytecode, in order to write a better execution trace facility for Python.


## <a id='s1-1' />Execution traces in the bash shell

I am a big fan of traces in the scripting language of the bash shell. The [set -x](https://www.gnu.org/software/bash/manual/bash.html#index-BASH\_005fXTRACEFD) command enables a special trace mode, where the change and side effect of each line are displayed in the traces written to the standard error stream. Let's examine a few example of this feature; I think it will be relatively easy to understand the program, by looking at both the program code and its exeuction trace, even if one is not all to familiar with the bash scripting language.

The following example computes a factorial in a recursive way:


__Source:__

```python
#!/bin/bash

set -x 

factorial()
{
  if [ $1 -le 1 ]
  then
    echo 1
  else
    result=$(factorial $[$1-1])
    echo $((result*$1))
  fi
}

factorial 5

```

__Result:__
<pre>
+ factorial 5
+ '[' 5 -le 1 ']'
++ factorial 4
++ '[' 4 -le 1 ']'
+++ factorial 3
+++ '[' 3 -le 1 ']'
++++ factorial 2
++++ '[' 2 -le 1 ']'
+++++ factorial 1
+++++ '[' 1 -le 1 ']'
+++++ echo 1
++++ result=1
++++ echo 2
+++ result=2
+++ echo 6
++ result=6
++ echo 24
+ result=24
+ echo 120
120
</pre>

For examle the start of the invocation looks as follow

```
+ factorial 5
+ '[' 5 -le 1 ']'
```
The bash shell is an interpreter, it translates the source code into an in memory tree representation that is called the [abstract syntax tree](https://en.wikipedia.org/wiki/Abstract\_syntax\_tree)

The next step for the bash interpreter to evaluate the program, it does so by following the nodes of the abstract syntax tree.
This technique allows the bash interpreter to show an intuitive trace output for the function invocation and the test expression, it is all produced while evaluating the in memory representation / abstract syntax tree of the program.


The following example computes a factorial in an iterative way, note that the arithmethic bash expressions are not traced with the same level of detail as in the case of the test expressions!


__Source:__

```python
#!/bin/bash

set -x 


factorial()
{
    local num=$1
    fact=1
    for ((i=1;i<=num;i++))
    do
        fact=$(($fact*$i))
    done
    echo "$fact"
}

factorial 5

```

__Result:__
<pre>
+ factorial 5
+ local num=5
+ fact=1
+ (( i=1 ))
+ (( i<=num ))
+ fact=1
+ (( i++ ))
+ (( i<=num ))
+ fact=2
+ (( i++ ))
+ (( i<=num ))
+ fact=6
+ (( i++ ))
+ (( i<=num ))
+ fact=24
+ (( i++ ))
+ (( i<=num ))
+ fact=120
+ (( i++ ))
+ (( i<=num ))
+ echo 120
120
</pre>


## <a id='s1-2' />Execution trace in Python

The python standard library has the [trace](https://docs.python.org/3/library/trace.html) module, one of its features is to print out the source lines of a program, as the program is executed. Unfortunately, it does not show the variable values and does not show the modifications performed on these variables

(To be true, the trace module is a very versatile one, it can also be used to provides coverage analysis and can be used as a simle profiler)

Let's get the trace of a factorial program with the trace module, by running the following command 
```python3 -m trace --trace fac.py```



__Source:__

```python


def fac(arg_n):
    if arg_n == 1:
        return arg_n
    return arg_n * fac(arg_n - 1)

print(fac(6))

```

__Result:__
<pre>
--- modulename: fac, funcname: <module>
fac.py(3): def fac(arg_n):
fac.py(8): print(fac(6))
 --- modulename: fac, funcname: fac
fac.py(4):     if arg_n == 1:
fac.py(6):     return arg_n * fac(arg_n - 1)
 --- modulename: fac, funcname: fac
fac.py(4):     if arg_n == 1:
fac.py(6):     return arg_n * fac(arg_n - 1)
 --- modulename: fac, funcname: fac
fac.py(4):     if arg_n == 1:
fac.py(6):     return arg_n * fac(arg_n - 1)
 --- modulename: fac, funcname: fac
fac.py(4):     if arg_n == 1:
fac.py(6):     return arg_n * fac(arg_n - 1)
 --- modulename: fac, funcname: fac
fac.py(4):     if arg_n == 1:
fac.py(6):     return arg_n * fac(arg_n - 1)
 --- modulename: fac, funcname: fac
fac.py(4):     if arg_n == 1:
fac.py(5):         return arg_n
720
</pre>


## <a id='s1-3' />Let's make a better tracer for python!

Let's attemt to make a better trace facility for python.
The [sys.settrace](https://docs.python.org/3/library/sys.html#sys.settrace) function installs a callback, that is being called to trace the execution of every line; Now this function can install a special trace function, that will get called upon the exeuction of every opcode; here we could try and show the effect of load and store bytecode instructions. You can learn more about the python bytecode instructions [in this lesson](https://github.com/MoserMichael/pyasmtool/blob/master/bytecode\_disasm.md) 

A more complete implementation could trace the whole stack, as an expression is being evaluated and reduced on the stack, however i am a bit afraid, that the process would be very slow and a bit impractical. 


### <a id='s1-3-1' />The python tracer in action

Let's trace the execution of a recursive factorial function in python. Note that the tracer is defined as a decorator of the traced function. (You can learn more about decorators in [this lesson](https://github.com/MoserMichael/python-obj-system/blob/master/decorator.md)

The traced output is showing the file name, line numer and depth of the call stack, counting from the first call of the traced function.


__Source:__

```python
#!/usr/bin/env python3

import prettytrace


def fac(arg_n):
    if arg_n == 1:
        return arg_n
    return arg_n * fac(arg_n - 1)

fac = prettytrace.TraceMe(fac)

print( "fac(7):", fac(7))

```

__Result:__
<pre>
trace_fac_rec.py:6(1) def fac(arg_n):
trace_fac_rec.py:6(1) # arg_n=7
trace_fac_rec.py:7(1)     if arg_n == 1:
trace_fac_rec.py:7(1)     # load arg_n 7
trace_fac_rec.py:9(1)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(1)     # load arg_n 7
load_global: can't find  arg_n in any scope
trace_fac_rec.py:9(1)     # load arg_n 7
trace_fac_rec.py:6(2) def fac(arg_n):
trace_fac_rec.py:6(2)     # arg_n=6
trace_fac_rec.py:7(2)     if arg_n == 1:
trace_fac_rec.py:7(2)     # load arg_n 6
trace_fac_rec.py:9(2)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(2)     # load arg_n 6
load_global: can't find  arg_n in any scope
trace_fac_rec.py:9(2)     # load arg_n 6
trace_fac_rec.py:6(3) def fac(arg_n):
trace_fac_rec.py:6(3)     # arg_n=5
trace_fac_rec.py:7(3)     if arg_n == 1:
trace_fac_rec.py:7(3)     # load arg_n 5
trace_fac_rec.py:9(3)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(3)     # load arg_n 5
load_global: can't find  arg_n in any scope
trace_fac_rec.py:9(3)     # load arg_n 5
trace_fac_rec.py:6(4) def fac(arg_n):
trace_fac_rec.py:6(4)     # arg_n=4
trace_fac_rec.py:7(4)     if arg_n == 1:
trace_fac_rec.py:7(4)     # load arg_n 4
trace_fac_rec.py:9(4)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(4)     # load arg_n 4
load_global: can't find  arg_n in any scope
trace_fac_rec.py:9(4)     # load arg_n 4
trace_fac_rec.py:6(5) def fac(arg_n):
trace_fac_rec.py:6(5)     # arg_n=3
trace_fac_rec.py:7(5)     if arg_n == 1:
trace_fac_rec.py:7(5)     # load arg_n 3
trace_fac_rec.py:9(5)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(5)     # load arg_n 3
load_global: can't find  arg_n in any scope
trace_fac_rec.py:9(5)     # load arg_n 3
trace_fac_rec.py:6(6) def fac(arg_n):
trace_fac_rec.py:6(6)     # arg_n=2
trace_fac_rec.py:7(6)     if arg_n == 1:
trace_fac_rec.py:7(6)     # load arg_n 2
trace_fac_rec.py:9(6)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(6)     # load arg_n 2
load_global: can't find  arg_n in any scope
trace_fac_rec.py:9(6)     # load arg_n 2
trace_fac_rec.py:6(7) def fac(arg_n):
trace_fac_rec.py:6(7)     # arg_n=1
trace_fac_rec.py:7(7)     if arg_n == 1:
trace_fac_rec.py:7(7)     # load arg_n 1
trace_fac_rec.py:8(7)         return arg_n
trace_fac_rec.py:8(7)         # load arg_n 1
trace_fac_rec.py:8(7) return=1
trace_fac_rec.py:9(6) return=2
trace_fac_rec.py:9(5) return=6
trace_fac_rec.py:9(4) return=24
trace_fac_rec.py:9(3) return=120
trace_fac_rec.py:9(2) return=720
trace_fac_rec.py:9(1) return=5040
fac(7): 5040
</pre>

It is also possible to specify an indentation prefix that depends on the level of call nesting, just like in bash


__Source:__

```python
#!/usr/bin/env python3

import prettytrace


def fac(arg_n):
    if arg_n == 1:
        return arg_n
    return arg_n * fac(arg_n - 1)

fac = prettytrace.TraceMe(fac, trace_indent=True)

print( "fac(7):", fac(7))

```

__Result:__
<pre>
trace_fac_rec_indent.py:6(1). def fac(arg_n):
trace_fac_rec_indent.py:6(1). # arg_n=7
trace_fac_rec_indent.py:7(1).     if arg_n == 1:
trace_fac_rec_indent.py:7(1).     # load arg_n 7
trace_fac_rec_indent.py:9(1).     return arg_n * fac(arg_n - 1)
trace_fac_rec_indent.py:9(1).     # load arg_n 7
load_global: can't find  arg_n in any scope
trace_fac_rec_indent.py:9(1).     # load arg_n 7
trace_fac_rec_indent.py:6(2).. def fac(arg_n):
trace_fac_rec_indent.py:6(2)..     # arg_n=6
trace_fac_rec_indent.py:7(2)..     if arg_n == 1:
trace_fac_rec_indent.py:7(2)..     # load arg_n 6
trace_fac_rec_indent.py:9(2)..     return arg_n * fac(arg_n - 1)
trace_fac_rec_indent.py:9(2)..     # load arg_n 6
load_global: can't find  arg_n in any scope
trace_fac_rec_indent.py:9(2)..     # load arg_n 6
trace_fac_rec_indent.py:6(3)... def fac(arg_n):
trace_fac_rec_indent.py:6(3)...     # arg_n=5
trace_fac_rec_indent.py:7(3)...     if arg_n == 1:
trace_fac_rec_indent.py:7(3)...     # load arg_n 5
trace_fac_rec_indent.py:9(3)...     return arg_n * fac(arg_n - 1)
trace_fac_rec_indent.py:9(3)...     # load arg_n 5
load_global: can't find  arg_n in any scope
trace_fac_rec_indent.py:9(3)...     # load arg_n 5
trace_fac_rec_indent.py:6(4).... def fac(arg_n):
trace_fac_rec_indent.py:6(4)....     # arg_n=4
trace_fac_rec_indent.py:7(4)....     if arg_n == 1:
trace_fac_rec_indent.py:7(4)....     # load arg_n 4
trace_fac_rec_indent.py:9(4)....     return arg_n * fac(arg_n - 1)
trace_fac_rec_indent.py:9(4)....     # load arg_n 4
load_global: can't find  arg_n in any scope
trace_fac_rec_indent.py:9(4)....     # load arg_n 4
trace_fac_rec_indent.py:6(5)..... def fac(arg_n):
trace_fac_rec_indent.py:6(5).....     # arg_n=3
trace_fac_rec_indent.py:7(5).....     if arg_n == 1:
trace_fac_rec_indent.py:7(5).....     # load arg_n 3
trace_fac_rec_indent.py:9(5).....     return arg_n * fac(arg_n - 1)
trace_fac_rec_indent.py:9(5).....     # load arg_n 3
load_global: can't find  arg_n in any scope
trace_fac_rec_indent.py:9(5).....     # load arg_n 3
trace_fac_rec_indent.py:6(6)...... def fac(arg_n):
trace_fac_rec_indent.py:6(6)......     # arg_n=2
trace_fac_rec_indent.py:7(6)......     if arg_n == 1:
trace_fac_rec_indent.py:7(6)......     # load arg_n 2
trace_fac_rec_indent.py:9(6)......     return arg_n * fac(arg_n - 1)
trace_fac_rec_indent.py:9(6)......     # load arg_n 2
load_global: can't find  arg_n in any scope
trace_fac_rec_indent.py:9(6)......     # load arg_n 2
trace_fac_rec_indent.py:6(7)....... def fac(arg_n):
trace_fac_rec_indent.py:6(7).......     # arg_n=1
trace_fac_rec_indent.py:7(7).......     if arg_n == 1:
trace_fac_rec_indent.py:7(7).......     # load arg_n 1
trace_fac_rec_indent.py:8(7).......         return arg_n
trace_fac_rec_indent.py:8(7).......         # load arg_n 1
trace_fac_rec_indent.py:8(7)....... return=1
trace_fac_rec_indent.py:9(6)...... return=2
trace_fac_rec_indent.py:9(5)..... return=6
trace_fac_rec_indent.py:9(4).... return=24
trace_fac_rec_indent.py:9(3)... return=120
trace_fac_rec_indent.py:9(2).. return=720
trace_fac_rec_indent.py:9(1). return=5040
fac(7): 5040
</pre>

Let's trace the execution of an iterative factorial function in python


__Source:__

```python
#!/usr/bin/env python3

import prettytrace

def fac_iter(arg_n: int) -> int:
    res = 1
    for cur_n in range(1,arg_n+1):
        res *= cur_n
    return res

fac_iter = prettytrace.TraceMe(fac_iter)

print( "fac_iter(7):", fac_iter(7))

```

__Result:__
<pre>
trace_fac_iter.py:5(1) def fac_iter(arg_n: int) -> int:
trace_fac_iter.py:5(1) # arg_n=7
trace_fac_iter.py:6(1)     res = 1
trace_fac_iter.py:7(1)     # store res 1
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n+1):
load_global: can't find  arg_n in any scope
trace_fac_iter.py:7(1)     # load arg_n 7
trace_fac_iter.py:8(1)     # store cur_n 1
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 1
trace_fac_iter.py:8(1)         # load cur_n 1
trace_fac_iter.py:8(1)         # store res 1
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n+1):
trace_fac_iter.py:8(1)     # store cur_n 2
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 1
trace_fac_iter.py:8(1)         # load cur_n 2
trace_fac_iter.py:8(1)         # store res 2
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n+1):
trace_fac_iter.py:8(1)     # store cur_n 3
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 2
trace_fac_iter.py:8(1)         # load cur_n 3
trace_fac_iter.py:8(1)         # store res 6
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n+1):
trace_fac_iter.py:8(1)     # store cur_n 4
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 6
trace_fac_iter.py:8(1)         # load cur_n 4
trace_fac_iter.py:8(1)         # store res 24
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n+1):
trace_fac_iter.py:8(1)     # store cur_n 5
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 24
trace_fac_iter.py:8(1)         # load cur_n 5
trace_fac_iter.py:8(1)         # store res 120
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n+1):
trace_fac_iter.py:8(1)     # store cur_n 6
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 120
trace_fac_iter.py:8(1)         # load cur_n 6
trace_fac_iter.py:8(1)         # store res 720
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n+1):
trace_fac_iter.py:8(1)     # store cur_n 7
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 720
trace_fac_iter.py:8(1)         # load cur_n 7
trace_fac_iter.py:8(1)         # store res 5040
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n+1):
trace_fac_iter.py:9(1)     return res
trace_fac_iter.py:9(1)     # load res 5040
trace_fac_iter.py:9(1) return=5040
fac_iter(7): 5040
</pre>

So far the trace program did not need to access the evaluation stack of the python interpreter, the evalutation stack is currently not exposed by the interpreter to python code, as there is no field in the built-in frame object for it. I used a workaround, accessing the memory location referred to by the bytecode instruction before executing the [LOAD\_FAST](https://docs.python.org/3/library/dis.html#opcode-LOAD\_FAST) instruction, and accessing the modified location after running the [STORE\_FAST](https://docs.python.org/3/library/dis.html#opcode-STORE\_FAST) instruction, Hoever that trick is not feasible for the array and dictionary access instructions [STORE\_SUBSCR](https://docs.python.org/3.8/library/dis.html#opcode-STORE\_SUBSCR) and [BINARY\_SUBSCRIPT](https://docs.python.org/3.8/library/dis.html#opcode-LOAD\_SUBSCRIPT) bytecode instructions, here i would need to take a direct look at the evaluation stack.

It would however be possbible to do this trick, from python with the [ctypes module](https://docs.python.org/3/library/ctypes.html), without any native code at all! [see this discussion](https://stackoverflow.com/questions/44346433/in-c-python-accessing-the-bytecode-evaluation-stack), so back to the drawing board!

Given this trick, here is an example of tracing list and map access.


__Source:__

```python
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


```

__Result:__
<pre>
trace_lookup.py:7(1) def swap_list(arg_list):
trace_lookup.py:7(1) # arg_list=[1, 2]
trace_lookup.py:8(1)     tmp = arg_list[0]
trace_lookup.py:8(1)     # load arg_list [1, 2]
trace_lookup.py:8(1)     # binary_subscript arr[ 0 ]= 1
trace_lookup.py:9(1)     # store tmp 1
trace_lookup.py:9(1)     arg_list[0] = arg_list[1]
trace_lookup.py:9(1)     # load arg_list [1, 2]
trace_lookup.py:9(1)     # binary_subscript arr[ 1 ]= 2
trace_lookup.py:9(1)     # load arg_list [1, 2]
trace_lookup.py:9(1)     # store_subscript arr[ 0 ]= 2
trace_lookup.py:10(1)     arg_list[1] = tmp
trace_lookup.py:10(1)     # load tmp 1
trace_lookup.py:10(1)     # load arg_list [2, 2]
trace_lookup.py:10(1)     # store_subscript arr[ 1 ]= 1
trace_lookup.py:10(1) return=None
trace_lookup.py:12(1) def swap_dict(arg_dict):
trace_lookup.py:12(1) # arg_dict={'first': 'a', 'second': 'b'}
trace_lookup.py:13(1)     tmp = arg_dict['first']
trace_lookup.py:13(1)     # load arg_dict {'first': 'a', 'second': 'b'}
trace_lookup.py:13(1)     # binary_subscript arr[ 'first' ]= 'a'
trace_lookup.py:14(1)     # store tmp 'a'
trace_lookup.py:14(1)     arg_dict['first'] = arg_dict['second']
trace_lookup.py:14(1)     # load arg_dict {'first': 'a', 'second': 'b'}
trace_lookup.py:14(1)     # binary_subscript arr[ 'second' ]= 'b'
trace_lookup.py:14(1)     # load arg_dict {'first': 'a', 'second': 'b'}
trace_lookup.py:14(1)     # store_subscript arr[ 'first' ]= 'b'
trace_lookup.py:15(1)     arg_dict['second'] = tmp
trace_lookup.py:15(1)     # load tmp 'a'
trace_lookup.py:15(1)     # load arg_dict {'first': 'b', 'second': 'b'}
trace_lookup.py:15(1)     # store_subscript arr[ 'second' ]= 'a'
trace_lookup.py:15(1) return=None
[2, 1]
{'first': 'b', 'second': 'a'}
</pre>

Here is an example of accessing python objects. You can trace every method call of a class, here you need to define the class with the TraceClass metaclass. (You can learn more about metaclasses in [this lesson](https://github.com/MoserMichael/python-obj-system/blob/master/python-obj-system.md)


__Source:__

```python
#!/usr/bin/env python3

import prettytrace


class Complex(metaclass=prettytrace.TraceClass):
    def __init__(self, re, im=0.0):
        self.real = re
        self.imag = im

    def __add__(self, other):
        return Complex(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return Complex(self.real - other.real, self.imag - other.imag)

    def __mul__(self, other):
        return Complex((self.real * other.real) - (self.imag * other.imag),
            (self.imag * other.real) + (self.real * other.imag))

    def __truediv__(self, other):
        r = (other.real**2 + other.imag**2)
        return Complex((self.real*other.real - self.imag*other.imag)/r,
            (self.imag*other.real + self.real*other.imag)/r)

    def __abs__(self):
        print('\nAbsolute Value:')
        new = (self.real**2 + (self.imag**2)*-1)
        return Complex(sqrt(new.real))

    def __str__(self):
        return f"real: {self.real} imaginary: {self.imag}"

class Person:
    def  __init__(self, first_name, last_name):
        self.first_name  = first_name
        self.last_name = last_name
    def __str__(self):
        return f"first_name: {self.first_name} last_name: {self.last_name}"

class PersonWithTitle(Person, metaclass=prettytrace.TraceClass):
    def __init__(self, first_name, last_name, title):
        super().__init__(first_name, last_name)
        self.title = title
        #print(f"__init__ id: {id(self)} self.__dict__ {self.__dict__}")


    def __str__(self):
        #print(f"__str__ id: {id(self)} self.__dict__ {self.__dict__}")
        return f"Title: {self.title} {super().__str__()}"

num = Complex(2,3)
print(num)

per = PersonWithTitle("Pooh", "Bear", "Mr")
print(per)
print("eof")

```

__Result:__
<pre>
trace_obj.py:7(1)     def __init__(self, re, im=0.0):
trace_obj.py:7(1) # self=<object not initialised yet>
trace_obj.py:7(1) # re=2
trace_obj.py:7(1) # im=3
trace_obj.py:8(1)         self.real = re
trace_obj.py:8(1)         # load re 2
trace_obj.py:8(1)         # load self <object not initialised yet>
trace_obj.py:9(1)         self.imag = im
trace_obj.py:9(1)         # load im 3
trace_obj.py:9(1)         # load self <object not initialised yet>
trace_obj.py:9(1) return=None
trace_obj.py:31(1)     def __str__(self):
trace_obj.py:31(1) # self=real: 2 imaginary: 3
trace_obj.py:32(1)         return f"real: {self.real} imaginary: {self.imag}"
trace_obj.py:32(1)         # load self real: 2 imaginary: 3
trace_obj.py:32(1)         # load self real: 2 imaginary: 3
trace_obj.py:32(1) return=real: 2 imaginary: 3
trace_obj.py:42(1)     def __init__(self, first_name, last_name, title):
trace_obj.py:42(1) # self=<object not initialised yet>
trace_obj.py:42(1) # first_name=Pooh
trace_obj.py:42(1) # last_name=Bear
trace_obj.py:42(1) # title=Mr
trace_obj.py:43(1)         super().__init__(first_name, last_name)
load_global: can't find  self in any scope
trace_obj.py:43(1)         # load first_name Pooh
trace_obj.py:43(1)         # load last_name Bear
trace_obj.py:35(2)     def  __init__(self, first_name, last_name):
trace_obj.py:35(2)         # self=<object not initialised yet>
trace_obj.py:35(2)         # first_name=Pooh
trace_obj.py:35(2)         # last_name=Bear
trace_obj.py:36(2)         self.first_name  = first_name
trace_obj.py:36(2)         # load first_name Pooh
trace_obj.py:36(2)         # load self <object not initialised yet>
trace_obj.py:37(2)         self.last_name = last_name
trace_obj.py:37(2)         # load last_name Bear
trace_obj.py:37(2)         # load self <object not initialised yet>
trace_obj.py:37(2) return=None
trace_obj.py:44(1)         self.title = title
trace_obj.py:44(1)         # load title Mr
trace_obj.py:44(1)         # load self <object not initialised yet>
trace_obj.py:44(1) return=None
trace_obj.py:48(1)     def __str__(self):
trace_obj.py:48(1)         #print(f"__str__ id: {id(self)} self.__dict__ {self.__dict__}")
trace_obj.py:48(1) # self=Title: Mr first_name: Pooh last_name: Bear
trace_obj.py:50(1)         return f"Title: {self.title} {super().__str__()}"
trace_obj.py:50(1)         # load self Title: Mr first_name: Pooh last_name: Bear
Error: can't resolve argval Instruction: 116 argval: 1, frame: <frame at 0x7fc62bd85040, file '/Users/michaelmo/mystuff/pyasmtools/./trace_obj.py', line 50, code __str__>
trace_obj.py:38(2)     def __str__(self):
trace_obj.py:38(2)         # self=Title: Mr first_name: Pooh last_name: Bear
trace_obj.py:39(2)         return f"first_name: {self.first_name} last_name: {self.last_name}"
trace_obj.py:39(2)         # load self Title: Mr first_name: Pooh last_name: Bear
trace_obj.py:39(2)         # load self Title: Mr first_name: Pooh last_name: Bear
trace_obj.py:39(2) return=first_name: Pooh last_name: Bear
trace_obj.py:50(1) return=Title: Mr first_name: Pooh last_name: Bear
real: 2 imaginary: 3
Title: Mr first_name: Pooh last_name: Bear
eof
</pre>

Here is an example trace of a program, that number of occurances of each letter in its own text.


__Source:__

```python
#!/usr/bin/env python3

import prettytrace

#!/usr/bin/env python3

import prettytrace
import sys

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

compute_historgram = prettytrace.TraceMe(compute_historgram, out=sys.stdout) # out=sys.stdout - redirects trace output to sys.stdout

compute_historgram(__file__)


```

__Result:__
<pre>
load_global: can't find  file_name in any scope
trace_histo.py:10(1) def compute_historgram(file_name):
trace_histo.py:10(1) # file_name='/Users/michaelmo/mystuff/pyasmtools/./trace_histo.py'
trace_histo.py:11(1)     with open(file_name,'r') as file:
trace_histo.py:11(1)     # load file_name '/Users/michaelmo/mystuff/pyasmtools/./trace_histo.py'
trace_histo.py:12(1)     # store file <_io.TextIOWrapper name='/Users/michaelmo/mystuff/pyasmtools/./trace_histo.py' mode='r' encoding='UTF-8'>
trace_histo.py:12(1)         text = file.read()
trace_histo.py:12(1)         # load file <_io.TextIOWrapper name='/Users/michaelmo/mystuff/pyasmtools/./trace_histo.py' mode='r' encoding='UTF-8'>
trace_histo.py:14(1)         # store text '#!/usr/bin/env python3\n\nimport prettytrace\n\n#!/usr/bin/env python3\n\nimport prettytrace\nimport sys\n\ndef compute_historgram(file_name):\n    with open(file_name,\'r\') as file:\n        text = file.read()\n\n        histo = {}\n        for ch in text:\n            if not ch in histo:\n                histo[ch] = 1\n            else:\n                histo[ch] += 1\n\n        for ch in histo.keys():\n            print("char:", repr(ch), "frequency:", histo[ch])\n\ncompute_historgram = prettytrace.TraceMe(compute_historgram, out=sys.stdout) # out=sys.stdout - redirects trace output to sys.stdout\n\ncompute_historgram(__file__)\n\n'
trace_histo.py:14(1)         histo = {}
trace_histo.py:15(1)         # store histo {}
trace_histo.py:15(1)         for ch in text:
trace_histo.py:15(1)         # load text '#!/usr/bin/env python3\n\nimport prettytrace\n\n#!/usr/bin/env python3\n\nimport prettytrace\nimport sys\n\ndef compute_historgram(file_name):\n    with open(file_name,\'r\') as file:\n        text = file.read()\n\n        histo = {}\n        for ch in text:\n            if not ch in histo:\n                histo[ch] = 1\n            else:\n                histo[ch] += 1\n\n        for ch in histo.keys():\n            print("char:", repr(ch), "frequency:", histo[ch])\n\ncompute_historgram = prettytrace.TraceMe(compute_historgram, out=sys.stdout) # out=sys.stdout - redirects trace output to sys.stdout\n\ncompute_historgram(__file__)\n\n'
trace_histo.py:16(1)         # store ch '#'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '#'
trace_histo.py:16(1)             # load histo {}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {}
trace_histo.py:17(1)                 # load ch '#'
trace_histo.py:17(1)                 # store_subscript arr[ '#' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '!'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '!'
trace_histo.py:16(1)             # load histo {'#': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1}
trace_histo.py:17(1)                 # load ch '!'
trace_histo.py:17(1)                 # store_subscript arr[ '!' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '/'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '/'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1}
trace_histo.py:17(1)                 # load ch '/'
trace_histo.py:17(1)                 # store_subscript arr[ '/' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 1}
trace_histo.py:17(1)                 # load ch 'u'
trace_histo.py:17(1)                 # store_subscript arr[ 'u' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 1, 'u': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 1, 'u': 1}
trace_histo.py:17(1)                 # load ch 's'
trace_histo.py:17(1)                 # store_subscript arr[ 's' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 1, 'u': 1, 's': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 1, 'u': 1, 's': 1}
trace_histo.py:17(1)                 # load ch 'r'
trace_histo.py:17(1)                 # store_subscript arr[ 'r' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '/'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '/'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 1, 'u': 1, 's': 1, 'r': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 1, 'u': 1, 's': 1, 'r': 1}
trace_histo.py:19(1)                 # load ch '/'
trace_histo.py:19(1)                 # binary_subscript arr[ '/' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ '/' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'b'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'b'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 2, 'u': 1, 's': 1, 'r': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 2, 'u': 1, 's': 1, 'r': 1}
trace_histo.py:17(1)                 # load ch 'b'
trace_histo.py:17(1)                 # store_subscript arr[ 'b' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 2, 'u': 1, 's': 1, 'r': 1, 'b': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 2, 'u': 1, 's': 1, 'r': 1, 'b': 1}
trace_histo.py:17(1)                 # load ch 'i'
trace_histo.py:17(1)                 # store_subscript arr[ 'i' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 2, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 2, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1}
trace_histo.py:17(1)                 # load ch 'n'
trace_histo.py:17(1)                 # store_subscript arr[ 'n' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '/'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '/'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 2, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 2, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 1}
trace_histo.py:19(1)                 # load ch '/'
trace_histo.py:19(1)                 # binary_subscript arr[ '/' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ '/' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 1}
trace_histo.py:17(1)                 # load ch 'e'
trace_histo.py:17(1)                 # store_subscript arr[ 'e' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 1, 'e': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 1, 'e': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'v'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'v'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1}
trace_histo.py:17(1)                 # load ch 'v'
trace_histo.py:17(1)                 # store_subscript arr[ 'v' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1}
trace_histo.py:17(1)                 # load ch ' '
trace_histo.py:17(1)                 # store_subscript arr[ ' ' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1, ' ': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1, ' ': 1}
trace_histo.py:17(1)                 # load ch 'p'
trace_histo.py:17(1)                 # store_subscript arr[ 'p' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'y'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'y'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1, ' ': 1, 'p': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1, ' ': 1, 'p': 1}
trace_histo.py:17(1)                 # load ch 'y'
trace_histo.py:17(1)                 # store_subscript arr[ 'y' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1}
trace_histo.py:17(1)                 # load ch 't'
trace_histo.py:17(1)                 # store_subscript arr[ 't' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1}
trace_histo.py:17(1)                 # load ch 'h'
trace_histo.py:17(1)                 # store_subscript arr[ 'h' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1}
trace_histo.py:17(1)                 # load ch 'o'
trace_histo.py:17(1)                 # store_subscript arr[ 'o' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 2, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '3'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '3'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1}
trace_histo.py:17(1)                 # load ch '3'
trace_histo.py:17(1)                 # store_subscript arr[ '3' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1, '3': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1, '3': 1}
trace_histo.py:17(1)                 # load ch '\n'
trace_histo.py:17(1)                 # store_subscript arr[ '\n' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1, '3': 1, '\n': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1, '3': 1, '\n': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1, '3': 1, '\n': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 1, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1, '3': 1, '\n': 2}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1, '3': 1, '\n': 2}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1, '3': 1, '\n': 2}
trace_histo.py:17(1)                 # load ch 'm'
trace_histo.py:17(1)                 # store_subscript arr[ 'm' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 2, 'y': 1, 't': 1, 'h': 1, 'o': 1, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 2, 'y': 1, 't': 1, 'h': 1, 'o': 1, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 2, 'y': 1, 't': 1, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 1, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 2, 'y': 1, 't': 1, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 2, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 2, 'y': 1, 't': 1, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 2, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 2, 'y': 1, 't': 1, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 2, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 2, 'y': 1, 't': 2, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 2, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 1, 'p': 2, 'y': 1, 't': 2, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 2, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 2, 'p': 2, 'y': 1, 't': 2, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 2, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 2, 'p': 2, 'y': 1, 't': 2, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 2, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 2, 'p': 3, 'y': 1, 't': 2, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 2, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 2, 'p': 3, 'y': 1, 't': 2, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 3, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 2, 'p': 3, 'y': 1, 't': 2, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 3, 'b': 1, 'i': 2, 'n': 3, 'e': 1, 'v': 1, ' ': 2, 'p': 3, 'y': 1, 't': 2, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 3, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 1, 't': 2, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 3, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 1, 't': 2, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 3, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 1, 't': 3, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 3, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 1, 't': 3, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'y'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'y'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 3, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 1, 't': 4, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 3, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 1, 't': 4, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch 'y'
trace_histo.py:19(1)                 # binary_subscript arr[ 'y' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'y' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 3, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 4, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 3, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 4, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 3, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 3, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1}
trace_histo.py:17(1)                 # load ch 'a'
trace_histo.py:17(1)                 # store_subscript arr[ 'a' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1, 'a': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1, 'a': 1}
trace_histo.py:17(1)                 # load ch 'c'
trace_histo.py:17(1)                 # store_subscript arr[ 'c' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 2, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 2, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 3, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 3, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '#'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '#'
trace_histo.py:16(1)             # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 1, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch '#'
trace_histo.py:19(1)                 # binary_subscript arr[ '#' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ '#' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '!'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '!'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 1, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch '!'
trace_histo.py:19(1)                 # binary_subscript arr[ '!' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ '!' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '/'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '/'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 3, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch '/'
trace_histo.py:19(1)                 # binary_subscript arr[ '/' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ '/' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 4, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 4, 'u': 1, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 4, 'u': 2, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 4, 'u': 2, 's': 1, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 4, 'u': 2, 's': 2, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 4, 'u': 2, 's': 2, 'r': 4, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '/'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '/'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 4, 'u': 2, 's': 2, 'r': 5, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 4, 'u': 2, 's': 2, 'r': 5, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch '/'
trace_histo.py:19(1)                 # binary_subscript arr[ '/' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ '/' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'b'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'b'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 5, 'u': 2, 's': 2, 'r': 5, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 5, 'u': 2, 's': 2, 'r': 5, 'b': 1, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'b'
trace_histo.py:19(1)                 # binary_subscript arr[ 'b' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'b' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 5, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 5, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 2, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 5, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 5, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 3, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '/'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '/'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 5, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 4, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 5, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 4, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch '/'
trace_histo.py:19(1)                 # binary_subscript arr[ '/' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ '/' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 4, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 4, 'e': 3, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 4, 'e': 4, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 4, 'e': 4, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'v'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'v'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 1, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'v'
trace_histo.py:19(1)                 # binary_subscript arr[ 'v' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'v' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 2, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 3, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 3, 'p': 3, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'y'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'y'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 2, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'y'
trace_histo.py:19(1)                 # binary_subscript arr[ 'y' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'y' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 5, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 1, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 2, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 5, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '3'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '3'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 1, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch '3'
trace_histo.py:19(1)                 # binary_subscript arr[ '3' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ '3' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 2, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 2, '\n': 4, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 2, '\n': 5, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 2, '\n': 5, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 2, '\n': 6, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 3, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 2, '\n': 6, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 2, '\n': 6, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 2, '\n': 6, 'm': 1, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'm'
trace_histo.py:19(1)                 # binary_subscript arr[ 'm' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'm' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 4, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 5, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 5, 'y': 3, 't': 6, 'h': 2, 'o': 3, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 5, 'y': 3, 't': 6, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 5, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 5, 'y': 3, 't': 6, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 6, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 5, 'y': 3, 't': 6, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 6, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 5, 'y': 3, 't': 6, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 6, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 5, 'y': 3, 't': 7, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 6, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 3, 'p': 5, 'y': 3, 't': 7, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 6, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 4, 'p': 5, 'y': 3, 't': 7, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 6, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 4, 'p': 5, 'y': 3, 't': 7, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 6, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 4, 'p': 6, 'y': 3, 't': 7, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 6, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 4, 'p': 6, 'y': 3, 't': 7, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 7, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 4, 'p': 6, 'y': 3, 't': 7, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 7, 'b': 2, 'i': 4, 'n': 6, 'e': 4, 'v': 2, ' ': 4, 'p': 6, 'y': 3, 't': 7, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 7, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 3, 't': 7, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 7, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 3, 't': 7, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 7, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 3, 't': 8, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 7, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 3, 't': 8, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'y'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'y'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 7, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 3, 't': 9, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 7, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 3, 't': 9, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'y'
trace_histo.py:19(1)                 # binary_subscript arr[ 'y' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'y' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 7, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 9, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 7, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 9, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 7, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 7, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 1, 'c': 1}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 2, 'c': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 2, 'c': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 4, 'n': 6, 'e': 5, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 4, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 4, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 6, 'm': 2, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 4, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 7, 'm': 2, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 4, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 7, 'm': 2, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 7, 'm': 2, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 7, 'm': 2, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch 'm'
trace_histo.py:19(1)                 # binary_subscript arr[ 'm' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'm' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 6, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 7, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 7, 'y': 4, 't': 10, 'h': 2, 'o': 4, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 7, 'y': 4, 't': 10, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 8, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 7, 'y': 4, 't': 10, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 7, 'y': 4, 't': 10, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 7, 'y': 4, 't': 10, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 7, 'y': 4, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 4, 'p': 7, 'y': 4, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 4, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 2, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 4, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'y'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'y'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 3, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 4, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 3, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 4, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch 'y'
trace_histo.py:19(1)                 # binary_subscript arr[ 'y' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'y' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 3, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 3, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 7, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 8, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 8, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'd'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'd'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 2}
trace_histo.py:17(1)                 # load ch 'd'
trace_histo.py:17(1)                 # store_subscript arr[ 'd' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 2, 'd': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 6, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 2, 'd': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'f'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'f'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 2, 'd': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 2, 'd': 1}
trace_histo.py:17(1)                 # load ch 'f'
trace_histo.py:17(1)                 # store_subscript arr[ 'f' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 2, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 5, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 2, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 2, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 2, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 5, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 3, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 # load ch 'm'
trace_histo.py:19(1)                 # binary_subscript arr[ 'm' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'm' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 7, 'y': 5, 't': 11, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 11, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 2, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 11, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 11, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 11, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 12, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 7, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 12, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '_'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '_'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 12, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 12, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1}
trace_histo.py:17(1)                 # load ch '_'
trace_histo.py:17(1)                 # store_subscript arr[ '_' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 12, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 12, 'h': 2, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 12, 'h': 3, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 4, 'r': 9, 'b': 2, 'i': 5, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 12, 'h': 3, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 4, 'r': 9, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 12, 'h': 3, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 4, 'r': 9, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 12, 'h': 3, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 9, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 12, 'h': 3, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 9, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 12, 'h': 3, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 9, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 9, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 6, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 9, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 9, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'g'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'g'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 10, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 10, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1}
trace_histo.py:17(1)                 # load ch 'g'
trace_histo.py:17(1)                 # store_subscript arr[ 'g' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 10, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1, 'g': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 10, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1, 'g': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1, 'g': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 4, 'a': 2, 'c': 3, 'd': 1, 'f': 1, '_': 1, 'g': 1}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 4, 'a': 3, 'c': 3, 'd': 1, 'f': 1, '_': 1, 'g': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 4, 'a': 3, 'c': 3, 'd': 1, 'f': 1, '_': 1, 'g': 1}
trace_histo.py:19(1)                 # load ch 'm'
trace_histo.py:19(1)                 # binary_subscript arr[ 'm' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'm' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '('
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '('
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 1, '_': 1, 'g': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 1, '_': 1, 'g': 1}
trace_histo.py:17(1)                 # load ch '('
trace_histo.py:17(1)                 # store_subscript arr[ '(' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'f'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'f'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 1, '_': 1, 'g': 1, '(': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 1, '_': 1, 'g': 1, '(': 1}
trace_histo.py:19(1)                 # load ch 'f'
trace_histo.py:19(1)                 # binary_subscript arr[ 'f' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'f' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 2, '_': 1, 'g': 1, '(': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 6, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 2, '_': 1, 'g': 1, '(': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'l'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'l'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 2, '_': 1, 'g': 1, '(': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 2, '_': 1, 'g': 1, '(': 1}
trace_histo.py:17(1)                 # load ch 'l'
trace_histo.py:17(1)                 # store_subscript arr[ 'l' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 2, '_': 1, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 6, 'e': 8, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 2, '_': 1, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '_'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '_'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 6, 'e': 9, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 2, '_': 1, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 6, 'e': 9, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 2, '_': 1, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:19(1)                 # load ch '_'
trace_histo.py:19(1)                 # binary_subscript arr[ '_' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ '_' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 6, 'e': 9, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 6, 'e': 9, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 9, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 9, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 3, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 9, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 9, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 5, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:19(1)                 # load ch 'm'
trace_histo.py:19(1)                 # binary_subscript arr[ 'm' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'm' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 9, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 9, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ')'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ')'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1}
trace_histo.py:17(1)                 # load ch ')'
trace_histo.py:17(1)                 # store_subscript arr[ ')' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ':'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ':'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1}
trace_histo.py:17(1)                 # load ch ':'
trace_histo.py:17(1)                 # store_subscript arr[ ':' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 9, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 6, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 7, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 7, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 8, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 8, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 9, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 9, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'w'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'w'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 10, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 10, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1}
trace_histo.py:17(1)                 # load ch 'w'
trace_histo.py:17(1)                 # store_subscript arr[ 'w' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 10, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 7, 'n': 7, 'e': 10, 'v': 2, ' ': 10, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 10, 'v': 2, ' ': 10, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 10, 'v': 2, ' ': 10, 'p': 8, 'y': 5, 't': 13, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 10, 'v': 2, ' ': 10, 'p': 8, 'y': 5, 't': 14, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 10, 'v': 2, ' ': 10, 'p': 8, 'y': 5, 't': 14, 'h': 3, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 10, 'v': 2, ' ': 10, 'p': 8, 'y': 5, 't': 14, 'h': 4, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 10, 'v': 2, ' ': 10, 'p': 8, 'y': 5, 't': 14, 'h': 4, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 10, 'v': 2, ' ': 11, 'p': 8, 'y': 5, 't': 14, 'h': 4, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 10, 'v': 2, ' ': 11, 'p': 8, 'y': 5, 't': 14, 'h': 4, 'o': 7, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 10, 'v': 2, ' ': 11, 'p': 8, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 10, 'v': 2, ' ': 11, 'p': 8, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 10, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 10, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 11, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 7, 'e': 11, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '('
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '('
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 8, 'e': 11, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 8, 'e': 11, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 1, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch '('
trace_histo.py:19(1)                 # binary_subscript arr[ '(' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ '(' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'f'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'f'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 8, 'e': 11, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 2, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 8, 'e': 11, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 2, '_': 2, 'g': 1, '(': 2, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'f'
trace_histo.py:19(1)                 # binary_subscript arr[ 'f' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'f' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 8, 'e': 11, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 3, '_': 2, 'g': 1, '(': 2, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 8, 'n': 8, 'e': 11, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 3, '_': 2, 'g': 1, '(': 2, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'l'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'l'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 8, 'e': 11, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 3, '_': 2, 'g': 1, '(': 2, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 8, 'e': 11, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 3, '_': 2, 'g': 1, '(': 2, 'l': 1, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'l'
trace_histo.py:19(1)                 # binary_subscript arr[ 'l' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'l' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 8, 'e': 11, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 3, '_': 2, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 8, 'e': 11, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 3, '_': 2, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '_'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '_'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 8, 'e': 12, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 3, '_': 2, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 8, 'e': 12, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 3, '_': 2, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch '_'
trace_histo.py:19(1)                 # binary_subscript arr[ '_' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ '_' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 8, 'e': 12, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 8, 'e': 12, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 9, 'e': 12, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 9, 'e': 12, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 4, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 9, 'e': 12, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 9, 'e': 12, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 6, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'm'
trace_histo.py:19(1)                 # binary_subscript arr[ 'm' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'm' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 9, 'e': 12, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 9, 'e': 12, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ','
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ','
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1}
trace_histo.py:17(1)                 # load ch ','
trace_histo.py:17(1)                 # store_subscript arr[ ',' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch "'"
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch "'"
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1, ',': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1, ',': 1}
trace_histo.py:17(1)                 # load ch "'"
trace_histo.py:17(1)                 # store_subscript arr[ "'" ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1, ',': 1, "'": 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 11, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1, ',': 1, "'": 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch "'"
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch "'"
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1, ',': 1, "'": 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1, ',': 1, "'": 1}
trace_histo.py:19(1)                 # load ch "'"
trace_histo.py:19(1)                 # binary_subscript arr[ "'" ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ "'" ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ')'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ')'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 1, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch ')'
trace_histo.py:19(1)                 # binary_subscript arr[ ')' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ ')' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 11, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 12, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 12, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 5, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 12, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 5, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 12, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 12, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 12, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'f'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'f'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 3, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch 'f'
trace_histo.py:19(1)                 # binary_subscript arr[ 'f' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'f' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 9, 'n': 9, 'e': 13, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'l'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'l'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 13, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 13, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 2, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch 'l'
trace_histo.py:19(1)                 # binary_subscript arr[ 'l' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'l' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 13, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 13, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ':'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ':'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 1, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch ':'
trace_histo.py:19(1)                 # binary_subscript arr[ ':' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ ':' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 10, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 13, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 14, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 14, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 14
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 15
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 15, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 15, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 15
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 16
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 16, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 16, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 16
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 17
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 17, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 17, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 17
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 18
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 18, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 18, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 18
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 19
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 19, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 19, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 19
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 20
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 20, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 20, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 20
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 21
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 21, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 21, 'p': 9, 'y': 5, 't': 14, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 14
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 15
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 21, 'p': 9, 'y': 5, 't': 15, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 14, 'v': 2, ' ': 21, 'p': 9, 'y': 5, 't': 15, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 14
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 15
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'x'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'x'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 21, 'p': 9, 'y': 5, 't': 15, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 21, 'p': 9, 'y': 5, 't': 15, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2}
trace_histo.py:17(1)                 # load ch 'x'
trace_histo.py:17(1)                 # store_subscript arr[ 'x' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 21, 'p': 9, 'y': 5, 't': 15, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 21, 'p': 9, 'y': 5, 't': 15, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 15
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 16
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 21, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 21, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 21
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 22
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '='
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '='
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 22, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 22, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1}
trace_histo.py:17(1)                 # load ch '='
trace_histo.py:17(1)                 # store_subscript arr[ '=' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 22, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 22, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 22
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 23
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'f'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'f'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 4, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1}
trace_histo.py:19(1)                 # load ch 'f'
trace_histo.py:19(1)                 # binary_subscript arr[ 'f' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'f' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 10, 'n': 9, 'e': 15, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'l'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'l'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 11, 'n': 9, 'e': 15, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 11, 'n': 9, 'e': 15, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 3, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1}
trace_histo.py:19(1)                 # load ch 'l'
trace_histo.py:19(1)                 # binary_subscript arr[ 'l' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'l' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 11, 'n': 9, 'e': 15, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 11, 'n': 9, 'e': 15, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 15
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 16
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '.'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '.'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 11, 'n': 9, 'e': 16, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 11, 'n': 9, 'e': 16, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1}
trace_histo.py:17(1)                 # load ch '.'
trace_histo.py:17(1)                 # store_subscript arr[ '.' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 11, 'n': 9, 'e': 16, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 12, 'b': 2, 'i': 11, 'n': 9, 'e': 16, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 16, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 16, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 16
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 17
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 6, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'd'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'd'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 7, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 7, 'c': 3, 'd': 1, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch 'd'
trace_histo.py:19(1)                 # binary_subscript arr[ 'd' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'd' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '('
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '('
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 2, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch '('
trace_histo.py:19(1)                 # binary_subscript arr[ '(' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ '(' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ')'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ')'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 2, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch ')'
trace_histo.py:19(1)                 # binary_subscript arr[ ')' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ ')' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 11, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 12, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 12, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 23, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 23
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 24
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 24, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 24, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 24
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 25
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 25, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 25, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 25
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 26
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 26, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 26, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 26
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 27
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 27, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 27, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 27
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 28
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 28, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 28, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 28
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 29
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 29, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 29, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 29
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 30
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 30, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 30, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 30
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 31
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 31, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 31, 'p': 9, 'y': 5, 't': 16, 'h': 4, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 31, 'p': 9, 'y': 5, 't': 16, 'h': 5, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 11, 'n': 9, 'e': 17, 'v': 2, ' ': 31, 'p': 9, 'y': 5, 't': 16, 'h': 5, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 31, 'p': 9, 'y': 5, 't': 16, 'h': 5, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 6, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 31, 'p': 9, 'y': 5, 't': 16, 'h': 5, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 31, 'p': 9, 'y': 5, 't': 16, 'h': 5, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 31, 'p': 9, 'y': 5, 't': 16, 'h': 5, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 16
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 17
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 31, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 31, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 8, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 31, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 31, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 31
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 32
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '='
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '='
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 32, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 32, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 1, '.': 1}
trace_histo.py:19(1)                 # load ch '='
trace_histo.py:19(1)                 # binary_subscript arr[ '=' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ '=' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 32, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 32, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 32
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 33
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '{'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '{'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 33, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 33, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1}
trace_histo.py:17(1)                 # load ch '{'
trace_histo.py:17(1)                 # store_subscript arr[ '{' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '}'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '}'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 33, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 33, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1}
trace_histo.py:17(1)                 # load ch '}'
trace_histo.py:17(1)                 # store_subscript arr[ '}' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 33, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 33, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 13, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 33, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 33, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 33
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 34
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 34, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 34, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 34
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 35
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 35, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 35, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 35
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 36
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 36, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 36, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 36
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 37
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 37, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 37, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 37
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 38
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 38, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 38, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 38
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 39
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 39, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 39, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 39
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 40
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 40, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 40, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 40
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 41
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'f'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'f'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 41, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 41, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 5, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'f'
trace_histo.py:19(1)                 # binary_subscript arr[ 'f' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'f' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 41, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 41, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 9, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 41, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 13, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 41, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 41, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 41, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 41
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 42
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 42, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 42, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 3, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 42, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 42, 'p': 9, 'y': 5, 't': 17, 'h': 5, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 42, 'p': 9, 'y': 5, 't': 17, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 42, 'p': 9, 'y': 5, 't': 17, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 42
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 43
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 43, 'p': 9, 'y': 5, 't': 17, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 12, 'n': 9, 'e': 17, 'v': 2, ' ': 43, 'p': 9, 'y': 5, 't': 17, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 9, 'e': 17, 'v': 2, ' ': 43, 'p': 9, 'y': 5, 't': 17, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 9, 'e': 17, 'v': 2, ' ': 43, 'p': 9, 'y': 5, 't': 17, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 17, 'v': 2, ' ': 43, 'p': 9, 'y': 5, 't': 17, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 17, 'v': 2, ' ': 43, 'p': 9, 'y': 5, 't': 17, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 43
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 44
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 17, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 17, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 17, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 17, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 17
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 18
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 17, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 18, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 17, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 18, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 17
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 18
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'x'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'x'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 18, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 18, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 1, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'x'
trace_histo.py:19(1)                 # binary_subscript arr[ 'x' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'x' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 18, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 18, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 18
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 19
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ':'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ':'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 2, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ':'
trace_histo.py:19(1)                 # binary_subscript arr[ ':' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ ':' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 14, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 14
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 15
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 44, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 44
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 45
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 45, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 45, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 45
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 46
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 46, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 46, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 46
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 47
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 47, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 47, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 47
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 48
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 48, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 48, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 48
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 49
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 49, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 49, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 49
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 50
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 50, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 50, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 50
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 51
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 51, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 51, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 51
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 52
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 52, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 52, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 52
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 53
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 53, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 53, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 53
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 54
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 54, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 54, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 54
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 55
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 55, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 55, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 55
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 56
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 56, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 13, 'n': 10, 'e': 18, 'v': 2, ' ': 56, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'f'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'f'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 10, 'e': 18, 'v': 2, ' ': 56, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 10, 'e': 18, 'v': 2, ' ': 56, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 6, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'f'
trace_histo.py:19(1)                 # binary_subscript arr[ 'f' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'f' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 10, 'e': 18, 'v': 2, ' ': 56, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 10, 'e': 18, 'v': 2, ' ': 56, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 56
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 57
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 10, 'e': 18, 'v': 2, ' ': 57, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 10, 'e': 18, 'v': 2, ' ': 57, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 57, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 57, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 10, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 57, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 57, 'p': 9, 'y': 5, 't': 19, 'h': 6, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 19
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 20
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 57, 'p': 9, 'y': 5, 't': 20, 'h': 6, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 57, 'p': 9, 'y': 5, 't': 20, 'h': 6, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 57
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 58
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 58, 'p': 9, 'y': 5, 't': 20, 'h': 6, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 58, 'p': 9, 'y': 5, 't': 20, 'h': 6, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 4, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 58, 'p': 9, 'y': 5, 't': 20, 'h': 6, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 58, 'p': 9, 'y': 5, 't': 20, 'h': 6, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 58, 'p': 9, 'y': 5, 't': 20, 'h': 7, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 58, 'p': 9, 'y': 5, 't': 20, 'h': 7, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 58
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 59
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 59, 'p': 9, 'y': 5, 't': 20, 'h': 7, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 14, 'n': 11, 'e': 18, 'v': 2, ' ': 59, 'p': 9, 'y': 5, 't': 20, 'h': 7, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 14
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 15
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 15, 'n': 11, 'e': 18, 'v': 2, ' ': 59, 'p': 9, 'y': 5, 't': 20, 'h': 7, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 15, 'n': 11, 'e': 18, 'v': 2, ' ': 59, 'p': 9, 'y': 5, 't': 20, 'h': 7, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 15, 'n': 12, 'e': 18, 'v': 2, ' ': 59, 'p': 9, 'y': 5, 't': 20, 'h': 7, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 15, 'n': 12, 'e': 18, 'v': 2, ' ': 59, 'p': 9, 'y': 5, 't': 20, 'h': 7, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 59
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 60
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 15, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 20, 'h': 7, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 15, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 20, 'h': 7, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 15, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 20, 'h': 8, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 15, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 20, 'h': 8, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 15
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 16
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 20, 'h': 8, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 7, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 20, 'h': 8, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 20, 'h': 8, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 20, 'h': 8, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 20
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 21
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 11, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ':'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ':'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 3, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ':'
trace_histo.py:19(1)                 # binary_subscript arr[ ':' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ ':' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 15, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 15
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 16
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 60, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 60
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 61
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 61, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 61, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 61
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 62
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 62, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 62, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 62
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 63
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 63, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 63, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 63
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 64
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 64, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 64, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 64
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 65
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 65, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 65, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 65
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 66
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 66, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 66, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 66
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 67
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 67, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 67, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 67
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 68
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 68, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 68, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 68
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 69
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 69, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 69, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 69
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 70
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 70, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 70, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 70
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 71
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 71, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 71, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 71
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 72
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 72, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 72, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 72
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 73
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 73, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 73, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 73
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 74
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 74, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 74, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 74
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 75
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 75, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 75, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 75
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 76
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 21, 'h': 8, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 21, 'h': 9, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 16, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 21, 'h': 9, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 16
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 17
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 21, 'h': 9, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 8, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 21, 'h': 9, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 21, 'h': 9, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 21, 'h': 9, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 21
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 22
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 22, 'h': 9, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 22, 'h': 9, 'o': 12, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '['
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '['
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 22, 'h': 9, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 22, 'h': 9, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1}
trace_histo.py:17(1)                 # load ch '['
trace_histo.py:17(1)                 # store_subscript arr[ '[' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 22, 'h': 9, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1, '[': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 22, 'h': 9, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 5, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1, '[': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 22, 'h': 9, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1, '[': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 22, 'h': 9, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1, '[': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ']'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ']'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1, '[': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1, '[': 1}
trace_histo.py:17(1)                 # load ch ']'
trace_histo.py:17(1)                 # store_subscript arr[ ']' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 76, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 76
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 77
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '='
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '='
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 77, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 77, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 2, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1}
trace_histo.py:19(1)                 # load ch '='
trace_histo.py:19(1)                 # binary_subscript arr[ '=' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ '=' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 77, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 77, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 77
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 78
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '1'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '1'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 78, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 78, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1}
trace_histo.py:17(1)                 # load ch '1'
trace_histo.py:17(1)                 # store_subscript arr[ '1' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 78, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 78, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 16, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 16
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 17
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 78, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 78, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 78
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 79
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 79, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 79, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 79
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 80
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 80, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 80, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 80
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 81
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 81, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 81, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 81
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 82
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 82, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 82, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 82
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 83
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 83, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 83, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 83
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 84
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 84, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 84, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 84
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 85
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 85, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 85, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 85
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 86
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 86, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 86, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 86
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 87
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 87, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 87, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 87
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 88
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 88, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 88, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 88
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 89
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 89, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 89, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 89
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 90
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 18, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 18
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 19
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'l'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'l'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 19, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 19, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 4, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch 'l'
trace_histo.py:19(1)                 # binary_subscript arr[ 'l' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'l' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 19, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 9, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 19, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 19, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 19, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 19
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 20
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ':'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ':'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 4, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ':'
trace_histo.py:19(1)                 # binary_subscript arr[ ':' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ ':' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 17, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 17
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 18
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 90, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 90
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 91
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 91, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 91, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 91
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 92
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 92, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 92, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 92
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 93
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 93, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 93, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 93
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 94
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 94, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 94, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 94
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 95
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 95, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 95, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 95
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 96
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 96, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 96, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 96
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 97
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 97, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 97, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 97
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 98
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 98, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 98, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 98
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 99
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 99, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 99, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 99
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 100
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 100, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 100, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 100
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 101
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 101, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 101, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 101
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 102
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 102, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 102, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 102
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 103
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 103, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 103, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 103
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 104
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 104, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 104, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 104
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 105
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 105, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 105, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 105
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 106
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 22, 'h': 10, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 22, 'h': 11, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 17, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 22, 'h': 11, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 17
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 18
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 22, 'h': 11, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 10, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 22, 'h': 11, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 22, 'h': 11, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 22, 'h': 11, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 22
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 23
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 23, 'h': 11, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 23, 'h': 11, 'o': 13, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '['
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '['
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 23, 'h': 11, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 23, 'h': 11, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 1, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch '['
trace_histo.py:19(1)                 # binary_subscript arr[ '[' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ '[' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 23, 'h': 11, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 2, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 23, 'h': 11, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 6, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 2, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 23, 'h': 11, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 2, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 23, 'h': 11, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 2, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ']'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ']'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 2, ']': 1, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 2, ']': 1, '1': 1}
trace_histo.py:19(1)                 # load ch ']'
trace_histo.py:19(1)                 # binary_subscript arr[ ']' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ ']' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 106, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 106
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 107
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '+'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '+'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 107, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 107, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 1}
trace_histo.py:17(1)                 # load ch '+'
trace_histo.py:17(1)                 # store_subscript arr[ '+' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '='
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '='
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 107, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 1, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 107, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 3, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 1, '+': 1}
trace_histo.py:19(1)                 # load ch '='
trace_histo.py:19(1)                 # binary_subscript arr[ '=' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ '=' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 107, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 1, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 107, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 1, '+': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 107
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 108
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '1'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '1'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 108, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 1, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 108, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 1, '+': 1}
trace_histo.py:19(1)                 # load ch '1'
trace_histo.py:19(1)                 # binary_subscript arr[ '1' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ '1' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 108, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 108, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 18, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 18
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 19
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 108, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 19, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 108, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 19, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 19
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 20
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 108, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 108, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 108
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 109
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 109, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 109, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 109
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 110
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 110, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 110, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 110
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 111
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 111, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 111, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 111
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 112
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 112, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 112, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 112
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 113
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 113, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 113, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 113
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 114
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 114, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 114, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 114
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 115
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 115, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 115, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 115
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 116
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'f'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'f'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 116, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 116, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 7, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch 'f'
trace_histo.py:19(1)                 # binary_subscript arr[ 'f' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'f' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 116, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 116, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 14, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 14
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 15
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 116, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 14, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 116, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 14
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 15
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 116, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 116, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 116
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 117
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 117, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 117, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 7, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 117, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 117, 'p': 9, 'y': 5, 't': 23, 'h': 12, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 117, 'p': 9, 'y': 5, 't': 23, 'h': 13, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 117, 'p': 9, 'y': 5, 't': 23, 'h': 13, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 117
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 118
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 118, 'p': 9, 'y': 5, 't': 23, 'h': 13, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 18, 'n': 12, 'e': 20, 'v': 2, ' ': 118, 'p': 9, 'y': 5, 't': 23, 'h': 13, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 18
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 19
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 19, 'n': 12, 'e': 20, 'v': 2, ' ': 118, 'p': 9, 'y': 5, 't': 23, 'h': 13, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 19, 'n': 12, 'e': 20, 'v': 2, ' ': 118, 'p': 9, 'y': 5, 't': 23, 'h': 13, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 19, 'n': 13, 'e': 20, 'v': 2, ' ': 118, 'p': 9, 'y': 5, 't': 23, 'h': 13, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 19, 'n': 13, 'e': 20, 'v': 2, ' ': 118, 'p': 9, 'y': 5, 't': 23, 'h': 13, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 118
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 119
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 19, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 23, 'h': 13, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 19, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 23, 'h': 13, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 19, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 23, 'h': 14, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 19, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 23, 'h': 14, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 19
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 20
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 23, 'h': 14, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 11, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 23, 'h': 14, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 23, 'h': 14, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 23, 'h': 14, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 23
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 24
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 24, 'h': 14, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 24, 'h': 14, 'o': 15, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 15
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 16
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '.'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '.'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 1, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:19(1)                 # load ch '.'
trace_histo.py:19(1)                 # binary_subscript arr[ '.' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ '.' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'k'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'k'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1}
trace_histo.py:17(1)                 # load ch 'k'
trace_histo.py:17(1)                 # store_subscript arr[ 'k' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 20, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 20
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 21
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'y'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'y'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 5, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch 'y'
trace_histo.py:19(1)                 # binary_subscript arr[ 'y' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'y' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 12, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '('
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '('
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 3, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch '('
trace_histo.py:19(1)                 # binary_subscript arr[ '(' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ '(' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ')'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ')'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 3, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ')'
trace_histo.py:19(1)                 # binary_subscript arr[ ')' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ ')' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ':'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ':'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 5, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ':'
trace_histo.py:19(1)                 # binary_subscript arr[ ':' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ ':' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 20, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 20
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 21
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 119, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 119
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 120
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 120, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 120, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 120
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 121
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 121, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 121, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 121
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 122
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 122, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 122, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 122
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 123
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 123, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 123, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 123
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 124
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 124, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 124, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 124
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 125
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 125, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 125, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 125
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 126
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 126, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 126, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 126
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 127
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 127, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 127, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 127
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 128
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 128, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 128, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 128
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 129
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 129, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 129, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 129
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 130
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 130, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 130, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 130
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 131
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 131, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 131, 'p': 9, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 15, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 15
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 16
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 20, 'n': 13, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 20
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 21
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 13, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 13, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 24, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 24
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 25
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '('
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '('
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 4, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:19(1)                 # load ch '('
trace_histo.py:19(1)                 # binary_subscript arr[ '(' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ '(' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '"'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '"'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1}
trace_histo.py:17(1)                 # load ch '"'
trace_histo.py:17(1)                 # store_subscript arr[ '"' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 8, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 14, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 14
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 15
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 7, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 1}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 16, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 16
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 17
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ':'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ':'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 17, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 17, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 6, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 1}
trace_histo.py:19(1)                 # load ch ':'
trace_histo.py:19(1)                 # binary_subscript arr[ ':' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ ':' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '"'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '"'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 17, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 17, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 1}
trace_histo.py:19(1)                 # load ch '"'
trace_histo.py:19(1)                 # binary_subscript arr[ '"' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ '"' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ','
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ','
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 17, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 17, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 1, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch ','
trace_histo.py:19(1)                 # binary_subscript arr[ ',' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ ',' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 17, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 17, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 131, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 131
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 132
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 17, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 132, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 17, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 132, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 17
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 18
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 18, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 132, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 18, 'b': 2, 'i': 21, 'n': 14, 'e': 21, 'v': 2, ' ': 132, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 21
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 22
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 18, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 18, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 10, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 18, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 18, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 18
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 19
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '('
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '('
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 5, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch '('
trace_histo.py:19(1)                 # binary_subscript arr[ '(' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ '(' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 9, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 15, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 15
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 16
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ')'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ')'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 4, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch ')'
trace_histo.py:19(1)                 # binary_subscript arr[ ')' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ ')' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ','
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ','
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 2, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch ','
trace_histo.py:19(1)                 # binary_subscript arr[ ',' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ ',' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 132, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 132
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 133
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '"'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '"'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 2}
trace_histo.py:19(1)                 # load ch '"'
trace_histo.py:19(1)                 # binary_subscript arr[ '"' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ '"' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'f'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'f'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 8, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3}
trace_histo.py:19(1)                 # load ch 'f'
trace_histo.py:19(1)                 # binary_subscript arr[ 'f' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'f' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 19, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 19
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 20
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 14, 'e': 22, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 22
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 23
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'q'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'q'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 14, 'e': 23, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 14, 'e': 23, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3}
trace_histo.py:17(1)                 # load ch 'q'
trace_histo.py:17(1)                 # store_subscript arr[ 'q' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 14, 'e': 23, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 3, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 14, 'e': 23, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 14, 'e': 23, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 14, 'e': 23, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 23
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 24
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 14, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 14, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 # load ch 'n'
trace_histo.py:19(1)                 # binary_subscript arr[ 'n' ]= 14
trace_histo.py:19(1)                 # store_subscript arr[ 'n' ]= 15
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 10, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'y'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'y'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 6, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 # load ch 'y'
trace_histo.py:19(1)                 # binary_subscript arr[ 'y' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'y' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ':'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ':'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 7, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 7, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 7, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 # load ch ':'
trace_histo.py:19(1)                 # binary_subscript arr[ ':' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ ':' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '"'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '"'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 7, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 7, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 3, 'q': 1}
trace_histo.py:19(1)                 # load ch '"'
trace_histo.py:19(1)                 # binary_subscript arr[ '"' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ '"' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ','
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ','
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 7, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 7, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 3, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch ','
trace_histo.py:19(1)                 # binary_subscript arr[ ',' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ ',' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 7, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 133, 'p': 11, 'y': 7, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 133
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 134
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 25, 'h': 16, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 16
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 17
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 25, 'h': 17, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 21, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 25, 'h': 17, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 21
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 22
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 25, 'h': 17, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 13, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 25, 'h': 17, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 25, 'h': 17, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 25, 'h': 17, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 25
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 26
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 17, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 17, 'o': 16, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 16
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 17
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '['
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '['
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 17, 'o': 17, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 17, 'o': 17, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 2, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch '['
trace_histo.py:19(1)                 # binary_subscript arr[ '[' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ '[' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 17, 'o': 17, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 17, 'o': 17, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 11, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 17, 'o': 17, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 12, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 17, 'o': 17, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 12, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 17
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 18
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ']'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ']'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 17, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 12, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 17, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 12, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 2, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch ']'
trace_histo.py:19(1)                 # binary_subscript arr[ ']' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ ']' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ')'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ')'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 17, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 12, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 17, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 12, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 5, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch ')'
trace_histo.py:19(1)                 # binary_subscript arr[ ')' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ ')' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 17, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 12, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 17, '3': 2, '\n': 21, 'm': 7, 'a': 8, 'c': 12, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 21
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 22
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 17, '3': 2, '\n': 22, 'm': 7, 'a': 8, 'c': 12, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 17, '3': 2, '\n': 22, 'm': 7, 'a': 8, 'c': 12, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 22
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 23
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 17, '3': 2, '\n': 23, 'm': 7, 'a': 8, 'c': 12, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 17, '3': 2, '\n': 23, 'm': 7, 'a': 8, 'c': 12, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 17, '3': 2, '\n': 23, 'm': 7, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 17, '3': 2, '\n': 23, 'm': 7, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 17
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 18
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 7, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 7, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'm'
trace_histo.py:19(1)                 # binary_subscript arr[ 'm' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'm' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 11, 'y': 7, 't': 26, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 26, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 4, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 26, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 26, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 26, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 26
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 27
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 27, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 24, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 27, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 24
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 25
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '_'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '_'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 27, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 27, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 3, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch '_'
trace_histo.py:19(1)                 # binary_subscript arr[ '_' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ '_' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 27, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 27, 'h': 18, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 18
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 19
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 27, 'h': 19, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 14, 'r': 20, 'b': 2, 'i': 22, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 27, 'h': 19, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 22
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 23
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 14, 'r': 20, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 27, 'h': 19, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 14, 'r': 20, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 27, 'h': 19, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 14
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 15
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 20, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 27, 'h': 19, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 20, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 27, 'h': 19, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 27
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 28
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 20, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 20, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 18, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 18
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 19
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 20, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 20, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 20
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 21
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'g'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'g'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 21, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 21, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 1, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'g'
trace_histo.py:19(1)                 # binary_subscript arr[ 'g' ]= 1
trace_histo.py:19(1)                 # store_subscript arr[ 'g' ]= 2
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 21, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 21, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 21
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 22
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 8, 'a': 8, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 8, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 8, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'm'
trace_histo.py:19(1)                 # binary_subscript arr[ 'm' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'm' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 134, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 134
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 135
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '='
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '='
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 135, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 135, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 4, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch '='
trace_histo.py:19(1)                 # binary_subscript arr[ '=' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ '=' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 135, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 135, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 135
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 136
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 136, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 136, 'p': 12, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 136, 'p': 13, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 22, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 136, 'p': 13, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 22
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 23
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 23, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 136, 'p': 13, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 23, 'b': 2, 'i': 23, 'n': 15, 'e': 25, 'v': 2, ' ': 136, 'p': 13, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 25
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 26
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 23, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 23, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 7, 't': 28, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 28
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 29
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 23, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 7, 't': 29, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 23, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 7, 't': 29, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 29
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 30
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'y'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'y'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 23, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 7, 't': 30, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 23, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 7, 't': 30, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'y'
trace_histo.py:19(1)                 # binary_subscript arr[ 'y' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'y' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 23, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 30, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 23, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 30, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 30
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 31
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 23, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 23, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 23
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 24
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 24, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 24, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 9, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 24, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 10, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 24, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 10, 'c': 13, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 24, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 10, 'c': 14, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 24, 'b': 2, 'i': 23, 'n': 15, 'e': 26, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 10, 'c': 14, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 26
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 27
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '.'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '.'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 24, 'b': 2, 'i': 23, 'n': 15, 'e': 27, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 10, 'c': 14, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 24, 'b': 2, 'i': 23, 'n': 15, 'e': 27, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 10, 'c': 14, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 2, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:19(1)                 # load ch '.'
trace_histo.py:19(1)                 # binary_subscript arr[ '.' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ '.' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'T'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'T'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 24, 'b': 2, 'i': 23, 'n': 15, 'e': 27, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 10, 'c': 14, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 24, 'b': 2, 'i': 23, 'n': 15, 'e': 27, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 10, 'c': 14, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1}
trace_histo.py:17(1)                 # load ch 'T'
trace_histo.py:17(1)                 # store_subscript arr[ 'T' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 24, 'b': 2, 'i': 23, 'n': 15, 'e': 27, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 10, 'c': 14, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 24, 'b': 2, 'i': 23, 'n': 15, 'e': 27, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 10, 'c': 14, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 24
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 25
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 27, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 10, 'c': 14, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 27, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 10, 'c': 14, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 27, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 14, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 27, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 14, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 14
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 15
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 27, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 15, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 27, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 15, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 27
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 28
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'M'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'M'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 28, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 15, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 28, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 15, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1}
trace_histo.py:17(1)                 # load ch 'M'
trace_histo.py:17(1)                 # store_subscript arr[ 'M' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 28, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 15, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 28, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 15, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 28
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 29
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '('
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '('
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 15, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 15, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 6, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch '('
trace_histo.py:19(1)                 # binary_subscript arr[ '(' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ '(' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 15, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 15, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 15
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 16
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 19, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 19
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 20
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 9, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'm'
trace_histo.py:19(1)                 # binary_subscript arr[ 'm' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'm' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 13, 'y': 8, 't': 31, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 31, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 5, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 31, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 31, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 31, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 31
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 32
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 32, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 29, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 32, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 29
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 30
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '_'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '_'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 32, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 32, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 4, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch '_'
trace_histo.py:19(1)                 # binary_subscript arr[ '_' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ '_' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 32, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 32, 'h': 19, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 19
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 20
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 32, 'h': 20, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 15, 'r': 25, 'b': 2, 'i': 23, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 32, 'h': 20, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 23
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 24
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 15, 'r': 25, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 32, 'h': 20, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 15, 'r': 25, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 32, 'h': 20, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 15
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 16
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 25, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 32, 'h': 20, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 25, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 32, 'h': 20, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 32
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 33
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 25, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 25, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 20, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 20
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 21
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 25, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 25, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 25
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 26
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'g'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'g'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 26, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 26, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 2, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'g'
trace_histo.py:19(1)                 # binary_subscript arr[ 'g' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'g' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 26, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 26, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 26
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 27
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 10, 'a': 11, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 10, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 10, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'm'
trace_histo.py:19(1)                 # binary_subscript arr[ 'm' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 'm' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ','
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ','
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 4, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch ','
trace_histo.py:19(1)                 # binary_subscript arr[ ',' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ ',' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 136, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 136
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 137
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 21, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 21
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 22
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 6, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 8, 't': 33, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 33
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 34
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '='
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '='
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 8, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 8, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 5, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch '='
trace_histo.py:19(1)                 # binary_subscript arr[ '=' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ '=' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 8, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 16, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 8, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 16
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 17
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'y'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'y'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 17, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 8, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 17, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 8, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'y'
trace_histo.py:19(1)                 # binary_subscript arr[ 'y' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'y' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 17, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 17, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 17
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 18
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '.'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '.'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 18, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 18, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 3, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch '.'
trace_histo.py:19(1)                 # binary_subscript arr[ '.' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ '.' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 18, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 18, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 18
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 19
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 34, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 34
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 35
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'd'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'd'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 35, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 35, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 2, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'd'
trace_histo.py:19(1)                 # binary_subscript arr[ 'd' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ 'd' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 35, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 35, 'h': 20, 'o': 22, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 22
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 23
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 35, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 7, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 35, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 35, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 35, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 35
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 36
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ')'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ')'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 6, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch ')'
trace_histo.py:19(1)                 # binary_subscript arr[ ')' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ ')' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 137, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 137
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 138
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '#'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '#'
trace_histo.py:16(1)             # load histo {'#': 2, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 138, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 2, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 138, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch '#'
trace_histo.py:19(1)                 # binary_subscript arr[ '#' ]= 2
trace_histo.py:19(1)                 # store_subscript arr[ '#' ]= 3
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 138, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 138, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 138
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 139
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 23, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 23
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 24
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 8, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 9, 't': 36, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 36
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 37
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '='
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '='
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 9, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 9, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 6, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch '='
trace_histo.py:19(1)                 # binary_subscript arr[ '=' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ '=' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 9, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 19, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 9, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 19
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 20
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'y'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'y'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 20, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 9, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 20, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 9, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'y'
trace_histo.py:19(1)                 # binary_subscript arr[ 'y' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'y' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 20, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 20, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 20
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 21
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '.'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '.'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 21, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 21, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 4, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch '.'
trace_histo.py:19(1)                 # binary_subscript arr[ '.' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ '.' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 21, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 21, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 21
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 22
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 37, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 37
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 38
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'd'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'd'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 38, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 38, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 3, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'd'
trace_histo.py:19(1)                 # binary_subscript arr[ 'd' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'd' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 38, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 38, 'h': 20, 'o': 24, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 24
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 25
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 38, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 9, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 38, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 38, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 38, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 38
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 39
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 139, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 139
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 140
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '-'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '-'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 140, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:17(1)                 histo[ch] = 1
trace_histo.py:17(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 140, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1}
trace_histo.py:17(1)                 # load ch '-'
trace_histo.py:17(1)                 # store_subscript arr[ '-' ]= 1
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 140, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 140, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 140
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 141
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 27, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 27
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 28
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 28, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 28, 'b': 2, 'i': 24, 'n': 15, 'e': 30, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 30
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 31
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'd'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'd'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 28, 'b': 2, 'i': 24, 'n': 15, 'e': 31, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 28, 'b': 2, 'i': 24, 'n': 15, 'e': 31, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 4, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'd'
trace_histo.py:19(1)                 # binary_subscript arr[ 'd' ]= 4
trace_histo.py:19(1)                 # store_subscript arr[ 'd' ]= 5
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 28, 'b': 2, 'i': 24, 'n': 15, 'e': 31, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 28, 'b': 2, 'i': 24, 'n': 15, 'e': 31, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 24
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 25
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 28, 'b': 2, 'i': 25, 'n': 15, 'e': 31, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 28, 'b': 2, 'i': 25, 'n': 15, 'e': 31, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 28
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 29
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 31, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 31, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 31
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 32
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 16, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 16
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 17
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 39, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 39
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 40
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 40, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 22, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 40, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 22
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 23
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 40, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 141, 'p': 14, 'y': 10, 't': 40, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 141
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 142
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 142, 'p': 14, 'y': 10, 't': 40, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 142, 'p': 14, 'y': 10, 't': 40, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 40
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 41
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 142, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 29, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 142, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 29
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 30
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 142, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 142, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 12, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 142, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 142, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 17, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 17
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 18
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 142, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 32, 'v': 2, ' ': 142, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 32
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 33
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 142, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 142, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 142
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 143
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 25, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 25
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 26
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 10, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 11, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 11, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 14, 'y': 10, 't': 41, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 41
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 42
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 11, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 14, 'y': 10, 't': 42, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 11, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 14, 'y': 10, 't': 42, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 14
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 15
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 11, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 15, 'y': 10, 't': 42, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 11, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 15, 'y': 10, 't': 42, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 15, 'y': 10, 't': 42, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 15, 'y': 10, 't': 42, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 42
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 43
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 15, 'y': 10, 't': 43, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 143, 'p': 15, 'y': 10, 't': 43, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 143
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 144
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 144, 'p': 15, 'y': 10, 't': 43, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 144, 'p': 15, 'y': 10, 't': 43, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 43
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 44
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 144, 'p': 15, 'y': 10, 't': 44, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 144, 'p': 15, 'y': 10, 't': 44, 'h': 20, 'o': 26, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 26
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 27
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ' '
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ' '
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 144, 'p': 15, 'y': 10, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 144, 'p': 15, 'y': 10, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch ' '
trace_histo.py:19(1)                 # binary_subscript arr[ ' ' ]= 144
trace_histo.py:19(1)                 # store_subscript arr[ ' ' ]= 145
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 10, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 23, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 10, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 23
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 24
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'y'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'y'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 24, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 10, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 24, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 10, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'y'
trace_histo.py:19(1)                 # binary_subscript arr[ 'y' ]= 10
trace_histo.py:19(1)                 # store_subscript arr[ 'y' ]= 11
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 24, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 24, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 24
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 25
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '.'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '.'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 25, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 25, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 5, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch '.'
trace_histo.py:19(1)                 # binary_subscript arr[ '.' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ '.' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 25, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 25, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 25
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 26
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 44, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 44
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 45
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'd'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'd'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 45, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 45, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 5, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'd'
trace_histo.py:19(1)                 # binary_subscript arr[ 'd' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'd' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 45, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 45, 'h': 20, 'o': 27, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 27
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 28
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 45, 'h': 20, 'o': 28, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 12, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 45, 'h': 20, 'o': 28, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 45, 'h': 20, 'o': 28, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 45, 'h': 20, 'o': 28, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 45
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 46
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 46, 'h': 20, 'o': 28, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 46, 'h': 20, 'o': 28, '3': 2, '\n': 23, 'm': 11, 'a': 13, 'c': 18, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 23
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 24
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 46, 'h': 20, 'o': 28, '3': 2, '\n': 24, 'm': 11, 'a': 13, 'c': 18, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 46, 'h': 20, 'o': 28, '3': 2, '\n': 24, 'm': 11, 'a': 13, 'c': 18, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 24
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 25
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'c'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'c'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 46, 'h': 20, 'o': 28, '3': 2, '\n': 25, 'm': 11, 'a': 13, 'c': 18, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 46, 'h': 20, 'o': 28, '3': 2, '\n': 25, 'm': 11, 'a': 13, 'c': 18, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'c'
trace_histo.py:19(1)                 # binary_subscript arr[ 'c' ]= 18
trace_histo.py:19(1)                 # store_subscript arr[ 'c' ]= 19
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 46, 'h': 20, 'o': 28, '3': 2, '\n': 25, 'm': 11, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 46, 'h': 20, 'o': 28, '3': 2, '\n': 25, 'm': 11, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 28
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 29
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 46, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 11, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 46, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 11, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'm'
trace_histo.py:19(1)                 # binary_subscript arr[ 'm' ]= 11
trace_histo.py:19(1)                 # store_subscript arr[ 'm' ]= 12
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'p'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'p'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 46, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 15, 'y': 11, 't': 46, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'p'
trace_histo.py:19(1)                 # binary_subscript arr[ 'p' ]= 15
trace_histo.py:19(1)                 # store_subscript arr[ 'p' ]= 16
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'u'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'u'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 46, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 13, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 46, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'u'
trace_histo.py:19(1)                 # binary_subscript arr[ 'u' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ 'u' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 46, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 46, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 46
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 47
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 47, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 33, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 47, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 33
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 34
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '_'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '_'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 47, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 47, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 5, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch '_'
trace_histo.py:19(1)                 # binary_subscript arr[ '_' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ '_' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'h'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'h'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 47, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 47, 'h': 20, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'h'
trace_histo.py:19(1)                 # binary_subscript arr[ 'h' ]= 20
trace_histo.py:19(1)                 # store_subscript arr[ 'h' ]= 21
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 47, 'h': 21, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 26, 'r': 30, 'b': 2, 'i': 25, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 47, 'h': 21, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 25
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 26
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 's'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 's'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 26, 'r': 30, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 47, 'h': 21, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 26, 'r': 30, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 47, 'h': 21, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 's'
trace_histo.py:19(1)                 # binary_subscript arr[ 's' ]= 26
trace_histo.py:19(1)                 # store_subscript arr[ 's' ]= 27
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 't'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 't'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 30, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 47, 'h': 21, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 30, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 47, 'h': 21, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 't'
trace_histo.py:19(1)                 # binary_subscript arr[ 't' ]= 47
trace_histo.py:19(1)                 # store_subscript arr[ 't' ]= 48
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'o'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'o'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 30, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 30, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 29, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'o'
trace_histo.py:19(1)                 # binary_subscript arr[ 'o' ]= 29
trace_histo.py:19(1)                 # store_subscript arr[ 'o' ]= 30
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 30, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 30, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 30
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 31
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'g'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'g'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 31, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 31, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 3, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'g'
trace_histo.py:19(1)                 # binary_subscript arr[ 'g' ]= 3
trace_histo.py:19(1)                 # store_subscript arr[ 'g' ]= 4
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'r'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'r'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 31, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 4, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 31, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 4, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'r'
trace_histo.py:19(1)                 # binary_subscript arr[ 'r' ]= 31
trace_histo.py:19(1)                 # store_subscript arr[ 'r' ]= 32
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'a'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'a'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 4, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 12, 'a': 13, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 4, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'a'
trace_histo.py:19(1)                 # binary_subscript arr[ 'a' ]= 13
trace_histo.py:19(1)                 # store_subscript arr[ 'a' ]= 14
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'm'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'm'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 12, 'a': 14, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 4, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 12, 'a': 14, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 4, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'm'
trace_histo.py:19(1)                 # binary_subscript arr[ 'm' ]= 12
trace_histo.py:19(1)                 # store_subscript arr[ 'm' ]= 13
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '('
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '('
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 4, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 4, '(': 7, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch '('
trace_histo.py:19(1)                 # binary_subscript arr[ '(' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ '(' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '_'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '_'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 4, '(': 8, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 9, '_': 6, 'g': 4, '(': 8, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch '_'
trace_histo.py:19(1)                 # binary_subscript arr[ '_' ]= 6
trace_histo.py:19(1)                 # store_subscript arr[ '_' ]= 7
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '_'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '_'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 9, '_': 7, 'g': 4, '(': 8, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 9, '_': 7, 'g': 4, '(': 8, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch '_'
trace_histo.py:19(1)                 # binary_subscript arr[ '_' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ '_' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'f'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'f'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 9, '_': 8, 'g': 4, '(': 8, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 9, '_': 8, 'g': 4, '(': 8, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'f'
trace_histo.py:19(1)                 # binary_subscript arr[ 'f' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ 'f' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'i'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'i'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 8, 'g': 4, '(': 8, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 26, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 8, 'g': 4, '(': 8, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'i'
trace_histo.py:19(1)                 # binary_subscript arr[ 'i' ]= 26
trace_histo.py:19(1)                 # store_subscript arr[ 'i' ]= 27
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'l'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'l'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 8, 'g': 4, '(': 8, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 8, 'g': 4, '(': 8, 'l': 5, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'l'
trace_histo.py:19(1)                 # binary_subscript arr[ 'l' ]= 5
trace_histo.py:19(1)                 # store_subscript arr[ 'l' ]= 6
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch 'e'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch 'e'
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 8, 'g': 4, '(': 8, 'l': 6, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 34, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 8, 'g': 4, '(': 8, 'l': 6, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch 'e'
trace_histo.py:19(1)                 # binary_subscript arr[ 'e' ]= 34
trace_histo.py:19(1)                 # store_subscript arr[ 'e' ]= 35
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '_'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '_'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 8, 'g': 4, '(': 8, 'l': 6, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 8, 'g': 4, '(': 8, 'l': 6, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch '_'
trace_histo.py:19(1)                 # binary_subscript arr[ '_' ]= 8
trace_histo.py:19(1)                 # store_subscript arr[ '_' ]= 9
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '_'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '_'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 9, 'g': 4, '(': 8, 'l': 6, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 9, 'g': 4, '(': 8, 'l': 6, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch '_'
trace_histo.py:19(1)                 # binary_subscript arr[ '_' ]= 9
trace_histo.py:19(1)                 # store_subscript arr[ '_' ]= 10
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch ')'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch ')'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 7, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch ')'
trace_histo.py:19(1)                 # binary_subscript arr[ ')' ]= 7
trace_histo.py:19(1)                 # store_subscript arr[ ')' ]= 8
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 25, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 25
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 26
trace_histo.py:15(1)         for ch in text:
trace_histo.py:16(1)         # store ch '\n'
trace_histo.py:16(1)             if not ch in histo:
trace_histo.py:16(1)             # load ch '\n'
trace_histo.py:16(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 26, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 histo[ch] += 1
trace_histo.py:19(1)                 # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 26, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:19(1)                 # load ch '\n'
trace_histo.py:19(1)                 # binary_subscript arr[ '\n' ]= 26
trace_histo.py:19(1)                 # store_subscript arr[ '\n' ]= 27
trace_histo.py:15(1)         for ch in text:
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:21(1)         # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)         # store ch '#'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '#'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '#'
trace_histo.py:22(1)             # binary_subscript arr[ '#' ]= 3
char: '#' frequency: 3
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '!'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '!'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '!'
trace_histo.py:22(1)             # binary_subscript arr[ '!' ]= 2
char: '!' frequency: 2
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '/'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '/'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '/'
trace_histo.py:22(1)             # binary_subscript arr[ '/' ]= 6
char: '/' frequency: 6
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'u'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'u'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'u'
trace_histo.py:22(1)             # binary_subscript arr[ 'u' ]= 14
char: 'u' frequency: 14
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 's'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 's'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 's'
trace_histo.py:22(1)             # binary_subscript arr[ 's' ]= 27
char: 's' frequency: 27
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'r'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'r'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'r'
trace_histo.py:22(1)             # binary_subscript arr[ 'r' ]= 32
char: 'r' frequency: 32
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'b'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'b'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'b'
trace_histo.py:22(1)             # binary_subscript arr[ 'b' ]= 2
char: 'b' frequency: 2
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'i'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'i'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'i'
trace_histo.py:22(1)             # binary_subscript arr[ 'i' ]= 27
char: 'i' frequency: 27
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'n'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'n'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'n'
trace_histo.py:22(1)             # binary_subscript arr[ 'n' ]= 15
char: 'n' frequency: 15
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'e'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'e'
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'e'
trace_histo.py:22(1)             # binary_subscript arr[ 'e' ]= 35
char: 'e' frequency: 35
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'v'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'v'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'v'
trace_histo.py:22(1)             # binary_subscript arr[ 'v' ]= 2
char: 'v' frequency: 2
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch ' '
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch ' '
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch ' '
trace_histo.py:22(1)             # binary_subscript arr[ ' ' ]= 145
char: ' ' frequency: 145
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'p'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'p'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'p'
trace_histo.py:22(1)             # binary_subscript arr[ 'p' ]= 16
char: 'p' frequency: 16
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'y'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'y'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'y'
trace_histo.py:22(1)             # binary_subscript arr[ 'y' ]= 11
char: 'y' frequency: 11
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 't'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 't'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 't'
trace_histo.py:22(1)             # binary_subscript arr[ 't' ]= 48
char: 't' frequency: 48
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'h'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'h'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'h'
trace_histo.py:22(1)             # binary_subscript arr[ 'h' ]= 21
char: 'h' frequency: 21
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'o'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'o'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'o'
trace_histo.py:22(1)             # binary_subscript arr[ 'o' ]= 30
char: 'o' frequency: 30
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '3'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '3'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '3'
trace_histo.py:22(1)             # binary_subscript arr[ '3' ]= 2
char: '3' frequency: 2
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '\n'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '\n'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '\n'
trace_histo.py:22(1)             # binary_subscript arr[ '\n' ]= 27
char: '\n' frequency: 27
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'm'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'm'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'm'
trace_histo.py:22(1)             # binary_subscript arr[ 'm' ]= 13
char: 'm' frequency: 13
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'a'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'a'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'a'
trace_histo.py:22(1)             # binary_subscript arr[ 'a' ]= 14
char: 'a' frequency: 14
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'c'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'c'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'c'
trace_histo.py:22(1)             # binary_subscript arr[ 'c' ]= 19
char: 'c' frequency: 19
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'd'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'd'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'd'
trace_histo.py:22(1)             # binary_subscript arr[ 'd' ]= 6
char: 'd' frequency: 6
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'f'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'f'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'f'
trace_histo.py:22(1)             # binary_subscript arr[ 'f' ]= 10
char: 'f' frequency: 10
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '_'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '_'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '_'
trace_histo.py:22(1)             # binary_subscript arr[ '_' ]= 10
char: '_' frequency: 10
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'g'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'g'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'g'
trace_histo.py:22(1)             # binary_subscript arr[ 'g' ]= 4
char: 'g' frequency: 4
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '('
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '('
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '('
trace_histo.py:22(1)             # binary_subscript arr[ '(' ]= 8
char: '(' frequency: 8
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'l'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'l'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'l'
trace_histo.py:22(1)             # binary_subscript arr[ 'l' ]= 6
char: 'l' frequency: 6
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch ')'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch ')'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch ')'
trace_histo.py:22(1)             # binary_subscript arr[ ')' ]= 8
char: ')' frequency: 8
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch ':'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch ':'
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
load_global: can't find  histo in any scope
load_global: can't find  ch in any scope
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch ':'
trace_histo.py:22(1)             # binary_subscript arr[ ':' ]= 8
char: ':' frequency: 8
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'w'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'w'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'w'
trace_histo.py:22(1)             # binary_subscript arr[ 'w' ]= 1
char: 'w' frequency: 1
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch ','
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch ','
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch ','
trace_histo.py:22(1)             # binary_subscript arr[ ',' ]= 5
char: ',' frequency: 5
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch "'"
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch "'"
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch "'"
trace_histo.py:22(1)             # binary_subscript arr[ "'" ]= 2
char: "'" frequency: 2
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'x'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'x'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'x'
trace_histo.py:22(1)             # binary_subscript arr[ 'x' ]= 2
char: 'x' frequency: 2
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '='
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '='
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '='
trace_histo.py:22(1)             # binary_subscript arr[ '=' ]= 7
char: '=' frequency: 7
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '.'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '.'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '.'
trace_histo.py:22(1)             # binary_subscript arr[ '.' ]= 6
char: '.' frequency: 6
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '{'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '{'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '{'
trace_histo.py:22(1)             # binary_subscript arr[ '{' ]= 1
char: '{' frequency: 1
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '}'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '}'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '}'
trace_histo.py:22(1)             # binary_subscript arr[ '}' ]= 1
char: '}' frequency: 1
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '['
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '['
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '['
trace_histo.py:22(1)             # binary_subscript arr[ '[' ]= 3
char: '[' frequency: 3
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch ']'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch ']'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch ']'
trace_histo.py:22(1)             # binary_subscript arr[ ']' ]= 3
char: ']' frequency: 3
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '1'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '1'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '1'
trace_histo.py:22(1)             # binary_subscript arr[ '1' ]= 2
char: '1' frequency: 2
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '+'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '+'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '+'
trace_histo.py:22(1)             # binary_subscript arr[ '+' ]= 1
char: '+' frequency: 1
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'k'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'k'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'k'
trace_histo.py:22(1)             # binary_subscript arr[ 'k' ]= 1
char: 'k' frequency: 1
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '"'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '"'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '"'
trace_histo.py:22(1)             # binary_subscript arr[ '"' ]= 4
char: '"' frequency: 4
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'q'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'q'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'q'
trace_histo.py:22(1)             # binary_subscript arr[ 'q' ]= 1
char: 'q' frequency: 1
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'T'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'T'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'T'
trace_histo.py:22(1)             # binary_subscript arr[ 'T' ]= 1
char: 'T' frequency: 1
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch 'M'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch 'M'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch 'M'
trace_histo.py:22(1)             # binary_subscript arr[ 'M' ]= 1
char: 'M' frequency: 1
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:22(1)         # store ch '-'
trace_histo.py:22(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:22(1)             # load ch '-'
trace_histo.py:22(1)             # load histo {'#': 3, '!': 2, '/': 6, 'u': 14, 's': 27, 'r': 32, 'b': 2, 'i': 27, 'n': 15, 'e': 35, 'v': 2, ' ': 145, 'p': 16, 'y': 11, 't': 48, 'h': 21, 'o': 30, '3': 2, '\n': 27, 'm': 13, 'a': 14, 'c': 19, 'd': 6, 'f': 10, '_': 10, 'g': 4, '(': 8, 'l': 6, ')': 8, ':': 8, 'w': 1, ',': 5, "'": 2, 'x': 2, '=': 7, '.': 6, '{': 1, '}': 1, '[': 3, ']': 3, '1': 2, '+': 1, 'k': 1, '"': 4, 'q': 1, 'T': 1, 'M': 1, '-': 1}
trace_histo.py:22(1)             # load ch '-'
trace_histo.py:22(1)             # binary_subscript arr[ '-' ]= 1
char: '-' frequency: 1
trace_histo.py:21(1)         for ch in histo.keys():
trace_histo.py:21(1) return=None
</pre>


