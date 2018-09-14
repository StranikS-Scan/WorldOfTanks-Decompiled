# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_versionpredicate.py
"""Tests harness for distutils.versionpredicate.

"""
import distutils.versionpredicate
import doctest
from test.test_support import run_unittest

def test_suite():
    return doctest.DocTestSuite(distutils.versionpredicate)


if __name__ == '__main__':
    run_unittest(test_suite())
