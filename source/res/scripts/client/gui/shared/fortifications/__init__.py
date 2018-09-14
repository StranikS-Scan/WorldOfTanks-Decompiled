# Embedded file name: scripts/client/gui/shared/fortifications/__init__.py
import types
import BigWorld
from debug_utils import LOG_DEBUG
from FortifiedRegionBase import FORT_STATE

def getClientFortMgr():
    return getattr(BigWorld.player(), 'fort', None)


def getClientFort():
    fortMgr = getClientFortMgr()
    fort = None
    if fortMgr:
        fort = getattr(fortMgr, '_fort', None)
    return fort


def getClanFortState():
    state = None
    fortMgr = getClientFortMgr()
    if fortMgr:
        state = getattr(fortMgr, 'state', None)
    return state


def isStartingScriptDone():
    state = getClanFortState()
    result = False
    if type(state) is types.IntType:
        result = state & FORT_STATE.FIRST_BUILD_DONE > 0
    return result


def isStartingScriptNotStarted():
    state = getClanFortState()
    result = False
    if type(state) is types.IntType:
        result = state & FORT_STATE.FIRST_DIR_OPEN == 0
    return result


def isSortieEnabled():
    return isStartingScriptDone()


def isFortificationEnabled():
    try:
        import fortified_regions
        return fortified_regions.g_cache.isSupported
    except Exception:
        LOG_DEBUG('There is problem while getting fortifications supporting flag.Fortification availability value is default')
        return False


def isFortificationBattlesEnabled():
    try:
        return not BigWorld.player().serverSettings['isFortBattlesDisabled']
    except Exception:
        LOG_DEBUG('There is problem while getting fortifications battles supporting flag.Fortification availability value is default')
        return False


def getDirectionFromDirPos(dirPos):
    return dirPos >> 4 & 15


def getPositionFromDirPos(dirPos):
    return dirPos & 15
