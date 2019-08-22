# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/battle_royale_helpers.py
import logging
import math
import BigWorld
import CommandMapping
from helpers.i18n import makeString
from gui.Scaleform.locale.READABLE_KEY_NAMES import READABLE_KEY_NAMES
_logger = logging.getLogger(__name__)

def getCircularVisionAngle(vehicle=None):
    if vehicle is None:
        player = BigWorld.player()
        if hasattr(player, 'getVehicleAttached'):
            vehicle = player.getVehicleAttached()
            if vehicle is None:
                _logger.warning('Vehicle has not been created yet!')
                return
        else:
            _logger.warning('Player is not Avatar!')
            return
    if not hasattr(vehicle, 'circularVisionAngle'):
        _logger.warning('Vehicle attribute "circularVisionAngle" is not found!')
        return
    else:
        return math.degrees(vehicle.circularVisionAngle)


def getHotKeyString(command):
    return ' +'.join(_getHotKeyList(command))


def getHotKeyListByIndex(index):
    if index == 0:
        command = CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_LEFT
    else:
        command = CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_RIGHT
    return _getHotKeyList(command)


def _getHotKeyList(command):
    keys = []
    key, satelliteKeys = CommandMapping.g_instance.getCommandKeys(command)
    for satelliteKey in satelliteKeys:
        keys.append(makeString(READABLE_KEY_NAMES.key(BigWorld.keyToString(satelliteKey))))

    keys.append(makeString(READABLE_KEY_NAMES.key(BigWorld.keyToString(key))))
    return keys


def isIncorrectVehicle(vehicle):
    return vehicle is None or not vehicle.isOnlyForBattleRoyaleBattles
