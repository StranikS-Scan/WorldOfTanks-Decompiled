# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ConfigParser.py
try:
    from collections import OrderedDict as _default_dict
except ImportError:
    _default_dict = dict

import re
__all__ = ['NoSectionError',
 'DuplicateSectionError',
 'NoOptionError',
 'InterpolationError',
 'InterpolationDepthError',
 'InterpolationSyntaxError',
 'ParsingError',
 'MissingSectionHeaderError',
 'ConfigParser',
 'SafeConfigParser',
 'RawConfigParser',
 'DEFAULTSECT',
 'MAX_INTERPOLATION_DEPTH']
DEFAULTSECT = 'DEFAULT'
MAX_INTERPOLATION_DEPTH = 10

class Error(Exception):

    def _get_message(self):
        return self.__message

    def _set_message(self, value):
        self.__message = value

    message = property(_get_message, _set_message)

    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__


class NoSectionError(Error):

    def __init__(self, section):
        Error.__init__(self, 'No section: %r' % (section,))
        self.section = section
        self.args = (section,)


class DuplicateSectionError(Error):

    def __init__(self, section):
        Error.__init__(self, 'Section %r already exists' % section)
        self.section = section
        self.args = (section,)


class NoOptionError(Error):

    def __init__(self, option, section):
        Error.__init__(self, 'No option %r in section: %r' % (option, section))
        self.option = option
        self.section = section
        self.args = (option, section)


class InterpolationError(Error):

    def __init__(self, option, section, msg):
        Error.__init__(self, msg)
        self.option = option
        self.section = section
        self.args = (option, section, msg)


class InterpolationMissingOptionError(InterpolationError):

    def __init__(self, option, section, rawval, reference):
        msg = 'Bad value substitution:\n\tsection: [%s]\n\toption : %s\n\tkey    : %s\n\trawval : %s\n' % (section,
         option,
         reference,
         rawval)
        InterpolationError.__init__(self, option, section, msg)
        self.reference = reference
        self.args = (option,
         section,
         rawval,
         reference)


class InterpolationSyntaxError(InterpolationError):
    pass


class InterpolationDepthError(InterpolationError):

    def __init__(self, option, section, rawval):
        msg = 'Value interpolation too deeply recursive:\n\tsection: [%s]\n\toption : %s\n\trawval : %s\n' % (section, option, rawval)
        InterpolationError.__init__(self, option, section, msg)
        self.args = (option, section, rawval)


class ParsingError(Error):

    def __init__(self, filename):
        Error.__init__(self, 'File contains parsing errors: %s' % filename)
        self.filename = filename
        self.errors = []
        self.args = (filename,)

    def append(self, lineno, line):
        self.errors.append((lineno, line))
        self.message += '\n\t[line %2d]: %s' % (lineno, line)


class MissingSectionHeaderError(ParsingError):

    def __init__(self, filename, lineno, line):
        Error.__init__(self, 'File contains no section headers.\nfile: %s, line: %d\n%r' % (filename, lineno, line))
        self.filename = filename
        self.lineno = lineno
        self.line = line
        self.args = (filename, lineno, line)


