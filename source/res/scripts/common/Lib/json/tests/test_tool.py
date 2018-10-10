# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/json/tests/test_tool.py
import os
import sys
import textwrap
import unittest
import subprocess
from test import test_support
from test.script_helper import assert_python_ok

class TestTool(unittest.TestCase):
    data = '\n\n        [["blorpie"],[ "whoops" ] , [\n                                 ],\t"d-shtaeou",\r"d-nthiouh",\n        "i-vhbjkhnth", {"nifty":87}, {"morefield" :\tfalse,"field"\n            :"yes"}  ]\n           '
    expect = textwrap.dedent('    [\n        [\n            "blorpie"\n        ],\n        [\n            "whoops"\n        ],\n        [],\n        "d-shtaeou",\n        "d-nthiouh",\n        "i-vhbjkhnth",\n        {\n            "nifty": 87\n        },\n        {\n            "field": "yes",\n            "morefield": false\n        }\n    ]\n    ')

    def test_stdin_stdout(self):
        proc = subprocess.Popen((sys.executable, '-m', 'json.tool'), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = proc.communicate(self.data.encode())
        self.assertEqual(out.splitlines(), self.expect.encode().splitlines())
        self.assertEqual(err, None)
        return

    def _create_infile(self):
        infile = test_support.TESTFN
        with open(infile, 'w') as fp:
            self.addCleanup(os.remove, infile)
            fp.write(self.data)
        return infile

    def test_infile_stdout(self):
        infile = self._create_infile()
        rc, out, err = assert_python_ok('-m', 'json.tool', infile)
        self.assertEqual(out.splitlines(), self.expect.encode().splitlines())
        self.assertEqual(err, '')

    def test_infile_outfile(self):
        infile = self._create_infile()
        outfile = test_support.TESTFN + '.out'
        rc, out, err = assert_python_ok('-m', 'json.tool', infile, outfile)
        self.addCleanup(os.remove, outfile)
        with open(outfile, 'r') as fp:
            self.assertEqual(fp.read(), self.expect)
        self.assertEqual(out, '')
        self.assertEqual(err, '')
