
import threading
import sys
import os
import linecache
import dataclasses
import inspect
import functools
import dis
import opcode

TRACE_INDENT=1
TRACE_LOC=2
TABS_TO_SPACES=4

_LOAD_OPCODES = {}
_STORE_OPCODES = {}

# weird tls in python... https://bugs.python.org/issue24020
local_data_ = threading.local()

#class LineEntry:
#    def __init__(self):
#        self.load_instr = []
#        self.store_instr = []

@dataclasses.dataclass
class TraceParam: 
    trace_indent: bool
    trace_loc: bool

def _add_opcode( op_name, op_map, op_func):
    if op_name in opcode.opmap:
        op_code = opcode.opmap[ op_name ]
        print("adding",op_name,op_code)
        op_map[op_code] = op_func
        
# For reference; the frame level bytecode interter in cpython is implemented in function _PyEval_EvalFrameDefault
# cpython repo: https://github.com/python/cpython
# see query results of this github query:
#   https://github.com/python/cpython/search?q=_PyEval_EvalFrameDefault&type=code
#
# It's in file  cpython/Python/ceval.c
#  https://github.com/python/cpython/blob/31e43cbe5f01cdd5b5ab330ec3040920e8b61a91/Python/ceval.c
#
# Some of the fields of the frame object visible in Python are explained here: 
#   https://docs.python.org/3/library/inspect.html


# lOAD_FAST gets the value from macro 
# #define GETLOCAL(i)     (frame->localsplus[i])

def _show_load_fast(frame, instr, argval, prefix):
    varname = frame.f_code.co_varnames[ argval ] 
    val = frame.f_locals[ varname ]
    print(f"{prefix} # load {varname} {val}")

def _show_store_fast(frame, asm_instr, argval, prefix):
    varname = frame.f_code.co_varnames[ argval ] 
    val = frame.f_locals[ varname ]
    print(f"{prefix} # store {varname} {val}")


def _show_return_value(fame, asm_instr, argval):
    pass

def _init_opcodes():
    _add_opcode( "LOAD_FAST", _LOAD_OPCODES, _show_load_fast)
    _add_opcode( "STORE_FAST", _STORE_OPCODES, _show_store_fast)

class ThreadTraceCtx:
    def __init__(self, params : TraceParam):
        self.reinit(params)

    def reinit(self, params : TraceParam):
        self.nesting = 0
        self.paams = params
        self.in_trace = False
        self.instr_cache = {}
        self.prev_instr = None
        self.prev_instr_arg = None
        self.prefix_spaces = 0
#       self.prev_line_entry = None

    def on_prepare(self, frame):
        self.filename = frame.f_code.co_filename
        self.bname = os.path.basename(self.filename)
        if self.bname == "prettytrace.py" or self.bname == "<string>":
            return False
        return True

    def on_push_frame(self, frame):
        self.nesting += 1
        #print("on_push_frame nesting:", id(self), self.nesting, "type(frame):", type(frame), frame.f_code.co_filename, frame.f_code.co_name)
        firstline = frame.f_code.co_firstlineno

        linestarts = next(dis.findlinestarts(frame.f_code))[1]

        #self.disasm_func( frame.f_code )

        while firstline < linestarts:
            line = linecache.getline(self.filename, firstline)
            print(f"{self.get_line_prefix(frame, 0)} {line}", end="")
            firstline += 1

        arg_info = inspect.getargvalues(frame)
        #print("arg_info:", arg_info)
        for arg in arg_info.args:
            print(f"{self.get_line_prefix(frame, 1)} # {arg}={arg_info.locals[arg]}")

        #print(frame.f_code.co_filename, frame.f_code.co_name, "firstline:", firstline, "first-code-line:", linestarts[1])

    def on_prev_opcode(self, frame):
        if self.prev_instr is not None:
            #print("prev_instr:", self.prev_instr)
            func = _STORE_OPCODES.get(self.prev_instr, None)
            if func is not None:
                func(frame, self.prev_instr, self.prev_instr_arg, self.get_line_prefix(frame, 1))
                self.prev_instr = None

 
    def on_opcode(self, frame):
        self.on_prev_opcode(frame)

        byte_index = frame.f_lasti
        instr = frame.f_code.co_code[byte_index]

        func = _LOAD_OPCODES.get(instr, None)
        arg = frame.f_code.co_code[byte_index+1]
        if func is not None:
            func(frame, instr, arg, self.get_line_prefix(frame, 1))

        self.prev_instr = instr
        self.prev_instr_arg = arg

    def get_line_prefix(self, frame, add_prefix):
        lineno = frame.f_lineno
        return f"{self.bname}:{lineno}({self.nesting})" + (" " * self.prefix_spaces * add_prefix)


    def on_line(self, frame):
        # after completion of the previous line - show stores for that line.