class RawConfigParser():

    def __init__(self, defaults=None, dict_type=_default_dict, allow_no_value=False):
        self._dict = dict_type
        self._sections = self._dict()
        self._defaults = self._dict()
        if allow_no_value:
            self._optcre = self.OPTCRE_NV
        else:
            self._optcre = self.OPTCRE
        if defaults:
            for key, value in defaults.items():
                self._defaults[self.optionxform(key)] = value

    def defaults(self):
        return self._defaults

    def sections(self):
        return self._sections.keys()

    def add_section(self, section):
        if section.lower() == 'default':
            raise ValueError, 'Invalid section name: %s' % section
        if section in self._sections:
            raise DuplicateSectionError(section)
        self._sections[section] = self._dict()

    def has_section(self, section):
        return section in self._sections

    def options(self, section):
        try:
            opts = self._sections[section].copy()
        except KeyError:
            raise NoSectionError(section)

        opts.update(self._defaults)
        if '__name__' in opts:
            del opts['__name__']
        return opts.keys()

    def read(self, filenames):
        if isinstance(filenames, basestring):
            filenames = [filenames]
        read_ok = []
        for filename in filenames:
            try:
                fp = open(filename)
            except IOError:
                continue

            self._read(fp, filename)
            fp.close()
            read_ok.append(filename)

        return read_ok

    def readfp(self, fp, filename=None):
        if filename is None:
            try:
                filename = fp.name
            except AttributeError:
                filename = '<???>'

        self._read(fp, filename)
        return

    def get(self, section, option):
        opt = self.optionxform(option)
        if section not in self._sections:
            if section != DEFAULTSECT:
                raise NoSectionError(section)
            if opt in self._defaults:
                return self._defaults[opt]
            raise NoOptionError(option, section)
        else:
            if opt in self._sections[section]:
                return self._sections[section][opt]
            if opt in self._defaults:
                return self._defaults[opt]
            raise NoOptionError(option, section)

    def items(self, section):
        try:
            d2 = self._sections[section]
        except KeyError:
            if section != DEFAULTSECT:
                raise NoSectionError(section)
            d2 = self._dict()

        d = self._defaults.copy()
        d.update(d2)
        if '__name__' in d:
            del d['__name__']
        return d.items()

    def _get(self, section, conv, option):
        return conv(self.get(section, option))

    def getint(self, section, option):
        return self._get(section, int, option)

    def getfloat(self, section, option):
        return self._get(section, float, option)

    _boolean_states = {'1': True,
     'yes': True,
     'true': True,
     'on': True,
     '0': False,
     'no': False,
     'false': False,
     'off': False}

    def getboolean(self, section, option):
        v = self.get(section, option)
        if v.lower() not in self._boolean_states:
            raise ValueError, 'Not a boolean: %s' % v
        return self._boolean_states[v.lower()]

    def optionxform(self, optionstr):
        return optionstr.lower()

    def has_option(self, section, option):
        if not section or section == DEFAULTSECT:
            option = self.optionxform(option)
            return option in self._defaults
        elif section not in self._sections:
            return False
        else:
            option = self.optionxform(option)
            return option in self._sections[section] or option in self._defaults

    def set(self, section, option, value=None):
        if not section or section == DEFAULTSECT:
            sectdict = self._defaults
        else:
            try:
                sectdict = self._sections[section]
            except KeyError:
                raise NoSectionError(section)

        sectdict[self.optionxform(option)] = value

    def write(self, fp):
        if self._defaults:
            fp.write('[%s]\n' % DEFAULTSECT)
            for key, value in self._defaults.items():
                fp.write('%s = %s\n' % (key, str(value).replace('\n', '\n\t')))

            fp.write('\n')
        for section in self._sections:
            fp.write('[%s]\n' % section)
            for key, value in self._sections[section].items():
                if key == '__name__':
                    continue
                if value is not None or self._optcre == self.OPTCRE:
                    key = ' = '.join((key, str(value).replace('\n', '\n\t')))
                fp.write('%s\n' % key)

            fp.write('\n')

        return

    def remove_option(self, section, option):
        if not section or section == DEFAULTSECT:
            sectdict = self._defaults
        else:
            try:
                sectdict = self._sections[section]
            except KeyError:
                raise NoSectionError(section)

        option = self.optionxform(option)
        existed = option in sectdict
        if existed:
            del sectdict[option]
        return existed

    def remove_section(self, section):
        existed = section in self._sections
        if existed:
            del self._sections[section]
        return existed

    SECTCRE = re.compile('\\[(?P<header>[^]]+)\\]')
    OPTCRE = re.compile('(?P<option>[^:=\\s][^:=]*)\\s*(?P<vi>[:=])\\s*(?P<value>.*)$')
    OPTCRE_NV = re.compile('(?P<option>[^:=\\s][^:=]*)\\s*(?:(?P<vi>[:=])\\s*(?P<value>.*))?$')

    def _read(self, fp, fpname):
        cursect = None
        optname = None
        lineno = 0
        e = None
        while True:
            line = fp.readline()
            if not line:
                break
            lineno = lineno + 1
            if line.strip() == '' or line[0] in '#;':
                continue
            if line.split(None, 1)[0].lower() == 'rem' and line[0] in 'rR':
                continue
            if line[0].isspace() and cursect is not None and optname:
                value = line.strip()
                if value:
                    cursect[optname].append(value)
            mo = self.SECTCRE.match(line)
            if mo:
                sectname = mo.group('header')
                if sectname in self._sections:
                    cursect = self._sections[sectname]
                elif sectname == DEFAULTSECT:
                    cursect = self._defaults
                else:
                    cursect = self._dict()
                    cursect['__name__'] = sectname
                    self._sections[sectname] = cursect
                optname = None
            if cursect is None:
                raise MissingSectionHeaderError(fpname, lineno, line)
            mo = self._optcre.match(line)
            if mo:
                optname, vi, optval = mo.group('option', 'vi', 'value')
                optname = self.optionxform(optname.rstrip())
                if optval is not None:
                    if vi in ('=', ':') and ';' in optval:
                        pos = optval.find(';')
                        if pos != -1 and optval[pos - 1].isspace():
                            optval = optval[:pos]
                    optval = optval.strip()
                    if optval == '""':
                        optval = ''
                    cursect[optname] = [optval]
                else:
                    cursect[optname] = optval
            if not e:
                e = ParsingError(fpname)
            e.append(lineno, repr(line))

        if e:
            raise e
        all_sections = [self._defaults]
        all_sections.extend(self._sections.values())
        for options in all_sections:
            for name, val in options.items():
                if isinstance(val, list):
                    options[name] = '\n'.join(val)

        return


