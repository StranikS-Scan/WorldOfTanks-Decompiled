# Embedded file name: scripts/common/BWUtil.py
import ResMgr
from bwdebug import TRACE_MSG
try:
    orig_open = __builtins__['open']
except TypeError as e:
    orig_open = __builtins__.open

def bwResRelativeOpen(name, *args):
    try:
        absname = ResMgr.resolveToAbsolutePath(name)
    except:
        raise IOError(2, 'No such file or directory')

    absname = unicode(absname)
    return orig_open(absname, *args)


def monkeyPatchOpen():
    TRACE_MSG('BWUtil.monkeyPatchOpen: Patching open()')
    try:
        __builtins__['open'] = bwResRelativeOpen
    except TypeErorr as e:
        __builtins__.open = bwResRelativeOpen
