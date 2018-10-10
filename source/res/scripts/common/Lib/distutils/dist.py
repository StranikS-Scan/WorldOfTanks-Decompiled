# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/dist.py
__revision__ = '$Id$'
import sys, os, re
from email import message_from_file
try:
    import warnings
except ImportError:
    warnings = None

from distutils.errors import DistutilsOptionError, DistutilsArgError, DistutilsModuleError, DistutilsClassError
from distutils.fancy_getopt import FancyGetopt, translate_longopt
from distutils.util import check_environ, strtobool, rfc822_escape
from distutils import log
from distutils.debug import DEBUG
PKG_INFO_ENCODING = 'utf-8'
command_re = re.compile('^[a-zA-Z]([a-zA-Z0-9_]*)$')

class Distribution():
    global_options = [('verbose', 'v', 'run verbosely (default)', 1),
     ('quiet', 'q', 'run quietly (turns verbosity off)'),
     ('dry-run', 'n', "don't actually do anything"),
     ('help', 'h', 'show detailed help message'),
     ('no-user-cfg', None, 'ignore pydistutils.cfg in your home directory')]
    common_usage = "Common commands: (see '--help-commands' for more)\n\n  setup.py build      will build the package underneath 'build/'\n  setup.py install    will install the package\n"
    display_options = [('help-commands', None, 'list all available commands'),
     ('name', None, 'print package name'),
     ('version', 'V', 'print package version'),
     ('fullname', None, 'print <package name>-<version>'),
     ('author', None, "print the author's name"),
     ('author-email', None, "print the author's email address"),
     ('maintainer', None, "print the maintainer's name"),
     ('maintainer-email', None, "print the maintainer's email address"),
     ('contact', None, "print the maintainer's name if known, else the author's"),
     ('contact-email', None, "print the maintainer's email address if known, else the author's"),
     ('url', None, 'print the URL for this package'),
     ('license', None, 'print the license of the package'),
     ('licence', None, 'alias for --license'),
     ('description', None, 'print the package description'),
     ('long-description', None, 'print the long package description'),
     ('platforms', None, 'print the list of platforms'),
     ('classifiers', None, 'print the list of classifiers'),
     ('keywords', None, 'print the list of keywords'),
     ('provides', None, 'print the list of packages/modules provided'),
     ('requires', None, 'print the list of packages/modules required'),
     ('obsoletes', None, 'print the list of packages/modules made obsolete')]
    display_option_names = map(lambda x: translate_longopt(x[0]), display_options)
    negative_opt = {'quiet': 'verbose'}

    def __init__(self, attrs=None):
        self.verbose = 1
        self.dry_run = 0
        self.help = 0
        for attr in self.display_option_names:
            setattr(self, attr, 0)

        self.metadata = DistributionMetadata()
        for basename in self.metadata._METHOD_BASENAMES:
            method_name = 'get_' + basename
            setattr(self, method_name, getattr(self.metadata, method_name))

        self.cmdclass = {}
        self.command_packages = None
        self.script_name = None
        self.script_args = None
        self.command_options = {}
        self.dist_files = []
        self.packages = None
        self.package_data = {}
        self.package_dir = None
        self.py_modules = None
        self.libraries = None
        self.headers = None
        self.ext_modules = None
        self.ext_package = None
        self.include_dirs = None
        self.extra_path = None
        self.scripts = None
        self.data_files = None
        self.password = ''
        self.command_obj = {}
        self.have_run = {}
        if attrs:
            options = attrs.get('options')
            if options is not None:
                del attrs['options']
                for command, cmd_options in options.items():
                    opt_dict = self.get_option_dict(command)
                    for opt, val in cmd_options.items():
                        opt_dict[opt] = ('setup script', val)

            if 'licence' in attrs:
                attrs['license'] = attrs['licence']
                del attrs['licence']
                msg = "'licence' distribution option is deprecated; use 'license'"
                if warnings is not None:
                    warnings.warn(msg)
                else:
                    sys.stderr.write(msg + '\n')
            for key, val in attrs.items():
                if hasattr(self.metadata, 'set_' + key):
                    getattr(self.metadata, 'set_' + key)(val)
                if hasattr(self.metadata, key):
                    setattr(self.metadata, key, val)
                if hasattr(self, key):
                    setattr(self, key, val)
                msg = 'Unknown distribution option: %s' % repr(key)
                if warnings is not None:
                    warnings.warn(msg)
                sys.stderr.write(msg + '\n')

        self.want_user_cfg = True
        if self.script_args is not None:
            for arg in self.script_args:
                if not arg.startswith('-'):
                    break
                if arg == '--no-user-cfg':
                    self.want_user_cfg = False
                    break

        self.finalize_options()
        return

    def get_option_dict(self, command):
        dict = self.command_options.get(command)
        if dict is None:
            dict = self.command_options[command] = {}
        return dict

    def dump_option_dicts(self, header=None, commands=None, indent=''):
        from pprint import pformat
        if commands is None:
            commands = self.command_options.keys()
            commands.sort()
        if header is not None:
            self.announce(indent + header)
            indent = indent + '  '
        if not commands:
            self.announce(indent + 'no commands known yet')
            return
        else:
            for cmd_name in commands:
                opt_dict = self.command_options.get(cmd_name)
                if opt_dict is None:
                    self.announce(indent + "no option dict for '%s' command" % cmd_name)
                self.announce(indent + "option dict for '%s' command:" % cmd_name)
                out = pformat(opt_dict)
                for line in out.split('\n'):
                    self.announce(indent + '  ' + line)

            return

    def find_config_files(self):
        files = []
        check_environ()
        sys_dir = os.path.dirname(sys.modules['distutils'].__file__)
        sys_file = os.path.join(sys_dir, 'distutils.cfg')
        if os.path.isfile(sys_file):
            files.append(sys_file)
        if os.name == 'posix':
            user_filename = '.pydistutils.cfg'
        else:
            user_filename = 'pydistutils.cfg'
        if self.want_user_cfg:
            user_file = os.path.join(os.path.expanduser('~'), user_filename)
            if os.path.isfile(user_file):
                files.append(user_file)
        local_file = 'setup.cfg'
        if os.path.isfile(local_file):
            files.append(local_file)
        if DEBUG:
            self.announce('using config files: %s' % ', '.join(files))
        return files

    def parse_config_files(self, filenames=None):
        from ConfigParser import ConfigParser
        if filenames is None:
            filenames = self.find_config_files()
        if DEBUG:
            self.announce('Distribution.parse_config_files():')
        parser = ConfigParser()
        for filename in filenames:
            if DEBUG:
                self.announce('  reading %s' % filename)
            parser.read(filename)
            for section in parser.sections():
                options = parser.options(section)
                opt_dict = self.get_option_dict(section)
                for opt in options:
                    if opt != '__name__':
                        val = parser.get(section, opt)
                        opt = opt.replace('-', '_')
                        opt_dict[opt] = (filename, val)

            parser.__init__()

        if 'global' in self.command_options:
            for opt, (src, val) in self.command_options['global'].items():
                alias = self.negative_opt.get(opt)
                try:
                    if alias:
                        setattr(self, alias, not strtobool(val))
                    elif opt in ('verbose', 'dry_run'):
                        setattr(self, opt, strtobool(val))
                    else:
                        setattr(self, opt, val)
                except ValueError as msg:
                    raise DistutilsOptionError, msg

        return

    def parse_command_line(self):
        toplevel_options = self._get_toplevel_options()
        self.commands = []
        parser = FancyGetopt(toplevel_options + self.display_options)
        parser.set_negative_aliases(self.negative_opt)
        parser.set_aliases({'licence': 'license'})
        args = parser.getopt(args=self.script_args, object=self)
        option_order = parser.get_option_order()
        log.set_verbosity(self.verbose)
        if self.handle_display_options(option_order):
            return
        else:
            while args:
                args = self._parse_command_opts(parser, args)
                if args is None:
                    return

            if self.help:
                self._show_help(parser, display_options=len(self.commands) == 0, commands=self.commands)
                return
            if not self.commands:
                raise DistutilsArgError, 'no commands supplied'
            return 1

    def _get_toplevel_options(self):
        return self.global_options + [('command-packages=', None, 'list of packages that provide distutils commands')]

    def _parse_command_opts(self, parser, args):
        from distutils.cmd import Command
        command = args[0]
        if not command_re.match(command):
            raise SystemExit, "invalid command name '%s'" % command
        self.commands.append(command)
        try:
            cmd_class = self.get_command_class(command)
        except DistutilsModuleError as msg:
            raise DistutilsArgError, msg

        if not issubclass(cmd_class, Command):
            raise DistutilsClassError, 'command class %s must subclass Command' % cmd_class
        if not (hasattr(cmd_class, 'user_options') and isinstance(cmd_class.user_options, list)):
            raise DistutilsClassError, ('command class %s must provide ' + "'user_options' attribute (a list of tuples)") % cmd_class
        negative_opt = self.negative_opt
        if hasattr(cmd_class, 'negative_opt'):
            negative_opt = negative_opt.copy()
            negative_opt.update(cmd_class.negative_opt)
        if hasattr(cmd_class, 'help_options') and isinstance(cmd_class.help_options, list):
            help_options = fix_help_options(cmd_class.help_options)
        else:
            help_options = []
        parser.set_option_table(self.global_options + cmd_class.user_options + help_options)
        parser.set_negative_aliases(negative_opt)
        args, opts = parser.getopt(args[1:])
        if hasattr(opts, 'help') and opts.help:
            self._show_help(parser, display_options=0, commands=[cmd_class])
            return
        if hasattr(cmd_class, 'help_options'):
            if isinstance(cmd_class.help_options, list):
                help_option_found = 0
                for help_option, short, desc, func in cmd_class.help_options:
                    if hasattr(opts, parser.get_attr_name(help_option)):
                        help_option_found = 1
                        if hasattr(func, '__call__'):
                            func()
                        else:
                            raise DistutilsClassError("invalid help function %r for help option '%s': must be a callable object (function, etc.)" % (func, help_option))

                return help_option_found and None
        opt_dict = self.get_option_dict(command)
        for name, value in vars(opts).items():
            opt_dict[name] = ('command line', value)

        return args

    def finalize_options(self):
        for attr in ('keywords', 'platforms'):
            value = getattr(self.metadata, attr)
            if value is None:
                continue
            if isinstance(value, str):
                value = [ elm.strip() for elm in value.split(',') ]
                setattr(self.metadata, attr, value)

        return

    def _show_help(self, parser, global_options=1, display_options=1, commands=[]):
        from distutils.core import gen_usage
        from distutils.cmd import Command
        if global_options:
            if display_options:
                options = self._get_toplevel_options()
            else:
                options = self.global_options
            parser.set_option_table(options)
            parser.print_help(self.common_usage + '\nGlobal options:')
            print ''
        if display_options:
            parser.set_option_table(self.display_options)
            parser.print_help('Information display options (just display ' + 'information, ignore any commands)')
            print ''
        for command in self.commands:
            if isinstance(command, type) and issubclass(command, Command):
                klass = command
            else:
                klass = self.get_command_class(command)
            if hasattr(klass, 'help_options') and isinstance(klass.help_options, list):
                parser.set_option_table(klass.user_options + fix_help_options(klass.help_options))
            else:
                parser.set_option_table(klass.user_options)
            parser.print_help("Options for '%s' command:" % klass.__name__)
            print ''

        print gen_usage(self.script_name)

    def handle_display_options(self, option_order):
        from distutils.core import gen_usage
        if self.help_commands:
            self.print_commands()
            print ''
            print gen_usage(self.script_name)
            return 1
        any_display_options = 0
        is_display_option = {}
        for option in self.display_options:
            is_display_option[option[0]] = 1

        for opt, val in option_order:
            if val and is_display_option.get(opt):
                opt = translate_longopt(opt)
                value = getattr(self.metadata, 'get_' + opt)()
                if opt in ('keywords', 'platforms'):
                    print ','.join(value)
                elif opt in ('classifiers', 'provides', 'requires', 'obsoletes'):
                    print '\n'.join(value)
                else:
                    print value
                any_display_options = 1

        return any_display_options

    def print_command_list(self, commands, header, max_length):
        print header + ':'
        for cmd in commands:
            klass = self.cmdclass.get(cmd)
            if not klass:
                klass = self.get_command_class(cmd)
            try:
                description = klass.description
            except AttributeError:
                description = '(no description available)'

            print '  %-*s  %s' % (max_length, cmd, description)

    def print_commands(self):
        import distutils.command
        std_commands = distutils.command.__all__
        is_std = {}
        for cmd in std_commands:
            is_std[cmd] = 1

        extra_commands = []
        for cmd in self.cmdclass.keys():
            if not is_std.get(cmd):
                extra_commands.append(cmd)

        max_length = 0
        for cmd in std_commands + extra_commands:
            if len(cmd) > max_length:
                max_length = len(cmd)

        self.print_command_list(std_commands, 'Standard commands', max_length)
        if extra_commands:
            print
            self.print_command_list(extra_commands, 'Extra commands', max_length)

    def get_command_list(self):
        import distutils.command
        std_commands = distutils.command.__all__
        is_std = {}
        for cmd in std_commands:
            is_std[cmd] = 1

        extra_commands = []
        for cmd in self.cmdclass.keys():
            if not is_std.get(cmd):
                extra_commands.append(cmd)

        rv = []
        for cmd in std_commands + extra_commands:
            klass = self.cmdclass.get(cmd)
            if not klass:
                klass = self.get_command_class(cmd)
            try:
                description = klass.description
            except AttributeError:
                description = '(no description available)'

            rv.append((cmd, description))

        return rv

    def get_command_packages(self):
        pkgs = self.command_packages
        if not isinstance(pkgs, list):
            if pkgs is None:
                pkgs = ''
            pkgs = [ pkg.strip() for pkg in pkgs.split(',') if pkg != '' ]
            if 'distutils.command' not in pkgs:
                pkgs.insert(0, 'distutils.command')
            self.command_packages = pkgs
        return pkgs

    def get_command_class(self, command):
        klass = self.cmdclass.get(command)
        if klass:
            return klass
        for pkgname in self.get_command_packages():
            module_name = '%s.%s' % (pkgname, command)
            klass_name = command
            try:
                __import__(module_name)
                module = sys.modules[module_name]
            except ImportError:
                continue

            try:
                klass = getattr(module, klass_name)
            except AttributeError:
                raise DistutilsModuleError, "invalid command '%s' (no class '%s' in module '%s')" % (command, klass_name, module_name)

            self.cmdclass[command] = klass
            return klass

        raise DistutilsModuleError("invalid command '%s'" % command)

    def get_command_obj(self, command, create=1):
        cmd_obj = self.command_obj.get(command)
        if not cmd_obj and create:
            if DEBUG:
                self.announce("Distribution.get_command_obj(): creating '%s' command object" % command)
            klass = self.get_command_class(command)
            cmd_obj = self.command_obj[command] = klass(self)
            self.have_run[command] = 0
            options = self.command_options.get(command)
            if options:
                self._set_command_options(cmd_obj, options)
        return cmd_obj

    def _set_command_options(self, command_obj, option_dict=None):
        command_name = command_obj.get_command_name()
        if option_dict is None:
            option_dict = self.get_option_dict(command_name)
        if DEBUG:
            self.announce("  setting options for '%s' command:" % command_name)
        for option, (source, value) in option_dict.items():
            if DEBUG:
                self.announce('    %s = %s (from %s)' % (option, value, source))
            try:
                bool_opts = map(translate_longopt, command_obj.boolean_options)
            except AttributeError:
                bool_opts = []

            try:
                neg_opt = command_obj.negative_opt
            except AttributeError:
                neg_opt = {}

            try:
                is_string = isinstance(value, str)
                if option in neg_opt and is_string:
                    setattr(command_obj, neg_opt[option], not strtobool(value))
                elif option in bool_opts and is_string:
                    setattr(command_obj, option, strtobool(value))
                elif hasattr(command_obj, option):
                    setattr(command_obj, option, value)
                else:
                    raise DistutilsOptionError, "error in %s: command '%s' has no such option '%s'" % (source, command_name, option)
            except ValueError as msg:
                raise DistutilsOptionError, msg

        return

    def reinitialize_command(self, command, reinit_subcommands=0):
        from distutils.cmd import Command
        if not isinstance(command, Command):
            command_name = command
            command = self.get_command_obj(command_name)
        else:
            command_name = command.get_command_name()
        if not command.finalized:
            return command
        command.initialize_options()
        command.finalized = 0
        self.have_run[command_name] = 0
        self._set_command_options(command)
        if reinit_subcommands:
            for sub in command.get_sub_commands():
                self.reinitialize_command(sub, reinit_subcommands)

        return command

    def announce(self, msg, level=log.INFO):
        log.log(level, msg)

    def run_commands(self):
        for cmd in self.commands:
            self.run_command(cmd)

    def run_command(self, command):
        if self.have_run.get(command):
            return
        log.info('running %s', command)
        cmd_obj = self.get_command_obj(command)
        cmd_obj.ensure_finalized()
        cmd_obj.run()
        self.have_run[command] = 1

    def has_pure_modules(self):
        return len(self.packages or self.py_modules or []) > 0

    def has_ext_modules(self):
        return self.ext_modules and len(self.ext_modules) > 0

    def has_c_libraries(self):
        return self.libraries and len(self.libraries) > 0

    def has_modules(self):
        return self.has_pure_modules() or self.has_ext_modules()

    def has_headers(self):
        return self.headers and len(self.headers) > 0

    def has_scripts(self):
        return self.scripts and len(self.scripts) > 0

    def has_data_files(self):
        return self.data_files and len(self.data_files) > 0

    def is_pure(self):
        return self.has_pure_modules() and not self.has_ext_modules() and not self.has_c_libraries()


