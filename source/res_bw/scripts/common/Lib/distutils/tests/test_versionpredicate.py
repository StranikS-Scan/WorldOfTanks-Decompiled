# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_versionpredicate.py
# Compiled at: 2010-05-25 20:46:16
"""Tests harness for distutils.versionpredicate.

"""
import distutils.versionpredicate
import doctest

def test_suite():
    return doctest.DocTestSuite(distutils.versionpredicate)
