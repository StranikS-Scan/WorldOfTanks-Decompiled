# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/dist.py
# Compiled at: 2010-05-25 20:46:16
"""distutils.dist

Provides the Distribution class, which represents the module distribution
being built/installed/distributed.
"""
__revision__ = '$Id: dist.py 68035 2008-12-29 22:36:22Z tarek.ziade $'
import sys, os, string, re
from types import *
from copy import copy
try:
    import warnings
except ImportError:
    warnings = None

from distutils.errors import *
from distutils.fancy_getopt import FancyGetopt, translate_longopt
from distutils.util import check_environ, strtobool, rfc822_escape
from distutils import log
from distutils.debug import DEBUG
PKG_INFO_ENCODING = 'utf-8'
command_re = re.compile('^[a-zA-Z]([a-zA-Z0-9_]*)$')

class Distribution():
    """The core of the Distutils.  Most of the work hiding behind 'setup'
    is really done within a Distribution instance, which farms the work out
    to the Distutils commands specified on the command line.
    
    Setup scripts will almost never instantiate Distribution directly,
    unless the 'setup()' function is totally inadequate to their needs.
    However, it is conceivable that a setup script might wish to subclass
    Distribution for some specialized purpose, and then pass the subclass
    to 'setup()' as the 'distclass' keyword argument.  If so, it is
    necessary to respect the expectations that 'setup' has of Distribution.
    See the code for 'setup()', in core.py, for details.
    """
    global_options = [('verbose', 'v', 'run verbosely (default)', 1),
     ('quiet', 'q', 'run quietly (turns verbosity off)'),
     ('dry-run', 'n', "don't actually do anything"),
     ('help', 'h', 'show detailed help message')]
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
        """Construct a new Distribution instance: initialize all the
        attributes of a Distribution, and then use 'attrs' (a dictionary
        mapping attribute names to values) to assign some of those
        attributes their "real" values.  (Any attributes not mentioned in
        'attrs' will be assigned to some null value: 0, None, an empty list
        or dictionary, etc.)  Most importantly, initialize the
        'command_obj' attribute to the empty dictionary; this will be
        filled in with real command objects by 'parse_command_line()'.
        """
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
                elif hasattr(self.metadata, key):
                    setattr(self.metadata, key, val)
                elif hasattr(self, key):
                    setattr(self, key, val)
                else:
                    msg = 'Unknown distribution option: %s' % repr(key)
                    if warnings is not None:
                        warnings.warn(msg)
                    else:
                        sys.stderr.write(msg + '\n')

        self.finalize_options()
        return

    def get_option_dict(self, command):
        """Get the option dictionary for a given command.  If that
        command's option dictionary hasn't been created yet, then create it
        and return the new dictionary; otherwise, return the existing
        option dictionary.
        """
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
            print indent + header
            indent = indent + '  '
        if not commands:
            print indent + 'no commands known yet'
            return
        else:
            for cmd_name in commands:
                opt_dict = self.command_options.get(cmd_name)
                if opt_dict is None:
                    print indent + "no option dict for '%s' command" % cmd_name
                else:
                    print indent + "option dict for '%s' command:" % cmd_name
                    out = pformat(opt_dict)
                    for line in string.split(out, '\n'):
                        print indent + '  ' + line

            return

    def find_config_files(self):
        """Find as many configuration files as should be processed for this
        platform, and return a list of filenames in the order in which they
        should be parsed.  The filenames returned are guaranteed to exist
        (modulo nasty race conditions).
        
        There are three possible config files: distutils.cfg in the
        Distutils installation directory (ie. where the top-level
        Distutils __inst__.py file lives), a file in the user's home
        directory named .pydistutils.cfg on Unix and pydistutils.cfg
        on Windows/Mac, and setup.cfg in the current directory.
        """
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
        user_file = os.path.join(os.path.expanduser('~'), user_filename)
        if os.path.isfile(user_file):
            files.append(user_file)
        local_file = 'setup.cfg'
        if os.path.isfile(local_file):
            files.append(local_file)
        return files

    def parse_config_files(self, filenames=None):
        from ConfigParser import ConfigParser
        if filenames is None:
            filenames = self.find_config_files()
        if DEBUG:
            print 'Distribution.parse_config_files():'
        parser = ConfigParser()
        for filename in filenames:
            if DEBUG:
                print '  reading', filename
            parser.read(filename)
            for section in parser.sections():
                options = parser.options(section)
                opt_dict = self.get_option_dict(section)
                for opt in options:
                    if opt != '__name__':
                        val = parser.get(section, opt)
                        opt = string.replace(opt, '-', '_')
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
        """Parse the setup script's command line, taken from the
        'script_args' instance attribute (which defaults to 'sys.argv[1:]'
        -- see 'setup()' in core.py).  This list is first processed for
        "global options" -- options that set attributes of the Distribution
        instance.  Then, it is alternately scanned for Distutils commands
        and options for that command.  Each new command terminates the
        options for the previous command.  The allowed options for a
        command are determined by the 'user_options' attribute of the
        command class -- thus, we have to be able to load command classes
        in order to parse the command line.  Any error in that 'options'
        attribute raises DistutilsGetoptError; any error on the
        command-line raises DistutilsArgError.  If no Distutils commands
        were found on the command line, raises DistutilsArgError.  Return
        true if command-line was successfully parsed and we should carry
        on with executing commands; false if no errors but we shouldn't
        execute commands (currently, this only happens if user asks for
        help).
        """
        toplevel_options = self._get_toplevel_options()
        if sys.platform == 'mac':
            import EasyDialogs
            cmdlist = self.get_command_list()
            self.script_args = EasyDialogs.GetArgv(toplevel_options + self.display_options, cmdlist)
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
            while 1:
                if args:
                    args = self._parse_command_opts(parser, args)
                    return args is None and None

            if self.help:
                self._show_help(parser, display_options=len(self.commands) == 0, commands=self.commands)
                return
            if not self.commands:
                raise DistutilsArgError, 'no commands supplied'
            return 1

    def _get_toplevel_options(self):
        """Return the non-display options recognized at the top level.
        
        This includes options that are recognized *only* at the top
        level as well as options recognized for commands.
        """
        return self.global_options + [('command-packages=', None, 'list of packages that provide distutils commands')]

    def _parse_command_opts(self, parser, args):
        """Parse the command-line options for a single command.
        'parser' must be a FancyGetopt instance; 'args' must be the list
        of arguments, starting with the current command (whose options
        we are about to parse).  Returns a new version of 'args' with
        the next command at the front of the list; will be the empty
        list if there are no more commands on the command line.  Returns
        None if the user asked for help on this command.
        """
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
        if hasattr(cmd_class, 'user_options'):
            if not type(cmd_class.user_options) is ListType:
                raise DistutilsClassError, ('command class %s must provide ' + "'user_options' attribute (a list of tuples)") % cmd_class
            negative_opt = self.negative_opt
            if hasattr(cmd_class, 'negative_opt'):
                negative_opt = copy(negative_opt)
                negative_opt.update(cmd_class.negative_opt)
            if hasattr(cmd_class, 'help_options') and type(cmd_class.help_options) is ListType:
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
                help_option_found = type(cmd_class.help_options) is ListType and 0
                for help_option, short, desc, func in cmd_class.help_options:
                    if hasattr(opts, parser.get_attr_name(help_option)):
                        help_option_found = 1
                        if callable(func):
                            func()
                        else:
                            raise DistutilsClassError("invalid help function %r for help option '%s': must be a callable object (function, etc.)" % (func, help_option))

                return help_option_found and None
        opt_dict = self.get_option_dict(command)
        for name, value in vars(opts).items():
            opt_dict[name] = ('command line', value)

        return args

    def finalize_options(self):
        """Set final values for all the options on the Distribution
        instance, analogous to the .finalize_options() method of Command
        objects.
        """
        keywords = self.metadata.keywords
        if keywords is not None:
            if type(keywords) is StringType:
                keywordlist = string.split(keywords, ',')
                self.metadata.keywords = map(string.strip, keywordlist)
        platforms = self.metadata.platforms
        if platforms is not None:
            if type(platforms) is StringType:
                platformlist = string.split(platforms, ',')
                self.metadata.platforms = map(string.strip, platformlist)
        return

    def _show_help(self, parser, global_options=1, display_options=1, commands=[]):
        """Show help for the setup script command-line in the form of
        several lists of command-line options.  'parser' should be a
        FancyGetopt instance; do not expect it to be returned in the
        same state, as its option table will be reset to make it
        generate the correct help text.
        
        If 'global_options' is true, lists the global options:
        --verbose, --dry-run, etc.  If 'display_options' is true, lists
        the "display-only" options: --name, --version, etc.  Finally,
        lists per-command help for every command name or command class
        in 'commands'.
        """
        from distutils.core import gen_usage
        from distutils.cmd import Command
        if global_options:
            if display_options:
                options = self._get_toplevel_options()
            else:
                options = self.global_options
            parser.set_option_table(options)
            parser.print_help(self.common_usage + '\nGlobal options:')
            print
        if display_options:
            parser.set_option_table(self.display_options)
            parser.print_help('Information display options (just display ' + 'information, ignore any commands)')
            print
        for command in self.commands:
            if type(command) is ClassType and issubclass(command, Command):
                klass = command
            else:
                klass = self.get_command_class(command)
            if hasattr(klass, 'help_options') and type(klass.help_options) is ListType:
                parser.set_option_table(klass.user_options + fix_help_options(klass.help_options))
            else:
                parser.set_option_table(klass.user_options)
            parser.print_help("Options for '%s' command:" % klass.__name__)
            print

        print gen_usage(self.script_name)

    def handle_display_options(self, option_order):
        """If there were any non-global "display-only" options
        (--help-commands or the metadata display options) on the command
        line, display the requested info and return true; else return
        false.
        """
        from distutils.core import gen_usage
        if self.help_commands:
            self.print_commands()
            print
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
                    print string.join(value, ',')
                elif opt in ('classifiers', 'provides', 'requires', 'obsoletes'):
                    print string.join(value, '\n')
                else:
                    print value
                any_display_options = 1

        return any_display_options

    def print_command_list(self, commands, header, max_length):
        """Print a subset of the list of all commands -- used by
        'print_commands()'.
        """
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
        """Print out a help message listing all available commands with a
        description of each.  The list is divided into "standard commands"
        (listed in distutils.command.__all__) and "extra commands"
        (mentioned in self.cmdclass, but not a standard command).  The
        descriptions come from the command class attribute
        'description'.
        """
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
        """Get a list of (command, description) tuples.
        The list is divided into "standard commands" (listed in
        distutils.command.__all__) and "extra commands" (mentioned in
        self.cmdclass, but not a standard command).  The descriptions come
        from the command class attribute 'description'.
        """
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
        """Return a list of packages from which commands are loaded."""
        pkgs = self.command_packages
        if not isinstance(pkgs, type([])):
            pkgs = string.split(pkgs or '', ',')
            for i in range(len(pkgs)):
                pkgs[i] = string.strip(pkgs[i])

            pkgs = filter(None, pkgs)
            if 'distutils.command' not in pkgs:
                pkgs.insert(0, 'distutils.command')
            self.command_packages = pkgs
        return pkgs

    def get_command_class(self, command):
        """Return the class that implements the Distutils command named by
        'command'.  First we check the 'cmdclass' dictionary; if the
        command is mentioned there, we fetch the class object from the
        dictionary and return it.  Otherwise we load the command module
        ("distutils.command." + command) and fetch the command class from
        the module.  The loaded class is also stored in 'cmdclass'
        to speed future calls to 'get_command_class()'.
        
        Raises DistutilsModuleError if the expected module could not be
        found, or if that module does not define the expected class.
        """
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
        """Return the command object for 'command'.  Normally this object
        is cached on a previous call to 'get_command_obj()'; if no command
        object for 'command' is in the cache, then we either create and
        return it (if 'create' is true) or return None.
        """
        cmd_obj = self.command_obj.get(command)
        if not cmd_obj and create:
            if DEBUG:
                print "Distribution.get_command_obj(): creating '%s' command object" % command
            klass = self.get_command_class(command)
            cmd_obj = self.command_obj[command] = klass(self)
            self.have_run[command] = 0
            options = self.command_options.get(command)
            if options:
                self._set_command_options(cmd_obj, options)
        return cmd_obj

    def _set_command_options(self, command_obj, option_dict=None):
        """Set the options for 'command_obj' from 'option_dict'.  Basically
        this means copying elements of a dictionary ('option_dict') to
        attributes of an instance ('command').
        
        'command_obj' must be a Command instance.  If 'option_dict' is not
        supplied, uses the standard option dictionary for this command
        (from 'self.command_options').
        """
        command_name = command_obj.get_command_name()
        if option_dict is None:
            option_dict = self.get_option_dict(command_name)
        if DEBUG:
            print "  setting options for '%s' command:" % command_name
        for option, (source, value) in option_dict.items():
            if DEBUG:
                print '    %s = %s (from %s)' % (option, value, source)
            try:
                bool_opts = map(translate_longopt, command_obj.boolean_options)
            except AttributeError:
                bool_opts = []

            try:
                neg_opt = command_obj.negative_opt
            except AttributeError:
                neg_opt = {}

            try:
                is_string = type(value) is StringType
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
        """Reinitializes a command to the state it was in when first
        returned by 'get_command_obj()': ie., initialized but not yet
        finalized.  This provides the opportunity to sneak option
        values in programmatically, overriding or supplementing
        user-supplied values from the config files and command line.
        You'll have to re-finalize the command object (by calling
        'finalize_options()' or 'ensure_finalized()') before using it for
        real.
        
        'command' should be a command name (string) or command object.  If
        'reinit_subcommands' is true, also reinitializes the command's
        sub-commands, as declared by the 'sub_commands' class attribute (if
        it has one).  See the "install" command for an example.  Only
        reinitializes the sub-commands that actually matter, ie. those
        whose test predicates return true.
        
        Returns the reinitialized command object.
        """
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

    def announce(self, msg, level=1):
        log.debug(msg)

    def run_commands(self):
        """Run each command that was seen on the setup script command line.
        Uses the list of commands found and cache of command objects
        created by 'get_command_obj()'.
        """
        for cmd in self.commands:
            self.run_command(cmd)

    def run_command(self, command):
        """Do whatever it takes to run a command (including nothing at all,
        if the command has already been run).  Specifically: if we have
        already created and run the command named by 'command', return
        silently without doing anything.  If the command named by 'command'
        doesn't even have a command object yet, create one.  Then invoke
        'run()' on that command object (or an existing one).
        """
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
    """Dummy class to hold the distribution meta-data: name, version,
    author, and so forth.
    """
    _METHOD_BASENAMES = ('name', 'version', 'author', 'author_email', 'maintainer', 'maintainer_email', 'url', 'license', 'description', 'long_description', 'keywords', 'platforms', 'fullname', 'contact', 'contact_email', 'license', 'classifiers', 'download_url', 'provides', 'requires', 'obsoletes')

    def __init__(self):
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

    def write_pkg_info(self, base_dir):
        """Write the PKG-INFO file into the release tree.
        """
        pkg_info = open(os.path.join(base_dir, 'PKG-INFO'), 'w')
        self.write_pkg_file(pkg_info)
        pkg_info.close()

    def write_pkg_file(self, file):
        """Write the PKG-INFO format data to a file object.
        """
        version = '1.0'
        if self.provides or self.requires or self.obsoletes:
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
        keywords = string.join(self.get_keywords(), ',')
        if keywords:
            self._write_field(file, 'Keywords', keywords)
        self._write_list(file, 'Platform', self.get_platforms())
        self._write_list(file, 'Classifier', self.get_classifiers())
        self._write_list(file, 'Requires', self.get_requires())
        self._write_list(file, 'Provides', self.get_provides())
        self._write_list(file, 'Obsoletes', self.get_obsoletes())

    def _write_field(self, file, name, value):
        if isinstance(value, unicode):
            value = value.encode(PKG_INFO_ENCODING)
        else:
            value = str(value)
        file.write('%s: %s\n' % (name, value))

    def _write_list(self, file, name, values):
        for value in values:
            self._write_field(file, name, value)

    def get_name--- This code section failed: ---

