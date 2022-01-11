* [Execution traces in Python](#s1)
  * [Execution traces in the bash shell](#s1-1)
  * [Execution trace in Python](#s1-2)
  * [Let's make a better tracer for python!](#s1-3)
      * [The python tracer in action](#s1-3-1)


# <a id='s1' />Execution traces in Python

This section will examine, how to use our understanding of the Python bytecode, in order to write a better execution trace facility for Python.

The tracer will be specific to the [cpython](https://github.com/python/cpython/) environment, I doubt that it will work on all python environments, reasons are explained below.


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
120
</pre>

For examle the start of the invocation looks as follow

```
+ factorial 5
+ '[' 5 -le 1 ']'
```
The bash shell is an interpreter, it translates the source code into an in memory tree representation that is called the [abstract syntax tree](https://en.wikipedia.org/wiki/Abstract\_syntax\_tree)

The next step for the bash interpreter to evaluate the program, it does so by following the nodes of the abstract syntax tree in [Post order (LRN)](https://en.wikipedia.org/wiki/Tree\_traversal#Post-order,\_LRN), first the left and the right subtree are evaluated, in order to get all the arguments for operator of the current tree node, then the current node is evaluated.
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
--- modulename: fac, funcname: &lt;module&gt;
fac.py(1): def fac(arg_n):
fac.py(6): print(fac(6))
 --- modulename: fac, funcname: fac
fac.py(2):     if arg_n == 1:
fac.py(4):     return arg_n * fac(arg_n - 1)
 --- modulename: fac, funcname: fac
fac.py(2):     if arg_n == 1:
fac.py(4):     return arg_n * fac(arg_n - 1)
 --- modulename: fac, funcname: fac
fac.py(2):     if arg_n == 1:
fac.py(4):     return arg_n * fac(arg_n - 1)
 --- modulename: fac, funcname: fac
fac.py(2):     if arg_n == 1:
fac.py(4):     return arg_n * fac(arg_n - 1)
 --- modulename: fac, funcname: fac
fac.py(2):     if arg_n == 1:
fac.py(4):     return arg_n * fac(arg_n - 1)
 --- modulename: fac, funcname: fac
fac.py(2):     if arg_n == 1:
fac.py(3):         return arg_n
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

import pyasmtools


def fac(arg_n):
    if arg_n == 1:
        return arg_n
    return arg_n * fac(arg_n - 1)

fac = pyasmtools.TraceMe(fac)

print( "fac(7):", fac(7))

```

__Result:__
<pre>
fac(7): 5040
</pre>

It is also possible to specify an indentation prefix that depends on the level of call nesting, just like in bash


__Source:__

```python
#!/usr/bin/env python3

import pyasmtools


def fac(arg_n):
    if arg_n == 1:
        return arg_n
    return arg_n * fac(arg_n - 1)

fac = pyasmtools.TraceMe(fac, trace_indent=True)

print( "fac(7):", fac(7))

```

__Result:__
<pre>
fac(7): 5040
</pre>

Let's trace the execution of an iterative factorial function in python


__Source:__

```python
#!/usr/bin/env python3

import pyasmtools

def fac_iter(arg_n: int) -> int:
    res = 1
    for cur_n in range(1,arg_n+1):
        res *= cur_n
    return res

fac_iter = pyasmtools.TraceMe(fac_iter)

print( "fac_iter(7):", fac_iter(7))

```

__Result:__
<pre>
fac_iter(7): 5040
</pre>

So far the trace program did not need to access the evaluation stack of the python interpreter, the evalutation stack is currently not exposed by the interpreter to python code, as there is no field in the built-in frame object for it. I used a workaround, accessing the memory location referred to by the bytecode instruction before executing the [LOAD\_FAST](https://docs.python.org/3/library/dis.html#opcode-LOAD\_FAST) instruction, and accessing the modified location after running the [STORE\_FAST](https://docs.python.org/3/library/dis.html#opcode-STORE\_FAST) instruction, Hoever that trick is not feasible for the array and dictionary access instructions [STORE\_SUBSCR](https://docs.python.org/3.8/library/dis.html#opcode-STORE\_SUBSCR) and [BINARY\_SUBSCRIPT](https://docs.python.org/3.8/library/dis.html#opcode-LOAD\_SUBSCRIPT) bytecode instructions, here i would need to take a direct look at the evaluation stack.

It would however be possbible to do this trick, from python with the [ctypes module](https://docs.python.org/3/library/ctypes.html), without any native code at all! [see this discussion](https://stackoverflow.com/questions/44346433/in-c-python-accessing-the-bytecode-evaluation-stack), so back to the drawing board!

Given this trick, here is an example of tracing list and map access.


__Source:__

```python
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


```

__Result:__
<pre>
[2, 1]
{'first': 'b', 'second': 'a'}
</pre>

Here is an example of accessing python objects. You can trace every method call of a class, here you need to define the class with the TraceClass metaclass. (You can learn more about metaclasses in [this lesson](https://github.com/MoserMichael/python-obj-system/blob/master/python-obj-system.md)


__Source:__

```python
#!/usr/bin/env python3

import pyasmtools


class Complex(metaclass=pyasmtools.TraceClass):
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

class PersonWithTitle(Person, metaclass=pyasmtools.TraceClass):
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
real: 2 imaginary: 3
Title: Mr first_name: Pooh last_name: Bear
eof
</pre>

Here is an example trace of a program, that counts the number of occurrences of each letter in a given text file.


__Source:__

```python
#!/usr/bin/env python3

import pyasmtools
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

compute_historgram = pyasmtools.TraceMe(compute_historgram, out=sys.stdout) # out=sys.stdout - redirects trace output to sys.stdout

compute_historgram("./example_text.txt")


```

__Result:__
<pre>
trace_histo.py:6(1) def compute_historgram(file_name):
trace_histo.py:6(1) # file_name='./example_text.txt'
trace_histo.py:7(1)     with open(file_name,'r') as file:
trace_histo.py:7(1)     # load_global open &lt;built-in function open&gt; (type: class builtin_function_or_method)
trace_histo.py:7(1)     # load file_name './example_text.txt'
trace_histo.py:8(1)     # store file &lt;_io.TextIOWrapper name='./example_text.txt' mode='r' encoding='UTF-8'&gt;
trace_histo.py:8(1)         text = file.read()
trace_histo.py:8(1)         # load file &lt;_io.TextIOWrapper name='./example_text.txt' mode='r' encoding='UTF-8'&gt;
trace_histo.py:10(1)         # store text 'Attack at dawn!\n'
trace_histo.py:10(1)         histo = {}
trace_histo.py:11(1)         # store histo {}
trace_histo.py:11(1)         for ch in text:
trace_histo.py:11(1)         # load text 'Attack at dawn!\n'
trace_histo.py:12(1)         # store ch 'A'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch 'A'
trace_histo.py:12(1)             # load histo {}
trace_histo.py:13(1)                 histo[ch] = 1
trace_histo.py:13(1)                 # load histo {}
trace_histo.py:13(1)                 # load ch 'A'
trace_histo.py:13(1)                 # store dict-on-stack['A']=1
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch 't'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch 't'
trace_histo.py:12(1)             # load histo {'A': 1}
trace_histo.py:13(1)                 histo[ch] = 1
trace_histo.py:13(1)                 # load histo {'A': 1}
trace_histo.py:13(1)                 # load ch 't'
trace_histo.py:13(1)                 # store dict-on-stack['t']=1
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch 't'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch 't'
trace_histo.py:12(1)             # load histo {'A': 1, 't': 1}
trace_histo.py:15(1)                 histo[ch] += 1
trace_histo.py:15(1)                 # load histo {'A': 1, 't': 1}
trace_histo.py:15(1)                 # load ch 't'
trace_histo.py:15(1)                 # load dict_on_stack['t'] 1
trace_histo.py:15(1)                 # store dict-on-stack['t']=2
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch 'a'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch 'a'
trace_histo.py:12(1)             # load histo {'A': 1, 't': 2}
trace_histo.py:13(1)                 histo[ch] = 1
trace_histo.py:13(1)                 # load histo {'A': 1, 't': 2}
trace_histo.py:13(1)                 # load ch 'a'
trace_histo.py:13(1)                 # store dict-on-stack['a']=1
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch 'c'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch 'c'
trace_histo.py:12(1)             # load histo {'A': 1, 't': 2, 'a': 1}
trace_histo.py:13(1)                 histo[ch] = 1
trace_histo.py:13(1)                 # load histo {'A': 1, 't': 2, 'a': 1}
trace_histo.py:13(1)                 # load ch 'c'
trace_histo.py:13(1)                 # store dict-on-stack['c']=1
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch 'k'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch 'k'
trace_histo.py:12(1)             # load histo {'A': 1, 't': 2, 'a': 1, 'c': 1}
trace_histo.py:13(1)                 histo[ch] = 1
trace_histo.py:13(1)                 # load histo {'A': 1, 't': 2, 'a': 1, 'c': 1}
trace_histo.py:13(1)                 # load ch 'k'
trace_histo.py:13(1)                 # store dict-on-stack['k']=1
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch ' '
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch ' '
trace_histo.py:12(1)             # load histo {'A': 1, 't': 2, 'a': 1, 'c': 1, 'k': 1}
trace_histo.py:13(1)                 histo[ch] = 1
trace_histo.py:13(1)                 # load histo {'A': 1, 't': 2, 'a': 1, 'c': 1, 'k': 1}
trace_histo.py:13(1)                 # load ch ' '
trace_histo.py:13(1)                 # store dict-on-stack[' ']=1
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch 'a'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch 'a'
trace_histo.py:12(1)             # load histo {'A': 1, 't': 2, 'a': 1, 'c': 1, 'k': 1, ' ': 1}
trace_histo.py:15(1)                 histo[ch] += 1
trace_histo.py:15(1)                 # load histo {'A': 1, 't': 2, 'a': 1, 'c': 1, 'k': 1, ' ': 1}
trace_histo.py:15(1)                 # load ch 'a'
trace_histo.py:15(1)                 # load dict_on_stack['a'] 1
trace_histo.py:15(1)                 # store dict-on-stack['a']=2
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch 't'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch 't'
trace_histo.py:12(1)             # load histo {'A': 1, 't': 2, 'a': 2, 'c': 1, 'k': 1, ' ': 1}
trace_histo.py:15(1)                 histo[ch] += 1
trace_histo.py:15(1)                 # load histo {'A': 1, 't': 2, 'a': 2, 'c': 1, 'k': 1, ' ': 1}
trace_histo.py:15(1)                 # load ch 't'
trace_histo.py:15(1)                 # load dict_on_stack['t'] 2
trace_histo.py:15(1)                 # store dict-on-stack['t']=3
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch ' '
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch ' '
trace_histo.py:12(1)             # load histo {'A': 1, 't': 3, 'a': 2, 'c': 1, 'k': 1, ' ': 1}
trace_histo.py:15(1)                 histo[ch] += 1
trace_histo.py:15(1)                 # load histo {'A': 1, 't': 3, 'a': 2, 'c': 1, 'k': 1, ' ': 1}
trace_histo.py:15(1)                 # load ch ' '
trace_histo.py:15(1)                 # load dict_on_stack[' '] 1
trace_histo.py:15(1)                 # store dict-on-stack[' ']=2
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch 'd'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch 'd'
trace_histo.py:12(1)             # load histo {'A': 1, 't': 3, 'a': 2, 'c': 1, 'k': 1, ' ': 2}
trace_histo.py:13(1)                 histo[ch] = 1
trace_histo.py:13(1)                 # load histo {'A': 1, 't': 3, 'a': 2, 'c': 1, 'k': 1, ' ': 2}
trace_histo.py:13(1)                 # load ch 'd'
trace_histo.py:13(1)                 # store dict-on-stack['d']=1
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch 'a'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch 'a'
trace_histo.py:12(1)             # load histo {'A': 1, 't': 3, 'a': 2, 'c': 1, 'k': 1, ' ': 2, 'd': 1}
trace_histo.py:15(1)                 histo[ch] += 1
trace_histo.py:15(1)                 # load histo {'A': 1, 't': 3, 'a': 2, 'c': 1, 'k': 1, ' ': 2, 'd': 1}
trace_histo.py:15(1)                 # load ch 'a'
trace_histo.py:15(1)                 # load dict_on_stack['a'] 2
trace_histo.py:15(1)                 # store dict-on-stack['a']=3
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch 'w'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch 'w'
trace_histo.py:12(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1}
trace_histo.py:13(1)                 histo[ch] = 1
trace_histo.py:13(1)                 # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1}
trace_histo.py:13(1)                 # load ch 'w'
trace_histo.py:13(1)                 # store dict-on-stack['w']=1
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch 'n'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch 'n'
trace_histo.py:12(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1}
trace_histo.py:13(1)                 histo[ch] = 1
trace_histo.py:13(1)                 # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1}
trace_histo.py:13(1)                 # load ch 'n'
trace_histo.py:13(1)                 # store dict-on-stack['n']=1
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch '!'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch '!'
trace_histo.py:12(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1}
trace_histo.py:13(1)                 histo[ch] = 1
trace_histo.py:13(1)                 # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1}
trace_histo.py:13(1)                 # load ch '!'
trace_histo.py:13(1)                 # store dict-on-stack['!']=1
trace_histo.py:11(1)         for ch in text:
trace_histo.py:12(1)         # store ch '\n'
trace_histo.py:12(1)             if not ch in histo:
trace_histo.py:12(1)             # load ch '\n'
trace_histo.py:12(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1}
trace_histo.py:13(1)                 histo[ch] = 1
trace_histo.py:13(1)                 # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1}
trace_histo.py:13(1)                 # load ch '\n'
trace_histo.py:13(1)                 # store dict-on-stack['\n']=1
trace_histo.py:11(1)         for ch in text:
trace_histo.py:17(1)         for ch in histo.keys():
trace_histo.py:17(1)         # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1, '\n': 1}
trace_histo.py:18(1)         # store ch 'A'
trace_histo.py:18(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:18(1)             # load_global print &lt;built-in function print&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load_global repr &lt;built-in function repr&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load ch 'A'
trace_histo.py:18(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1, '\n': 1}
trace_histo.py:18(1)             # load ch 'A'
trace_histo.py:18(1)             # load dict_on_stack['A'] 1
char: 'A' frequency: 1
trace_histo.py:17(1)         for ch in histo.keys():
trace_histo.py:18(1)         # store ch 't'
trace_histo.py:18(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:18(1)             # load_global print &lt;built-in function print&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load_global repr &lt;built-in function repr&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load ch 't'
trace_histo.py:18(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1, '\n': 1}
trace_histo.py:18(1)             # load ch 't'
trace_histo.py:18(1)             # load dict_on_stack['t'] 3
char: 't' frequency: 3
trace_histo.py:17(1)         for ch in histo.keys():
trace_histo.py:18(1)         # store ch 'a'
trace_histo.py:18(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:18(1)             # load_global print &lt;built-in function print&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load_global repr &lt;built-in function repr&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load ch 'a'
trace_histo.py:18(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1, '\n': 1}
trace_histo.py:18(1)             # load ch 'a'
trace_histo.py:18(1)             # load dict_on_stack['a'] 3
char: 'a' frequency: 3
trace_histo.py:17(1)         for ch in histo.keys():
trace_histo.py:18(1)         # store ch 'c'
trace_histo.py:18(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:18(1)             # load_global print &lt;built-in function print&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load_global repr &lt;built-in function repr&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load ch 'c'
trace_histo.py:18(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1, '\n': 1}
trace_histo.py:18(1)             # load ch 'c'
trace_histo.py:18(1)             # load dict_on_stack['c'] 1
char: 'c' frequency: 1
trace_histo.py:17(1)         for ch in histo.keys():
trace_histo.py:18(1)         # store ch 'k'
trace_histo.py:18(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:18(1)             # load_global print &lt;built-in function print&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load_global repr &lt;built-in function repr&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load ch 'k'
trace_histo.py:18(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1, '\n': 1}
trace_histo.py:18(1)             # load ch 'k'
trace_histo.py:18(1)             # load dict_on_stack['k'] 1
char: 'k' frequency: 1
trace_histo.py:17(1)         for ch in histo.keys():
trace_histo.py:18(1)         # store ch ' '
trace_histo.py:18(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:18(1)             # load_global print &lt;built-in function print&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load_global repr &lt;built-in function repr&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load ch ' '
trace_histo.py:18(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1, '\n': 1}
trace_histo.py:18(1)             # load ch ' '
trace_histo.py:18(1)             # load dict_on_stack[' '] 2
char: ' ' frequency: 2
trace_histo.py:17(1)         for ch in histo.keys():
trace_histo.py:18(1)         # store ch 'd'
trace_histo.py:18(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:18(1)             # load_global print &lt;built-in function print&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load_global repr &lt;built-in function repr&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load ch 'd'
trace_histo.py:18(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1, '\n': 1}
trace_histo.py:18(1)             # load ch 'd'
trace_histo.py:18(1)             # load dict_on_stack['d'] 1
char: 'd' frequency: 1
trace_histo.py:17(1)         for ch in histo.keys():
trace_histo.py:18(1)         # store ch 'w'
trace_histo.py:18(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:18(1)             # load_global print &lt;built-in function print&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load_global repr &lt;built-in function repr&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load ch 'w'
trace_histo.py:18(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1, '\n': 1}
trace_histo.py:18(1)             # load ch 'w'
trace_histo.py:18(1)             # load dict_on_stack['w'] 1
char: 'w' frequency: 1
trace_histo.py:17(1)         for ch in histo.keys():
trace_histo.py:18(1)         # store ch 'n'
trace_histo.py:18(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:18(1)             # load_global print &lt;built-in function print&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load_global repr &lt;built-in function repr&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load ch 'n'
trace_histo.py:18(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1, '\n': 1}
trace_histo.py:18(1)             # load ch 'n'
trace_histo.py:18(1)             # load dict_on_stack['n'] 1
char: 'n' frequency: 1
trace_histo.py:17(1)         for ch in histo.keys():
trace_histo.py:18(1)         # store ch '!'
trace_histo.py:18(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:18(1)             # load_global print &lt;built-in function print&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load_global repr &lt;built-in function repr&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load ch '!'
trace_histo.py:18(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1, '\n': 1}
trace_histo.py:18(1)             # load ch '!'
trace_histo.py:18(1)             # load dict_on_stack['!'] 1
char: '!' frequency: 1
trace_histo.py:17(1)         for ch in histo.keys():
trace_histo.py:18(1)         # store ch '\n'
trace_histo.py:18(1)             print("char:", repr(ch), "frequency:", histo[ch])
trace_histo.py:18(1)             # load_global print &lt;built-in function print&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load_global repr &lt;built-in function repr&gt; (type: class builtin_function_or_method)
trace_histo.py:18(1)             # load ch '\n'
trace_histo.py:18(1)             # load histo {'A': 1, 't': 3, 'a': 3, 'c': 1, 'k': 1, ' ': 2, 'd': 1, 'w': 1, 'n': 1, '!': 1, '\n': 1}
trace_histo.py:18(1)             # load ch '\n'
trace_histo.py:18(1)             # load dict_on_stack['\n'] 1
char: '\n' frequency: 1
trace_histo.py:17(1)         for ch in histo.keys():
trace_histo.py:17(1)         return=None
</pre>


