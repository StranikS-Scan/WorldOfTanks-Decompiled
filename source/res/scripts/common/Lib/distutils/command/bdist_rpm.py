# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/command/bdist_rpm.py
__revision__ = '$Id$'
import sys
import os
import string
from distutils.core import Command
from distutils.debug import DEBUG
from distutils.file_util import write_file
from distutils.sysconfig import get_python_version
from distutils.errors import DistutilsOptionError, DistutilsPlatformError, DistutilsFileError, DistutilsExecError
from distutils import log

class bdist_rpm(Command):
    description = 'create an RPM distribution'
    user_options = [('bdist-base=', None, 'base directory for creating built distributions'),
     ('rpm-base=', None, 'base directory for creating RPMs (defaults to "rpm" under --bdist-base; must be specified for RPM 2)'),
     ('dist-dir=', 'd', 'directory to put final RPM files in (and .spec files if --spec-only)'),
     ('python=', None, 'path to Python interpreter to hard-code in the .spec file (default: "python")'),
     ('fix-python', None, 'hard-code the exact path to the current Python interpreter in the .spec file'),
     ('spec-only', None, 'only regenerate spec file'),
     ('source-only', None, 'only generate source RPM'),
     ('binary-only', None, 'only generate binary RPM'),
     ('use-bzip2', None, 'use bzip2 instead of gzip to create source distribution'),
     ('distribution-name=', None, 'name of the (Linux) distribution to which this RPM applies (*not* the name of the module distribution!)'),
     ('group=', None, 'package classification [default: "Development/Libraries"]'),
     ('release=', None, 'RPM release number'),
     ('serial=', None, 'RPM serial number'),
     ('vendor=', None, 'RPM "vendor" (eg. "Joe Blow <joe@example.com>") [default: maintainer or author from setup script]'),
     ('packager=', None, 'RPM packager (eg. "Jane Doe <jane@example.net>")[default: vendor]'),
     ('doc-files=', None, 'list of documentation files (space or comma-separated)'),
     ('changelog=', None, 'RPM changelog'),
     ('icon=', None, 'name of icon file'),
     ('provides=', None, 'capabilities provided by this package'),
     ('requires=', None, 'capabilities required by this package'),
     ('conflicts=', None, 'capabilities which conflict with this package'),
     ('build-requires=', None, 'capabilities required to build this package'),
     ('obsoletes=', None, 'capabilities made obsolete by this package'),
     ('no-autoreq', None, 'do not automatically calculate dependencies'),
     ('keep-temp', 'k', "don't clean up RPM build directory"),
     ('no-keep-temp', None, 'clean up RPM build directory [default]'),
     ('use-rpm-opt-flags', None, 'compile with RPM_OPT_FLAGS when building from source RPM'),
     ('no-rpm-opt-flags', None, 'do not pass any RPM CFLAGS to compiler'),
     ('rpm3-mode', None, 'RPM 3 compatibility mode (default)'),
     ('rpm2-mode', None, 'RPM 2 compatibility mode'),
     ('prep-script=', None, 'Specify a script for the PREP phase of RPM building'),
     ('build-script=', None, 'Specify a script for the BUILD phase of RPM building'),
     ('pre-install=', None, 'Specify a script for the pre-INSTALL phase of RPM building'),
     ('install-script=', None, 'Specify a script for the INSTALL phase of RPM building'),
     ('post-install=', None, 'Specify a script for the post-INSTALL phase of RPM building'),
     ('pre-uninstall=', None, 'Specify a script for the pre-UNINSTALL phase of RPM building'),
     ('post-uninstall=', None, 'Specify a script for the post-UNINSTALL phase of RPM building'),
     ('clean-script=', None, 'Specify a script for the CLEAN phase of RPM building'),
     ('verify-script=', None, 'Specify a script for the VERIFY phase of the RPM build'),
     ('force-arch=', None, 'Force an architecture onto the RPM build process'),
     ('quiet', 'q', 'Run the INSTALL phase of RPM building in quiet mode')]
    boolean_options = ['keep-temp',
     'use-rpm-opt-flags',
     'rpm3-mode',
     'no-autoreq',
     'quiet']
    negative_opt = {'no-keep-temp': 'keep-temp',
     'no-rpm-opt-flags': 'use-rpm-opt-flags',
     'rpm2-mode': 'rpm3-mode'}

    def initialize_options(self):
        self.bdist_base = None
        self.rpm_base = None
        self.dist_dir = None
        self.python = None
        self.fix_python = None
        self.spec_only = None
        self.binary_only = None
        self.source_only = None
        self.use_bzip2 = None
        self.distribution_name = None
        self.group = None
        self.release = None
        self.serial = None
        self.vendor = None
        self.packager = None
        self.doc_files = None
        self.changelog = None
        self.icon = None
        self.prep_script = None
        self.build_script = None
        self.install_script = None
        self.clean_script = None
        self.verify_script = None
        self.pre_install = None
        self.post_install = None
        self.pre_uninstall = None
        self.post_uninstall = None
        self.prep = None
        self.provides = None
        self.requires = None
        self.conflicts = None
        self.build_requires = None
        self.obsoletes = None
        self.keep_temp = 0
        self.use_rpm_opt_flags = 1
        self.rpm3_mode = 1
        self.no_autoreq = 0
        self.force_arch = None
        self.quiet = 0
        return

    def finalize_options(self):
        self.set_undefined_options('bdist', ('bdist_base', 'bdist_base'))
        if self.rpm_base is None:
            if not self.rpm3_mode:
                raise DistutilsOptionError, 'you must specify --rpm-base in RPM 2 mode'
            self.rpm_base = os.path.join(self.bdist_base, 'rpm')
        if self.python is None:
            if self.fix_python:
                self.python = sys.executable
            else:
                self.python = 'python'
        elif self.fix_python:
            raise DistutilsOptionError, '--python and --fix-python are mutually exclusive options'
        if os.name != 'posix':
            raise DistutilsPlatformError, "don't know how to create RPM distributions on platform %s" % os.name
        if self.binary_only and self.source_only:
            raise DistutilsOptionError, "cannot supply both '--source-only' and '--binary-only'"
        if not self.distribution.has_ext_modules():
            self.use_rpm_opt_flags = 0
        self.set_undefined_options('bdist', ('dist_dir', 'dist_dir'))
        self.finalize_package_data()
        return

    def finalize_package_data(self):
        self.ensure_string('group', 'Development/Libraries')
        self.ensure_string('vendor', '%s <%s>' % (self.distribution.get_contact(), self.distribution.get_contact_email()))
        self.ensure_string('packager')
        self.ensure_string_list('doc_files')
        if isinstance(self.doc_files, list):
            for readme in ('README', 'README.txt'):
                if os.path.exists(readme) and readme not in self.doc_files:
                    self.doc_files.append(readme)

        self.ensure_string('release', '1')
        self.ensure_string('serial')
        self.ensure_string('distribution_name')
        self.ensure_string('changelog')
        self.changelog = self._format_changelog(self.changelog)
        self.ensure_filename('icon')
        self.ensure_filename('prep_script')
        self.ensure_filename('build_script')
        self.ensure_filename('install_script')
        self.ensure_filename('clean_script')
        self.ensure_filename('verify_script')
        self.ensure_filename('pre_install')
        self.ensure_filename('post_install')
        self.ensure_filename('pre_uninstall')
        self.ensure_filename('post_uninstall')
        self.ensure_string_list('provides')
        self.ensure_string_list('requires')
        self.ensure_string_list('conflicts')
        self.ensure_string_list('build_requires')
        self.ensure_string_list('obsoletes')
        self.ensure_string('force_arch')

    def run(self):
        if DEBUG:
            print 'before _get_package_data():'
            print 'vendor =', self.vendor
            print 'packager =', self.packager
            print 'doc_files =', self.doc_files
            print 'changelog =', self.changelog
        if self.spec_only:
            spec_dir = self.dist_dir
            self.mkpath(spec_dir)
        else:
            rpm_dir = {}
            for d in ('SOURCES', 'SPECS', 'BUILD', 'RPMS', 'SRPMS'):
                rpm_dir[d] = os.path.join(self.rpm_base, d)
                self.mkpath(rpm_dir[d])

            spec_dir = rpm_dir['SPECS']
        spec_path = os.path.join(spec_dir, '%s.spec' % self.distribution.get_name())
        self.execute(write_file, (spec_path, self._make_spec_file()), "writing '%s'" % spec_path)
        if self.spec_only:
            return
        else:
            saved_dist_files = self.distribution.dist_files[:]
            sdist = self.reinitialize_command('sdist')
            if self.use_bzip2:
                sdist.formats = ['bztar']
            else:
                sdist.formats = ['gztar']
            self.run_command('sdist')
            self.distribution.dist_files = saved_dist_files
            source = sdist.get_archive_files()[0]
            source_dir = rpm_dir['SOURCES']
            self.copy_file(source, source_dir)
            if self.icon:
                if os.path.exists(self.icon):
                    self.copy_file(self.icon, source_dir)
                else:
                    raise DistutilsFileError, "icon file '%s' does not exist" % self.icon
            log.info('building RPMs')
            rpm_cmd = ['rpm']
            if os.path.exists('/usr/bin/rpmbuild') or os.path.exists('/bin/rpmbuild'):
                rpm_cmd = ['rpmbuild']
            if self.source_only:
                rpm_cmd.append('-bs')
            elif self.binary_only:
                rpm_cmd.append('-bb')
            else:
                rpm_cmd.append('-ba')
            if self.rpm3_mode:
                rpm_cmd.extend(['--define', '_topdir %s' % os.path.abspath(self.rpm_base)])
            if not self.keep_temp:
                rpm_cmd.append('--clean')
            if self.quiet:
                rpm_cmd.append('--quiet')
            rpm_cmd.append(spec_path)
            nvr_string = '%{name}-%{version}-%{release}'
            src_rpm = nvr_string + '.src.rpm'
            non_src_rpm = '%{arch}/' + nvr_string + '.%{arch}.rpm'
            q_cmd = "rpm -q --qf '%s %s\\n' --specfile '%s'" % (src_rpm, non_src_rpm, spec_path)
            out = os.popen(q_cmd)
            try:
                binary_rpms = []
                source_rpm = None
                while 1:
                    line = out.readline()
                    if not line:
                        break
                    l = string.split(string.strip(line))
                    binary_rpms.append(l[1])
                    if source_rpm is None:
                        source_rpm = l[0]

                status = out.close()
                if status:
                    raise DistutilsExecError('Failed to execute: %s' % repr(q_cmd))
            finally:
                out.close()

            self.spawn(rpm_cmd)
            if not self.dry_run:
                if self.distribution.has_ext_modules():
                    pyversion = get_python_version()
                else:
                    pyversion = 'any'
                if not self.binary_only:
                    srpm = os.path.join(rpm_dir['SRPMS'], source_rpm)
                    self.move_file(srpm, self.dist_dir)
                    filename = os.path.join(self.dist_dir, source_rpm)
                    self.distribution.dist_files.append(('bdist_rpm', pyversion, filename))
                if not self.source_only:
                    for rpm in binary_rpms:
                        rpm = os.path.join(rpm_dir['RPMS'], rpm)
                        if os.path.exists(rpm):
                            self.move_file(rpm, self.dist_dir)
                            filename = os.path.join(self.dist_dir, os.path.basename(rpm))
                            self.distribution.dist_files.append(('bdist_rpm', pyversion, filename))

            return

    def _dist_path(self, path):
        return os.path.join(self.dist_dir, os.path.basename(path))

    def _make_spec_file(self):
        spec_file = ['%define name ' + self.distribution.get_name(),
         '%define version ' + self.distribution.get_version().replace('-', '_'),
         '%define unmangled_version ' + self.distribution.get_version(),
         '%define release ' + self.release.replace('-', '_'),
         '',
         'Summary: ' + self.distribution.get_description()]
        spec_file.extend(['Name: %{name}', 'Version: %{version}', 'Release: %{release}'])
        if self.use_bzip2:
            spec_file.append('Source0: %{name}-%{unmangled_version}.tar.bz2')
        else:
            spec_file.append('Source0: %{name}-%{unmangled_version}.tar.gz')
        spec_file.extend(['License: ' + self.distribution.get_license(),
         'Group: ' + self.group,
         'BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot',
         'Prefix: %{_prefix}'])
        if not self.force_arch:
            if not self.distribution.has_ext_modules():
                spec_file.append('BuildArch: noarch')
        else:
            spec_file.append('BuildArch: %s' % self.force_arch)
        for field in ('Vendor', 'Packager', 'Provides', 'Requires', 'Conflicts', 'Obsoletes'):
            val = getattr(self, string.lower(field))
            if isinstance(val, list):
                spec_file.append('%s: %s' % (field, string.join(val)))
            if val is not None:
                spec_file.append('%s: %s' % (field, val))

        if self.distribution.get_url() != 'UNKNOWN':
            spec_file.append('Url: ' + self.distribution.get_url())
        if self.distribution_name:
            spec_file.append('Distribution: ' + self.distribution_name)
        if self.build_requires:
            spec_file.append('BuildRequires: ' + string.join(self.build_requires))
        if self.icon:
            spec_file.append('Icon: ' + os.path.basename(self.icon))
        if self.no_autoreq:
            spec_file.append('AutoReq: 0')
        spec_file.extend(['', '%description', self.distribution.get_long_description()])
        def_setup_call = '%s %s' % (self.python, os.path.basename(sys.argv[0]))
        def_build = '%s build' % def_setup_call
        if self.use_rpm_opt_flags:
            def_build = 'env CFLAGS="$RPM_OPT_FLAGS" ' + def_build
        install_cmd = '%s install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES' % def_setup_call
        script_options = [('prep', 'prep_script', '%setup -n %{name}-%{unmangled_version}'),
         ('build', 'build_script', def_build),
         ('install', 'install_script', install_cmd),
         ('clean', 'clean_script', 'rm -rf $RPM_BUILD_ROOT'),
         ('verifyscript', 'verify_script', None),
         ('pre', 'pre_install', None),
         ('post', 'post_install', None),
         ('preun', 'pre_uninstall', None),
         ('postun', 'post_uninstall', None)]
        for rpm_opt, attr, default in script_options:
            val = getattr(self, attr)
            if val or default:
                spec_file.extend(['', '%' + rpm_opt])
                if val:
                    spec_file.extend(string.split(open(val, 'r').read(), '\n'))
                else:
                    spec_file.append(default)

        spec_file.extend(['', '%files -f INSTALLED_FILES', '%defattr(-,root,root)'])
        if self.doc_files:
            spec_file.append('%doc ' + string.join(self.doc_files))
        if self.changelog:
            spec_file.extend(['', '%changelog'])
            spec_file.extend(self.changelog)
        return spec_file

    def _format_changelog(self, changelog):
        if not changelog:
            return changelog
        new_changelog = []
        for line in string.split(string.strip(changelog), '\n'):
            line = string.strip(line)
            if line[0] == '*':
                new_changelog.extend(['', line])
            if line[0] == '-':
                new_changelog.append(line)
            new_changelog.append('  ' + line)

        if not new_changelog[0]:
            del new_changelog[0]
        return new_changelog
