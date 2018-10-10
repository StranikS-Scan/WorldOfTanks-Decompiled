# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/command/build_scripts.py
__revision__ = '$Id$'
import os, re
from stat import ST_MODE
from distutils.core import Command
from distutils.dep_util import newer
from distutils.util import convert_path
from distutils import log
first_line_re = re.compile('^#!.*python[0-9.]*([ \t].*)?$')

class build_scripts(Command):
    description = '"build" scripts (copy and fixup #! line)'
    user_options = [('build-dir=', 'd', 'directory to "build" (copy) to'), ('force', 'f', 'forcibly build everything (ignore file timestamps'), ('executable=', 'e', 'specify final destination interpreter path')]
    boolean_options = ['force']

    def initialize_options(self):
        self.build_dir = None
        self.scripts = None
        self.force = None
        self.executable = None
        self.outfiles = None
        return

    def finalize_options(self):
        self.set_undefined_options('build', ('build_scripts', 'build_dir'), ('force', 'force'), ('executable', 'executable'))
        self.scripts = self.distribution.scripts

    def get_source_files(self):
        return self.scripts

    def run(self):
        if not self.scripts:
            return
        self.copy_scripts()

    def copy_scripts(self):
        _sysconfig = __import__('sysconfig')
        self.mkpath(self.build_dir)
        outfiles = []
        for script in self.scripts:
            adjust = 0
            script = convert_path(script)
            outfile = os.path.join(self.build_dir, os.path.basename(script))
            outfiles.append(outfile)
            if not self.force and not newer(script, outfile):
                log.debug('not copying %s (up-to-date)', script)
                continue
            try:
                f = open(script, 'r')
            except IOError:
                if not self.dry_run:
                    raise
                f = None
            else:
                first_line = f.readline()
                if not first_line:
                    self.warn('%s is an empty file (skipping)' % script)
                    continue
                match = first_line_re.match(first_line)
                if match:
                    adjust = 1
                    post_interp = match.group(1) or ''

            if adjust:
                log.info('copying and adjusting %s -> %s', script, self.build_dir)
                if not self.dry_run:
                    outf = open(outfile, 'w')
                    if not _sysconfig.is_python_build():
                        outf.write('#!%s%s\n' % (self.executable, post_interp))
                    else:
                        outf.write('#!%s%s\n' % (os.path.join(_sysconfig.get_config_var('BINDIR'), 'python%s%s' % (_sysconfig.get_config_var('VERSION'), _sysconfig.get_config_var('EXE'))), post_interp))
                    outf.writelines(f.readlines())
                    outf.close()
                if f:
                    f.close()
            if f:
                f.close()
            self.copy_file(script, outfile)

        if os.name == 'posix':
            for file in outfiles:
                if self.dry_run:
                    log.info('changing mode of %s', file)
                oldmode = os.stat(file)[ST_MODE] & 4095
                newmode = (oldmode | 365) & 4095
                if newmode != oldmode:
                    log.info('changing mode of %s from %o to %o', file, oldmode, newmode)
                    os.chmod(file, newmode)

        return
