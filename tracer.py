#!/usr/bin/env python3

from mdpyformat import *

header_md("Execution traces in Python", nesting=1)

print_md("""
This section will examine, how to use our understanding of the Python bytecode, gained in the [previous lesson](https://github.com/MoserMichael/pyasmtool/blob/master/bytecode_disasm.md) in order to write a better execution trace facility for Python.

The tracer will be specific to the [cpython](https://github.com/python/cpython/) environment, I doubt that it will work on all python environments, reasons are explained below.
""")

header_md("Execution traces in the bash shell", nesting=2)

print_md("""
I am a big fan of traces in the scripting language of the bash shell. The [set -x](https://www.gnu.org/software/bash/manual/bash.html#index-BASH_005fXTRACEFD) command enables a special trace mode, where the change and side effect of each line are displayed in the traces written to the standard error stream. Let's examine a few example of this feature; I think it will be relatively easy to understand the program, by looking at both the program code and its execution trace, even if one is not all to familiar with the bash scripting language.

The following example computes a factorial in a recursive way:
""")

run_and_quote("./fac.sh", command="", line_prefix="", quote_lt_gt=True)

print_md("""
For example the start of the invocation looks as follow
```
+ factorial 5
+ '[' 5 -le 1 ']'
```
The bash shell is an interpreter, it translates the source code into an in memory tree representation that is called the [abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree)

The next step for the bash interpreter to evaluate the program, it does so by following the nodes of the abstract syntax tree in [Post order (LRN)](https://en.wikipedia.org/wiki/Tree_traversal#Post-order,_LRN), first the left and the right subtree are evaluated, in order to get all the arguments for operator of the current tree node, the next step is to evaluate the operator designated by the current node
This technique of evaluation is also known as a [Tree-Walk interpreter](https://craftinginterpreters.com/a-tree-walk-interpreter.html), it allows the bash interpreter to show an intuitive trace output for the function invocation and the test expression, it is all produced while evaluating the in memory representation / abstract syntax tree of the program.

""")

print_md("""
The following example computes a factorial in an iterative way, note that the arithmetic bash expressions are not traced with the same level of detail, as in the case of the test expressions!
""")

run_and_quote("./fac2.sh", command="", line_prefix="", quote_lt_gt=True)

header_md("The trace module in the standard library of Python", nesting=2)

print_md("""The python standard library has the [trace](https://docs.python.org/3/library/trace.html) module, one of its features is to print out the source lines of a program, as the program is executed. Unfortunately, it does not show the variable values and does not show the modifications performed on these variables

To be true, the trace module is a very versatile one, it can also be used to provides coverage analysis and can be used as a simple profiler; also they make an effort to stick to functionality that is common to all python interpreters/runtime environments.

Let's get the trace of a factorial program with the trace module, by running the following command ```python3 -m trace --trace fac.py```
""")

run_and_quote("./fac.py", command="python3 -m trace --trace", line_prefix="", quote_lt_gt=True)

header_md("Let's make a tracer for python!", nesting=2)

print_md("""
Let's attempt to make a trace facility for python, that also shows the content of accessed variables.
The [sys.settrace](https://docs.python.org/3/library/sys.html#sys.settrace) function installs a callback, that is being called to trace the execution of every line; Now this function can install a special trace function, that will get called upon the execution of every opcode; here we could try and show the effect of load and store bytecode instructions. You can learn more about the python bytecode instructions [in this lesson](https://github.com/MoserMichael/pyasmtool/blob/master/bytecode_disasm.md) )

I am not sure, that the opcode tracing capabilities of sys.setrace are equally supported in all python environments; For example [PyPy](https://www.pypy.org/) is implementation a just in time compiler that is supposed to translate the bytecode instructions into native code, at some oint. I didn't check this trick for that environment.

A more complete implementation could trace the whole stack, as an expression is being evaluated and reduced on the stack, however i am a bit afraid, that the process would be very slow, in addition to being quite difficult to implement.
""")

