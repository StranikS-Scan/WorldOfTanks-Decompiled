# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/optparse.py
__version__ = '1.5.3'
__all__ = ['Option',
 'make_option',
 'SUPPRESS_HELP',
 'SUPPRESS_USAGE',
 'Values',
 'OptionContainer',
 'OptionGroup',
 'OptionParser',
 'HelpFormatter',
 'IndentedHelpFormatter',
 'TitledHelpFormatter',
 'OptParseError',
 'OptionError',
 'OptionConflictError',
 'OptionValueError',
 'BadOptionError']
__copyright__ = '\nCopyright (c) 2001-2006 Gregory P. Ward.  All rights reserved.\nCopyright (c) 2002-2006 Python Software Foundation.  All rights reserved.\n\nRedistribution and use in source and binary forms, with or without\nmodification, are permitted provided that the following conditions are\nmet:\n\n  * Redistributions of source code must retain the above copyright\n    notice, this list of conditions and the following disclaimer.\n\n  * Redistributions in binary form must reproduce the above copyright\n    notice, this list of conditions and the following disclaimer in the\n    documentation and/or other materials provided with the distribution.\n\n  * Neither the name of the author nor the names of its\n    contributors may be used to endorse or promote products derived from\n    this software without specific prior written permission.\n\nTHIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS\nIS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED\nTO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A\nPARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR\nCONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,\nEXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,\nPROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR\nPROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF\nLIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING\nNEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS\nSOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.\n'
import sys, os
import types
import textwrap

def _repr(self):
    return '<%s at 0x%x: %s>' % (self.__class__.__name__, id(self), self)


try:
    from gettext import gettext
except ImportError:

    def gettext(message):
        return message


_ = gettext

