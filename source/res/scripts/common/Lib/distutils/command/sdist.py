# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/command/sdist.py
__revision__ = '$Id$'
import os
import string
import sys
from glob import glob
from warnings import warn
from distutils.core import Command
from distutils import dir_util, dep_util, file_util, archive_util
from distutils.text_file import TextFile
from distutils.errors import DistutilsPlatformError, DistutilsOptionError, DistutilsTemplateError
from distutils.filelist import FileList
from distutils import log
from distutils.util import convert_path

def show_formats():
    from distutils.fancy_getopt import FancyGetopt
    from distutils.archive_util import ARCHIVE_FORMATS
    formats = []
    for format in ARCHIVE_FORMATS.keys():
        formats.append(('formats=' + format, None, ARCHIVE_FORMATS[format][2]))

    formats.sort()
    FancyGetopt(formats).print_help('List of available source distribution formats:')
    return


class sdist(Command):
    description = 'create a source distribution (tarball, zip file, etc.)'

    def checking_metadata(self):
        return self.metadata_check

    user_options = [('template=', 't', 'name of manifest template file [default: MANIFEST.in]'),
     ('manifest=', 'm', 'name of manifest file [default: MANIFEST]'),
     ('use-defaults', None, 'include the default file set in the manifest [default; disable with --no-defaults]'),
     ('no-defaults', None, "don't include the default file set"),
     ('prune', None, 'specifically exclude files/directories that should not be distributed (build tree, RCS/CVS dirs, etc.) [default; disable with --no-prune]'),
     ('no-prune', None, "don't automatically exclude anything"),
     ('manifest-only', 'o', 'just regenerate the manifest and then stop (implies --force-manifest)'),
     ('force-manifest', 'f', 'forcibly regenerate the manifest and carry on as usual. Deprecated: now the manifest is always regenerated.'),
     ('formats=', None, 'formats for source distribution (comma-separated list)'),
     ('keep-temp', 'k', 'keep the distribution tree around after creating ' + 'archive file(s)'),
     ('dist-dir=', 'd', 'directory to put the source distribution archive(s) in [default: dist]'),
     ('metadata-check', None, 'Ensure that all required elements of meta-data are supplied. Warn if any missing. [default]'),
     ('owner=', 'u', 'Owner name used when creating a tar file [default: current user]'),
     ('group=', 'g', 'Group name used when creating a tar file [default: current group]')]
    boolean_options = ['use-defaults',
     'prune',
     'manifest-only',
     'force-manifest',
     'keep-temp',
     'metadata-check']
    help_options = [('help-formats',
      None,
      'list available distribution formats',
      show_formats)]
    negative_opt = {'no-defaults': 'use-defaults',
     'no-prune': 'prune'}
    default_format = {'posix': 'gztar',
     'nt': 'zip'}
    sub_commands = [('check', checking_metadata)]

    def initialize_options(self):
        self.template = None
        self.manifest = None
        self.use_defaults = 1
        self.prune = 1
        self.manifest_only = 0
        self.force_manifest = 0
        self.formats = None
        self.keep_temp = 0
        self.dist_dir = None
        self.archive_files = None
        self.metadata_check = 1
        self.owner = None
        self.group = None
        return

    def finalize_options(self):
        if self.manifest is None:
            self.manifest = 'MANIFEST'
        if self.template is None:
            self.template = 'MANIFEST.in'
        self.ensure_string_list('formats')
        if self.formats is None:
            try:
                self.formats = [self.default_format[os.name]]
            except KeyError:
                raise DistutilsPlatformError, "don't know how to create source distributions " + 'on platform %s' % os.name

        bad_format = archive_util.check_archive_formats(self.formats)
        if bad_format:
            raise DistutilsOptionError, "unknown archive format '%s'" % bad_format
        if self.dist_dir is None:
            self.dist_dir = 'dist'
        return

    def run(self):
        self.filelist = FileList()
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        self.get_file_list()
        if self.manifest_only:
            return
        self.make_distribution()

    def check_metadata(self):
        warn('distutils.command.sdist.check_metadata is deprecated,               use the check command instead', PendingDeprecationWarning)
        check = self.distribution.get_command_obj('check')
        check.ensure_finalized()
        check.run()

    def get_file_list(self):
        template_exists = os.path.isfile(self.template)
        if not template_exists and self._manifest_is_not_generated():
            self.read_manifest()
            self.filelist.sort()
            self.filelist.remove_duplicates()
            return
        if not template_exists:
            self.warn(("manifest template '%s' does not exist " + '(using default file list)') % self.template)
        self.filelist.findall()
        if self.use_defaults:
            self.add_defaults()
        if template_exists:
            self.read_template()
        if self.prune:
            self.prune_file_list()
        self.filelist.sort()
        self.filelist.remove_duplicates()
        self.write_manifest()

    def add_defaults(self):
        standards = [('README', 'README.txt'), self.distribution.script_name]
        for fn in standards:
            if isinstance(fn, tuple):
                alts = fn
                got_it = 0
                for fn in alts:
                    if os.path.exists(fn):
                        got_it = 1
                        self.filelist.append(fn)
                        break

                if not got_it:
                    self.warn('standard file not found: should have one of ' + string.join(alts, ', '))
            if os.path.exists(fn):
                self.filelist.append(fn)
            self.warn("standard file '%s' not found" % fn)

        optional = ['test/test*.py', 'setup.cfg']
        for pattern in optional:
            files = filter(os.path.isfile, glob(pattern))
            if files:
                self.filelist.extend(files)

        build_py = self.get_finalized_command('build_py')
        if self.distribution.has_pure_modules():
            self.filelist.extend(build_py.get_source_files())
        for pkg, src_dir, build_dir, filenames in build_py.data_files:
            for filename in filenames:
                self.filelist.append(os.path.join(src_dir, filename))

        if self.distribution.has_data_files():
            for item in self.distribution.data_files:
                if isinstance(item, str):
                    item = convert_path(item)
                    if os.path.isfile(item):
                        self.filelist.append(item)
                dirname, filenames = item
                for f in filenames:
                    f = convert_path(f)
                    if os.path.isfile(f):
                        self.filelist.append(f)

        if self.distribution.has_ext_modules():
            build_ext = self.get_finalized_command('build_ext')
            self.filelist.extend(build_ext.get_source_files())
        if self.distribution.has_c_libraries():
            build_clib = self.get_finalized_command('build_clib')
            self.filelist.extend(build_clib.get_source_files())
        if self.distribution.has_scripts():
            build_scripts = self.get_finalized_command('build_scripts')
            self.filelist.extend(build_scripts.get_source_files())

    def read_template(self):
        log.info("reading manifest template '%s'", self.template)
        template = TextFile(self.template, strip_comments=1, skip_blanks=1, join_lines=1, lstrip_ws=1, rstrip_ws=1, collapse_join=1)
        try:
            while 1:
                line = template.readline()
                if line is None:
                    break
                try:
                    self.filelist.process_template_line(line)
                except (DistutilsTemplateError, ValueError) as msg:
                    self.warn('%s, line %d: %s' % (template.filename, template.current_line, msg))

        finally:
            template.close()

        return

    def prune_file_list(self):
        build = self.get_finalized_command('build')
        base_dir = self.distribution.get_fullname()
        self.filelist.exclude_pattern(None, prefix=build.build_base)
        self.filelist.exclude_pattern(None, prefix=base_dir)
        if sys.platform == 'win32':
            seps = '/|\\\\'
        else:
            seps = '/'
        vcs_dirs = ['RCS',
         'CVS',
         '\\.svn',
         '\\.hg',
         '\\.git',
         '\\.bzr',
         '_darcs']
        vcs_ptrn = '(^|%s)(%s)(%s).*' % (seps, '|'.join(vcs_dirs), seps)
        self.filelist.exclude_pattern(vcs_ptrn, is_regex=1)
        return

    def write_manifest(self):
        if self._manifest_is_not_generated():
            log.info("not writing to manually maintained manifest file '%s'" % self.manifest)
            return
        content = self.filelist.files[:]
        content.insert(0, '# file GENERATED by distutils, do NOT edit')
        self.execute(file_util.write_file, (self.manifest, content), "writing manifest file '%s'" % self.manifest)

    def _manifest_is_not_generated(self):
        if not os.path.isfile(self.manifest):
            return False
        fp = open(self.manifest, 'rU')
        try:
            first_line = fp.readline()
        finally:
            fp.close()

        return first_line != '# file GENERATED by distutils, do NOT edit\n'

    def read_manifest(self):
        log.info("reading manifest file '%s'", self.manifest)
        manifest = open(self.manifest)
        for line in manifest:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            self.filelist.append(line)

        manifest.close()

    def make_release_tree(self, base_dir, files):
        self.mkpath(base_dir)
        dir_util.create_tree(base_dir, files, dry_run=self.dry_run)
        if hasattr(os, 'link'):
            link = 'hard'
            msg = 'making hard links in %s...' % base_dir
        else:
            link = None
            msg = 'copying files to %s...' % base_dir
        if not files:
            log.warn('no files to distribute -- empty manifest?')
        else:
            log.info(msg)
        for file in files:
            if not os.path.isfile(file):
                log.warn("'%s' not a regular file -- skipping" % file)
            dest = os.path.join(base_dir, file)
            self.copy_file(file, dest, link=link)

        self.distribution.metadata.write_pkg_info(base_dir)
        return

    def make_distribution(self):
        base_dir = self.distribution.get_fullname()
        base_name = os.path.join(self.dist_dir, base_dir)
        self.make_release_tree(base_dir, self.filelist.files)
        archive_files = []
        if 'tar' in self.formats:
            self.formats.append(self.formats.pop(self.formats.index('tar')))
        for fmt in self.formats:
            file = self.make_archive(base_name, fmt, base_dir=base_dir, owner=self.owner, group=self.group)
            archive_files.append(file)
            self.distribution.dist_files.append(('sdist', '', file))

        self.archive_files = archive_files
        if not self.keep_temp:
            dir_util.remove_tree(base_dir, dry_run=self.dry_run)

    def get_archive_files(self):
        return self.archive_files
