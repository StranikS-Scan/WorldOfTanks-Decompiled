# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/command/install_data.py
__revision__ = '$Id$'
import os
from distutils.core import Command
from distutils.util import change_root, convert_path

class install_data(Command):
    description = 'install data files'
    user_options = [('install-dir=', 'd', 'base directory for installing data files (default: installation base dir)'), ('root=', None, 'install everything relative to this alternate root directory'), ('force', 'f', 'force installation (overwrite existing files)')]
    boolean_options = ['force']

    def initialize_options(self):
        self.install_dir = None
        self.outfiles = []
        self.root = None
        self.force = 0
        self.data_files = self.distribution.data_files
        self.warn_dir = 1
        return

    def finalize_options(self):
        self.set_undefined_options('install', ('install_data', 'install_dir'), ('root', 'root'), ('force', 'force'))

    def run(self):
        self.mkpath(self.install_dir)
        for f in self.data_files:
            if isinstance(f, str):
                f = convert_path(f)
                if self.warn_dir:
                    self.warn("setup script did not provide a directory for '%s' -- installing right in '%s'" % (f, self.install_dir))
                out, _ = self.copy_file(f, self.install_dir)
                self.outfiles.append(out)
            dir = convert_path(f[0])
            if not os.path.isabs(dir):
                dir = os.path.join(self.install_dir, dir)
            elif self.root:
                dir = change_root(self.root, dir)
            self.mkpath(dir)
            if f[1] == []:
                self.outfiles.append(dir)
            for data in f[1]:
                data = convert_path(data)
                out, _ = self.copy_file(data, dir)
                self.outfiles.append(out)

    def get_inputs(self):
        return self.data_files or []

    def get_outputs(self):
        return self.outfiles
