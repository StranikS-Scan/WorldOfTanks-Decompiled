# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/dep_util.py
__revision__ = '$Id$'
import os
from stat import ST_MTIME
from distutils.errors import DistutilsFileError

def newer(source, target):
    if not os.path.exists(source):
        raise DistutilsFileError("file '%s' does not exist" % os.path.abspath(source))
    return True if not os.path.exists(target) else os.stat(source)[ST_MTIME] > os.stat(target)[ST_MTIME]


def newer_pairwise(sources, targets):
    if len(sources) != len(targets):
        raise ValueError, "'sources' and 'targets' must be same length"
    n_sources = []
    n_targets = []
    for source, target in zip(sources, targets):
        if newer(source, target):
            n_sources.append(source)
            n_targets.append(target)

    return (n_sources, n_targets)


def newer_group(sources, target, missing='error'):
    if not os.path.exists(target):
        return True
    target_mtime = os.stat(target)[ST_MTIME]
    for source in sources:
        if not os.path.exists(source):
            if missing == 'error':
                pass
            elif missing == 'ignore':
                continue
            elif missing == 'newer':
                return True
        if os.stat(source)[ST_MTIME] > target_mtime:
            return True

    return False