class OptParseError(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class OptionError(OptParseError):

    def __init__(self, msg, option):
        self.msg = msg
        self.option_id = str(option)

    def __str__(self):
        if self.option_id:
            return 'option %s: %s' % (self.option_id, self.msg)
        else:
            return self.msg


class OptionConflictError(OptionError):
    pass


class OptionValueError(OptParseError):
    pass


class BadOptionError(OptParseError):

    def __init__(self, opt_str):
        self.opt_str = opt_str

    def __str__(self):
        return _('no such option: %s') % self.opt_str


class AmbiguousOptionError(BadOptionError):

    def __init__(self, opt_str, possibilities):
        BadOptionError.__init__(self, opt_str)
        self.possibilities = possibilities

    def __str__(self):
        return _('ambiguous option: %s (%s?)') % (self.opt_str, ', '.join(self.possibilities))


class HelpFormatter():
    NO_DEFAULT_VALUE = 'none'

    def __init__(self, indent_increment, max_help_position, width, short_first):
        self.parser = None
        self.indent_increment = indent_increment
        if width is None:
            try:
                width = int(os.environ['COLUMNS'])
            except (KeyError, ValueError):
                width = 80

            width -= 2
        self.width = width
        self.help_position = self.max_help_position = min(max_help_position, max(width - 20, indent_increment * 2))
        self.current_indent = 0
        self.level = 0
        self.help_width = None
        self.short_first = short_first
        self.default_tag = '%default'
        self.option_strings = {}
        self._short_opt_fmt = '%s %s'
        self._long_opt_fmt = '%s=%s'
        return

    def set_parser(self, parser):
        self.parser = parser

    def set_short_opt_delimiter(self, delim):
        if delim not in ('', ' '):
            raise ValueError('invalid metavar delimiter for short options: %r' % delim)
        self._short_opt_fmt = '%s' + delim + '%s'

    def set_long_opt_delimiter(self, delim):
        if delim not in ('=', ' '):
            raise ValueError('invalid metavar delimiter for long options: %r' % delim)
        self._long_opt_fmt = '%s' + delim + '%s'

    def indent(self):
        self.current_indent += self.indent_increment
        self.level += 1

    def dedent(self):
        self.current_indent -= self.indent_increment
        self.level -= 1

    def format_usage(self, usage):
        raise NotImplementedError, 'subclasses must implement'

    def format_heading(self, heading):
        raise NotImplementedError, 'subclasses must implement'

    def _format_text(self, text):
        text_width = max(self.width - self.current_indent, 11)
        indent = ' ' * self.current_indent
        return textwrap.fill(text, text_width, initial_indent=indent, subsequent_indent=indent)

    def format_description(self, description):
        if description:
            return self._format_text(description) + '\n'
        else:
            return ''

    def format_epilog(self, epilog):
        if epilog:
            return '\n' + self._format_text(epilog) + '\n'
        else:
            return ''

    def expand_default(self, option):
        if self.parser is None or not self.default_tag:
            return option.help
        else:
            default_value = self.parser.defaults.get(option.dest)
            if default_value is NO_DEFAULT or default_value is None:
                default_value = self.NO_DEFAULT_VALUE
            return option.help.replace(self.default_tag, str(default_value))

    def format_option(self, option):
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        if len(opts) > opt_width:
            opts = '%*s%s\n' % (self.current_indent, '', opts)
            indent_first = self.help_position
        else:
            opts = '%*s%-*s  ' % (self.current_indent,
             '',
             opt_width,
             opts)
            indent_first = 0
        result.append(opts)
        if option.help:
            help_text = self.expand_default(option)
            help_lines = textwrap.wrap(help_text, self.help_width)
            result.append('%*s%s\n' % (indent_first, '', help_lines[0]))
            result.extend([ '%*s%s\n' % (self.help_position, '', line) for line in help_lines[1:] ])
        elif opts[-1] != '\n':
            result.append('\n')
        return ''.join(result)

    def store_option_strings(self, parser):
        self.indent()
        max_len = 0
        for opt in parser.option_list:
            strings = self.format_option_strings(opt)
            self.option_strings[opt] = strings
            max_len = max(max_len, len(strings) + self.current_indent)

        self.indent()
        for group in parser.option_groups:
            for opt in group.option_list:
                strings = self.format_option_strings(opt)
                self.option_strings[opt] = strings
                max_len = max(max_len, len(strings) + self.current_indent)

        self.dedent()
        self.dedent()
        self.help_position = min(max_len + 2, self.max_help_position)
        self.help_width = max(self.width - self.help_position, 11)

    def format_option_strings(self, option):
        if option.takes_value():
            metavar = option.metavar or option.dest.upper()
            short_opts = [ self._short_opt_fmt % (sopt, metavar) for sopt in option._short_opts ]
            long_opts = [ self._long_opt_fmt % (lopt, metavar) for lopt in option._long_opts ]
        else:
            short_opts = option._short_opts
            long_opts = option._long_opts
        if self.short_first:
            opts = short_opts + long_opts
        else:
            opts = long_opts + short_opts
        return ', '.join(opts)


class IndentedHelpFormatter(HelpFormatter):

    def __init__(self, indent_increment=2, max_help_position=24, width=None, short_first=1):
        HelpFormatter.__init__(self, indent_increment, max_help_position, width, short_first)

    def format_usage(self, usage):
        return _('Usage: %s\n') % usage

    def format_heading(self, heading):
        return '%*s%s:\n' % (self.current_indent, '', heading)


class TitledHelpFormatter(HelpFormatter):

    def __init__(self, indent_increment=0, max_help_position=24, width=None, short_first=0):
        HelpFormatter.__init__(self, indent_increment, max_help_position, width, short_first)

    def format_usage(self, usage):
        return '%s  %s\n' % (self.format_heading(_('Usage')), usage)

    def format_heading(self, heading):
        return '%s\n%s\n' % (heading, '=-'[self.level] * len(heading))


def _parse_num(val, type):
    if val[:2].lower() == '0x':
        radix = 16
    elif val[:2].lower() == '0b':
        radix = 2
        val = val[2:] or '0'
    elif val[:1] == '0':
        radix = 8
    else:
        radix = 10
    return type(val, radix)


def _parse_int(val):
    return _parse_num(val, int)


def _parse_long(val):
    return _parse_num(val, long)


_builtin_cvt = {'int': (_parse_int, _('integer')),
 'long': (_parse_long, _('long integer')),
 'float': (float, _('floating-point')),
 'complex': (complex, _('complex'))}

def check_builtin(option, opt, value):
    cvt, what = _builtin_cvt[option.type]
    try:
        return cvt(value)
    except ValueError:
        raise OptionValueError(_('option %s: invalid %s value: %r') % (opt, what, value))


def check_choice(option, opt, value):
    if value in option.choices:
        return value
    choices = ', '.join(map(repr, option.choices))
    raise OptionValueError(_('option %s: invalid choice: %r (choose from %s)') % (opt, value, choices))


NO_DEFAULT = ('NO', 'DEFAULT')

class Option():
    ATTRS = ['action',
     'type',
     'dest',
     'default',
     'nargs',
     'const',
     'choices',
     'callback',
     'callback_args',
     'callback_kwargs',
     'help',
     'metavar']
    ACTIONS = ('store', 'store_const', 'store_true', 'store_false', 'append', 'append_const', 'count', 'callback', 'help', 'version')
    STORE_ACTIONS = ('store', 'store_const', 'store_true', 'store_false', 'append', 'append_const', 'count')
    TYPED_ACTIONS = ('store', 'append', 'callback')
    ALWAYS_TYPED_ACTIONS = ('store', 'append')
    CONST_ACTIONS = ('store_const', 'append_const')
    TYPES = ('string', 'int', 'long', 'float', 'complex', 'choice')
    TYPE_CHECKER = {'int': check_builtin,
     'long': check_builtin,
     'float': check_builtin,
     'complex': check_builtin,
     'choice': check_choice}
    CHECK_METHODS = None

    def __init__(self, *opts, **attrs):
        self._short_opts = []
        self._long_opts = []
        opts = self._check_opt_strings(opts)
        self._set_opt_strings(opts)
        self._set_attrs(attrs)
        for checker in self.CHECK_METHODS:
            checker(self)

    def _check_opt_strings(self, opts):
        opts = filter(None, opts)
        if not opts:
            raise TypeError('at least one option string must be supplied')
        return opts

    def _set_opt_strings(self, opts):
        for opt in opts:
            if len(opt) < 2:
                raise OptionError('invalid option string %r: must be at least two characters long' % opt, self)
            if len(opt) == 2:
                if not (opt[0] == '-' and opt[1] != '-'):
                    raise OptionError('invalid short option string %r: must be of the form -x, (x any non-dash char)' % opt, self)
                self._short_opts.append(opt)
            if not (opt[0:2] == '--' and opt[2] != '-'):
                raise OptionError('invalid long option string %r: must start with --, followed by non-dash' % opt, self)
            self._long_opts.append(opt)

    def _set_attrs(self, attrs):
        for attr in self.ATTRS:
            if attr in attrs:
                setattr(self, attr, attrs[attr])
                del attrs[attr]
            if attr == 'default':
                setattr(self, attr, NO_DEFAULT)
            setattr(self, attr, None)

        if attrs:
            attrs = attrs.keys()
            attrs.sort()
            raise OptionError('invalid keyword arguments: %s' % ', '.join(attrs), self)
        return

    def _check_action(self):
        if self.action is None:
            self.action = 'store'
        elif self.action not in self.ACTIONS:
            raise OptionError('invalid action: %r' % self.action, self)
        return

    def _check_type(self):
        if self.type is None:
            if self.action in self.ALWAYS_TYPED_ACTIONS:
                if self.choices is not None:
                    self.type = 'choice'
                else:
                    self.type = 'string'
        else:
            import __builtin__
            if type(self.type) is types.TypeType or hasattr(self.type, '__name__') and getattr(__builtin__, self.type.__name__, None) is self.type:
                self.type = self.type.__name__
            if self.type == 'str':
                self.type = 'string'
            if self.type not in self.TYPES:
                raise OptionError('invalid option type: %r' % self.type, self)
            if self.action not in self.TYPED_ACTIONS:
                raise OptionError('must not supply a type for action %r' % self.action, self)
        return

    def _check_choice(self):
        if self.type == 'choice':
            if self.choices is None:
                raise OptionError("must supply a list of choices for type 'choice'", self)
            elif type(self.choices) not in (types.TupleType, types.ListType):
                raise OptionError("choices must be a list of strings ('%s' supplied)" % str(type(self.choices)).split("'")[1], self)
        elif self.choices is not None:
            raise OptionError('must not supply choices for type %r' % self.type, self)
        return

    def _check_dest(self):
        takes_value = self.action in self.STORE_ACTIONS or self.type is not None
        if self.dest is None and takes_value:
            if self._long_opts:
                self.dest = self._long_opts[0][2:].replace('-', '_')
            else:
                self.dest = self._short_opts[0][1]
        return

    def _check_const(self):
        if self.action not in self.CONST_ACTIONS and self.const is not None:
            raise OptionError("'const' must not be supplied for action %r" % self.action, self)
        return

    def _check_nargs(self):
        if self.action in self.TYPED_ACTIONS:
            if self.nargs is None:
                self.nargs = 1
        elif self.nargs is not None:
            raise OptionError("'nargs' must not be supplied for action %r" % self.action, self)
        return

    def _check_callback(self):
        if self.action == 'callback':
            if not hasattr(self.callback, '__call__'):
                raise OptionError('callback not callable: %r' % self.callback, self)
            if self.callback_args is not None and type(self.callback_args) is not types.TupleType:
                raise OptionError('callback_args, if supplied, must be a tuple: not %r' % self.callback_args, self)
            if self.callback_kwargs is not None and type(self.callback_kwargs) is not types.DictType:
                raise OptionError('callback_kwargs, if supplied, must be a dict: not %r' % self.callback_kwargs, self)
        else:
            if self.callback is not None:
                raise OptionError('callback supplied (%r) for non-callback option' % self.callback, self)
            if self.callback_args is not None:
                raise OptionError('callback_args supplied for non-callback option', self)
            if self.callback_kwargs is not None:
                raise OptionError('callback_kwargs supplied for non-callback option', self)
        return

    CHECK_METHODS = [_check_action,
     _check_type,
     _check_choice,
     _check_dest,
     _check_const,
     _check_nargs,
     _check_callback]

    def __str__(self):
        return '/'.join(self._short_opts + self._long_opts)

    __repr__ = _repr

    def takes_value(self):
        return self.type is not None

    def get_opt_string(self):
        if self._long_opts:
            return self._long_opts[0]
        else:
            return self._short_opts[0]

    def check_value(self, opt, value):
        checker = self.TYPE_CHECKER.get(self.type)
        if checker is None:
            return value
        else:
            return checker(self, opt, value)
            return

    def convert_value(self, opt, value):
        if value is not None:
            if self.nargs == 1:
                return self.check_value(opt, value)
            else:
                return tuple([ self.check_value(opt, v) for v in value ])
        return

    def process(self, opt, value, values, parser):
        value = self.convert_value(opt, value)
        return self.take_action(self.action, self.dest, opt, value, values, parser)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == 'store':
            setattr(values, dest, value)
        elif action == 'store_const':
            setattr(values, dest, self.const)
        elif action == 'store_true':
            setattr(values, dest, True)
        elif action == 'store_false':
            setattr(values, dest, False)
        elif action == 'append':
            values.ensure_value(dest, []).append(value)
        elif action == 'append_const':
            values.ensure_value(dest, []).append(self.const)
        elif action == 'count':
            setattr(values, dest, values.ensure_value(dest, 0) + 1)
        elif action == 'callback':
            args = self.callback_args or ()
            kwargs = self.callback_kwargs or {}
            self.callback(self, opt, value, parser, *args, **kwargs)
        elif action == 'help':
            parser.print_help()
            parser.exit()
        elif action == 'version':
            parser.print_version()
            parser.exit()
        else:
            raise ValueError('unknown action %r' % self.action)


SUPPRESS_HELP = 'SUPPRESS' + 'HELP'
SUPPRESS_USAGE = 'SUPPRESS' + 'USAGE'
try:
    basestring
except NameError:

    def isbasestring(x):
        return isinstance(x, (types.StringType, types.UnicodeType))


else:

    def isbasestring(x):
        return isinstance(x, basestring)


class Values():

    def __init__(self, defaults=None):
        if defaults:
            for attr, val in defaults.items():
                setattr(self, attr, val)

    def __str__(self):
        return str(self.__dict__)

    __repr__ = _repr

    def __cmp__(self, other):
        if isinstance(other, Values):
            return cmp(self.__dict__, other.__dict__)
        elif isinstance(other, types.DictType):
            return cmp(self.__dict__, other)
        else:
            return -1

    def _update_careful(self, dict):
        for attr in dir(self):
            if attr in dict:
                dval = dict[attr]
                if dval is not None:
                    setattr(self, attr, dval)

        return

    def _update_loose(self, dict):
        self.__dict__.update(dict)

    def _update(self, dict, mode):
        if mode == 'careful':
            self._update_careful(dict)
        elif mode == 'loose':
            self._update_loose(dict)
        else:
            raise ValueError, 'invalid update mode: %r' % mode

    def read_module(self, modname, mode='careful'):
        __import__(modname)
        mod = sys.modules[modname]
        self._update(vars(mod), mode)

    def read_file(self, filename, mode='careful'):
        vars = {}
        execfile(filename, vars)
        self._update(vars, mode)

    def ensure_value(self, attr, value):
        if not hasattr(self, attr) or getattr(self, attr) is None:
            setattr(self, attr, value)
        return getattr(self, attr)


class OptionContainer():

    def __init__(self, option_class, conflict_handler, description):
        self._create_option_list()
        self.option_class = option_class
        self.set_conflict_handler(conflict_handler)
        self.set_description(description)

    def _create_option_mappings(self):
        self._short_opt = {}
        self._long_opt = {}
        self.defaults = {}

    def _share_option_mappings(self, parser):
        self._short_opt = parser._short_opt
        self._long_opt = parser._long_opt
        self.defaults = parser.defaults

    def set_conflict_handler(self, handler):
        if handler not in ('error', 'resolve'):
            raise ValueError, 'invalid conflict_resolution value %r' % handler
        self.conflict_handler = handler

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def destroy(self):
        del self._short_opt
        del self._long_opt
        del self.defaults

    def _check_conflict(self, option):
        conflict_opts = []
        for opt in option._short_opts:
            if opt in self._short_opt:
                conflict_opts.append((opt, self._short_opt[opt]))

        for opt in option._long_opts:
            if opt in self._long_opt:
                conflict_opts.append((opt, self._long_opt[opt]))

        if conflict_opts:
            handler = self.conflict_handler
            if handler == 'error':
                raise OptionConflictError('conflicting option string(s): %s' % ', '.join([ co[0] for co in conflict_opts ]), option)
            elif handler == 'resolve':
                for opt, c_option in conflict_opts:
                    if opt.startswith('--'):
                        c_option._long_opts.remove(opt)
                        del self._long_opt[opt]
                    else:
                        c_option._short_opts.remove(opt)
                        del self._short_opt[opt]
                    if not (c_option._short_opts or c_option._long_opts):
                        c_option.container.option_list.remove(c_option)

    def add_option(self, *args, **kwargs):
        if type(args[0]) in types.StringTypes:
            option = self.option_class(*args, **kwargs)
        elif len(args) == 1 and not kwargs:
            option = args[0]
            if not isinstance(option, Option):
                raise TypeError, 'not an Option instance: %r' % option
        else:
            raise TypeError, 'invalid arguments'
        self._check_conflict(option)
        self.option_list.append(option)
        option.container = self
        for opt in option._short_opts:
            self._short_opt[opt] = option

        for opt in option._long_opts:
            self._long_opt[opt] = option

        if option.dest is not None:
            if option.default is not NO_DEFAULT:
                self.defaults[option.dest] = option.default
            elif option.dest not in self.defaults:
                self.defaults[option.dest] = None
        return option

    def add_options(self, option_list):
        for option in option_list:
            self.add_option(option)

    def get_option(self, opt_str):
        return self._short_opt.get(opt_str) or self._long_opt.get(opt_str)

    def has_option(self, opt_str):
        return opt_str in self._short_opt or opt_str in self._long_opt

    def remove_option(self, opt_str):
        option = self._short_opt.get(opt_str)
        if option is None:
            option = self._long_opt.get(opt_str)
        if option is None:
            raise ValueError('no such option %r' % opt_str)
        for opt in option._short_opts:
            del self._short_opt[opt]

        for opt in option._long_opts:
            del self._long_opt[opt]

        option.container.option_list.remove(option)
        return

    def format_option_help(self, formatter):
        if not self.option_list:
            return ''
        result = []
        for option in self.option_list:
            if option.help is not SUPPRESS_HELP:
                result.append(formatter.format_option(option))

        return ''.join(result)

    def format_description(self, formatter):
        return formatter.format_description(self.get_description())

    def format_help(self, formatter):
        result = []
        if self.description:
            result.append(self.format_description(formatter))
        if self.option_list:
            result.append(self.format_option_help(formatter))
        return '\n'.join(result)


class OptionGroup(OptionContainer):

    def __init__(self, parser, title, description=None):
        self.parser = parser
        OptionContainer.__init__(self, parser.option_class, parser.conflict_handler, description)
        self.title = title

    def _create_option_list(self):
        self.option_list = []
        self._share_option_mappings(self.parser)

    def set_title(self, title):
        self.title = title

    def destroy(self):
        OptionContainer.destroy(self)
        del self.option_list

    def format_help(self, formatter):
        result = formatter.format_heading(self.title)
        formatter.indent()
        result += OptionContainer.format_help(self, formatter)
        formatter.dedent()
        return result


class OptionParser(OptionContainer):
    standard_option_list = []

    def __init__(self, usage=None, option_list=None, option_class=Option, version=None, conflict_handler='error', description=None, formatter=None, add_help_option=True, prog=None, epilog=None):
        OptionContainer.__init__(self, option_class, conflict_handler, description)
        self.set_usage(usage)
        self.prog = prog
        self.version = version
        self.allow_interspersed_args = True
        self.process_default_values = True
        if formatter is None:
            formatter = IndentedHelpFormatter()
        self.formatter = formatter
        self.formatter.set_parser(self)
        self.epilog = epilog
        self._populate_option_list(option_list, add_help=add_help_option)
        self._init_parsing_state()
        return

    def destroy(self):
        OptionContainer.destroy(self)
        for group in self.option_groups:
            group.destroy()

        del self.option_list
        del self.option_groups
        del self.formatter

    def _create_option_list(self):
        self.option_list = []
        self.option_groups = []
        self._create_option_mappings()

    def _add_help_option(self):
        self.add_option('-h', '--help', action='help', help=_('show this help message and exit'))

    def _add_version_option(self):
        self.add_option('--version', action='version', help=_("show program's version number and exit"))

    def _populate_option_list(self, option_list, add_help=True):
        if self.standard_option_list:
            self.add_options(self.standard_option_list)
        if option_list:
            self.add_options(option_list)
        if self.version:
            self._add_version_option()
        if add_help:
            self._add_help_option()

    def _init_parsing_state(self):
        self.rargs = None
        self.largs = None
        self.values = None
        return

    def set_usage(self, usage):
        if usage is None:
            self.usage = _('%prog [options]')
        elif usage is SUPPRESS_USAGE:
            self.usage = None
        elif usage.lower().startswith('usage: '):
            self.usage = usage[7:]
        else:
            self.usage = usage
        return

    def enable_interspersed_args(self):
        self.allow_interspersed_args = True

    def disable_interspersed_args(self):
        self.allow_interspersed_args = False

    def set_process_default_values(self, process):
        self.process_default_values = process

    def set_default(self, dest, value):
        self.defaults[dest] = value

    def set_defaults(self, **kwargs):
        self.defaults.update(kwargs)

    def _get_all_options(self):
        options = self.option_list[:]
        for group in self.option_groups:
            options.extend(group.option_list)

        return options

    def get_default_values(self):
        if not self.process_default_values:
            return Values(self.defaults)
        defaults = self.defaults.copy()
        for option in self._get_all_options():
            default = defaults.get(option.dest)
            if isbasestring(default):
                opt_str = option.get_opt_string()
                defaults[option.dest] = option.check_value(opt_str, default)

        return Values(defaults)

    def add_option_group(self, *args, **kwargs):
        if type(args[0]) is types.StringType:
            group = OptionGroup(self, *args, **kwargs)
        elif len(args) == 1 and not kwargs:
            group = args[0]
            if not isinstance(group, OptionGroup):
                raise TypeError, 'not an OptionGroup instance: %r' % group
            if group.parser is not self:
                raise ValueError, 'invalid OptionGroup (wrong parser)'
        else:
            raise TypeError, 'invalid arguments'
        self.option_groups.append(group)
        return group

    def get_option_group(self, opt_str):
        option = self._short_opt.get(opt_str) or self._long_opt.get(opt_str)
        return option.container if option and option.container is not self else None

    def _get_args(self, args):
        if args is None:
            return sys.argv[1:]
        else:
            return args[:]
            return

    def parse_args(self, args=None, values=None):
        rargs = self._get_args(args)
        if values is None:
            values = self.get_default_values()
        self.rargs = rargs
        self.largs = largs = []
        self.values = values
        try:
            stop = self._process_args(largs, rargs, values)
        except (BadOptionError, OptionValueError) as err:
            self.error(str(err))

        args = largs + rargs
        return self.check_values(values, args)

    def check_values(self, values, args):
        return (values, args)

    def _process_args(self, largs, rargs, values):
        while rargs:
            arg = rargs[0]
            if arg == '--':
                del rargs[0]
                return
            if arg[0:2] == '--':
                self._process_long_opt(rargs, values)
            if arg[:1] == '-' and len(arg) > 1:
                self._process_short_opts(rargs, values)
            if self.allow_interspersed_args:
                largs.append(arg)
                del rargs[0]
            return

    def _match_long_opt(self, opt):
        return _match_abbrev(opt, self._long_opt)

    def _process_long_opt(self, rargs, values):
        arg = rargs.pop(0)
        if '=' in arg:
            opt, next_arg = arg.split('=', 1)
            rargs.insert(0, next_arg)
            had_explicit_value = True
        else:
            opt = arg
            had_explicit_value = False
        opt = self._match_long_opt(opt)
        option = self._long_opt[opt]
        if option.takes_value():
            nargs = option.nargs
            if len(rargs) < nargs:
                if nargs == 1:
                    self.error(_('%s option requires an argument') % opt)
                else:
                    self.error(_('%s option requires %d arguments') % (opt, nargs))
            elif nargs == 1:
                value = rargs.pop(0)
            else:
                value = tuple(rargs[0:nargs])
                del rargs[0:nargs]
        elif had_explicit_value:
            self.error(_('%s option does not take a value') % opt)
        else:
            value = None
        option.process(opt, value, values, self)
        return

    def _process_short_opts(self, rargs, values):
        arg = rargs.pop(0)
        stop = False
        i = 1
        for ch in arg[1:]:
            opt = '-' + ch
            option = self._short_opt.get(opt)
            i += 1
            if not option:
                raise BadOptionError(opt)
            if option.takes_value():
                if i < len(arg):
                    rargs.insert(0, arg[i:])
                    stop = True
                nargs = option.nargs
                if len(rargs) < nargs:
                    if nargs == 1:
                        self.error(_('%s option requires an argument') % opt)
                    else:
                        self.error(_('%s option requires %d arguments') % (opt, nargs))
                elif nargs == 1:
                    value = rargs.pop(0)
                else:
                    value = tuple(rargs[0:nargs])
                    del rargs[0:nargs]
            else:
                value = None
            option.process(opt, value, values, self)
            if stop:
                break

        return

    def get_prog_name(self):
        if self.prog is None:
            return os.path.basename(sys.argv[0])
        else:
            return self.prog
            return

    def expand_prog_name(self, s):
        return s.replace('%prog', self.get_prog_name())

    def get_description(self):
        return self.expand_prog_name(self.description)

    def exit(self, status=0, msg=None):
        if msg:
            sys.stderr.write(msg)
        sys.exit(status)

    def error(self, msg):
        self.print_usage(sys.stderr)
        self.exit(2, '%s: error: %s\n' % (self.get_prog_name(), msg))

    def get_usage(self):
        if self.usage:
            return self.formatter.format_usage(self.expand_prog_name(self.usage))
        else:
            return ''

    def print_usage(self, file=None):
        if self.usage:
            print >> file, self.get_usage()

    def get_version(self):
        if self.version:
            return self.expand_prog_name(self.version)
        else:
            return ''

    def print_version(self, file=None):
        if self.version:
            print >> file, self.get_version()

    def format_option_help(self, formatter=None):
        if formatter is None:
            formatter = self.formatter
        formatter.store_option_strings(self)
        result = []
        result.append(formatter.format_heading(_('Options')))
        formatter.indent()
        if self.option_list:
            result.append(OptionContainer.format_option_help(self, formatter))
            result.append('\n')
        for group in self.option_groups:
            result.append(group.format_help(formatter))
            result.append('\n')

        formatter.dedent()
        return ''.join(result[:-1])

    def format_epilog(self, formatter):
        return formatter.format_epilog(self.epilog)

    def format_help(self, formatter=None):
        if formatter is None:
            formatter = self.formatter
        result = []
        if self.usage:
            result.append(self.get_usage() + '\n')
        if self.description:
            result.append(self.format_description(formatter) + '\n')
        result.append(self.format_option_help(formatter))
        result.append(self.format_epilog(formatter))
        return ''.join(result)

    def _get_encoding(self, file):
        encoding = getattr(file, 'encoding', None)
        if not encoding:
            encoding = sys.getdefaultencoding()
        return encoding

    def print_help(self, file=None):
        if file is None:
            file = sys.stdout
        encoding = self._get_encoding(file)
        file.write(self.format_help().encode(encoding, 'replace'))
        return


def _match_abbrev(s, wordmap):
    if s in wordmap:
        return s
    possibilities = [ word for word in wordmap.keys() if word.startswith(s) ]
    if len(possibilities) == 1:
        return possibilities[0]
    if not possibilities:
        raise BadOptionError(s)
    else:
        possibilities.sort()
        raise AmbiguousOptionError(s, possibilities)


make_option = Option
