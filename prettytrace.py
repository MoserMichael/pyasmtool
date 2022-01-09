import threading
import sys
import os
import linecache
import dataclasses
import inspect
import ctypes
import functools
import dis
import opcode

try:
    import ctypes
    _CTYPES_ENABLED = 0
except ImportError:
    _CTYPES_ENABLED = -1


# For reference; the frame level bytecode interter in cpython is implemented in function _PyEval_EvalFrameDefault
# cpython repo: https://github.com/python/cpython
# see query results of this github query:
#   https://github.com/python/cpython/search?q=_PyEval_EvalFrameDefault&type=code
#
# It's in file  cpython/Python/ceval.c
#  https://github.com/python/cpython/blob/31e43cbe5f01cdd5b5ab330ec3040920e8b61a91/Python/ceval.c
#
# Some of the fields of the frame object visible in Python via the Frame builtin type, and are explained here:
#   https://docs.python.org/3/library/inspect.html


_TABS_TO_SPACES = 4
_LOAD_OPCODES = {}
_STORE_OPCODES = {}
_CTYPES_POINTER_SIZE = -1
_CTYPES_ID_TYPE=ctypes.c_ulong


# weird tls in python... https://bugs.python.org/issue24020
local_data_ = threading.local()

# configuration parameters for tracing
@dataclasses.dataclass
class TraceParam:
    trace_indent: bool
    trace_loc: bool
    show_obj: int
    ignore_stdlib: bool

# adding a handler for an opcode
def _add_opcode( op_name, op_map, op_func):
    if op_name in opcode.opmap:
        op_code = opcode.opmap[ op_name ]
        #print("adding",op_name,op_code)
        op_map[op_code] = op_func
    else:
        print("Can't handle op code:", op_name)
###
# Stack access hacks (required for showing stores to dicts/vectors)
###
class PyObject(ctypes.Structure):
    _fields_ = (
        ('ob_refcnt', ctypes.c_ssize_t),
        ('ob_type', ctypes.c_void_p))

class PyVarObject(ctypes.Structure):
    _fields_ = (
        ('ob_refcnt', ctypes.c_ssize_t),
        ('ob_type', ctypes.c_void_p),
        ('ob_size', ctypes.c_ssize_t))

# lets hope the layout didn't change too much between versions...
#
# from: Include/cpython/frameobject.h
#
# struct _frame {
#    PyObject_VAR_HEAD
#    struct _frame *f_back;      /* previous frame, or NULL */
#    PyCodeObject *f_code;       /* code segment */
#    PyObject *f_builtins;       /* builtin symbol table (PyDictObject) */
#    PyObject *f_globals;        /* global symbol table (PyDictObject) */
#    PyObject *f_locals;         /* local symbol table (any mapping) */
#    PyObject **f_valuestack;    /* points after the last local */
#    /* Next free slot in f_valuestack.  Frame creation sets to f_valuestack.
#       Frame evaluation usually NULLs it, but a frame that yields sets it
#       to the current stack top. */
#    PyObject **f_stacktop;
#
# Usage in Python/ceval.c function: _PyEval_EvalFrameDefault
#
class PyFrm(PyVarObject):
    _fields_ = (
        ("f_back", ctypes.c_void_p),
        ("f_code", ctypes.c_void_p),
        ("f_builtins", ctypes.c_void_p),
        ("f_globals", ctypes.c_void_p),
        ("f_locals", ctypes.c_void_p),
        ("f_valuestack",  ctypes.c_void_p),
        ("f_stacktop",  ctypes.c_void_p),
        ("f_trace",  ctypes.c_void_p)
      )

class PyVoidPtr(ctypes.Structure):
    _fields_ = (
        ("ptr", ctypes.c_void_p),
        )

#def _access_stack(frame, num_entries):
#    # id(frame) - is the pointer to the frame structure.
#    # PyFrame.from_addr(id(frame)) - get ctypes wraper that points to the same address as the original frame object.
#    py_frame = PyFrm.from_address(id(frame))
#
#    assert frame.f_stacktop.value is not None
#    assert stack_top = frame.f_stacktop.value

