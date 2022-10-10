# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/inspect.py
__author__ = 'Ka-Ping Yee <ping@lfw.org>'
__date__ = '1 Jan 2001'
import sys
import os
import types
import string
import re
import dis
import imp
import tokenize
import linecache
from operator import attrgetter
from collections import namedtuple
CO_OPTIMIZED, CO_NEWLOCALS, CO_VARARGS, CO_VARKEYWORDS = (1, 2, 4, 8)
CO_NESTED, CO_GENERATOR, CO_NOFREE = (16, 32, 64)
TPFLAGS_IS_ABSTRACT = 1048576

def ismodule(object):
    return isinstance(object, types.ModuleType)


def isclass(object):
    return isinstance(object, (type, types.ClassType))


def ismethod(object):
    return isinstance(object, types.MethodType)


def ismethoddescriptor(object):
    return hasattr(object, '__get__') and not hasattr(object, '__set__') and not ismethod(object) and not isfunction(object) and not isclass(object)


def isdatadescriptor(object):
    return hasattr(object, '__set__') and hasattr(object, '__get__')


if hasattr(types, 'MemberDescriptorType'):

    def ismemberdescriptor(object):
        return isinstance(object, types.MemberDescriptorType)


else:

    def ismemberdescriptor(object):
        return False


if hasattr(types, 'GetSetDescriptorType'):

    def isgetsetdescriptor(object):
        return isinstance(object, types.GetSetDescriptorType)


else:

    def isgetsetdescriptor(object):
        return False


def isfunction(object):
    return isinstance(object, types.FunctionType)


def isgeneratorfunction(object):
    return bool((isfunction(object) or ismethod(object)) and object.func_code.co_flags & CO_GENERATOR)


def isgenerator(object):
    return isinstance(object, types.GeneratorType)


def istraceback(object):
    return isinstance(object, types.TracebackType)


def isframe(object):
    return isinstance(object, types.FrameType)


def iscode(object):
    return isinstance(object, types.CodeType)


def isbuiltin(object):
    return isinstance(object, types.BuiltinFunctionType)


def isroutine(object):
    return isbuiltin(object) or isfunction(object) or ismethod(object) or ismethoddescriptor(object)


def isabstract(object):
    return bool(isinstance(object, type) and object.__flags__ & TPFLAGS_IS_ABSTRACT)


def getmembers(object, predicate=None):
    results = []
    for key in dir(object):
        try:
            value = getattr(object, key)
        except AttributeError:
            continue

        if not predicate or predicate(value):
            results.append((key, value))

    results.sort()
    return results


Attribute = namedtuple('Attribute', 'name kind defining_class object')

def classify_class_attrs(cls):
    mro = getmro(cls)
    names = dir(cls)
    result = []
    for name in names:
        homecls = None
        for base in (cls,) + mro:
            if name in base.__dict__:
                obj = base.__dict__[name]
                homecls = base
                break
        else:
            obj = getattr(cls, name)
            homecls = getattr(obj, '__objclass__', homecls)

        if isinstance(obj, staticmethod):
            kind = 'static method'
        elif isinstance(obj, classmethod):
            kind = 'class method'
        elif isinstance(obj, property):
            kind = 'property'
        elif ismethoddescriptor(obj):
            kind = 'method'
        elif isdatadescriptor(obj):
            kind = 'data'
        else:
            obj_via_getattr = getattr(cls, name)
            if ismethod(obj_via_getattr) or ismethoddescriptor(obj_via_getattr):
                kind = 'method'
            else:
                kind = 'data'
            obj = obj_via_getattr
        result.append(Attribute(name, kind, homecls, obj))

    return result


def _searchbases(cls, accum):
    if cls in accum:
        return
    accum.append(cls)
    for base in cls.__bases__:
        _searchbases(base, accum)


def getmro(cls):
    if hasattr(cls, '__mro__'):
        return cls.__mro__
    else:
        result = []
        _searchbases(cls, result)
        return tuple(result)


def indentsize(line):
    expline = string.expandtabs(line)
    return len(expline) - len(string.lstrip(expline))


def getdoc(object):
    try:
        doc = object.__doc__
    except AttributeError:
        return None

    return None if not isinstance(doc, types.StringTypes) else cleandoc(doc)


