# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/core.py
__revision__ = '$Id$'
import sys
import os
from distutils.debug import DEBUG
from distutils.errors import DistutilsSetupError, DistutilsArgError, DistutilsError, CCompilerError
from distutils.dist import Distribution
from distutils.cmd import Command
from distutils.config import PyPIRCCommand
from distutils.extension import Extension
USAGE = 'usage: %(script)s [global_opts] cmd1 [cmd1_opts] [cmd2 [cmd2_opts] ...]\n   or: %(script)s --help [cmd1 cmd2 ...]\n   or: %(script)s --help-commands\n   or: %(script)s cmd --help\n'

def gen_usage(script_name):
    script = os.path.basename(script_name)
    return USAGE % {'script': script}


_setup_stop_after = None
_setup_distribution = None
setup_keywords = ('distclass', 'script_name', 'script_args', 'options', 'name', 'version', 'author', 'author_email', 'maintainer', 'maintainer_email', 'url', 'license', 'description', 'long_description', 'keywords', 'platforms', 'classifiers', 'download_url', 'requires', 'provides', 'obsoletes')
extension_keywords = ('name', 'sources', 'include_dirs', 'define_macros', 'undef_macros', 'library_dirs', 'libraries', 'runtime_library_dirs', 'extra_objects', 'extra_compile_args', 'extra_link_args', 'swig_opts', 'export_symbols', 'depends', 'language')

def setup(**attrs):
    global _setup_stop_after
    global _setup_distribution
    klass = attrs.get('distclass')
    if klass:
        del attrs['distclass']
    else:
        klass = Distribution
    if 'script_name' not in attrs:
        attrs['script_name'] = os.path.basename(sys.argv[0])
    if 'script_args' not in attrs:
        attrs['script_args'] = sys.argv[1:]
    try:
        _setup_distribution = dist = klass(attrs)
    except DistutilsSetupError as msg:
        if 'name' in attrs:
            raise SystemExit, 'error in %s setup command: %s' % (attrs['name'], msg)
        else:
            raise SystemExit, 'error in setup command: %s' % msg

    if _setup_stop_after == 'init':
        return dist
    dist.parse_config_files()
    if DEBUG:
        print 'options (after parsing config files):'
        dist.dump_option_dicts()
    if _setup_stop_after == 'config':
        return dist
    try:
        ok = dist.parse_command_line()
    except DistutilsArgError as msg:
        raise SystemExit, gen_usage(dist.script_name) + '\nerror: %s' % msg

    if DEBUG:
        print 'options (after parsing command line):'
        dist.dump_option_dicts()
    if _setup_stop_after == 'commandline':
        return dist
    if ok:
        try:
            dist.run_commands()
        except KeyboardInterrupt:
            raise SystemExit, 'interrupted'
        except (IOError, os.error) as exc:
            if DEBUG:
                sys.stderr.write('error: %s\n' % (exc,))
                raise
            else:
                raise SystemExit, 'error: %s' % (exc,)
        except (DistutilsError, CCompilerError) as msg:
            if DEBUG:
                raise
            else:
                raise SystemExit, 'error: ' + str(msg)

    return dist


def run_setup(script_name, script_args=None, stop_after='run'):
    global _setup_stop_after
    if stop_after not in ('init', 'config', 'commandline', 'run'):
        raise ValueError, "invalid value for 'stop_after': %r" % (stop_after,)
    _setup_stop_after = stop_after
    save_argv = sys.argv
    g = {'__file__': script_name}
    l = {}
    try:
        try:
            sys.argv[0] = script_name
            if script_args is not None:
                sys.argv[1:] = script_args
            f = open(script_name)
            try:
                exec f.read() in g, l
            finally:
                f.close()

        finally:
            sys.argv = save_argv
            _setup_stop_after = None

    except SystemExit:
        pass
    except:
        raise

    if _setup_distribution is None:
        raise RuntimeError, "'distutils.core.setup()' was never called -- perhaps '%s' is not a Distutils setup script?" % script_name
    return _setup_distribution
