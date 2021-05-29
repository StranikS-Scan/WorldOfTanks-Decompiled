# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bwdeprecations.py
import functools
import sys
import warnings

def deprecatedAlias(method, oldname):

    def warnAndCallWrapper(*args, **kwargs):
        warnings.warn('%s.%s is deprecated, use %s.%s instead' % (method.__module__,
         oldname,
         method.__module__,
         method.__name__), DeprecationWarning, 2)
        return method(*args, **kwargs)

    return functools.wraps(method)(warnAndCallWrapper)


def addDeprecatedAliasOf(module, newname, oldname):
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
