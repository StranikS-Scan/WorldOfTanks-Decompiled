# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/getopt.py
__all__ = ['GetoptError',
 'error',
 'getopt',
 'gnu_getopt']
import os

class GetoptError(Exception):
    opt = ''
    msg = ''

    def __init__(self, msg, opt=''):
        self.msg = msg
        self.opt = opt
        Exception.__init__(self, msg, opt)

    def __str__(self):
        return self.msg


error = GetoptError

def getopt(args, shortopts, longopts=[]):
    opts = []
    if type(longopts) == type(''):
        longopts = [longopts]
    else:
        longopts = list(longopts)
    while args and args[0].startswith('-') and args[0] != '-':
        if args[0] == '--':
            args = args[1:]
            break
        if args[0].startswith('--'):
            opts, args = do_longs(opts, args[0][2:], longopts, args[1:])
        opts, args = do_shorts(opts, args[0][1:], shortopts, args[1:])

    return (opts, args)


def gnu_getopt(args, shortopts, longopts=[]):
    opts = []
    prog_args = []
    if isinstance(longopts, str):
        longopts = [longopts]
    else:
        longopts = list(longopts)
    if shortopts.startswith('+'):
        shortopts = shortopts[1:]
        all_options_first = True
    elif os.environ.get('POSIXLY_CORRECT'):
        all_options_first = True
    else:
        all_options_first = False
    while args:
        if args[0] == '--':
            prog_args += args[1:]
            break
        if args[0][:2] == '--':
            opts, args = do_longs(opts, args[0][2:], longopts, args[1:])
        if args[0][:1] == '-' and args[0] != '-':
            opts, args = do_shorts(opts, args[0][1:], shortopts, args[1:])
        if all_options_first:
            prog_args += args
            break
        prog_args.append(args[0])
        args = args[1:]

    return (opts, prog_args)


def do_longs(opts, opt, longopts, args):
    try:
        i = opt.index('=')
    except ValueError:
        optarg = None
    else:
        opt, optarg = opt[:i], opt[i + 1:]

    has_arg, opt = long_has_args(opt, longopts)
    if has_arg:
        if optarg is None:
            if not args:
                raise GetoptError('option --%s requires argument' % opt, opt)
            optarg, args = args[0], args[1:]
    elif optarg is not None:
        raise GetoptError('option --%s must not have an argument' % opt, opt)
    opts.append(('--' + opt, optarg or ''))
    return (opts, args)


def long_has_args(opt, longopts):
    possibilities = [ o for o in longopts if o.startswith(opt) ]
    if not possibilities:
        raise GetoptError('option --%s not recognized' % opt, opt)
    if opt in possibilities:
        return (False, opt)
    if opt + '=' in possibilities:
        return (True, opt)
    if len(possibilities) > 1:
        raise GetoptError('option --%s not a unique prefix' % opt, opt)
    unique_match = possibilities[0]
    has_arg = unique_match.endswith('=')
    if has_arg:
        unique_match = unique_match[:-1]
    return (has_arg, unique_match)


def do_shorts(opts, optstring, shortopts, args):
    while optstring != '':
        opt, optstring = optstring[0], optstring[1:]
        if short_has_arg(opt, shortopts):
            if optstring == '':
                if not args:
                    raise GetoptError('option -%s requires argument' % opt, opt)
                optstring, args = args[0], args[1:]
            optarg, optstring = optstring, ''
        else:
            optarg = ''
        opts.append(('-' + opt, optarg))

    return (opts, args)


def short_has_arg(opt, shortopts):
    for i in range(len(shortopts)):
        if opt == shortopts[i] != ':':
            return shortopts.startswith(':', i + 1)

    raise GetoptError('option -%s not recognized' % opt, opt)


if __name__ == '__main__':
    import sys
    print getopt(sys.argv[1:], 'a:b', ['alpha=', 'beta'])
