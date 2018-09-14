# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bwdeprecations.py
"""
This module is imported by the BigWorld engine before BWAutoImport, and handles
connecting wrappers for deprecated methods and types to their new names.

It is also the canonical record of the BigWorld Python API deprecation schedule.

It should be safe to backport newer versions into older releases.
"""
import functools
import sys
import warnings

def deprecatedAlias(method, oldname):
    """
    Decorator function, enclosing module, oldname, newname and warnings.
    """

    def warnAndCallWrapper(*args, **kwargs):
        """
        Wrapper around method to raise a DeprecationWarning
        and call through to method
        """
        warnings.warn('%s.%s is deprecated, use %s.%s instead' % (method.__module__,
         oldname,
         method.__module__,
         method.__name__), DeprecationWarning, 2)
        return method(*args, **kwargs)

    return functools.wraps(method)(warnAndCallWrapper)


def addDeprecatedAliasOf(module, newname, oldname):
    """
    Add oldname as a deprecated alias of newname in __module__
    """
    if not hasattr(module, newname):
        return
    if hasattr(module, oldname):
        return
    method = getattr(module, newname)
    setattr(module, oldname, deprecatedAlias(method, oldname))


import BigWorld
if BigWorld.component == 'client':
    addDeprecatedAliasOf(BigWorld, 'serverTime', 'stime')
addDeprecatedAliasOf(BigWorld, 'ThirdPersonTargetingMatrix', 'ThirdPersonTargettingMatrix')
addDeprecatedAliasOf(BigWorld, 'MouseTargetingMatrix', 'MouseTargettingMatrix')
if BigWorld.component == 'client':
    if not hasattr(BigWorld, 'cachedEntities'):
        BigWorld.cachedEntities = {}
    if not hasattr(BigWorld, 'allEntities'):
        BigWorld.allEntities = BigWorld.entities
if BigWorld.component == 'cell':
    import OldSpaceData
