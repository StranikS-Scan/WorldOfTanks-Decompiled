# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/getpass.py
import os, sys, warnings
__all__ = ['getpass', 'getuser', 'GetPassWarning']

class GetPassWarning(UserWarning):
    pass


def unix_getpass(prompt='Password: ', stream=None):
    fd = None
    tty = None
    try:
        fd = os.open('/dev/tty', os.O_RDWR | os.O_NOCTTY)
        tty = os.fdopen(fd, 'w+', 1)
        input = tty
        if not stream:
            stream = tty
    except EnvironmentError as e:
        try:
            fd = sys.stdin.fileno()
        except (AttributeError, ValueError):
            passwd = fallback_getpass(prompt, stream)

        input = sys.stdin
        if not stream:
            stream = sys.stderr

    if fd is not None:
        passwd = None
        try:
            old = termios.tcgetattr(fd)
            new = old[:]
            new[3] &= ~termios.ECHO
            tcsetattr_flags = termios.TCSAFLUSH
            if hasattr(termios, 'TCSASOFT'):
                tcsetattr_flags |= termios.TCSASOFT
            try:
                termios.tcsetattr(fd, tcsetattr_flags, new)
                passwd = _raw_input(prompt, stream, input=input)
            finally:
                termios.tcsetattr(fd, tcsetattr_flags, old)
                stream.flush()

        except termios.error as e:
            if passwd is not None:
                raise
            del input
            del tty
            passwd = fallback_getpass(prompt, stream)

    stream.write('\n')
    return passwd


def win_getpass(prompt='Password: ', stream=None):
    if sys.stdin is not sys.__stdin__:
        return fallback_getpass(prompt, stream)
    import msvcrt
    for c in prompt:
        msvcrt.putch(c)

    pw = ''
    while 1:
        c = msvcrt.getch()
        if c == '\r' or c == '\n':
            break
        if c == '\x03':
            raise KeyboardInterrupt
        if c == '\x08':
            pw = pw[:-1]
        pw = pw + c

    msvcrt.putch('\r')
    msvcrt.putch('\n')
    return pw


def fallback_getpass(prompt='Password: ', stream=None):
    warnings.warn('Can not control echo on the terminal.', GetPassWarning, stacklevel=2)
    if not stream:
        stream = sys.stderr
    print >> stream, 'Warning: Password input may be echoed.'
    return _raw_input(prompt, stream)


def _raw_input(prompt='', stream=None, input=None):
    if not stream:
        stream = sys.stderr
    if not input:
        input = sys.stdin
    prompt = str(prompt)
    if prompt:
        stream.write(prompt)
        stream.flush()
    line = input.readline()
    if not line:
        raise EOFError
    if line[-1] == '\n':
        line = line[:-1]
    return line


def getuser():
    import os
    for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.environ.get(name)
        if user:
            return user

    import pwd
    return pwd.getpwuid(os.getuid())[0]


try:
    import termios
    (termios.tcgetattr, termios.tcsetattr)
except (ImportError, AttributeError):
    try:
        import msvcrt
    except ImportError:
        try:
            from EasyDialogs import AskPassword
        except ImportError:
            getpass = fallback_getpass
        else:
            getpass = AskPassword

    else:
        getpass = win_getpass

else:
    getpass = unix_getpass