header_md("The python tracer in action", nesting=3)

print_md("""
You can install the library that includes the tracer with ```pip3 install pyasmtools```. 

Note that the tracer is defined as a decorator of the traced function. (You can learn more about decorators in [this lesson](https://github.com/MoserMichael/python-obj-system/blob/master/decorator.md)

The trace output is showing the file name, line number and depth of the call stack, counting from the first call of the traced function. You also see some added comments that show the load operations of variables from memory to python evaluation stack, as well of store instructions (these move the stack values back to the memory location of the variables)
""")

run_and_quote("./trace_fac_rec.py", command="", line_prefix="", quote_lt_gt=True)

print_md("""
It is also possible to specify an indentation prefix that depends on the level of call nesting, just like in bash
""")

run_and_quote("./trace_fac_rec_indent.py", command="", line_prefix="", quote_lt_gt=True)


print_md("""
Let's trace the execution of an iterative factorial function in python
""")

run_and_quote("./trace_fac_iter.py", command="", line_prefix="", quote_lt_gt=True)

print_md("""
So far the trace program did not need to access the evaluation stack of the python interpreter, the evaluation stack is currently not exposed by the interpreter to python code, as there is no field in the built-in frame object for it. I used a workaround, accessing the memory location referred to by the bytecode instruction before executing the [LOAD_FAST](https://docs.python.org/3/library/dis.html#opcode-LOAD_FAST) instruction, and accessing the modified location after running the [STORE_FAST](https://docs.python.org/3/library/dis.html#opcode-STORE_FAST) instruction, However that trick is not feasible for the array and dictionary access instructions [STORE_SUBSCR](https://docs.python.org/3.8/library/dis.html#opcode-STORE_SUBSCR) and [BINARY_SUBSCRIPT](https://docs.python.org/3.8/library/dis.html#opcode-LOAD_SUBSCRIPT) bytecode instructions, here i would need to take a direct look at the evaluation stack.

It would however be possible to do this trick, from python with the [ctypes module](https://docs.python.org/3/library/ctypes.html), without any native code at all! [see this discussion](https://stackoverflow.com/questions/44346433/in-c-python-accessing-the-bytecode-evaluation-stack), so back to the drawing board!
""")

print_md("""
Given this trick, here is an example of tracing list and map access. 
""")
run_and_quote("./trace_lookup.py", command="", line_prefix="", quote_lt_gt=True)


print_md("""
Here is an example of accessing python objects. You can trace every method call of a class, here you need to define the class with the TraceClass meta-class. (You can learn more about metaclasses in [this lesson](https://github.com/MoserMichael/python-obj-system/blob/master/python-obj-system.md)
The TraceClass metaclass will create a wrapper method for each method of the marked class, calling the method will result in tracing it.
""")
run_and_quote("./trace_obj.py", command="", line_prefix="", quote_lt_gt=True)


print_md("""
Here is an example trace of a program, that counts the number of occurrences of each letter in a given text file.
""")

run_and_quote("./trace_histo.py", command="", line_prefix="", quote_lt_gt=True)

header_md("tracer reference", nesting=3)

print_md(""""

Both the TraceMe function decorator class and the TraceClass metaclass accept the same set of arguments, these are listed here:

- trace_indent : bool = False  :: show a prefix of dots for each line (number of dots equals to call depth)
- show_obj : int = 1           :: level of detail for values displayed (0 - str(val), 1 - repr(val), 2 - pprint.pformat(val))
- ignore_stdlib : bool = True  :: do not trace functions/objects in standard library
- out = sys.stderr             :: destination stream of trace output

""")

header_md("Conclusion", nesting=2)

print_md("""
The [sys.settrace](https://docs.python.org/3/library/sys.html#sys.settrace) function is quite powerful. It gives us an insight into the working of the python interpreter, if combined with some knowledge of the python bytecode.
""")


