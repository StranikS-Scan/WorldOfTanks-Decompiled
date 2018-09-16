# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/cProfile.py
__all__ = ['run',
 'runctx',
 'help',
 'Profile']
import _lsprof

def run(statement, filename=None, sort=-1):
    prof = Profile()
    result = None
    try:
        try:
            prof = prof.run(statement)
        except SystemExit:
            pass

    finally:
        if filename is not None:
            prof.dump_stats(filename)
        else:
            result = prof.print_stats(sort)

    return result


def runctx(statement, globals, locals, filename=None, sort=-1):
    prof = Profile()
    result = None
    try:
        try:
            prof = prof.runctx(statement, globals, locals)
        except SystemExit:
            pass

    finally:
        if filename is not None:
            prof.dump_stats(filename)
        else:
            result = prof.print_stats(sort)

    return result


def help():
    print 'Documentation for the profile/cProfile modules can be found '
    print "in the Python Library Reference, section 'The Python Profiler'."


class Profile(_lsprof.Profiler):

    def print_stats(self, sort=-1):
        import pstats
        pstats.Stats(self).strip_dirs().sort_stats(sort).print_stats()

    def dump_stats(self, file):
        import marshal
        f = open(file, 'wb')
        self.create_stats()
        marshal.dump(self.stats, f)
        f.close()

    def create_stats(self):
        self.disable()
        self.snapshot_stats()

    def snapshot_stats(self):
        entries = self.getstats()
        self.stats = {}
        callersdicts = {}
        for entry in entries:
            func = label(entry.code)
            nc = entry.callcount
            cc = nc - entry.reccallcount
            tt = entry.inlinetime
            ct = entry.totaltime
            callers = {}
            callersdicts[id(entry.code)] = callers
            self.stats[func] = (cc,
             nc,
             tt,
             ct,
             callers)

        for entry in entries:
            if entry.calls:
                func = label(entry.code)
                for subentry in entry.calls:
                    try:
                        callers = callersdicts[id(subentry.code)]
                    except KeyError:
                        continue

                    nc = subentry.callcount
                    cc = nc - subentry.reccallcount
                    tt = subentry.inlinetime
                    ct = subentry.totaltime
                    if func in callers:
                        prev = callers[func]
                        nc += prev[0]
                        cc += prev[1]
                        tt += prev[2]
                        ct += prev[3]
                    callers[func] = (nc,
                     cc,
                     tt,
                     ct)

    def run(self, cmd):
        import __main__
        dict = __main__.__dict__
        return self.runctx(cmd, dict, dict)

    def runctx(self, cmd, globals, locals):
        self.enable()
        try:
            exec cmd in globals, locals
        finally:
            self.disable()

        return self

    def runcall(self, func, *args, **kw):
        self.enable()
        try:
            return func(*args, **kw)
        finally:
            self.disable()


def label(code):
    if isinstance(code, str):
        return ('~', 0, code)
    else:
        return (code.co_filename, code.co_firstlineno, code.co_name)


def main():
    import os, sys
    from optparse import OptionParser
    usage = 'cProfile.py [-o output_file_path] [-s sort] scriptfile [arg] ...'
    parser = OptionParser(usage=usage)
    parser.allow_interspersed_args = False
    parser.add_option('-o', '--outfile', dest='outfile', help='Save stats to <outfile>', default=None)
    parser.add_option('-s', '--sort', dest='sort', help='Sort order when printing to stdout, based on pstats.Stats class', default=-1)
    if not sys.argv[1:]:
        parser.print_usage()
        sys.exit(2)
    options, args = parser.parse_args()
    sys.argv[:] = args
    if len(args) > 0:
        progname = args[0]
        sys.path.insert(0, os.path.dirname(progname))
        with open(progname, 'rb') as fp:
            code = compile(fp.read(), progname, 'exec')
        globs = {'__file__': progname,
         '__name__': '__main__',
         '__package__': None}
        runctx(code, globs, None, options.outfile, options.sort)
    else:
        parser.print_usage()
    return parser


if __name__ == '__main__':
    main()