def cleandoc(doc):
    try:
        lines = string.split(string.expandtabs(doc), '\n')
    except UnicodeError:
        return None

    margin = sys.maxint
    for line in lines[1:]:
        content = len(string.lstrip(line))
        if content:
            indent = len(line) - content
            margin = min(margin, indent)

    if lines:
        lines[0] = lines[0].lstrip()
    if margin < sys.maxint:
        for i in range(1, len(lines)):
            lines[i] = lines[i][margin:]

    while lines and not lines[-1]:
        lines.pop()

    while lines and not lines[0]:
        lines.pop(0)

    return string.join(lines, '\n')
    return None


def getfile(object):
    if ismodule(object):
        if hasattr(object, '__file__'):
            return object.__file__
        raise TypeError('{!r} is a built-in module'.format(object))
    if isclass(object):
        object = sys.modules.get(object.__module__)
        if hasattr(object, '__file__'):
            return object.__file__
        raise TypeError('{!r} is a built-in class'.format(object))
    if ismethod(object):
        object = object.im_func
    if isfunction(object):
        object = object.func_code
    if istraceback(object):
        object = object.tb_frame
    if isframe(object):
        object = object.f_code
    if iscode(object):
        return object.co_filename
    raise TypeError('{!r} is not a module, class, method, function, traceback, frame, or code object'.format(object))


ModuleInfo = namedtuple('ModuleInfo', 'name suffix mode module_type')

def getmoduleinfo(path):
    filename = os.path.basename(path)
    suffixes = map(lambda info: (-len(info[0]),
     info[0],
     info[1],
     info[2]), imp.get_suffixes())
    suffixes.sort()
    for neglen, suffix, mode, mtype in suffixes:
        if filename[neglen:] == suffix:
            return ModuleInfo(filename[:neglen], suffix, mode, mtype)


def getmodulename(path):
    info = getmoduleinfo(path)
    return info[0] if info else None


def getsourcefile(object):
    filename = getfile(object)
    if string.lower(filename[-4:]) in ('.pyc', '.pyo'):
        filename = filename[:-4] + '.py'
    for suffix, mode, kind in imp.get_suffixes():
        if 'b' in mode and string.lower(filename[-len(suffix):]) == suffix:
            return None

    if os.path.exists(filename):
        return filename
    elif hasattr(getmodule(object, filename), '__loader__'):
        return filename
    else:
        return filename if filename in linecache.cache else None


def getabsfile(object, _filename=None):
    if _filename is None:
        _filename = getsourcefile(object) or getfile(object)
    return os.path.normcase(os.path.abspath(_filename))


modulesbyfile = {}
_filesbymodname = {}

def getmodule(object, _filename=None):
    if ismodule(object):
        return object
    elif hasattr(object, '__module__'):
        return sys.modules.get(object.__module__)
    elif _filename is not None and _filename in modulesbyfile:
        return sys.modules.get(modulesbyfile[_filename])
    else:
        try:
            file = getabsfile(object, _filename)
        except TypeError:
            return

        if file in modulesbyfile:
            return sys.modules.get(modulesbyfile[file])
        for modname, module in sys.modules.items():
            if ismodule(module) and hasattr(module, '__file__'):
                f = module.__file__
                if f == _filesbymodname.get(modname, None):
                    continue
                _filesbymodname[modname] = f
                f = getabsfile(module)
                modulesbyfile[f] = modulesbyfile[os.path.realpath(f)] = module.__name__

        if file in modulesbyfile:
            return sys.modules.get(modulesbyfile[file])
        main = sys.modules['__main__']
        if not hasattr(object, '__name__'):
            return
        if hasattr(main, object.__name__):
            mainobject = getattr(main, object.__name__)
            if mainobject is object:
                return main
        builtin = sys.modules['__builtin__']
        if hasattr(builtin, object.__name__):
            builtinobject = getattr(builtin, object.__name__)
            if builtinobject is object:
                return builtin
        return


