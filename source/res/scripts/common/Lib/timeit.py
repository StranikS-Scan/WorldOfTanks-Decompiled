# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/timeit.py
import gc
import sys
import time
try:
    import itertools
except ImportError:
    itertools = None

__all__ = ['Timer']
dummy_src_name = '<timeit-src>'
default_number = 1000000
default_repeat = 3
if sys.platform == 'win32':
    default_timer = time.clock
else:
    default_timer = time.time
template = '\ndef inner(_it, _timer):\n    %(setup)s\n    _t0 = _timer()\n    for _i in _it:\n        %(stmt)s\n    _t1 = _timer()\n    return _t1 - _t0\n'

def reindent(src, indent):
    return src.replace('\n', '\n' + ' ' * indent)


def _template_func(setup, func):

    def inner(_it, _timer, _func=func):
        setup()
        _t0 = _timer()
        for _i in _it:
            _func()

        _t1 = _timer()
        return _t1 - _t0

    return inner


class Timer:

    def __init__(self, stmt='pass', setup='pass', timer=default_timer):
        self.timer = timer
        ns = {}
        if isinstance(stmt, basestring):
            stmt = reindent(stmt, 8)
            if isinstance(setup, basestring):
                setup = reindent(setup, 4)
                src = template % {'stmt': stmt,
                 'setup': setup}
            elif hasattr(setup, '__call__'):
                src = template % {'stmt': stmt,
                 'setup': '_setup()'}
                ns['_setup'] = setup
            else:
                raise ValueError('setup is neither a string nor callable')
            self.src = src
            code = compile(src, dummy_src_name, 'exec')
            exec code in globals(), ns
            self.inner = ns['inner']
        elif hasattr(stmt, '__call__'):
            self.src = None
            if isinstance(setup, basestring):
                _setup = setup

                def setup():
                    exec _setup in globals(), ns

            elif not hasattr(setup, '__call__'):
                raise ValueError('setup is neither a string nor callable')
            self.inner = _template_func(setup, stmt)
        else:
            raise ValueError('stmt is neither a string nor callable')
        return

    def print_exc(self, file=None):
        import linecache, traceback
        if self.src is not None:
            linecache.cache[dummy_src_name] = (len(self.src),
             None,
             self.src.split('\n'),
             dummy_src_name)
        traceback.print_exc(file=file)
        return

    def timeit(self, number=default_number):
        if itertools:
            it = itertools.repeat(None, number)
        else:
            it = [None] * number
        gcold = gc.isenabled()
        gc.disable()
        try:
            timing = self.inner(it, self.timer)
        finally:
            if gcold:
                gc.enable()

        return timing

    def repeat(self, repeat=default_repeat, number=default_number):
        r = []
        for i in range(repeat):
            t = self.timeit(number)
            r.append(t)

        return r


def timeit(stmt='pass', setup='pass', timer=default_timer, number=default_number):
    return Timer(stmt, setup, timer).timeit(number)


def repeat(stmt='pass', setup='pass', timer=default_timer, repeat=default_repeat, number=default_number):
    return Timer(stmt, setup, timer).repeat(repeat, number)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    import getopt
    try:
        opts, args = getopt.getopt(args, 'n:s:r:tcvh', ['number=',
         'setup=',
         'repeat=',
         'time',
         'clock',
         'verbose',
         'help'])
    except getopt.error as err:
        print err
        print 'use -h/--help for command line help'
        return 2

    timer = default_timer
    stmt = '\n'.join(args) or 'pass'
    number = 0
    setup = []
    repeat = default_repeat
    verbose = 0
    precision = 3
    for o, a in opts:
        if o in ('-n', '--number'):
            number = int(a)
        if o in ('-s', '--setup'):
            setup.append(a)
        if o in ('-r', '--repeat'):
            repeat = int(a)
            if repeat <= 0:
                repeat = 1
        if o in ('-t', '--time'):
            timer = time.time
        if o in ('-c', '--clock'):
            timer = time.clock
        if o in ('-v', '--verbose'):
            if verbose:
                precision += 1
            verbose += 1
        if o in ('-h', '--help'):
            print __doc__,
            return 0

    setup = '\n'.join(setup) or 'pass'
    import os
    sys.path.insert(0, os.curdir)
    t = Timer(stmt, setup, timer)
    if number == 0:
        for i in range(1, 10):
            number = 10 ** i
            try:
                x = t.timeit(number)
            except:
                t.print_exc()
                return 1

            if verbose:
                print '%d loops -> %.*g secs' % (number, precision, x)
            if x >= 0.2:
                break

    try:
        r = t.repeat(repeat, number)
    except:
        t.print_exc()
        return 1

    best = min(r)
    if verbose:
        print 'raw times:', ' '.join([ '%.*g' % (precision, x) for x in r ])
    print '%d loops,' % number,
    usec = best * 1000000.0 / number
    if usec < 1000:
        print 'best of %d: %.*g usec per loop' % (repeat, precision, usec)
    else:
        msec = usec / 1000
        if msec < 1000:
            print 'best of %d: %.*g msec per loop' % (repeat, precision, msec)
        else:
            sec = msec / 1000
            print 'best of %d: %.*g sec per loop' % (repeat, precision, sec)
    return


if __name__ == '__main__':
    sys.exit(main())
