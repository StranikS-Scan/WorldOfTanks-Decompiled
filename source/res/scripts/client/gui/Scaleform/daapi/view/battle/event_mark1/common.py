# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/common.py
from Math import Vector3
import WWISE
from constants import FLAG_TYPES, FLAG_STATE, MARK1_TEAM_NUMBER
from CTFManager import g_ctfManager
from gui.battle_control.controllers.event_mark1.bonus_ctrl import EXTRA_BIG_GUN, EXTRA_MACHINE_GUN
FLAG_MARKER2D_POSITION_ADJUSTMENT = Vector3(0.0, 18.0, 0.0)
MARK1_AT_BASE_WARNING_SOUND = 'ev_mark_at_base'
FLAG_MARK1 = 'EventStaticMarkerUI'
MINIMAP_MARK1_ENTRY = 'mark1MarkerUI'
MINIMAP_MARK1_FLAG = 'Mark1FlagUI'
MINIMAP_ENTRY_STATE_MARK1_ALLY = 'allyMark1'
MINIMAP_ENTRY_STATE_MARK1_ENEMY = 'enemyMark1'
MINIMAP_ENTRY_STATE_ABSORPTION = 'absorptionPoint'
MINIMAP_ENTRY_STATE_ALERT = 'enemyTarget'
MARK1_FLAG_ALLY = {FLAG_TYPES.REPAIR_KIT: 'allyRepair',
 FLAG_TYPES.EXPLOSIVE: 'allyBomb',
 FLAG_TYPES.AMMO1: 'allyAmmo',
 FLAG_TYPES.OTHER: 'bonusBigGun'}
MARK1_FLAG_ENEMY = {FLAG_TYPES.REPAIR_KIT: 'enemyRepair',
 FLAG_TYPES.EXPLOSIVE: 'enemyBomb',
 FLAG_TYPES.AMMO1: 'enemyAmmo',
 FLAG_TYPES.OTHER: 'unknownBonus'}

class BONUS_NAMES(object):
    BIG_GUN = 'bonusBigGun'
    MACHINE_GUN = 'bonusMachineGun'


BONUS_EXTRA_TO_NAME = {EXTRA_BIG_GUN: BONUS_NAMES.BIG_GUN,
 EXTRA_MACHINE_GUN: BONUS_NAMES.MACHINE_GUN,
 None: ''}

class _MARKER2D_ABSORPTION_STATE(object):
    ABSENT = None
    TARGET = 'target'
    ALERT = 'alert'


def isFlagNeedsUpdate(flagID):
    flagType = g_ctfManager.getFlagType(flagID)
    needsUpdate = flagType != FLAG_TYPES.OTHER
    return needsUpdate


def getMark1FlagType(flagType, isAlly=True):
    if isAlly:
        return MARK1_FLAG_ALLY[flagType]
    else:
        return MARK1_FLAG_ENEMY[flagType]


def getMarkers2DAbsorbState(isBearer):
    if isBearer:
        result = _MARKER2D_ABSORPTION_STATE.TARGET
    elif isRepairKitInGame():
        result = _MARKER2D_ABSORPTION_STATE.ALERT
    else:
        result = _MARKER2D_ABSORPTION_STATE.ABSENT
    return result


def isRepairKitInGame():
    hasRepairKit = False
    for flagID, flagInfo in g_ctfManager.getFlags():
        if flagInfo['flagType'] == FLAG_TYPES.REPAIR_KIT and flagInfo['state'] in (FLAG_STATE.ON_GROUND, FLAG_STATE.ON_SPAWN, FLAG_STATE.ON_VEHICLE):
            hasRepairKit = True
            break

    return hasRepairKit


def playMark1AtBaseWarningSound(soundLock):
    if soundLock is not None and not soundLock.isLocked():
        soundLock.lock()
        WWISE.WW_eventGlobal(MARK1_AT_BASE_WARNING_SOUND)
    return
