* [Execution traces in Python](#s1)
  * [Execution traces in the bash shell](#s1-1)
  * [Execution trace in Python](#s1-2)
  * [Let's make a better tracer!](#s1-3)


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

The following example computes a factorial in an iterative way


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

The python standard library has the [trace](https://docs.python.org/3/library/trace.html) module, one of its features is to print out the source lines of a program, as the program is executed. Unfortunately it does not show the variable values and does not show the modifications performed on these variables

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


## <a id='s1-3' />Let's make a better tracer!

Let's attemt to make a better trace facility for python.
The [sys.settrace](https://docs.python.org/3/library/sys.html#sys.settrace) function installs a callback that is being called to trace the execution of every line; Now this function can install a special trace function, that will get called upon the exeuction of every opcode; here we could try and show all load and store instructions

Let's trace the execution of a recursive factorial function in python. Note that the tracer is defined as a decorator of the traced function.

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
adding LOAD_FAST 124
adding STORE_FAST 125
trace_fac_rec.py:6(1) def fac(arg_n):
trace_fac_rec.py:6(1) # arg_n=7
trace_fac_rec.py:7(1)     if arg_n == 1:
trace_fac_rec.py:7(1)     # load arg_n 7
trace_fac_rec.py:9(1)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(1)     # load arg_n 7
trace_fac_rec.py:9(1)     # load arg_n 7
trace_fac_rec.py:6(2) def fac(arg_n):
trace_fac_rec.py:6(2)     # arg_n=6
trace_fac_rec.py:7(2)     if arg_n == 1:
trace_fac_rec.py:7(2)     # load arg_n 6
trace_fac_rec.py:9(2)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(2)     # load arg_n 6
trace_fac_rec.py:9(2)     # load arg_n 6
trace_fac_rec.py:6(3) def fac(arg_n):
trace_fac_rec.py:6(3)     # arg_n=5
trace_fac_rec.py:7(3)     if arg_n == 1:
trace_fac_rec.py:7(3)     # load arg_n 5
trace_fac_rec.py:9(3)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(3)     # load arg_n 5
trace_fac_rec.py:9(3)     # load arg_n 5
trace_fac_rec.py:6(4) def fac(arg_n):
trace_fac_rec.py:6(4)     # arg_n=4
trace_fac_rec.py:7(4)     if arg_n == 1:
trace_fac_rec.py:7(4)     # load arg_n 4
trace_fac_rec.py:9(4)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(4)     # load arg_n 4
trace_fac_rec.py:9(4)     # load arg_n 4
trace_fac_rec.py:6(5) def fac(arg_n):
trace_fac_rec.py:6(5)     # arg_n=3
trace_fac_rec.py:7(5)     if arg_n == 1:
trace_fac_rec.py:7(5)     # load arg_n 3
trace_fac_rec.py:9(5)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(5)     # load arg_n 3
trace_fac_rec.py:9(5)     # load arg_n 3
trace_fac_rec.py:6(6) def fac(arg_n):
trace_fac_rec.py:6(6)     # arg_n=2
trace_fac_rec.py:7(6)     if arg_n == 1:
trace_fac_rec.py:7(6)     # load arg_n 2
trace_fac_rec.py:9(6)     return arg_n * fac(arg_n - 1)
trace_fac_rec.py:9(6)     # load arg_n 2
trace_fac_rec.py:9(6)     # load arg_n 2
trace_fac_rec.py:6(7) def fac(arg_n):
trace_fac_rec.py:6(7)     # arg_n=1
trace_fac_rec.py:7(7)     if arg_n == 1:
trace_fac_rec.py:7(7)     # load arg_n 1
trace_fac_rec.py:8(7)         return arg_n
trace_fac_rec.py:8(7)         # load arg_n 1
trace_fac_rec.py:8(7) return=1
prettytrace.py:9(6) return=2
prettytrace.py:9(5) return=6
prettytrace.py:9(4) return=24
prettytrace.py:9(3) return=120
prettytrace.py:9(2) return=720
prettytrace.py:9(1) return=5040
fac(7): 5040
</pre>

Let's trace the execution of an iterative factorial function in python


__Source:__

```python
#!/usr/bin/env python3

import prettytrace

def fac_iter(arg_n: int) -> int:
    res = 1
    for cur_n in range(1,arg_n):
        res *= cur_n
    return res

fac_iter = prettytrace.TraceMe(fac_iter)

print( "fac_iter(7):", fac_iter(7))

```

__Result:__
<pre>
adding LOAD_FAST 124
adding STORE_FAST 125
trace_fac_iter.py:5(1) def fac_iter(arg_n: int) -> int:
trace_fac_iter.py:5(1) # arg_n=7
trace_fac_iter.py:6(1)     res = 1
trace_fac_iter.py:7(1)     # store res 1
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n):
trace_fac_iter.py:7(1)     # load arg_n 7
trace_fac_iter.py:8(1)     # store cur_n 1
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 1
trace_fac_iter.py:8(1)         # load cur_n 1
trace_fac_iter.py:8(1)         # store res 1
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n):
trace_fac_iter.py:8(1)     # store cur_n 2
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 1
trace_fac_iter.py:8(1)         # load cur_n 2
trace_fac_iter.py:8(1)         # store res 2
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n):
trace_fac_iter.py:8(1)     # store cur_n 3
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 2
trace_fac_iter.py:8(1)         # load cur_n 3
trace_fac_iter.py:8(1)         # store res 6
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n):
trace_fac_iter.py:8(1)     # store cur_n 4
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 6
trace_fac_iter.py:8(1)         # load cur_n 4
trace_fac_iter.py:8(1)         # store res 24
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n):
trace_fac_iter.py:8(1)     # store cur_n 5
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 24
trace_fac_iter.py:8(1)         # load cur_n 5
trace_fac_iter.py:8(1)         # store res 120
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n):
trace_fac_iter.py:8(1)     # store cur_n 6
trace_fac_iter.py:8(1)         res *= cur_n
trace_fac_iter.py:8(1)         # load res 120
trace_fac_iter.py:8(1)         # load cur_n 6
trace_fac_iter.py:8(1)         # store res 720
trace_fac_iter.py:7(1)     for cur_n in range(1,arg_n):
trace_fac_iter.py:9(1)     return res
trace_fac_iter.py:9(1)     # load res 720
trace_fac_iter.py:9(1) return=720
fac_iter(7): 720
</pre>

Unfortunately there is a limit to this approach: we cannot access the function evaluation stack, the evalutation stack is currently not exposed by the interpreter to python code, as there is no field in the built-in frame object for it. It is therefore not possible to trace instructions like [MAP\_ADD](https://docs.python.org/3.8/library/dis.html#opcode-MAP\_ADD) that modify a given dictionary object.

It would however be possbible to do this trick, if we were to write some extension in the C language, that would allow us to access these fields... 


