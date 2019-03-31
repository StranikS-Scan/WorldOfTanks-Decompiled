# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_config.py
# Compiled at: 2010-10-21 18:49:01
"""Tests for distutils.pypirc.pypirc."""
import sys
import os
import unittest
from distutils.core import PyPIRCCommand
from distutils.core import Distribution
from distutils.log import set_threshold
from distutils.log import WARN
from distutils.tests import support
PYPIRC = '[distutils]\n\nindex-servers =\n    server1\n    server2\n\n[server1]\nusername:me\npassword:secret\n\n[server2]\nusername:meagain\npassword: secret\nrealm:acme\nrepository:http://another.pypi/\n'
PYPIRC_OLD = '[server-login]\nusername:tarek\npassword:secret\n'
WANTED = '[distutils]\nindex-servers =\n    pypi\n\n[pypi]\nusername:tarek\npassword:xxx\n'

class PyPIRCCommandTestCase(support.TempdirManager, unittest.TestCase):

    def setUp(self):
        """Patches the environment."""
        super(PyPIRCCommandTestCase, self).setUp()
        if os.environ.has_key('HOME'):
            self._old_home = os.environ['HOME']
        else:
            self._old_home = None
        tempdir = self.mkdtemp()
        os.environ['HOME'] = tempdir
        self.rc = os.path.join(tempdir, '.pypirc')
        self.dist = Distribution()

        class command(PyPIRCCommand):

            def __init__(self, dist):
                PyPIRCCommand.__init__(self, dist)

            def initialize_options(self):
                pass

            finalize_options = initialize_options

        self._cmd = command
        self.old_threshold = set_threshold(WARN)
        return

    def tearDown(self):
        """Removes the patch."""
        if self._old_home is None:
            del os.environ['HOME']
        else:
            os.environ['HOME'] = self._old_home
        set_threshold(self.old_threshold)
        super(PyPIRCCommandTestCase, self).tearDown()
        return

    def test_server_registration(self):
        f = open(self.rc, 'w')
        try:
            f.write(PYPIRC)
        finally:
            f.close()

        cmd = self._cmd(self.dist)
        config = cmd._read_pypirc()
        config = config.items()
        config.sort()
        waited = [('password', 'secret'),
         ('realm', 'pypi'),
         ('repository', 'http://pypi.python.org/pypi'),
         ('server', 'server1'),
         ('username', 'me')]
        self.assertEquals(config, waited)
        f = open(self.rc, 'w')
        f.write(PYPIRC_OLD)
        f.close()
        config = cmd._read_pypirc()
        config = config.items()
        config.sort()
        waited = [('password', 'secret'),
         ('realm', 'pypi'),
         ('repository', 'http://pypi.python.org/pypi'),
         ('server', 'server-login'),
         ('username', 'tarek')]
        self.assertEquals(config, waited)

    def test_server_empty_registration(self):
        cmd = self._cmd(self.dist)
        rc = cmd._get_rc_file()
        self.assert_(not os.path.exists(rc))
        cmd._store_pypirc('tarek', 'xxx')
        self.assert_(os.path.exists(rc))
        content = open(rc).read()
        self.assertEquals(content, WANTED)


def test_suite():
    return unittest.makeSuite(PyPIRCCommandTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