1132       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'name'
           6	JUMP_IF_TRUE      '12'

Syntax error at or near 'LOAD_ATTR' token at offset 3

    def get_version--- This code section failed: ---

1135       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'version'
           6	JUMP_IF_TRUE      '12'

Syntax error at or near 'LOAD_ATTR' token at offset 3

    def get_fullname(self):
        return '%s-%s' % (self.get_name(), self.get_version())

    def get_author--- This code section failed: ---

1141       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'author'
           6	JUMP_IF_TRUE      '12'

Syntax error at or near 'LOAD_ATTR' token at offset 3

    def get_author_email--- This code section failed: ---

1144       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'author_email'
           6	JUMP_IF_TRUE      '12'

Syntax error at or near 'LOAD_ATTR' token at offset 3

    def get_maintainer--- This code section failed: ---

1147       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'maintainer'
           6	JUMP_IF_TRUE      '12'

Syntax error at or near 'LOAD_ATTR' token at offset 3

    def get_maintainer_email--- This code section failed: ---

1150       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'maintainer_email'
           6	JUMP_IF_TRUE      '12'

Syntax error at or near 'LOAD_ATTR' token at offset 3

    def get_contact--- This code section failed: ---

1153       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'maintainer'
           6	JUMP_IF_TRUE      '21'