def findsource(object):
    file = getfile(object)
    sourcefile = getsourcefile(object)
    if not sourcefile and file[:1] + file[-1:] != '<>':
        raise IOError('source code not available')
    file = sourcefile if sourcefile else file
    module = getmodule(object, file)
    if module:
        lines = linecache.getlines(file, module.__dict__)
    else:
        lines = linecache.getlines(file)
    if not lines:
        raise IOError('could not get source code')
    if ismodule(object):
        return (lines, 0)
    if isclass(object):
        name = object.__name__
        pat = re.compile('^(\\s*)class\\s*' + name + '\\b')
        candidates = []
        for i in range(len(lines)):
            match = pat.match(lines[i])
            if match:
                if lines[i][0] == 'c':
                    return (lines, i)
                candidates.append((match.group(1), i))

        if candidates:
            candidates.sort()
            return (lines, candidates[0][1])
        raise IOError('could not find class definition')
    if ismethod(object):
        object = object.im_func
    if isfunction(object):
        object = object.func_code
    if istraceback(object):
        object = object.tb_frame
    if isframe(object):
        object = object.f_code
    if iscode(object):
        if not hasattr(object, 'co_firstlineno'):
            raise IOError('could not find function definition')
        lnum = object.co_firstlineno - 1
        pat = re.compile('^(\\s*def\\s)|(.*(?<!\\w)lambda(:|\\s))|^(\\s*@)')
        while lnum > 0:
            if pat.match(lines[lnum]):
                break
            lnum = lnum - 1

        return (lines, lnum)
    raise IOError('could not find code object')


def getcomments(object):
    try:
        lines, lnum = findsource(object)
    except (IOError, TypeError):
        return None

    if ismodule(object):
        start = 0
        if lines and lines[0][:2] == '#!':
            start = 1
        while start < len(lines) and string.strip(lines[start]) in ('', '#'):
            start = start + 1

        if start < len(lines) and lines[start][:1] == '#':
            comments = []
            end = start
            while end < len(lines) and lines[end][:1] == '#':
                comments.append(string.expandtabs(lines[end]))
                end = end + 1

            return string.join(comments, '')
    elif lnum > 0:
        indent = indentsize(lines[lnum])
        end = lnum - 1
        if end >= 0 and string.lstrip(lines[end])[:1] == '#' and indentsize(lines[end]) == indent:
            comments = [string.lstrip(string.expandtabs(lines[end]))]
            if end > 0:
                end = end - 1
                comment = string.lstrip(string.expandtabs(lines[end]))
                while comment[:1] == '#' and indentsize(lines[end]) == indent:
                    comments[:0] = [comment]
                    end = end - 1
                    if end < 0:
                        break
                    comment = string.lstrip(string.expandtabs(lines[end]))

            while comments and string.strip(comments[0]) == '#':
                comments[:1] = []

            while comments and string.strip(comments[-1]) == '#':
                comments[-1:] = []

            return string.join(comments, '')
    return None


class EndOfBlock(Exception):
    pass


class BlockFinder:

    def __init__(self):
        self.indent = 0
        self.islambda = False
        self.started = False
        self.passline = False
        self.last = 1

    def tokeneater(self, type, token, srow_scol, erow_ecol, line):
        srow, scol = srow_scol
        erow, ecol = erow_ecol
        if not self.started:
            if token in ('def', 'class', 'lambda'):
                if token == 'lambda':
                    self.islambda = True
                self.started = True
            self.passline = True
        elif type == tokenize.NEWLINE:
            self.passline = False
            self.last = srow
            if self.islambda:
                raise EndOfBlock
        elif self.passline:
            pass
        elif type == tokenize.INDENT:
            self.indent = self.indent + 1
            self.passline = True
        elif type == tokenize.DEDENT:
            self.indent = self.indent - 1
            if self.indent <= 0:
                raise EndOfBlock
        elif self.indent == 0 and type not in (tokenize.COMMENT, tokenize.NL):
            raise EndOfBlock


def getblock(lines):
    blockfinder = BlockFinder()
    try:
        tokenize.tokenize(iter(lines).next, blockfinder.tokeneater)
    except (EndOfBlock, IndentationError):
        pass

    return lines[:blockfinder.last]


def getsourcelines(object):
    lines, lnum = findsource(object)
    if istraceback(object):
        object = object.tb_frame
    if ismodule(object) or isframe(object) and object.f_code.co_name == '<module>':
        return (lines, 0)
    else:
        return (getblock(lines[lnum:]), lnum + 1)


def getsource(object):
    lines, lnum = getsourcelines(object)
    return string.join(lines, '')


def walktree(classes, children, parent):
    results = []
    classes.sort(key=attrgetter('__module__', '__name__'))
    for c in classes:
        results.append((c, c.__bases__))
        if c in children:
            results.append(walktree(children[c], children, c))

    return results


def getclasstree(classes, unique=0):
    children = {}
    roots = []
    for c in classes:
        if c.__bases__:
            for parent in c.__bases__:
                if parent not in children:
                    children[parent] = []
                if c not in children[parent]:
                    children[parent].append(c)
                if unique and parent in classes:
                    break

        if c not in roots:
            roots.append(c)

    for parent in children:
        if parent not in classes:
            roots.append(parent)

    return walktree(roots, children, None)


