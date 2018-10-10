# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/cgitb.py
import inspect
import keyword
import linecache
import os
import pydoc
import sys
import tempfile
import time
import tokenize
import traceback
import types

def reset():
    pass


__UNDEF__ = []

def small(text):
    if text:
        return '<small>' + text + '</small>'
    else:
        return ''


def strong(text):
    if text:
        return '<strong>' + text + '</strong>'
    else:
        return ''


def grey(text):
    if text:
        return '<font color="#909090">' + text + '</font>'
    else:
        return ''


def lookup(name, frame, locals):
    if name in locals:
        return ('local', locals[name])
    elif name in frame.f_globals:
        return ('global', frame.f_globals[name])
    else:
        if '__builtins__' in frame.f_globals:
            builtins = frame.f_globals['__builtins__']
            if type(builtins) is type({}):
                if name in builtins:
                    return ('builtin', builtins[name])
            elif hasattr(builtins, name):
                return ('builtin', getattr(builtins, name))
        return (None, __UNDEF__)


def scanvars(reader, frame, locals):
    vars, lasttoken, parent, prefix, value = ([],
     None,
     None,
     '',
     __UNDEF__)
    for ttype, token, start, end, line in tokenize.generate_tokens(reader):
        if ttype == tokenize.NEWLINE:
            break
        if ttype == tokenize.NAME and token not in keyword.kwlist:
            if lasttoken == '.':
                if parent is not __UNDEF__:
                    value = getattr(parent, token, __UNDEF__)
                    vars.append((prefix + token, prefix, value))
            else:
                where, value = lookup(token, frame, locals)
                vars.append((token, where, value))
        elif token == '.':
            prefix += lasttoken + '.'
            parent = value
        else:
            parent, prefix = (None, '')
        lasttoken = token

    return vars


def html(einfo, context=5):
    etype, evalue, etb = einfo
    if type(etype) is types.ClassType:
        etype = etype.__name__
    pyver = 'Python ' + sys.version.split()[0] + ': ' + sys.executable
    date = time.ctime(time.time())
    head = '<body bgcolor="#f0f0f8">' + pydoc.html.heading('<big><big>%s</big></big>' % strong(pydoc.html.escape(str(etype))), '#ffffff', '#6622aa', pyver + '<br>' + date) + '\n<p>A problem occurred in a Python script.  Here is the sequence of\nfunction calls leading up to the error, in the order they occurred.</p>'
    indent = '<tt>' + small('&nbsp;' * 5) + '&nbsp;</tt>'
    frames = []
    records = inspect.getinnerframes(etb, context)
    for frame, file, lnum, func, lines, index in records:
        if file:
            file = os.path.abspath(file)
            link = '<a href="file://%s">%s</a>' % (file, pydoc.html.escape(file))
        else:
            file = link = '?'
        args, varargs, varkw, locals = inspect.getargvalues(frame)
        call = ''
        if func != '?':
            call = 'in ' + strong(func) + inspect.formatargvalues(args, varargs, varkw, locals, formatvalue=lambda value: '=' + pydoc.html.repr(value))
        highlight = {}

        def reader(lnum=[lnum]):
            highlight[lnum[0]] = 1
            try:
                return linecache.getline(file, lnum[0])
            finally:
                lnum[0] += 1

        vars = scanvars(reader, frame, locals)
        rows = ['<tr><td bgcolor="#d8bbff">%s%s %s</td></tr>' % ('<big>&nbsp;</big>', link, call)]
        if index is not None:
            i = lnum - index
            for line in lines:
                num = small('&nbsp;' * (5 - len(str(i))) + str(i)) + '&nbsp;'
                if i in highlight:
                    line = '<tt>=&gt;%s%s</tt>' % (num, pydoc.html.preformat(line))
                    rows.append('<tr><td bgcolor="#ffccee">%s</td></tr>' % line)
                else:
                    line = '<tt>&nbsp;&nbsp;%s%s</tt>' % (num, pydoc.html.preformat(line))
                    rows.append('<tr><td>%s</td></tr>' % grey(line))
                i += 1

        done, dump = {}, []
        for name, where, value in vars:
            if name in done:
                continue
            done[name] = 1
            if value is not __UNDEF__:
                if where in ('global', 'builtin'):
                    name = '<em>%s</em> ' % where + strong(name)
                elif where == 'local':
                    name = strong(name)
                else:
                    name = where + strong(name.split('.')[-1])
                dump.append('%s&nbsp;= %s' % (name, pydoc.html.repr(value)))
            dump.append(name + ' <em>undefined</em>')

        rows.append('<tr><td>%s</td></tr>' % small(grey(', '.join(dump))))
        frames.append('\n<table width="100%%" cellspacing=0 cellpadding=0 border=0>\n%s</table>' % '\n'.join(rows))

    exception = ['<p>%s: %s' % (strong(pydoc.html.escape(str(etype))), pydoc.html.escape(str(evalue)))]
    if isinstance(evalue, BaseException):
        for name in dir(evalue):
            if name[:1] == '_':
                continue
            value = pydoc.html.repr(getattr(evalue, name))
            exception.append('\n<br>%s%s&nbsp;=\n%s' % (indent, name, value))

    return head + ''.join(frames) + ''.join(exception) + "\n\n\n<!-- The above is a description of an error in a Python program, formatted\n     for a Web browser because the 'cgitb' module was enabled.  In case you\n     are not reading this in a Web browser, here is the original traceback:\n\n%s\n-->\n" % pydoc.html.escape(''.join(traceback.format_exception(etype, evalue, etb)))


