# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/command/config.py
__revision__ = '$Id$'
import os
import re
from distutils.core import Command
from distutils.errors import DistutilsExecError
from distutils.sysconfig import customize_compiler
from distutils import log
LANG_EXT = {'c': '.c',
 'c++': '.cxx'}

class config(Command):
    description = 'prepare to build'
    user_options = [('compiler=', None, 'specify the compiler type'),
     ('cc=', None, 'specify the compiler executable'),
     ('include-dirs=', 'I', 'list of directories to search for header files'),
     ('define=', 'D', 'C preprocessor macros to define'),
     ('undef=', 'U', 'C preprocessor macros to undefine'),
     ('libraries=', 'l', 'external C libraries to link with'),
     ('library-dirs=', 'L', 'directories to search for external C libraries'),
     ('noisy', None, 'show every action (compile, link, run, ...) taken'),
     ('dump-source', None, 'dump generated source files before attempting to compile them')]

    def initialize_options(self):
        self.compiler = None
        self.cc = None
        self.include_dirs = None
        self.libraries = None
        self.library_dirs = None
        self.noisy = 1
        self.dump_source = 1
        self.temp_files = []
        return

    def finalize_options(self):
        if self.include_dirs is None:
            self.include_dirs = self.distribution.include_dirs or []
        elif isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)
        if self.libraries is None:
            self.libraries = []
        elif isinstance(self.libraries, str):
            self.libraries = [self.libraries]
        if self.library_dirs is None:
            self.library_dirs = []
        elif isinstance(self.library_dirs, str):
            self.library_dirs = self.library_dirs.split(os.pathsep)
        return

    def run(self):
        pass

    def _check_compiler(self):
        from distutils.ccompiler import CCompiler, new_compiler
        if not isinstance(self.compiler, CCompiler):
            self.compiler = new_compiler(compiler=self.compiler, dry_run=self.dry_run, force=1)
            customize_compiler(self.compiler)
            if self.include_dirs:
                self.compiler.set_include_dirs(self.include_dirs)
            if self.libraries:
                self.compiler.set_libraries(self.libraries)
            if self.library_dirs:
                self.compiler.set_library_dirs(self.library_dirs)

    def _gen_temp_sourcefile(self, body, headers, lang):
        filename = '_configtest' + LANG_EXT[lang]
        file = open(filename, 'w')
        if headers:
            for header in headers:
                file.write('#include <%s>\n' % header)

            file.write('\n')
        file.write(body)
        if body[-1] != '\n':
            file.write('\n')
        file.close()
        return filename

    def _preprocess(self, body, headers, include_dirs, lang):
        src = self._gen_temp_sourcefile(body, headers, lang)
        out = '_configtest.i'
        self.temp_files.extend([src, out])
        self.compiler.preprocess(src, out, include_dirs=include_dirs)
        return (src, out)

    def _compile(self, body, headers, include_dirs, lang):
        src = self._gen_temp_sourcefile(body, headers, lang)
        if self.dump_source:
            dump_file(src, "compiling '%s':" % src)
        obj = self.compiler.object_filenames([src])
        self.temp_files.extend([src, obj])
        self.compiler.compile([src], include_dirs=include_dirs)
        return (src, obj)

    def _link(self, body, headers, include_dirs, libraries, library_dirs, lang):
        src, obj = self._compile(body, headers, include_dirs, lang)
        prog = os.path.splitext(os.path.basename(src))[0]
        self.compiler.link_executable([obj], prog, libraries=libraries, library_dirs=library_dirs, target_lang=lang)
        if self.compiler.exe_extension is not None:
            prog = prog + self.compiler.exe_extension
        self.temp_files.append(prog)
        return (src, obj, prog)

    def _clean(self, *filenames):
        if not filenames:
            filenames = self.temp_files
            self.temp_files = []
        log.info('removing: %s', ' '.join(filenames))
        for filename in filenames:
            try:
                os.remove(filename)
            except OSError:
                pass

    def try_cpp(self, body=None, headers=None, include_dirs=None, lang='c'):
        from distutils.ccompiler import CompileError
        self._check_compiler()
        ok = 1
        try:
            self._preprocess(body, headers, include_dirs, lang)
        except CompileError:
            ok = 0

        self._clean()
        return ok

    def search_cpp(self, pattern, body=None, headers=None, include_dirs=None, lang='c'):
        self._check_compiler()
        src, out = self._preprocess(body, headers, include_dirs, lang)
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        file = open(out)
        match = 0
        while 1:
            line = file.readline()
            if line == '':
                break
            if pattern.search(line):
                match = 1
                break

        file.close()
        self._clean()
        return match

    def try_compile(self, body, headers=None, include_dirs=None, lang='c'):
        from distutils.ccompiler import CompileError
        self._check_compiler()
        try:
            self._compile(body, headers, include_dirs, lang)
            ok = 1
        except CompileError:
            ok = 0

        log.info(ok and 'success!' or 'failure.')
        self._clean()
        return ok

    def try_link(self, body, headers=None, include_dirs=None, libraries=None, library_dirs=None, lang='c'):
        from distutils.ccompiler import CompileError, LinkError
        self._check_compiler()
        try:
            self._link(body, headers, include_dirs, libraries, library_dirs, lang)
            ok = 1
        except (CompileError, LinkError):
            ok = 0

        log.info(ok and 'success!' or 'failure.')
        self._clean()
        return ok

    def try_run(self, body, headers=None, include_dirs=None, libraries=None, library_dirs=None, lang='c'):
        from distutils.ccompiler import CompileError, LinkError
        self._check_compiler()
        try:
            src, obj, exe = self._link(body, headers, include_dirs, libraries, library_dirs, lang)
            self.spawn([exe])
            ok = 1
        except (CompileError, LinkError, DistutilsExecError):
            ok = 0

        log.info(ok and 'success!' or 'failure.')
        self._clean()
        return ok

    def check_func(self, func, headers=None, include_dirs=None, libraries=None, library_dirs=None, decl=0, call=0):
        self._check_compiler()
        body = []
        if decl:
            body.append('int %s ();' % func)
        body.append('int main () {')
        if call:
            body.append('  %s();' % func)
        else:
            body.append('  %s;' % func)
        body.append('}')
        body = '\n'.join(body) + '\n'
        return self.try_link(body, headers, include_dirs, libraries, library_dirs)

    def check_lib(self, library, library_dirs=None, headers=None, include_dirs=None, other_libraries=[]):
        self._check_compiler()
        return self.try_link('int main (void) { }', headers, include_dirs, [library] + other_libraries, library_dirs)

    def check_header(self, header, include_dirs=None, library_dirs=None, lang='c'):
        return self.try_cpp(body='/* No body */', headers=[header], include_dirs=include_dirs)


def dump_file(filename, head=None):
    if head is None:
        log.info('%s' % filename)
    else:
        log.info(head)
    file = open(filename)
    try:
        log.info(file.read())
    finally:
        file.close()

    return