Arguments = namedtuple('Arguments', 'args varargs keywords')

def getargs(co):
    if not iscode(co):
        raise TypeError('{!r} is not a code object'.format(co))
    nargs = co.co_argcount
    names = co.co_varnames
    args = list(names[:nargs])
    step = 0
    for i in range(nargs):
        if args[i][:1] in ('', '.'):
            stack, remain, count = [], [], []
            while step < len(co.co_code):
                op = ord(co.co_code[step])
                step = step + 1
                if op >= dis.HAVE_ARGUMENT:
                    opname = dis.opname[op]
                    value = ord(co.co_code[step]) + ord(co.co_code[step + 1]) * 256
                    step = step + 2
                    if opname in ('UNPACK_TUPLE', 'UNPACK_SEQUENCE'):
                        remain.append(value)
                        count.append(value)
                    elif opname in ('STORE_FAST', 'STORE_DEREF'):
                        if opname == 'STORE_FAST':
                            stack.append(names[value])
                        else:
                            stack.append(co.co_cellvars[value])
                        if not remain:
                            stack[0] = [stack[0]]
                            break
                        else:
                            remain[-1] = remain[-1] - 1
                            while remain[-1] == 0:
                                remain.pop()
                                size = count.pop()
                                stack[-size:] = [stack[-size:]]
                                if not remain:
                                    break
                                remain[-1] = remain[-1] - 1

                            if not remain:
                                break

            args[i] = stack[0]

    varargs = None
    if co.co_flags & CO_VARARGS:
        varargs = co.co_varnames[nargs]
        nargs = nargs + 1
    varkw = None
    if co.co_flags & CO_VARKEYWORDS:
        varkw = co.co_varnames[nargs]
    return Arguments(args, varargs, varkw)


ArgSpec = namedtuple('ArgSpec', 'args varargs keywords defaults')

def getargspec(func):
    if ismethod(func):
        func = func.im_func
    if not isfunction(func):
        raise TypeError('{!r} is not a Python function'.format(func))
    args, varargs, varkw = getargs(func.func_code)
    return ArgSpec(args, varargs, varkw, func.func_defaults)


ArgInfo = namedtuple('ArgInfo', 'args varargs keywords locals')

def getargvalues(frame):
    args, varargs, varkw = getargs(frame.f_code)
    return ArgInfo(args, varargs, varkw, frame.f_locals)


def joinseq(seq):
    if len(seq) == 1:
        return '(' + seq[0] + ',)'
    else:
        return '(' + string.join(seq, ', ') + ')'


def strseq(object, convert, join=joinseq):
    if type(object) in (list, tuple):
        return join(map(lambda o, c=convert, j=join: strseq(o, c, j), object))
    else:
        return convert(object)


def formatargspec(args, varargs=None, varkw=None, defaults=None, formatarg=str, formatvarargs=lambda name: '*' + name, formatvarkw=lambda name: '**' + name, formatvalue=lambda value: '=' + repr(value), join=joinseq):
    specs = []
    if defaults:
        firstdefault = len(args) - len(defaults)
    for i, arg in enumerate(args):
        spec = strseq(arg, formatarg, join)
        if defaults and i >= firstdefault:
            spec = spec + formatvalue(defaults[i - firstdefault])
        specs.append(spec)

    if varargs is not None:
        specs.append(formatvarargs(varargs))
    if varkw is not None:
        specs.append(formatvarkw(varkw))
    return '(' + string.join(specs, ', ') + ')'


def formatargvalues(args, varargs, varkw, locals, formatarg=str, formatvarargs=lambda name: '*' + name, formatvarkw=lambda name: '**' + name, formatvalue=lambda value: '=' + repr(value), join=joinseq):

    def convert(name, locals=locals, formatarg=formatarg, formatvalue=formatvalue):
        return formatarg(name) + formatvalue(locals[name])

    specs = []
    for i in range(len(args)):
        specs.append(strseq(args[i], convert, join))

    if varargs:
        specs.append(formatvarargs(varargs) + formatvalue(locals[varargs]))
    if varkw:
        specs.append(formatvarkw(varkw) + formatvalue(locals[varkw]))
    return '(' + string.join(specs, ', ') + ')'


