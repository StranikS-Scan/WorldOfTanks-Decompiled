# Embedded file name: scripts/common/Lib/distutils/tests/test_upload.py
"""Tests for distutils.command.upload."""
import os
import unittest
from test.test_support import run_unittest
from distutils.command import upload as upload_mod
from distutils.command.upload import upload
from distutils.core import Distribution
from distutils.tests.test_config import PYPIRC, PyPIRCCommandTestCase
PYPIRC_LONG_PASSWORD = '[distutils]\n\nindex-servers =\n    server1\n    server2\n\n[server1]\nusername:me\npassword:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n\n[server2]\nusername:meagain\npassword: secret\nrealm:acme\nrepository:http://another.pypi/\n'
PYPIRC_NOPASSWORD = '[distutils]\n\nindex-servers =\n    server1\n\n[server1]\nusername:me\n'

class FakeOpen(object):

    def __init__(self, url):
        self.url = url
        if not isinstance(url, str):
            self.req = url
        else:
            self.req = None
        self.msg = 'OK'
        return

    def getcode(self):
        return 200


class uploadTestCase(PyPIRCCommandTestCase):

    def setUp(self):
        super(uploadTestCase, self).setUp()
        self.old_open = upload_mod.urlopen
        upload_mod.urlopen = self._urlopen
        self.last_open = None
        return

    def tearDown(self):
        upload_mod.urlopen = self.old_open
        super(uploadTestCase, self).tearDown()

    def _urlopen(self, url):
        self.last_open = FakeOpen(url)
        return self.last_open

    def test_finalize_options(self):
        self.write_file(self.rc, PYPIRC)
        dist = Distribution()
        cmd = upload(dist)
        cmd.finalize_options()
        for attr, waited in (('username', 'me'),
         ('password', 'secret'),
         ('realm', 'pypi'),
         ('repository', 'https://pypi.python.org/pypi')):
            self.assertEqual(getattr(cmd, attr), waited)

    def test_saved_password(self):
        self.write_file(self.rc, PYPIRC_NOPASSWORD)
        dist = Distribution()
        cmd = upload(dist)
        cmd.finalize_options()
        self.assertEqual(cmd.password, None)
        dist.password = 'xxx'
        cmd = upload(dist)
        cmd.finalize_options()
        self.assertEqual(cmd.password, 'xxx')
        return

    def test_upload(self):
        tmp = self.mkdtemp()
        path = os.path.join(tmp, 'xxx')
        self.write_file(path)
        command, pyversion, filename = 'xxx', '2.6', path
        dist_files = [(command, pyversion, filename)]
        self.write_file(self.rc, PYPIRC_LONG_PASSWORD)
        pkg_dir, dist = self.create_dist(dist_files=dist_files, author=u'd\xe9d\xe9')
        cmd = upload(dist)
        cmd.ensure_finalized()
        cmd.run()
        self.assertIn('d\xc3\xa9d\xc3\xa9', self.last_open.req.data)
        headers = dict(self.last_open.req.headers)
        self.assertEqual(headers['Content-length'], '2085')
        self.assertTrue(headers['Content-type'].startswith('multipart/form-data'))
        self.assertEqual(self.last_open.req.get_method(), 'POST')
        self.assertEqual(self.last_open.req.get_full_url(), 'https://pypi.python.org/pypi')
        self.assertIn('xxx', self.last_open.req.data)
        auth = self.last_open.req.headers['Authorization']
        self.assertNotIn('\n', auth)


def test_suite():
    return unittest.makeSuite(uploadTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
