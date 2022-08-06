# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/idle_test/mock_tk.py


class Event(object):

    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class Var(object):

    def __init__(self, master=None, value=None, name=None):
        self.master = master
        self.value = value
        self.name = name

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


class Mbox_func(object):

    def __init__(self, result=None):
        self.result = result

    def __call__(self, title, message, *args, **kwds):
        self.title = title
        self.message = message
        self.args = args
        self.kwds = kwds
        return self.result


class Mbox(object):
    askokcancel = Mbox_func()
    askquestion = Mbox_func()
    askretrycancel = Mbox_func()
    askyesno = Mbox_func()
    askyesnocancel = Mbox_func()
    showerror = Mbox_func()
    showinfo = Mbox_func()
    showwarning = Mbox_func()


from _tkinter import TclError

class Text(object):

    def __init__(self, master=None, cnf={}, **kw):
        self.data = ['', '\n']

    def index(self, index):
        return '%s.%s' % self._decode(index, endflag=1)

    def _decode(self, index, endflag=0):
        if isinstance(index, (float, bytes)):
            index = str(index)
        try:
            index = index.lower()
        except AttributeError:
            raise TclError('bad text index "%s"' % index)

        lastline = len(self.data) - 1
        if index == 'insert':
            return (lastline, len(self.data[lastline]) - 1)
        if index == 'end':
            return self._endex(endflag)
        line, char = index.split('.')
        line = int(line)
        if line < 1:
            return (1, 0)
        if line > lastline:
            return self._endex(endflag)
        linelength = len(self.data[line]) - 1
        if char.endswith(' lineend') or char == 'end':
            return (line, linelength)
        char = int(char)
        if char < 0:
            char = 0
        elif char > linelength:
            char = linelength
        return (line, char)

    def _endex(self, endflag):
        n = len(self.data)
        if endflag == 1:
            return (n, 0)
        else:
            n -= 1
            return (n, len(self.data[n]) + endflag)

    def insert(self, index, chars):
        if not chars:
            return
        chars = chars.splitlines(True)
        if chars[-1][-1] == '\n':
            chars.append('')
        line, char = self._decode(index, -1)
        before = self.data[line][:char]
        after = self.data[line][char:]
        self.data[line] = before + chars[0]
        self.data[line + 1:line + 1] = chars[1:]
        self.data[line + len(chars) - 1] += after

    def get(self, index1, index2=None):
        startline, startchar = self._decode(index1)
        if index2 is None:
            endline, endchar = startline, startchar + 1
        else:
            endline, endchar = self._decode(index2)
        if startline == endline:
            return self.data[startline][startchar:endchar]
        else:
            lines = [self.data[startline][startchar:]]
            for i in range(startline + 1, endline):
                lines.append(self.data[i])

            lines.append(self.data[endline][:endchar])
            return ''.join(lines)
            return

    def delete(self, index1, index2=None):
        startline, startchar = self._decode(index1, -1)
        if index2 is None:
            if startchar < len(self.data[startline]) - 1:
                endline, endchar = startline, startchar + 1
            elif startline < len(self.data) - 1:
                endline, endchar = startline + 1, 0
            else:
                return
        else:
            endline, endchar = self._decode(index2, -1)
        if startline == endline and startchar < endchar:
            self.data[startline] = self.data[startline][:startchar] + self.data[startline][endchar:]
        elif startline < endline:
            self.data[startline] = self.data[startline][:startchar] + self.data[endline][endchar:]
            startline += 1
            for i in range(startline, endline + 1):
                del self.data[startline]

        return

    def compare(self, index1, op, index2):
        line1, char1 = self._decode(index1)
        line2, char2 = self._decode(index2)
        if op == '<':
            return line1 < line2 or line1 == line2 and char1 < char2
        if op == '<=':
            return line1 < line2 or line1 == line2 and char1 <= char2
        if op == '>':
            return line1 > line2 or line1 == line2 and char1 > char2
        if op == '>=':
            return line1 > line2 or line1 == line2 and char1 >= char2
        if op == '==':
            return line1 == line2 and char1 == char2
        if op == '!=':
            return line1 != line2 or char1 != char2
        raise TclError('bad comparison operator "%s": must be <, <=, ==, >=, >, or !=' % op)

    def mark_set(self, name, index):
        pass

    def mark_unset(self, *markNames):
        pass

    def tag_remove(self, tagName, index1, index2=None):
        pass

    def scan_dragto(self, x, y):
        pass

    def scan_mark(self, x, y):
        pass

    def see(self, index):
        pass

    def bind(sequence=None, func=None, add=None):
        pass
