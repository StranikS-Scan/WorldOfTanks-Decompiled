# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_dist.py
# Compiled at: 2010-05-25 20:46:16
"""Tests for distutils.dist."""
import distutils.cmd
import distutils.dist
import os
import StringIO
import sys
import unittest
import warnings
from test.test_support import TESTFN

class test_dist(distutils.cmd.Command):
    """Sample distutils extension command."""
    user_options = [('sample-option=', 'S', 'help text')]

    def initialize_options(self):
        self.sample_option = None
        return


class TestDistribution(distutils.dist.Distribution):
    """Distribution subclasses that avoids the default search for
    configuration files.
    
    The ._config_files attribute must be set before
    .parse_config_files() is called.
    """

    def find_config_files(self):
        return self._config_files


class DistributionTestCase(unittest.TestCase):

    def setUp(self):
        self.argv = sys.argv[:]
        del sys.argv[1:]

    def tearDown(self):
        sys.argv[:] = self.argv

    def create_distribution(self, configfiles=()):
        d = TestDistribution()
        d._config_files = configfiles
        d.parse_config_files()
        d.parse_command_line()
        return d

    def test_command_packages_unspecified(self):
        sys.argv.append('build')
        d = self.create_distribution()
        self.assertEqual(d.get_command_packages(), ['distutils.command'])

    def test_command_packages_cmdline(self):
        from distutils.tests.test_dist import test_dist
        sys.argv.extend(['--command-packages',
         'foo.bar,distutils.tests',
         'test_dist',
         '-Ssometext'])
        d = self.create_distribution()
        self.assertEqual(d.get_command_packages(), ['distutils.command', 'foo.bar', 'distutils.tests'])
        cmd = d.get_command_obj('test_dist')
        self.assert_(isinstance(cmd, test_dist))
        self.assertEqual(cmd.sample_option, 'sometext')

    def test_command_packages_configfile(self):
        sys.argv.append('build')
        f = open(TESTFN, 'w')
        try:
            print >> f, '[global]'
            print >> f, 'command_packages = foo.bar, splat'
            f.close()
            d = self.create_distribution([TESTFN])
            self.assertEqual(d.get_command_packages(), ['distutils.command', 'foo.bar', 'splat'])
            sys.argv[1:] = ['--command-packages', 'spork', 'build']
            d = self.create_distribution([TESTFN])
            self.assertEqual(d.get_command_packages(), ['distutils.command', 'spork'])
            sys.argv[1:] = ['--command-packages', '', 'build']
            d = self.create_distribution([TESTFN])
            self.assertEqual(d.get_command_packages(), ['distutils.command'])
        finally:
            os.unlink(TESTFN)

    def test_write_pkg_file(self):
        my_file = os.path.join(os.path.dirname(__file__), 'f')
        klass = distutils.dist.Distribution
        dist = klass(attrs={'author': u'Mister Caf\xe9',
         'name': 'my.package',
         'maintainer': u'Caf\xe9 Junior',
         'description': u'Caf\xe9 torr\xe9fi\xe9',
         'long_description': u'H\xe9h\xe9h\xe9'})
        try:
            dist.metadata.write_pkg_file(open(my_file, 'w'))
        finally:
            if os.path.exists(my_file):
                os.remove(my_file)

        dist = klass(attrs={'author': 'Mister Cafe',
         'name': 'my.package',
         'maintainer': 'Cafe Junior',
         'description': 'Cafe torrefie',
         'long_description': 'Hehehe'})
        try:
            dist.metadata.write_pkg_file(open(my_file, 'w'))
        finally:
            if os.path.exists(my_file):
                os.remove(my_file)

    def test_empty_options(self):
        klass = distutils.dist.Distribution
        warns = []

        def _warn(msg):
            warns.append(msg)

        old_warn = warnings.warn
        warnings.warn = _warn
        try:
            dist = klass(attrs={'author': 'xxx',
             'name': 'xxx',
             'version': 'xxx',
             'url': 'xxxx',
             'options': {}})
        finally:
            warnings.warn = old_warn

        self.assertEquals(len(warns), 0)


