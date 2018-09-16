# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/cmd.py
__revision__ = '$Id$'
import sys, os, re
from distutils.errors import DistutilsOptionError
from distutils import util, dir_util, file_util, archive_util, dep_util
from distutils import log

class Command():
    sub_commands = []

    def __init__(self, dist):
        from distutils.dist import Distribution
        if not isinstance(dist, Distribution):
            raise TypeError, 'dist must be a Distribution instance'
        if self.__class__ is Command:
            raise RuntimeError, 'Command is an abstract class'
        self.distribution = dist
        self.initialize_options()
        self._dry_run = None
        self.verbose = dist.verbose
        self.force = None
        self.help = 0
        self.finalized = 0
        return

    def __getattr__(self, attr):
        if attr == 'dry_run':
            myval = getattr(self, '_' + attr)
            if myval is None:
                return getattr(self.distribution, attr)
            else:
                return myval
        else:
            raise AttributeError, attr
        return

    def ensure_finalized(self):
        if not self.finalized:
            self.finalize_options()
        self.finalized = 1

    def initialize_options(self):
        raise RuntimeError, 'abstract method -- subclass %s must override' % self.__class__

    def finalize_options(self):
        raise RuntimeError, 'abstract method -- subclass %s must override' % self.__class__

    def dump_options(self, header=None, indent=''):
        from distutils.fancy_getopt import longopt_xlate
        if header is None:
            header = "command options for '%s':" % self.get_command_name()
        self.announce(indent + header, level=log.INFO)
        indent = indent + '  '
        for option, _, _ in self.user_options:
            option = option.translate(longopt_xlate)
            if option[-1] == '=':
                option = option[:-1]
            value = getattr(self, option)
            self.announce(indent + '%s = %s' % (option, value), level=log.INFO)

        return

    def run(self):
        raise RuntimeError, 'abstract method -- subclass %s must override' % self.__class__

    def announce(self, msg, level=1):
        log.log(level, msg)

    def debug_print(self, msg):
        from distutils.debug import DEBUG
        if DEBUG:
            print msg
            sys.stdout.flush()

    def _ensure_stringlike(self, option, what, default=None):
        val = getattr(self, option)
        if val is None:
            setattr(self, option, default)
            return default
        else:
            if not isinstance(val, str):
                raise DistutilsOptionError, "'%s' must be a %s (got `%s`)" % (option, what, val)
            return val

    def ensure_string(self, option, default=None):
        self._ensure_stringlike(option, 'string', default)

    def ensure_string_list(self, option):
        val = getattr(self, option)
        if val is None:
            return
        else:
            if isinstance(val, str):
                setattr(self, option, re.split(',\\s*|\\s+', val))
            else:
                if isinstance(val, list):
                    ok = 1
                    for element in val:
                        if not isinstance(element, str):
                            ok = 0
                            break

                else:
                    ok = 0
                if not ok:
                    raise DistutilsOptionError, "'%s' must be a list of strings (got %r)" % (option, val)
            return

    def _ensure_tested_string(self, option, tester, what, error_fmt, default=None):
        val = self._ensure_stringlike(option, what, default)
        if val is not None and not tester(val):
            raise DistutilsOptionError, ("error in '%s' option: " + error_fmt) % (option, val)
        return

    def ensure_filename(self, option):
        self._ensure_tested_string(option, os.path.isfile, 'filename', "'%s' does not exist or is not a file")

    def ensure_dirname(self, option):
        self._ensure_tested_string(option, os.path.isdir, 'directory name', "'%s' does not exist or is not a directory")

    def get_command_name(self):
        if hasattr(self, 'command_name'):
            return self.command_name
        else:
            return self.__class__.__name__

    def set_undefined_options(self, src_cmd, *option_pairs):
        src_cmd_obj = self.distribution.get_command_obj(src_cmd)
        src_cmd_obj.ensure_finalized()
        for src_option, dst_option in option_pairs:
            if getattr(self, dst_option) is None:
                setattr(self, dst_option, getattr(src_cmd_obj, src_option))

        return

    def get_finalized_command(self, command, create=1):
        cmd_obj = self.distribution.get_command_obj(command, create)
        cmd_obj.ensure_finalized()
        return cmd_obj

    def reinitialize_command(self, command, reinit_subcommands=0):
        return self.distribution.reinitialize_command(command, reinit_subcommands)

    def run_command(self, command):
        self.distribution.run_command(command)

    def get_sub_commands(self):
        commands = []
        for cmd_name, method in self.sub_commands:
            if method is None or method(self):
                commands.append(cmd_name)

        return commands

    def warn(self, msg):
        log.warn('warning: %s: %s\n' % (self.get_command_name(), msg))

    def execute(self, func, args, msg=None, level=1):
        util.execute(func, args, msg, dry_run=self.dry_run)

    def mkpath(self, name, mode=511):
        dir_util.mkpath(name, mode, dry_run=self.dry_run)

    def copy_file(self, infile, outfile, preserve_mode=1, preserve_times=1, link=None, level=1):
        return file_util.copy_file(infile, outfile, preserve_mode, preserve_times, not self.force, link, dry_run=self.dry_run)

    def copy_tree(self, infile, outfile, preserve_mode=1, preserve_times=1, preserve_symlinks=0, level=1):
        return dir_util.copy_tree(infile, outfile, preserve_mode, preserve_times, preserve_symlinks, not self.force, dry_run=self.dry_run)

    def move_file(self, src, dst, level=1):
        return file_util.move_file(src, dst, dry_run=self.dry_run)

    def spawn(self, cmd, search_path=1, level=1):
        from distutils.spawn import spawn
        spawn(cmd, search_path, dry_run=self.dry_run)

    def make_archive(self, base_name, format, root_dir=None, base_dir=None, owner=None, group=None):
        return archive_util.make_archive(base_name, format, root_dir, base_dir, dry_run=self.dry_run, owner=owner, group=group)

    def make_file(self, infiles, outfile, func, args, exec_msg=None, skip_msg=None, level=1):
        if skip_msg is None:
            skip_msg = 'skipping %s (inputs unchanged)' % outfile
        if isinstance(infiles, str):
            infiles = (infiles,)
        elif not isinstance(infiles, (list, tuple)):
            raise TypeError, "'infiles' must be a string, or a list or tuple of strings"
        if exec_msg is None:
            exec_msg = 'generating %s from %s' % (outfile, ', '.join(infiles))
        if self.force or dep_util.newer_group(infiles, outfile):
            self.execute(func, args, exec_msg, level)
        else:
            log.debug(skip_msg)
        return


class install_misc(Command):
    user_options = [('install-dir=', 'd', 'directory to install the files to')]

    def initialize_options(self):
        self.install_dir = None
        self.outfiles = []
        return

    def _install_dir_from(self, dirname):
        self.set_undefined_options('install', (dirname, 'install_dir'))

    def _copy_files(self, filelist):
        self.outfiles = []
        if not filelist:
            return
        self.mkpath(self.install_dir)
        for f in filelist:
            self.copy_file(f, self.install_dir)
            self.outfiles.append(os.path.join(self.install_dir, f))

    def get_outputs(self):
        return self.outfiles
