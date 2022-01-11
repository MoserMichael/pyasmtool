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
+ factorial 5
+ local num=5
+ fact=1
+ (( i=1 ))
+ (( i&lt;=num ))
+ fact=1
+ (( i++ ))
+ (( i&lt;=num ))
+ fact=2
+ (( i++ ))
+ (( i&lt;=num ))
+ fact=6
+ (( i++ ))
+ (( i&lt;=num ))
+ fact=24
+ (( i++ ))
+ (( i&lt;=num ))
+ fact=120
+ (( i++ ))
+ (( i&lt;=num ))
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
--- modulename: fac, funcname: &lt;module&gt;
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
trace_fac_rec.py:9(1)     # load_global fac &lt;prettytrace.TraceMe object at 0x7feaee908fd0&gt; (type: class prettytrace.TraceMe)
trace_fac_rec.py:9(1)     # load arg_n 7
trace_fac_rec.py:6(2) def fac(arg_n):
trace_fac_rec.py:6(2)     # arg_n=6
trace_fac_rec.py:7(2)     if arg_n == 1:
trace_fac_rec.py:7(2)     # load arg_n 6
trace_fac_rec.py:9(2)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(2)     # load arg_n 6
trace_fac_rec.py:9(2)     # load_global fac &lt;prettytrace.TraceMe object at 0x7feaee908fd0&gt; (type: class prettytrace.TraceMe)
trace_fac_rec.py:9(2)     # load arg_n 6
trace_fac_rec.py:6(3) def fac(arg_n):
trace_fac_rec.py:6(3)     # arg_n=5
trace_fac_rec.py:7(3)     if arg_n == 1:
trace_fac_rec.py:7(3)     # load arg_n 5
trace_fac_rec.py:9(3)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(3)     # load arg_n 5
trace_fac_rec.py:9(3)     # load_global fac &lt;prettytrace.TraceMe object at 0x7feaee908fd0&gt; (type: class prettytrace.TraceMe)
trace_fac_rec.py:9(3)     # load arg_n 5
trace_fac_rec.py:6(4) def fac(arg_n):
trace_fac_rec.py:6(4)     # arg_n=4
trace_fac_rec.py:7(4)     if arg_n == 1:
trace_fac_rec.py:7(4)     # load arg_n 4
trace_fac_rec.py:9(4)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(4)     # load arg_n 4
trace_fac_rec.py:9(4)     # load_global fac &lt;prettytrace.TraceMe object at 0x7feaee908fd0&gt; (type: class prettytrace.TraceMe)
trace_fac_rec.py:9(4)     # load arg_n 4
trace_fac_rec.py:6(5) def fac(arg_n):
trace_fac_rec.py:6(5)     # arg_n=3
trace_fac_rec.py:7(5)     if arg_n == 1:
trace_fac_rec.py:7(5)     # load arg_n 3
trace_fac_rec.py:9(5)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(5)     # load arg_n 3
trace_fac_rec.py:9(5)     # load_global fac &lt;prettytrace.TraceMe object at 0x7feaee908fd0&gt; (type: class prettytrace.TraceMe)
trace_fac_rec.py:9(5)     # load arg_n 3
trace_fac_rec.py:6(6) def fac(arg_n):
trace_fac_rec.py:6(6)     # arg_n=2
trace_fac_rec.py:7(6)     if arg_n == 1:
trace_fac_rec.py:7(6)     # load arg_n 2
trace_fac_rec.py:9(6)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(6)     # load arg_n 2
trace_fac_rec.py:9(6)     # load_global fac &lt;prettytrace.TraceMe object at 0x7feaee908fd0&gt; (type: class prettytrace.TraceMe)
trace_fac_rec.py:9(6)     # load arg_n 2
trace_fac_rec.py:6(7) def fac(arg_n):
trace_fac_rec.py:6(7)     # arg_n=1
trace_fac_rec.py:7(7)     if arg_n == 1:
trace_fac_rec.py:7(7)     # load arg_n 1
trace_fac_rec.py:8(7)         return arg_n
trace_fac_rec.py:8(7)         # load arg_n 1
trace_fac_rec.py:8(7)         return=1
trace_fac_rec.py:9(6)         return=2
trace_fac_rec.py:9(5)         return=6
trace_fac_rec.py:9(4)         return=24
trace_fac_rec.py:9(3)         return=120
trace_fac_rec.py:9(2)         return=720
trace_fac_rec.py:9(1)         return=5040
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
trace_fac_rec_indent.py:9(1).     # load_global fac &lt;prettytrace.TraceMe object at 0x7fe493346370&gt; (type: class prettytrace.TraceMe)
trace_fac_rec_indent.py:9(1).     # load arg_n 7
trace_fac_rec_indent.py:6(2).. def fac(arg_n):
trace_fac_rec_indent.py:6(2)..     # arg_n=6
trace_fac_rec_indent.py:7(2)..     if arg_n == 1:
trace_fac_rec_indent.py:7(2)..     # load arg_n 6
trace_fac_rec_indent.py:9(2)..     return arg_n * fac(arg_n - 1)
trace_fac_rec_indent.py:9(2)..     # load arg_n 6
trace_fac_rec_indent.py:9(2)..     # load_global fac &lt;prettytrace.TraceMe object at 0x7fe493346370&gt; (type: class prettytrace.TraceMe)
trace_fac_rec_indent.py:9(2)..     # load arg_n 6
trace_fac_rec_indent.py:6(3)... def fac(arg_n):
trace_fac_rec_indent.py:6(3)...     # arg_n=5
trace_fac_rec_indent.py:7(3)...     if arg_n == 1:
trace_fac_rec_indent.py:7(3)...     # load arg_n 5
trace_fac_rec_indent.py:9(3)...     return arg_n * fac(arg_n - 1)
trace_fac_rec_indent.py:9(3)...     # load arg_n 5
trace_fac_rec_indent.py:9(3)...     # load_global fac &lt;prettytrace.TraceMe object at 0x7fe493346370&gt; (type: class prettytrace.TraceMe)
trace_fac_rec_indent.py:9(3)...     # load arg_n 5
trace_fac_rec_indent.py:6(4).... def fac(arg_n):
trace_fac_rec_indent.py:6(4)....     # arg_n=4
trace_fac_rec_indent.py:7(4)....     if arg_n == 1:
trace_fac_rec_indent.py:7(4)....     # load arg_n 4
trace_fac_rec_indent.py:9(4)....     return arg_n * fac(arg_n - 1)
trace_fac_rec_indent.py:9(4)....     # load arg_n 4
trace_fac_rec_indent.py:9(4)....     # load_global fac &lt;prettytrace.TraceMe object at 0x7fe493346370&gt; (type: class prettytrace.TraceMe)
trace_fac_rec_indent.py:9(4)....     # load arg_n 4
trace_fac_rec_indent.py:6(5)..... def fac(arg_n):
trace_fac_rec_indent.py:6(5).....     # arg_n=3
trace_fac_rec_indent.py:7(5).....     if arg_n == 1:
trace_fac_rec_indent.py:7(5).....     # load arg_n 3
trace_fac_rec_indent.py:9(5).....     return arg_n * fac(arg_n - 1)
trace_fac_rec_indent.py:9(5).....     # load arg_n 3
trace_fac_rec_indent.py:9(5).....     # load_global fac &lt;prettytrace.TraceMe object at 0x7fe493346370&gt; (type: class prettytrace.TraceMe)
trace_fac_rec_indent.py:9(5).....     # load arg_n 3
trace_fac_rec_indent.py:6(6)...... def fac(arg_n):
trace_fac_rec_indent.py:6(6)......     # arg_n=2
trace_fac_rec_indent.py:7(6)......     if arg_n == 1:
trace_fac_rec_indent.py:7(6)......     # load arg_n 2
trace_fac_rec_indent.py:9(6)......     return arg_n * fac(arg_n - 1)
trace_fac_rec_indent.py:9(6)......     # load arg_n 2
trace_fac_rec_indent.py:9(6)......     # load_global fac &lt;prettytrace.TraceMe object at 0x7fe493346370&gt; (type: class prettytrace.TraceMe)
trace_fac_rec_indent.py:9(6)......     # load arg_n 2
trace_fac_rec_indent.py:6(7)....... def fac(arg_n):
trace_fac_rec_indent.py:6(7).......     # arg_n=1
trace_fac_rec_indent.py:7(7).......     if arg_n == 1:
trace_fac_rec_indent.py:7(7).......     # load arg_n 1
trace_fac_rec_indent.py:8(7).......         return arg_n
trace_fac_rec_indent.py:8(7).......         # load arg_n 1
trace_fac_rec_indent.py:8(7).......         return=1
trace_fac_rec_indent.py:9(6)......         return=2
trace_fac_rec_indent.py:9(5).....         return=6
trace_fac_rec_indent.py:9(4)....         return=24
trace_fac_rec_indent.py:9(3)...         return=120
trace_fac_rec_indent.py:9(2)..         return=720
trace_fac_rec_indent.py:9(1).         return=5040
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
trace_fac_iter.py:5(1) def fac_iter(arg_n: int) -&gt; int:
trace_fac_iter.py:5(1) # arg_n=7
trace_fac_iter.py:6(1)     res = 1
trace_fac_iter.py:7(1)     # store res 1
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n+1):
trace_fac_iter.py:7(1)     # load_global range &lt;class 'range'&gt; (type: class type)
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
trace_fac_iter.py:9(1)     return=5040
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
trace_lookup.py:8(1)     # load list_on_stack[0] 1
trace_lookup.py:9(1)     # store tmp 1
trace_lookup.py:9(1)     arg_list[0] = arg_list[1]
trace_lookup.py:9(1)     # load arg_list [1, 2]
trace_lookup.py:9(1)     # load list_on_stack[1] 2
trace_lookup.py:9(1)     # load arg_list [1, 2]
trace_lookup.py:9(1)     # store list-on-stack[0]=2
trace_lookup.py:10(1)     arg_list[1] = tmp
trace_lookup.py:10(1)     # load tmp 1
trace_lookup.py:10(1)     # load arg_list [2, 2]
trace_lookup.py:10(1)     # store list-on-stack[1]=1
trace_lookup.py:10(1)     return=None
trace_lookup.py:12(1) def swap_dict(arg_dict):
trace_lookup.py:12(1) # arg_dict={'first': 'a', 'second': 'b'}
trace_lookup.py:13(1)     tmp = arg_dict['first']
trace_lookup.py:13(1)     # load arg_dict {'first': 'a', 'second': 'b'}
trace_lookup.py:13(1)     # load dict_on_stack['first'] 'a'
trace_lookup.py:14(1)     # store tmp 'a'
trace_lookup.py:14(1)     arg_dict['first'] = arg_dict['second']
trace_lookup.py:14(1)     # load arg_dict {'first': 'a', 'second': 'b'}
trace_lookup.py:14(1)     # load dict_on_stack['second'] 'b'
trace_lookup.py:14(1)     # load arg_dict {'first': 'a', 'second': 'b'}
trace_lookup.py:14(1)     # store dict-on-stack['first']='b'
trace_lookup.py:15(1)     arg_dict['second'] = tmp
trace_lookup.py:15(1)     # load tmp 'a'
trace_lookup.py:15(1)     # load arg_dict {'first': 'b', 'second': 'b'}
trace_lookup.py:15(1)     # store dict-on-stack['second']='a'
trace_lookup.py:15(1)     return=None
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
trace_obj.py:7(1) # self=&lt;__main__.Complex object at 0x7ffa45566bb0&gt;
trace_obj.py:7(1) # re=2
trace_obj.py:7(1) # im=3
trace_obj.py:8(1)         self.real = re
trace_obj.py:8(1)         # load re 2
trace_obj.py:8(1)         # load self &lt;__main__.Complex object at 0x7ffa45566bb0&gt;
trace_obj.py:9(1)         # store_attr class int.real=2
trace_obj.py:9(1)         self.imag = im
trace_obj.py:9(1)         # load im 3
trace_obj.py:9(1)         # load self &lt;__main__.Complex object at 0x7ffa45566bb0&gt;
trace_obj.py:9(1)         # store_attr class int.imag=2
trace_obj.py:9(1)         return=None
trace_obj.py:31(1)     def __str__(self):
trace_obj.py:31(1) # self=&lt;__main__.Complex object at 0x7ffa45566bb0&gt;
trace_obj.py:32(1)         return f"real: {self.real} imaginary: {self.imag}"
trace_obj.py:32(1)         # load self &lt;__main__.Complex object at 0x7ffa45566bb0&gt;
trace_obj.py:32(1)         # load_attr class __main__.Complex.real=2
trace_obj.py:32(1)         # load self &lt;__main__.Complex object at 0x7ffa45566bb0&gt;
trace_obj.py:32(1)         # load_attr class __main__.Complex.imag=3
trace_obj.py:32(1)         return='real: 2 imaginary: 3'
trace_obj.py:42(1)     def __init__(self, first_name, last_name, title):
trace_obj.py:42(1) # self=&lt;__main__.PersonWithTitle object at 0x7ffa45566be0&gt;
trace_obj.py:42(1) # first_name='Pooh'
trace_obj.py:42(1) # last_name='Bear'
trace_obj.py:42(1) # title='Mr'
trace_obj.py:43(1)         super().__init__(first_name, last_name)
trace_obj.py:43(1)         # load_global super &lt;class 'super'&gt; (type: class type)
trace_obj.py:43(1)         # load first_name 'Pooh'
trace_obj.py:43(1)         # load last_name 'Bear'
trace_obj.py:35(2)     def  __init__(self, first_name, last_name):
trace_obj.py:35(2)         # self=&lt;__main__.PersonWithTitle object at 0x7ffa45566be0&gt;
trace_obj.py:35(2)         # first_name='Pooh'
trace_obj.py:35(2)         # last_name='Bear'
trace_obj.py:36(2)         self.first_name  = first_name
trace_obj.py:36(2)         # load first_name 'Pooh'
trace_obj.py:36(2)         # load self &lt;__main__.PersonWithTitle object at 0x7ffa45566be0&gt;
trace_obj.py:37(2)         # store_attr class str.first_name='Pooh'
trace_obj.py:37(2)         self.last_name = last_name
trace_obj.py:37(2)         # load last_name 'Bear'
trace_obj.py:37(2)         # load self &lt;__main__.PersonWithTitle object at 0x7ffa45566be0&gt;
trace_obj.py:37(2)         # store_attr class str.last_name='Pooh'
trace_obj.py:37(2)         return=None
trace_obj.py:44(1)         self.title = title
trace_obj.py:44(1)         # load title 'Mr'
trace_obj.py:44(1)         # load self &lt;__main__.PersonWithTitle object at 0x7ffa45566be0&gt;
trace_obj.py:44(1)         # store_attr class cell.title='Mr'
trace_obj.py:44(1)         return=None
trace_obj.py:48(1)     def __str__(self):
trace_obj.py:48(1)         #print(f"__str__ id: {id(self)} self.__dict__ {self.__dict__}")
trace_obj.py:48(1) # self=&lt;__main__.PersonWithTitle object at 0x7ffa45566be0&gt;
trace_obj.py:50(1)         return f"Title: {self.title} {super().__str__()}"
trace_obj.py:50(1)         # load self &lt;__main__.PersonWithTitle object at 0x7ffa45566be0&gt;
trace_obj.py:50(1)         # load_attr class __main__.PersonWithTitle.title='Mr'
trace_obj.py:50(1)         # load_global super &lt;class 'super'&gt; (type: class type)
trace_obj.py:38(2)     def __str__(self):
trace_obj.py:38(2)         # self=&lt;__main__.PersonWithTitle object at 0x7ffa45566be0&gt;
trace_obj.py:39(2)         return f"first_name: {self.first_name} last_name: {self.last_name}"
trace_obj.py:39(2)         # load self &lt;__main__.PersonWithTitle object at 0x7ffa45566be0&gt;
trace_obj.py:39(2)         # load_attr class __main__.PersonWithTitle.first_name='Pooh'
trace_obj.py:39(2)         # load self &lt;__main__.PersonWithTitle object at 0x7ffa45566be0&gt;
trace_obj.py:39(2)         # load_attr class __main__.PersonWithTitle.last_name='Bear'
trace_obj.py:39(2)         return='first_name: Pooh last_name: Bear'
trace_obj.py:50(1)         return='Title: Mr first_name: Pooh last_name: Bear'
real: 2 imaginary: 3
Title: Mr first_name: Pooh last_name: Bear
eof
</pre>

Here is an example trace of a program, that counts the number of occurrences of each letter in a given text file.


__Source:__

```python
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