class DistributionMetadata():
    _METHOD_BASENAMES = ('name', 'version', 'author', 'author_email', 'maintainer', 'maintainer_email', 'url', 'license', 'description', 'long_description', 'keywords', 'platforms', 'fullname', 'contact', 'contact_email', 'license', 'classifiers', 'download_url', 'provides', 'requires', 'obsoletes')

    def __init__(self, path=None):
        if path is not None:
            self.read_pkg_file(open(path))
        else:
            self.name = None
            self.version = None
            self.author = None
            self.author_email = None
            self.maintainer = None
            self.maintainer_email = None
            self.url = None
            self.license = None
            self.description = None
            self.long_description = None
            self.keywords = None
            self.platforms = None
            self.classifiers = None
            self.download_url = None
            self.provides = None
            self.requires = None
            self.obsoletes = None
        return

    def read_pkg_file(self, file):
        msg = message_from_file(file)

        def _read_field(name):
            value = msg[name]
            return None if value == 'UNKNOWN' else value

        def _read_list(name):
            values = msg.get_all(name, None)
            return None if values == [] else values

        metadata_version = msg['metadata-version']
        self.name = _read_field('name')
        self.version = _read_field('version')
        self.description = _read_field('summary')
        self.author = _read_field('author')
        self.maintainer = None
        self.author_email = _read_field('author-email')
        self.maintainer_email = None
        self.url = _read_field('home-page')
        self.license = _read_field('license')
        if 'download-url' in msg:
            self.download_url = _read_field('download-url')
        else:
            self.download_url = None
        self.long_description = _read_field('description')
        self.description = _read_field('summary')
        if 'keywords' in msg:
            self.keywords = _read_field('keywords').split(',')
        self.platforms = _read_list('platform')
        self.classifiers = _read_list('classifier')
        if metadata_version == '1.1':
            self.requires = _read_list('requires')
            self.provides = _read_list('provides')
            self.obsoletes = _read_list('obsoletes')
        else:
            self.requires = None
            self.provides = None
            self.obsoletes = None
        return

    def write_pkg_info(self, base_dir):
        pkg_info = open(os.path.join(base_dir, 'PKG-INFO'), 'w')
        try:
            self.write_pkg_file(pkg_info)
        finally:
            pkg_info.close()

    def write_pkg_file(self, file):
        version = '1.0'
        if self.provides or self.requires or self.obsoletes or self.classifiers or self.download_url:
            version = '1.1'
        self._write_field(file, 'Metadata-Version', version)
        self._write_field(file, 'Name', self.get_name())
        self._write_field(file, 'Version', self.get_version())
        self._write_field(file, 'Summary', self.get_description())
        self._write_field(file, 'Home-page', self.get_url())
        self._write_field(file, 'Author', self.get_contact())
        self._write_field(file, 'Author-email', self.get_contact_email())
        self._write_field(file, 'License', self.get_license())
        if self.download_url:
            self._write_field(file, 'Download-URL', self.download_url)
        long_desc = rfc822_escape(self.get_long_description())
        self._write_field(file, 'Description', long_desc)
        keywords = ','.join(self.get_keywords())
        if keywords:
            self._write_field(file, 'Keywords', keywords)
        self._write_list(file, 'Platform', self.get_platforms())
        self._write_list(file, 'Classifier', self.get_classifiers())
        self._write_list(file, 'Requires', self.get_requires())
        self._write_list(file, 'Provides', self.get_provides())
        self._write_list(file, 'Obsoletes', self.get_obsoletes())

    def _write_field(self, file, name, value):
        file.write('%s: %s\n' % (name, self._encode_field(value)))

    def _write_list(self, file, name, values):
        for value in values:
            self._write_field(file, name, value)

    def _encode_field(self, value):
        if value is None:
            return
        else:
            return value.encode(PKG_INFO_ENCODING) if isinstance(value, unicode) else str(value)

    def get_name(self):
        return self.name or 'UNKNOWN'

    def get_version(self):
        return self.version or '0.0.0'

    def get_fullname(self):
        return '%s-%s' % (self.get_name(), self.get_version())

    def get_author(self):
        return self._encode_field(self.author) or 'UNKNOWN'

    def get_author_email(self):
        return self.author_email or 'UNKNOWN'

    def get_maintainer(self):
        return self._encode_field(self.maintainer) or 'UNKNOWN'

    def get_maintainer_email(self):
        return self.maintainer_email or 'UNKNOWN'

    def get_contact(self):
        return self._encode_field(self.maintainer) or self._encode_field(self.author) or 'UNKNOWN'

    def get_contact_email(self):
        return self.maintainer_email or self.author_email or 'UNKNOWN'

    def get_url(self):
        return self.url or 'UNKNOWN'

    def get_license(self):
        return self.license or 'UNKNOWN'

    get_licence = get_license

    def get_description(self):
        return self._encode_field(self.description) or 'UNKNOWN'

    def get_long_description(self):
        return self._encode_field(self.long_description) or 'UNKNOWN'

    def get_keywords(self):
        return self.keywords or []

    def get_platforms(self):
        return self.platforms or ['UNKNOWN']

    def get_classifiers(self):
        return self.classifiers or []

    def get_download_url(self):
        return self.download_url or 'UNKNOWN'

    def get_requires(self):
        return self.requires or []

    def set_requires(self, value):
        import distutils.versionpredicate
        for v in value:
            distutils.versionpredicate.VersionPredicate(v)

        self.requires = value

    def get_provides(self):
        return self.provides or []

    def set_provides(self, value):
        value = [ v.strip() for v in value ]
        for v in value:
            import distutils.versionpredicate
            distutils.versionpredicate.split_provision(v)

        self.provides = value

    def get_obsoletes(self):
        return self.obsoletes or []

    def set_obsoletes(self, value):
        import distutils.versionpredicate
        for v in value:
            distutils.versionpredicate.VersionPredicate(v)

        self.obsoletes = value


def fix_help_options(options):
    new_options = []
    for help_tuple in options:
        new_options.append(help_tuple[0:3])

    return new_options
