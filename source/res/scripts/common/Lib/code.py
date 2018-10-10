# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/code.py
import sys
import traceback
from codeop import CommandCompiler, compile_command
__all__ = ['InteractiveInterpreter',
 'InteractiveConsole',
 'interact',
 'compile_command']

def softspace(file, newvalue):
    oldvalue = 0
    try:
        oldvalue = file.softspace
    except AttributeError:
        pass

    try:
        file.softspace = newvalue
    except (AttributeError, TypeError):
        pass

    return oldvalue


class InteractiveInterpreter:

    def __init__(self, locals=None):
        if locals is None:
            locals = {'__name__': '__console__',
             '__doc__': None}
        self.locals = locals
        self.compile = CommandCompiler()
        return

    def runsource(self, source, filename='<input>', symbol='single'):
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            self.showsyntaxerror(filename)
            return False

        if code is None:
            return True
        else:
            self.runcode(code)
            return False

    def runcode(self, code):
        try:
            exec code in self.locals
        except SystemExit:
            raise
        except:
            self.showtraceback()
        else:
            if softspace(sys.stdout, 0):
                print

    def showsyntaxerror(self, filename=None):
        type, value, sys.last_traceback = sys.exc_info()
        sys.last_type = type
        sys.last_value = value
        if filename and type is SyntaxError:
            try:
                msg, (dummy_filename, lineno, offset, line) = value
            except:
                pass
            else:
                value = SyntaxError(msg, (filename,
                 lineno,
                 offset,
                 line))
                sys.last_value = value

        list = traceback.format_exception_only(type, value)
        map(self.write, list)

    def showtraceback(self):
        try:
            type, value, tb = sys.exc_info()
            sys.last_type = type
            sys.last_value = value
            sys.last_traceback = tb
            tblist = traceback.extract_tb(tb)
            del tblist[:1]
            list = traceback.format_list(tblist)
            if list:
                list.insert(0, 'Traceback (most recent call last):\n')
            list[len(list):] = traceback.format_exception_only(type, value)
        finally:
            tblist = tb = None

        map(self.write, list)
        return

    def write(self, data):
        sys.stderr.write(data)


class InteractiveConsole(InteractiveInterpreter):

    def __init__(self, locals=None, filename='<console>'):
        InteractiveInterpreter.__init__(self, locals)
        self.filename = filename
        self.resetbuffer()

    def resetbuffer(self):
        self.buffer = []

    def interact(self, banner=None):
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = '>>> '

        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = '... '

        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
        if banner is None:
            self.write('Python %s on %s\n%s\n(%s)\n' % (sys.version,
             sys.platform,
             cprt,
             self.__class__.__name__))
        else:
            self.write('%s\n' % str(banner))
        more = 0
        while 1:
            try:
                if more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = self.raw_input(prompt)
                    encoding = getattr(sys.stdin, 'encoding', None)
                    if encoding and not isinstance(line, unicode):
                        line = line.decode(encoding)
                except EOFError:
                    self.write('\n')
                    break
                else:
                    more = self.push(line)

            except KeyboardInterrupt:
                self.write('\nKeyboardInterrupt\n')
                self.resetbuffer()
                more = 0

        return

    def push(self, line):
        self.buffer.append(line)
        source = '\n'.join(self.buffer)
        more = self.runsource(source, self.filename)
        if not more:
            self.resetbuffer()
        return more

    def raw_input(self, prompt=''):
        return raw_input(prompt)


def interact(banner=None, readfunc=None, local=None):
    console = InteractiveConsole(local)
    if readfunc is not None:
        console.raw_input = readfunc
    else:
        try:
            import readline
        except ImportError:
            pass

    console.interact(banner)
    return


if __name__ == '__main__':
    interact()