def _check_frame_ctypes(prev_frame):
    current_frame = sys._getframe()
    hdr = PyFrm.from_address(id(current_frame))

    assert hex(hdr.f_back) == hex(id(current_frame.f_back))
    assert hex(id(prev_frame)) == hex(id(current_frame.f_back))
    assert hex(hdr.f_code) == hex(id(current_frame.f_code))

    return hex(hdr.f_back) == hex(id(current_frame.f_back)) and hex(id(prev_frame)) == hex(id(current_frame.f_back)) and hex(hdr.f_code) == hex(id(current_frame.f_code))


def _check_stack_access_sanity():
    global _CTYPES_ENABLED
    global _CTYPES_POINTER_SIZE
    global _CTYPES_ID_TYPE

    if not _check_frame_ctypes(sys._getframe()):
        print("Can't access stack directly; limited ability to trace variables")
        _CTYPES_ENABLED = -1
        return False

    _CTYPES_POINTER_SIZE = ctypes.sizeof(ctypes.c_void_p)

    # find integr size with same size as pointer sze
    if ctypes.sizeof(ctypes.c_ulonglong) == _CTYPES_POINTER_SIZE:
        _CTYPES_ID_TYPE = ctypes.c_ulonglong
    elif ctypes.sizeof(ctypes.c_ulong) == _CTYPES_POINTER_SIZE:
        _CTYPES_ID_TYPE = ctypes.c_ulong
    elif ctypes.sizeof(ctypes.c_uint) == _CTYPES_POINTER_SIZE:
        _CTYPES_ID_TYPE = ctypes.c_uint
    else:
        print("Can't find integral type for pointer size!!!")
        return False

    _CTYPES_ENABLED = 1
    return True


def _access_frame_stack(frame, from_stack = 2, num_entries = 2):
    hdr = PyFrm.from_address(id(frame))
    assert hdr.f_stacktop is not None

    ret = []

    item = 0
    top_of_stack = hdr.f_stacktop - (_CTYPES_POINTER_SIZE * from_stack)

    while item < num_entries:
        ptr_to_int = ctypes.c_ulong.from_address( top_of_stack )

        val =  ctypes.cast( ptr_to_int.value, ctypes.py_object).value

#        #value = _CTYPES_ID_TYPE.from_address(ptr_to_int.ptr).value
#        value = ctypes.c_ulong.from_address(ptr_to_int.value).value
#        print("item:", item, "value:", value)

        ret.append(val)
        item += 1
        top_of_stack += _CTYPES_POINTER_SIZE

    return ret


# lOAD_FAST gets the value from macro
# #define GETLOCAL(i)     (frame->localsplus[i])

def _show_load_fast(frame, instr, argval, ctx):
    varname = frame.f_code.co_varnames[ argval ]
    val = frame.f_locals[ varname ]
    prefix = ctx.get_line_prefix(frame, 1)
    sval = ctx.show_val(val)
    print(f"{prefix} # load {varname} {sval}")

def _show_load_global(frame, instr, argval, ctx):

    try:
        varname = frame.f_code.co_varnames[ argval ]
    except IndexError:
        print(f"Error: can't resolve argval Instruction: {instr} argval: {argval}, frame: {frame}")
        return

    if varname in frame.f_globals:
        val = frame.f_globals[ varname ]
    elif varname in frame.f_builtins:
        val = frame.f_builtins[ varname ]
    elif varname in globals():
        val = globals()[ varname ]
    else:
        print("load_global: can't find ", varname, "in any scope")
        return

    prefix = ctx.get_line_prefix(frame, 1)
    sval = ctx.show_val(val)
    print(f"{prefix} # load_global {varname} {sval}")

def _show_store_fast(frame, asm_instr, argval, ctx):
    varname = frame.f_code.co_varnames[ argval ]
    val = frame.f_locals[ varname ]
    prefix = ctx.get_line_prefix(frame, 1)
    sval = ctx.show_val(val)
    print(f"{prefix} # store {varname} {sval}")

def _show_store_global(frame, asm_instr, argval, ctx):
    varname = frame.f_code.co_varnames[ argval ]

    if varname in frame.f_globals:
        val = frame.f_globals[ varname ]
    elif varname in frame.f_builtins:
        val = frame.f_builtins[ varname ]
    elif varname in globals():
        val = globals()[ varname ]
    else:
        print("store_global: can't find ", varname, "in any scope")
        return

    prefix = ctx.get_line_prefix(frame, 1)
    sval = ctx.show_val(val)
    print(f"{prefix} # store_global {varname} {sval}")

