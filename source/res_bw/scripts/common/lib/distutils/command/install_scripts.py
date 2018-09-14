# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/command/install_scripts.py
"""distutils.command.install_scripts

Implements the Distutils 'install_scripts' command, for installing
Python scripts."""
__revision__ = '$Id$'
import os
from distutils.core import Command
from distutils import log
from stat import ST_MODE

class install_scripts(Command):
    description = 'install scripts (Python or otherwise)'
    user_options = [('install-dir=', 'd', 'directory to install scripts to'),
     ('build-dir=', 'b', 'build directory (where to install from)'),
     ('force', 'f', 'force installation (overwrite existing files)'),
     ('skip-build', None, 'skip the build steps')]
    boolean_options = ['force', 'skip-build']

    def initialize_options(self):
        self.install_dir = None
        self.force = 0
        self.build_dir = None
        self.skip_build = None
        return

    def finalize_options(self):
        self.set_undefined_options('build', ('build_scripts', 'build_dir'))
        self.set_undefined_options('install', ('install_scripts', 'install_dir'), ('force', 'force'), ('skip_build', 'skip_build'))

    def run(self):
        if not self.skip_build:
            self.run_command('build_scripts')
        self.outfiles = self.copy_tree(self.build_dir, self.install_dir)
        if os.name == 'posix':
            for file in self.get_outputs():
                if self.dry_run:
                    log.info('changing mode of %s', file)
                else:
                    mode = (os.stat(file)[ST_MODE] | 365) & 4095
                    log.info('changing mode of %s to %o', file, mode)
                    os.chmod(file, mode)

    def get_inputs(self):
        return self.distribution.scripts or []

    def get_outputs(self):
        return self.outfiles or []
