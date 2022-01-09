#!/usr/bin/env python3

from mdpyformat import *

header_md("Execution traces in Python", nesting=1)

print_md("""
This section will examine, how to use our understanding of the Python bytecode, in order to write a better execution trace facility for Python.
""")

header_md("Execution traces in the bash shell", nesting=2)

print_md("""
I am a big fan of traces in the scripting language of the bash shell. The [set -x](https://www.gnu.org/software/bash/manual/bash.html#index-BASH_005fXTRACEFD) command enables a special trace mode, where the change and side effect of each line are displayed in the traces written to the standard error stream. Let's examine a few example of this feature; I think it will be relatively easy to understand the program, by looking at both the program code and its exeuction trace, even if one is not all to familiar with the bash scripting language.

The following example computes a factorial in a recursive way:
""")

run_and_quote("./fac.sh", command="", line_prefix="")

print_md("""
The following example computes a factorial in an iterative way
""")

run_and_quote("./fac2.sh", command="", line_prefix="")

header_md("Execution trace in Python", nesting=2)

print_md("""The python standard library has the [trace](https://docs.python.org/3/library/trace.html) module, one of its features is to print out the source lines of a program, as the program is executed. Unfortunately it does not show the variable values and does not show the modifications performed on these variables

(To be true, the trace module is a very versatile one, it can also be used to provides coverage analysis and can be used as a simle profiler)

Let's get the trace of a factorial program with the trace module, by running the following command ```python3 -m trace --trace fac.py```

""")

run_and_quote("./fac.py", command="python3 -m trace --trace", line_prefix="")

header_md("Let's make a better tracer!", nesting=2)

print_md("""
Let's attemt to make a better trace facility for python.
The [sys.settrace](https://docs.python.org/3/library/sys.html#sys.settrace) function installs a callback that is being called to trace the execution of every line; Now this function can install a special trace function, that will get called upon the exeuction of every opcode; here we could try and show all load and store instructions
""")

print_md("""
Let's trace the execution of a recursive factorial function in python. Note that the tracer is defined as a decorator of the traced function.

The traced output is showing the file name, line numer and depth of the call stack, counting from the first call of the traced function.
""")

run_and_quote("./trace_fac_rec.py", command="", line_prefix="")

print_md("""
It is also possible to specify an indentation prefix that depends on the level of call nesting, just like in bash
""")

run_and_quote("./trace_fac_rec_indent.py", command="", line_prefix="")


print_md("""
Let's trace the execution of an iterative factorial function in python
""")

run_and_quote("./trace_fac_iter.py", command="", line_prefix="")

print_md("""
Unfortunately there is a limit to this approach: we cannot access the function evaluation stack, the evalutation stack is currently not exposed by the interpreter to python code, as there is no field in the built-in frame object for it. It is therefore not possible to trace instructions like [STORE_SUBSCRIPT](https://docs.python.org/3.8/library/dis.html#opcode-STORE_SUBSCRIPT) and [LOAD_SUBSCRIPT](https://docs.python.org/3.8/library/dis.html#opcode-LOAD_SUBSCRIPT) bytecode instructions, that modify a given dictionary object.

It would however be possbible to do this trick, if we were to write some extension in the C language, that would allow us to access these fields... But wait, it seems it is possible from python [see this discussion](https://stackoverflow.com/questions/44346433/in-c-python-accessing-the-bytecode-evaluation-stack), so back to the drawing board!
""")

print_md("""
Here is an example of tracing list and map access.
""")
run_and_quote("./trace_lookup.py", command="", line_prefix="")


print_md("""
Here is an example of accessing python objects..
""")
run_and_quote("./trace_obj.py", command="", line_prefix="")