class MetadataTestCase(unittest.TestCase):

    def test_simple_metadata(self):
        attrs = {'name': 'package',
         'version': '1.0'}
        dist = distutils.dist.Distribution(attrs)
        meta = self.format_metadata(dist)
        self.assert_('Metadata-Version: 1.0' in meta)
        self.assert_('provides:' not in meta.lower())
        self.assert_('requires:' not in meta.lower())
        self.assert_('obsoletes:' not in meta.lower())

    def test_provides(self):
        attrs = {'name': 'package',
         'version': '1.0',
         'provides': ['package', 'package.sub']}
        dist = distutils.dist.Distribution(attrs)
        self.assertEqual(dist.metadata.get_provides(), ['package', 'package.sub'])
        self.assertEqual(dist.get_provides(), ['package', 'package.sub'])
        meta = self.format_metadata(dist)
        self.assert_('Metadata-Version: 1.1' in meta)
        self.assert_('requires:' not in meta.lower())
        self.assert_('obsoletes:' not in meta.lower())

    def test_provides_illegal(self):
        self.assertRaises(ValueError, distutils.dist.Distribution, {'name': 'package',
         'version': '1.0',
         'provides': ['my.pkg (splat)']})

    def test_requires(self):
        attrs = {'name': 'package',
         'version': '1.0',
         'requires': ['other', 'another (==1.0)']}
        dist = distutils.dist.Distribution(attrs)
        self.assertEqual(dist.metadata.get_requires(), ['other', 'another (==1.0)'])
        self.assertEqual(dist.get_requires(), ['other', 'another (==1.0)'])
        meta = self.format_metadata(dist)
        self.assert_('Metadata-Version: 1.1' in meta)
        self.assert_('provides:' not in meta.lower())
        self.assert_('Requires: other' in meta)
        self.assert_('Requires: another (==1.0)' in meta)
        self.assert_('obsoletes:' not in meta.lower())

    def test_requires_illegal(self):
        self.assertRaises(ValueError, distutils.dist.Distribution, {'name': 'package',
         'version': '1.0',
         'requires': ['my.pkg (splat)']})

    def test_obsoletes(self):
        attrs = {'name': 'package',
         'version': '1.0',
         'obsoletes': ['other', 'another (<1.0)']}
        dist = distutils.dist.Distribution(attrs)
        self.assertEqual(dist.metadata.get_obsoletes(), ['other', 'another (<1.0)'])
        self.assertEqual(dist.get_obsoletes(), ['other', 'another (<1.0)'])
        meta = self.format_metadata(dist)
        self.assert_('Metadata-Version: 1.1' in meta)
        self.assert_('provides:' not in meta.lower())
        self.assert_('requires:' not in meta.lower())
        self.assert_('Obsoletes: other' in meta)
        self.assert_('Obsoletes: another (<1.0)' in meta)

    def test_obsoletes_illegal(self):
        self.assertRaises(ValueError, distutils.dist.Distribution, {'name': 'package',
         'version': '1.0',
         'obsoletes': ['my.pkg (splat)']})

    def format_metadata(self, dist):
        sio = StringIO.StringIO()
        dist.metadata.write_pkg_file(sio)
        return sio.getvalue()

    def test_custom_pydistutils(self):
        old = {}
        for env in ('HOME', 'HOMEPATH', 'HOMEDRIVE'):
            value = os.environ.get(env)
            old[env] = value
            if value is not None:
                del os.environ[env]

        if os.name == 'posix':
            user_filename = '.pydistutils.cfg'
        else:
            user_filename = 'pydistutils.cfg'
        curdir = os.path.dirname(__file__)
        user_filename = os.path.join(curdir, user_filename)
        f = open(user_filename, 'w')
        f.write('.')
        f.close()
        try:
            dist = distutils.dist.Distribution()
            if sys.platform in ('linux', 'darwin'):
                os.environ['HOME'] = curdir
                files = dist.find_config_files()
                self.assert_(user_filename in files)
            if sys.platform == 'win32':
                os.environ['HOME'] = curdir
                files = dist.find_config_files()
                self.assert_(user_filename in files, '%r not found in %r' % (user_filename, files))
        finally:
            for key, value in old.items():
                if value is None:
                    continue
                os.environ[key] = value

            os.remove(user_filename)

        return


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DistributionTestCase))
    suite.addTest(unittest.makeSuite(MetadataTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