def _binary_subscr(frame, asm_instr, argval, ctx):
    if _CTYPES_ENABLED != 1:
        return

    # implements TOS = TOS1[TOS]
    vals = _access_frame_stack(frame, from_stack=2, num_entries=2)

    deref_val = vals[0][ vals[1] ]
    prefix = ctx.get_line_prefix(frame, 1)
    sval = ctx.show_val(deref_val)

    print(f"{prefix} # binary_subscript arr[", repr(vals[1]), "]=", sval)

def _store_subscr(frame, asm_instr, argval, ctx):
    if _CTYPES_ENABLED != 1:
        return

    # implements TOS1[TOS] = TOS2
    vals = _access_frame_stack(frame, from_stack=3, num_entries=3)

    deref_val = vals[0]

    prefix = ctx.get_line_prefix(frame, 1)
    sval = ctx.show_val(deref_val)

    print(f"{prefix} # store_subscript arr[", repr(vals[2]), "]=", sval)


def _init_opcodes():
    _add_opcode( "LOAD_FAST", _LOAD_OPCODES, _show_load_fast)
    _add_opcode( "BINARY_SUBSCR", _LOAD_OPCODES, _binary_subscr)
    _add_opcode( "STORE_SUBSCR", _LOAD_OPCODES, _store_subscr)

    _add_opcode( "LOAD_GLOBAL", _LOAD_OPCODES, _show_load_global)
    _add_opcode( "STORE_FAST", _STORE_OPCODES, _show_store_fast)

    _check_stack_access_sanity()


class ThreadTraceCtx:
    def __init__(self, params : TraceParam):
        self.nesting = 0
        self.params = params
        self.in_trace = False
        self.instr_cache = {}
        self.prev_instr = None
        self.prev_instr_arg = None
        self.prefix_spaces = 0
#       self.prev_line_entry = None

    def show_val(self, val):
        try:
            if self.params.show_obj == 0:
                return str(val)
            elif self.params.show_obj == 1:
                return repr(val)
            return pprint.pformat(val)
        except AttributeError:
            return "<object not initialised yet>"


    def on_prepare(self, frame):
        self.filename = frame.f_code.co_filename
        self.bname = os.path.basename(self.filename)
        self.dirname = os.path.dirname(self.filename)
        if self.params.ignore_stdlib and self.dirname in sys.path:
            return False
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
        
        # if __init__ method, then don't show first param, self is not yet initialised.
#        is_init_method = False
#        if frame.f_code.co_name == "__init__":
#            is_init_method = True
#
        arg_info = inspect.getargvalues(frame)
        #print("arg_info:", arg_info)
        for arg in arg_info.args:
            sval = self.show_val(arg_info.locals[arg])
            print(f"{self.get_line_prefix(frame, 1)} # {arg}={sval}")

        #print(frame.f_code.co_filename, frame.f_code.co_name, "firstline:", firstline, "first-code-line:", linestarts[1])

    def on_prev_opcode(self, frame):
        if self.prev_instr is not None:
            #print("prev_instr:", self.prev_instr)
            func = _STORE_OPCODES.get(self.prev_instr, None)
            if func is not None:
                func(frame, self.prev_instr, self.prev_instr_arg, self) #self.get_line_prefix(frame, 1))
                self.prev_instr = None


    def on_opcode(self, frame):
        self.on_prev_opcode(frame)

        byte_index = frame.f_lasti
        instr = frame.f_code.co_code[byte_index]

        func = _LOAD_OPCODES.get(instr, None)
        arg = frame.f_code.co_code[byte_index+1]
        if func is not None:
            func(frame, instr, arg, self) #self.get_line_prefix(frame, 1))

        self.prev_instr = instr
        self.prev_instr_arg = arg

    def get_line_prefix(self, frame, add_prefix):
        lineno = frame.f_lineno
        ret = f"{self.bname}:{lineno}({self.nesting})" + (" " * self.prefix_spaces * add_prefix)
        if self.params.trace_indent:
            ret += ('.' * self.nesting)
        return ret


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
                spaces += _TABS_TO_SPACES
            else:
                break
            pos += 1

