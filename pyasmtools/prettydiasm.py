"""bytecode disassembler that prints source for each statement before the bytecode listing (note, doesn't work with exec/compile built-ins)"""

import dis
import inspect
import linecache
import os

__all__ = [ "prettydis" ]

# formatting function copied from disasm sources (adjusted from dis module)
def _disassemble(inst, show_opcode_as_links=False, lineno_width=3, mark_as_current=False, offset_width=4):

    _OPNAME_WIDTH = 20
    _OPARG_WIDTH = 5

    fields = []
    # Column: Source code line number
    if lineno_width:
        if inst.starts_line is not None:
            lineno_fmt = "%%%dd" % lineno_width
            fields.append(lineno_fmt % inst.starts_line)
        else:
            fields.append(' ' * lineno_width)
    # Column: Current instruction indicator
    if mark_as_current:
        fields.append('-->')
    else:
        fields.append('   ')
    # Column: Jump target marker
    if inst.is_jump_target:
        fields.append('>>')
    else:
        fields.append('  ')
    # Column: Instruction offset from start of code sequence
    fields.append(repr(inst.offset).rjust(offset_width))
    # Column: Opcode name
    if show_opcode_as_links:
        opname = f'<a href="https://docs.python.org/3/library/dis.html#opcode-{inst.opname}">{inst.opname}</a>'
    else:
        opname = inst.opname

    fields.append(opname.ljust(_OPNAME_WIDTH))
    # Column: Opcode argument
    if inst.arg is not None:
        fields.append(repr(inst.arg).rjust(_OPARG_WIDTH))
        # Column: Opcode argument details
        if inst.argrepr:
            fields.append('(' + inst.argrepr + ')')
    return ' '.join(fields).rstrip()

def _annotation(spec, argname, ret_val):
    if spec.annotations is not None and argname in spec.annotations:
        if ret_val:
            return " -> " + spec.annotations[ argname ].__qualname__
        return ": " + spec.annotations[ argname ].__qualname__

    return ""

def func_spec(spec):
    #print(spec)

    arg_desc=[]

    idx = 0
    for arg in spec.args:
        arg_spec=str(arg)
        arg_spec += _annotation(spec, arg, False)
        if spec.defaults is not None and idx < len(spec.defaults):
            arg_spec+=' = '+str(spec.defaults[idx])
        arg_desc.append(arg_spec)
        idx += 1

    if spec.varargs is not None:
        arg_desc.append("*" + spec.varargs)

    for arg in spec.kwonlyargs:
        arg_spec = str(arg)
        arg_spec += _annotation(spec, arg, False)
        if arg in spec.kwanlydefaults:
            arg_spec+=' = '+str(spec.kwonlydefaults[ arg ])
        arg_desc.append(arg_spec)

    if spec.varkw is not None:
        arg_desc.append("**" + spec.varkw)

    return ", ".join(arg_desc)


# functions that are adorned with decorators: need to get the real function value!
def get_real_func(func):
    while getattr(func,"__wrapped__", None) is not None:
        func = getattr(func,"__wrapped__")

    return func

def get_func_obj_spec(func):
    spec = inspect.getfullargspec(func)
    param_specs = func_spec( spec )
    return_spec = _annotation(spec, "return", True)
    return f"def {func.__qualname__}({param_specs}){return_spec}:"



def prettydis(func, show_opcode_as_links=False):
    """dissassemble function and show source. Note, doesn't work with compile/exec built-in functions"""

    func = get_real_func(func)

    #code_obj = dis.get_code_object(func)

    file_path = inspect.getfile( func )
    base_name = os.path.basename( file_path )

    print("File path:", file_path,"\n")
    #print("File path:", inspect.getsourcefile(func),"\n")

#    first_line = 0
#    instr = dis.get_instructions( func )
#    for inst in instr:
#        if inst.starts_line is not None:
#            first_line = inst.starts_line
#            break
#    first_line -= 1

    first_line = func.__code__.co_firstlineno 

#    spec = inspect.getfullargspec(func)
#    param_specs = func_spec( spec )
#    return_spec = _annotation(spec, "return", True)
#    print(f"{base_name}:{first_line} def {func.__qualname__}({param_specs}){return_spec}:")
    print(f"{base_name}:{first_line} {get_func_obj_spec(func)}")

    # don't remove the next line, please! It's a generator, and will continue after the first line...
    instr = dis.get_instructions( func )
    for inst in instr:
        if inst.starts_line is not None:
            line_str = linecache.getline( inspect.getfile(func), inst.starts_line)
            print(f"\n{base_name}:{inst.starts_line} \t{line_str}")
        print(_disassemble(inst,show_opcode_as_links=show_opcode_as_links))
        #print(inst)