#        if self.prev_line_entry is not None:
#            self.show_stores(frame)

        self.on_prev_opcode(frame)
        lineno = frame.f_lineno
        line = linecache.getline(self.filename, lineno)
        print(f"{self.get_line_prefix(frame, 0)} {line}", end='')

        # count prefix spaces.
        line_len = len(line)
        pos=0
        spaces=0
        while pos < line_len:
            if line[pos] == ' ':
                self.prefix_spaces = spaces + 1
                spaces+=1
            elif line[pos] == '\t':
                self.prefix_spaces = spaces + 1
                spaces += TABS_TO_SPACES 
            else:
                break
            pos += 1

#        self.prev_line_entry = self.instr_cache[ self.filename ][ frame.f_code.co_name ][ lineno ]
#        self.show_loads(frame)


    def on_pop_frame(self, frame, arg):
        #print("on_pop_frame type(frame):", type(frame), frame.f_code.co_filename, frame.f_code.co_name)
        print(f"{self.get_line_prefix(frame, 0)} return={arg}")
        self.nesting -= 1


    # disassemble a  function, for each line establih a LineEntry - it holds two sets. 1) the set of load 2) set of store type instructions.
    # Fill the instr_cache with entries self.instr_cache[ module ][ functon_name ][ line_number ] = LineEntry()

#    def disasm_func(self, func):
#        code = func
#        cache_entry = self.instr_cache.get( code.co_filename )
#        if cache_entry is None:
#            cache_entry = {}
#            self.instr_cache[ code.co_filename ] = cache_entry
#
#        func_entry = cache_entry.get(code.co_name)
#        if func_entry is not None:
#            return
#
#        func_entry = {}
#        cache_entry[code.co_name] = func_entry
#
#        instr = dis.get_instructions( func )
#        for inst in instr:
#            if inst.starts_line is not None:
#                cur_instr = LineEntry()
#                func_entry[ inst.starts_line ] = cur_instr
#            if _is_load_instr(inst):
#                cur_instr.load_instr.append(inst)
#            if _is_store_instr(inst):
#                cur_instr.store_instr.append(inst)

#    def show_stores(self,frame):
#        for instr in self.prev_line_entry.store_instr:
#            func = _STORE_OPODES[instr.opcode]
#            func(frame, instr)
#
#    def show_loads(self,frame):
#        for instr in self.prev_line_entry.load_instr:
#            func = _LOAD_OPCODES[instr.opcode]
#            func(frame, instr)
#

def _line_tracer(frame, why, arg):
    ctx = getattr(local_data_,"trace_ctx")
    if ctx.in_trace:
        return
    ctx.in_trace=True

    if why == 'line':
        ctx.on_line(frame)
    elif why == 'opcode':
        ctx.on_opcode(frame)
    elif why == 'return':
#        if not ctx.on_prepare(frame):
#            return
        ctx.on_pop_frame(frame, arg)

    ctx.in_trace=False
    return _line_tracer

def _func_tracer(frame, why, arg):
    ctx = getattr(local_data_,"trace_ctx")
    if ctx.in_trace:
        return
    if not ctx.on_prepare(frame):
        return
  
    frame.f_trace_opcodes = True
    ctx.in_trace=True
    if why == 'call':
        ctx.on_push_frame(frame)
        ctx.in_trace=False
        return _line_tracer

    ctx.in_trace=False


def _init_trace(trace_param : TraceParam):
    if not hasattr(local_data_, 'trace_ctx'):
        setattr(local_data_, "trace_ctx", ThreadTraceCtx(trace_param))
        return True
    return False

def _check_eof_trace():
    thread_ctx = getattr(local_data_, "trace_ctx")
    return thread_ctx.nesting == 0


    
class TraceMe:

    def __init__(self, func,  trace_indent : bool = False, trace_loc : bool = True):
        functools.update_wrapper(self, func)
        self.func = func
        self.trace_indent = trace_indent
        self.trace_loc = trace_loc


    def __call__(self, *args, **kwargs):
        if _init_trace( TraceParam(trace_indent=self.trace_indent, trace_loc=self.trace_loc) ):
            sys.settrace( _func_tracer )
        ret_val = self.func(*args, **kwargs)

        if _check_eof_trace():
            sys.settrace( None )

        return ret_val

# init at load time.
_init_opcodes()