import UserDict as _UserDict

class _Chainmap(_UserDict.DictMixin):

    def __init__(self, *maps):
        self._maps = maps

    def __getitem__(self, key):
        for mapping in self._maps:
            try:
                return mapping[key]
            except KeyError:
                pass

        raise KeyError(key)

    def keys(self):
        result = []
        seen = set()
        for mapping in self._maps:
            for key in mapping:
                if key not in seen:
                    result.append(key)
                    seen.add(key)

        return result


class ConfigParser(RawConfigParser):

    def get(self, section, option, raw=False, vars=None):
        sectiondict = {}
        try:
            sectiondict = self._sections[section]
        except KeyError:
            if section != DEFAULTSECT:
                raise NoSectionError(section)

        vardict = {}
        if vars:
            for key, value in vars.items():
                vardict[self.optionxform(key)] = value

        d = _Chainmap(vardict, sectiondict, self._defaults)
        option = self.optionxform(option)
        try:
            value = d[option]
        except KeyError:
            raise NoOptionError(option, section)

        if raw or value is None:
            return value
        else:
            return self._interpolate(section, option, value, d)
            return

    def items(self, section, raw=False, vars=None):
        d = self._defaults.copy()
        try:
            d.update(self._sections[section])
        except KeyError:
            if section != DEFAULTSECT:
                raise NoSectionError(section)

        if vars:
            for key, value in vars.items():
                d[self.optionxform(key)] = value

        options = d.keys()
        if '__name__' in options:
            options.remove('__name__')
        if raw:
            return [ (option, d[option]) for option in options ]
        else:
            return [ (option, self._interpolate(section, option, d[option], d)) for option in options ]

    def _interpolate(self, section, option, rawval, vars):
        value = rawval
        depth = MAX_INTERPOLATION_DEPTH
        while depth:
            depth -= 1
            if value and '%(' in value:
                value = self._KEYCRE.sub(self._interpolation_replace, value)
                try:
                    value = value % vars
                except KeyError as e:
                    raise InterpolationMissingOptionError(option, section, rawval, e.args[0])

            break

        if value and '%(' in value:
            raise InterpolationDepthError(option, section, rawval)
        return value

    _KEYCRE = re.compile('%\\(([^)]*)\\)s|.')

    def _interpolation_replace(self, match):
        s = match.group(1)
        if s is None:
            return match.group()
        else:
            return '%%(%s)s' % self.optionxform(s)
            return


class SafeConfigParser(ConfigParser):

    def _interpolate(self, section, option, rawval, vars):
        L = []
        self._interpolate_some(option, L, rawval, section, vars, 1)
        return ''.join(L)

    _interpvar_re = re.compile('%\\(([^)]+)\\)s')

    def _interpolate_some(self, option, accum, rest, section, map, depth):
        if depth > MAX_INTERPOLATION_DEPTH:
            raise InterpolationDepthError(option, section, rest)
        while rest:
            p = rest.find('%')
            if p < 0:
                accum.append(rest)
                return
            if p > 0:
                accum.append(rest[:p])
                rest = rest[p:]
            c = rest[1:2]
            if c == '%':
                accum.append('%')
                rest = rest[2:]
            if c == '(':
                m = self._interpvar_re.match(rest)
                if m is None:
                    raise InterpolationSyntaxError(option, section, 'bad interpolation variable reference %r' % rest)
                var = self.optionxform(m.group(1))
                rest = rest[m.end():]
                try:
                    v = map[var]
                except KeyError:
                    raise InterpolationMissingOptionError(option, section, rest, var)

                if '%' in v:
                    self._interpolate_some(option, accum, v, section, map, depth + 1)
                else:
                    accum.append(v)
            raise InterpolationSyntaxError(option, section, "'%%' must be followed by '%%' or '(', found: %r" % (rest,))

        return

    def set(self, section, option, value=None):
        if self._optcre is self.OPTCRE or value:
            if not isinstance(value, basestring):
                raise TypeError('option values must be strings')
        if value is not None:
            tmp_value = value.replace('%%', '')
            tmp_value = self._interpvar_re.sub('', tmp_value)
            if '%' in tmp_value:
                raise ValueError('invalid interpolation syntax in %r at position %d' % (value, tmp_value.find('%')))
        ConfigParser.set(self, section, option, value)
        return
