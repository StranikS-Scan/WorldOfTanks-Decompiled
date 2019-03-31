# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_register.py
# Compiled at: 2010-10-21 18:49:01
"""Tests for distutils.command.register."""
import sys
import os
import unittest
from distutils.command.register import register
from distutils.core import Distribution
from distutils.tests import support
from distutils.tests.test_config import PYPIRC, PyPIRCCommandTestCase

class RawInputs(object):
    """Fakes user inputs."""

    def __init__(self, *answers):
        self.answers = answers
        self.index = 0

    def __call__(self, prompt=''):
        try:
            return self.answers[self.index]
        finally:
            self.index += 1


WANTED_PYPIRC = '[distutils]\nindex-servers =\n    pypi\n\n[pypi]\nusername:tarek\npassword:xxx\n'

class registerTestCase(PyPIRCCommandTestCase):

    def test_create_pypirc(self):
        dist = Distribution()
        dist.metadata.url = 'xxx'
        dist.metadata.author = 'xxx'
        dist.metadata.author_email = 'xxx'
        dist.metadata.name = 'xxx'
        dist.metadata.version = 'xxx'
        cmd = register(dist)
        self.assert_(not os.path.exists(self.rc))
        inputs = RawInputs('1', 'tarek', 'y')
        from distutils.command import register as register_module
        register_module.raw_input = inputs.__call__

        def _getpass(prompt):
            pass

        register_module.getpass.getpass = _getpass

        class FakeServer(object):

            def __init__(self):
                self.calls = []

            def __call__(self, *args):
                els = args[0].items()
                els.sort()
                self.calls.append(tuple(els))

        cmd.post_to_server = pypi_server = FakeServer()
        cmd.run()
        self.assert_(os.path.exists(self.rc))
        content = open(self.rc).read()
        self.assertEquals(content, WANTED_PYPIRC)

        def _no_way(prompt=''):
            raise AssertionError(prompt)

        register_module.raw_input = _no_way
        cmd.run()
        self.assert_(len(pypi_server.calls), 2)
        self.assert_(pypi_server.calls[0], pypi_server.calls[1])


def test_suite():
    return unittest.makeSuite(registerTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