def text(einfo, context=5):
    etype, evalue, etb = einfo
    if type(etype) is types.ClassType:
        etype = etype.__name__
    pyver = 'Python ' + sys.version.split()[0] + ': ' + sys.executable
    date = time.ctime(time.time())
    head = '%s\n%s\n%s\n' % (str(etype), pyver, date) + '\nA problem occurred in a Python script.  Here is the sequence of\nfunction calls leading up to the error, in the order they occurred.\n'
    frames = []
    records = inspect.getinnerframes(etb, context)
    for frame, file, lnum, func, lines, index in records:
        file = file and os.path.abspath(file) or '?'
        args, varargs, varkw, locals = inspect.getargvalues(frame)
        call = ''
        if func != '?':
            call = 'in ' + func + inspect.formatargvalues(args, varargs, varkw, locals, formatvalue=lambda value: '=' + pydoc.text.repr(value))
        highlight = {}

        def reader(lnum=[lnum]):
            highlight[lnum[0]] = 1
            try:
                return linecache.getline(file, lnum[0])
            finally:
                lnum[0] += 1

        vars = scanvars(reader, frame, locals)
        rows = [' %s %s' % (file, call)]
        if index is not None:
            i = lnum - index
            for line in lines:
                num = '%5d ' % i
                rows.append(num + line.rstrip())
                i += 1

        done, dump = {}, []
        for name, where, value in vars:
            if name in done:
                continue
            done[name] = 1
            if value is not __UNDEF__:
                if where == 'global':
                    name = 'global ' + name
                elif where != 'local':
                    name = where + name.split('.')[-1]
                dump.append('%s = %s' % (name, pydoc.text.repr(value)))
            dump.append(name + ' undefined')

        rows.append('\n'.join(dump))
        frames.append('\n%s\n' % '\n'.join(rows))

    exception = ['%s: %s' % (str(etype), str(evalue))]
    if isinstance(evalue, BaseException):
        for name in dir(evalue):
            value = pydoc.text.repr(getattr(evalue, name))
            exception.append('\n%s%s = %s' % ('    ', name, value))

    return head + ''.join(frames) + ''.join(exception) + '\n\nThe above is a description of an error in a Python program.  Here is\nthe original traceback:\n\n%s\n' % ''.join(traceback.format_exception(etype, evalue, etb))


class Hook:

    def __init__(self, display=1, logdir=None, context=5, file=None, format='html'):
        self.display = display
        self.logdir = logdir
        self.context = context
        self.file = file or sys.stdout
        self.format = format

    def __call__(self, etype, evalue, etb):
        self.handle((etype, evalue, etb))

    def handle(self, info=None):
        info = info or sys.exc_info()
        if self.format == 'html':
            self.file.write(reset())
        formatter = self.format == 'html' and html or text
        plain = False
        try:
            doc = formatter(info, self.context)
        except:
            doc = ''.join(traceback.format_exception(*info))
            plain = True

        if self.display:
            if plain:
                doc = doc.replace('&', '&amp;').replace('<', '&lt;')
                self.file.write('<pre>' + doc + '</pre>\n')
            else:
                self.file.write(doc + '\n')
        else:
            self.file.write('<p>A problem occurred in a Python script.\n')
        if self.logdir is not None:
            suffix = ['.txt', '.html'][self.format == 'html']
            fd, path = tempfile.mkstemp(suffix=suffix, dir=self.logdir)
            try:
                file = os.fdopen(fd, 'w')
                file.write(doc)
                file.close()
                msg = '%s contains the description of this error.' % path
            except:
                msg = 'Tried to save traceback to %s, but failed.' % path

            if self.format == 'html':
                self.file.write('<p>%s</p>\n' % msg)
            else:
                self.file.write(msg + '\n')
        try:
            self.file.flush()
        except:
            pass

        return


handler = Hook().handle

def enable(display=1, logdir=None, context=5, format='html'):
    sys.excepthook = Hook(display=display, logdir=logdir, context=context, format=format)