def getcallargs(func, *positional, **named):
    args, varargs, varkw, defaults = getargspec(func)
    f_name = func.__name__
    arg2value = {}
    assigned_tuple_params = []

    def assign(arg, value):
        if isinstance(arg, str):
            arg2value[arg] = value
        else:
            assigned_tuple_params.append(arg)
            value = iter(value)
            for i, subarg in enumerate(arg):
                try:
                    subvalue = next(value)
                except StopIteration:
                    raise ValueError('need more than %d %s to unpack' % (i, 'values' if i > 1 else 'value'))

                assign(subarg, subvalue)

            try:
                next(value)
            except StopIteration:
                pass
            else:
                raise ValueError('too many values to unpack')

    def is_assigned(arg):
        return arg in arg2value if isinstance(arg, str) else arg in assigned_tuple_params

    if ismethod(func) and func.im_self is not None:
        positional = (func.im_self,) + positional
    num_pos = len(positional)
    num_total = num_pos + len(named)
    num_args = len(args)
    num_defaults = len(defaults) if defaults else 0
    for arg, value in zip(args, positional):
        assign(arg, value)

    if varargs:
        if num_pos > num_args:
            assign(varargs, positional[-(num_pos - num_args):])
        else:
            assign(varargs, ())
    elif 0 < num_args < num_pos:
        raise TypeError('%s() takes %s %d %s (%d given)' % (f_name,
         'at most' if defaults else 'exactly',
         num_args,
         'arguments' if num_args > 1 else 'argument',
         num_total))
    elif num_args == 0 and num_total:
        if varkw:
            if num_pos:
                raise TypeError('%s() takes exactly 0 arguments (%d given)' % (f_name, num_total))
        else:
            raise TypeError('%s() takes no arguments (%d given)' % (f_name, num_total))
    for arg in args:
        if isinstance(arg, str) and arg in named:
            if is_assigned(arg):
                raise TypeError("%s() got multiple values for keyword argument '%s'" % (f_name, arg))
            else:
                assign(arg, named.pop(arg))

    if defaults:
        for arg, value in zip(args[-num_defaults:], defaults):
            if not is_assigned(arg):
                assign(arg, value)

    if varkw:
        assign(varkw, named)
    elif named:
        unexpected = next(iter(named))
        try:
            unicode
        except NameError:
            pass
        else:
            if isinstance(unexpected, unicode):
                unexpected = unexpected.encode(sys.getdefaultencoding(), 'replace')

        raise TypeError("%s() got an unexpected keyword argument '%s'" % (f_name, unexpected))
    unassigned = num_args - len([ arg for arg in args if is_assigned(arg) ])
    if unassigned:
        num_required = num_args - num_defaults
        raise TypeError('%s() takes %s %d %s (%d given)' % (f_name,
         'at least' if defaults else 'exactly',
         num_required,
         'arguments' if num_required > 1 else 'argument',
         num_total))
    return arg2value


Traceback = namedtuple('Traceback', 'filename lineno function code_context index')

def getframeinfo(frame, context=1):
    if istraceback(frame):
        lineno = frame.tb_lineno
        frame = frame.tb_frame
    else:
        lineno = frame.f_lineno
    if not isframe(frame):
        raise TypeError('{!r} is not a frame or traceback object'.format(frame))
    filename = getsourcefile(frame) or getfile(frame)
    if context > 0:
        start = lineno - 1 - context // 2
        try:
            lines, lnum = findsource(frame)
        except IOError:
            lines = index = None
        else:
            start = max(start, 1)
            start = max(0, min(start, len(lines) - context))
            lines = lines[start:start + context]
            index = lineno - 1 - start

    else:
        lines = index = None
    return Traceback(filename, lineno, frame.f_code.co_name, lines, index)


def getlineno(frame):
    return frame.f_lineno


def getouterframes(frame, context=1):
    framelist = []
    while frame:
        framelist.append((frame,) + getframeinfo(frame, context))
        frame = frame.f_back

    return framelist


def getinnerframes(tb, context=1):
    framelist = []
    while tb:
        framelist.append((tb.tb_frame,) + getframeinfo(tb, context))
        tb = tb.tb_next

    return framelist


if hasattr(sys, '_getframe'):
    currentframe = sys._getframe
else:
    currentframe = lambda _=None: None

def stack(context=1):
    return getouterframes(sys._getframe(1), context)


def trace(context=1):
    return getinnerframes(sys.exc_info()[2], context)