#        self.prev_line_entry = self.instr_cache[ self.filename ][ frame.f_code.co_name ][ lineno ]
#        self.show_loads(frame)


    def on_pop_frame(self, frame, arg):
        #print("on_pop_frame type(frame):", type(frame), frame.f_code.co_filename, frame.f_code.co_name)
        sval = self.show_val(arg)
        print(f"{self.get_line_prefix(frame, 0)} return={sval}")
        self.nesting -= 1


    # disassemble a  function, for each line establih a LineEntry - it holds two sets. 1) the set of load 2) set of store type instructions.
    # Fill the instr_cache with entries self.instr_cache[ module ][ functon_name ][ line_number ] = LineEntry()


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

    if not hasattr(local_data_, "trace_ctx") or getattr( local_data_, "trace_ctx") is None:
        setattr(local_data_, "trace_ctx", ThreadTraceCtx(trace_param))
        return True
    return False

def _check_eof_trace():
    thread_ctx = getattr(local_data_, "trace_ctx")
    if thread_ctx is not None and thread_ctx.nesting == 0:
        setattr(local_data_,"trace_ctx", None)
        sys.settrace( None )




class TraceMe:

    def __init__(self, func, *, trace_indent : bool = False, trace_loc : bool = True, show_obj : int = 0, ignore_stdlib : bool = True):
        functools.update_wrapper(self, func)
        self.func = func
        self.trace_indent = trace_indent
        self.trace_loc = trace_loc
        self.show_obj = show_obj
        self.ignore_stdlib = ignore_stdlib


    def __call__(self, *args, **kwargs):

        # first invocation sets up tracing hook
        if _init_trace( TraceParam(trace_indent=self.trace_indent, trace_loc=self.trace_loc, show_obj=self.show_obj, ignore_stdlib=self.ignore_stdlib) ):
            sys.settrace( _func_tracer )

        func_fwd = self.func
        ret_val = func_fwd(*args, **kwargs)

        # clean up trace hook if finished tracing
        _check_eof_trace()

        return ret_val

# init at load time.
_init_opcodes()

def disable_stack_access():
    global _CTYPES_ENABLED

    _CTYPES_ENABLED = -1

# metaclass, adds tracers to all methods of a class
class TraceClass(type):
    def __new__(meta_class, name, bases, cls_dict, *, trace_indent : bool = False, trace_loc : bool = True, show_obj : int = 0, ignore_stdlib : bool = True):

        #
        # see trick here: https://stackoverflow.com/questions/11349183/how-to-wrap-every-method-of-a-class ]
        # need to modify the cls_dict object in order to wrap each member function!
        #
        trace_param = TraceParam(trace_indent=trace_indent, trace_loc=trace_loc, show_obj=show_obj, ignore_stdlib=ignore_stdlib)
        new_class_dict = {}
        for entry,val_func in cls_dict.items():
            if inspect.isfunction(val_func):
                # hack - avoids looking at the same value of val_func !!! see https://stackoverflow.com/questions/8946868/is-there-a-pythonic-way-to-close-over-a-loop-variable
                # the variable that the closure should remember is passed as argument, this makes a separate copy of the value in the called function frame?
                # (what a language...)
                def wrapper_factory(val_func):
                    def wrapper_fun(*args, **kwargs):

                        functools.wraps(val_func)

                        if _init_trace( trace_param ):
                            sys.settrace( _func_tracer )

                        ret_val = val_func(*args, **kwargs)

                        # clean up trace hook if finished tracing
                        _check_eof_trace()

                        return ret_val
                    return wrapper_fun

                val_func = wrapper_factory(val_func)
            new_class_dict[entry] = val_func
            

        class_instance = super().__new__(meta_class, name, bases, new_class_dict)

        print(f"return {class_instance} {id(class_instance)}")
        return class_instance

#    def __call__(cls, *args, **kwargs):
#        instance = cls.__new__(cls)
#        print(f"type: {type(instance)} instance: {instance}")
#        print(f"cls: {cls} {id(cls)} args: {args} kwargs: {kwargs}")
#        instance.__init__(*args, **kwargs)
#
#        return instance

