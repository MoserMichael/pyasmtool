# Pyasmtools - looking at the python bytecode for fun and profit.

The pyasmtools library is made up of two parts
- A python bytecode disassembler . See [Python bytecode explained](https://github.com/MoserMichael/pyasmtool/blob/master/bytecode_disasm.md)
- A tracer for python, that displays the source code of each executed line, along with the variables loaded and stored. See [Execution traces in Python](https://github.com/MoserMichael/pyasmtool/blob/master/tracer.md)

All this is part of my [tutorial on advanced python topics](https://github.com/MoserMichael/python-obj-system/blob/master/README.md)

Note that some of the goodness in this library is cpython specific, i don't expect it to work on every python based environment.

## Installation

You can install this library with ```pip3 install pyasmtools```. Instructions are in the above mentioned links.