1154       9	LOAD_FAST         'self'
          12	LOAD_ATTR         'author'
          15	JUMP_IF_TRUE      '21'

Syntax error at or near 'LOAD_ATTR' token at offset 12

    def get_contact_email--- This code section failed: ---

1158       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'maintainer_email'
           6	JUMP_IF_TRUE      '21'

1159       9	LOAD_FAST         'self'
          12	LOAD_ATTR         'author_email'
          15	JUMP_IF_TRUE      '21'

Syntax error at or near 'LOAD_ATTR' token at offset 12

    def get_url--- This code section failed: ---

1163       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'url'
           6	JUMP_IF_TRUE      '12'

Syntax error at or near 'LOAD_ATTR' token at offset 3

    def get_license--- This code section failed: ---

1166       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'license'
           6	JUMP_IF_TRUE      '12'

Syntax error at or near 'LOAD_ATTR' token at offset 3

    get_licence = get_license

    def get_description--- This code section failed: ---

1170       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'description'
           6	JUMP_IF_TRUE      '12'

Syntax error at or near 'LOAD_ATTR' token at offset 3

    def get_long_description--- This code section failed: ---

1173       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'long_description'
           6	JUMP_IF_TRUE      '12'

Syntax error at or near 'LOAD_ATTR' token at offset 3

    def get_keywords(self):
        return self.keywords or []

    def get_platforms(self):
        return self.platforms or ['UNKNOWN']

    def get_classifiers(self):
        return self.classifiers or []

    def get_download_url--- This code section failed: ---

1185       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'download_url'
           6	JUMP_IF_TRUE      '12'

Syntax error at or near 'LOAD_ATTR' token at offset 3

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
    """Convert a 4-tuple 'help_options' list as found in various command
    classes to the 3-tuple form required by FancyGetopt.
    """
    new_options = []
    for help_tuple in options:
        new_options.append(help_tuple[0:3])

    return new_options


if __name__ == '__main__':
    dist = Distribution()
    print 'ok'