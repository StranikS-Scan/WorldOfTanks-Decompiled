# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/battle_royale/br_helpers.py
import logging
import math
import BigWorld
import CommandMapping
from helpers import dependency
from items import vehicles
from skeletons.gui.game_control import IBattleRoyaleController
from gui.Scaleform.daapi.view.common.keybord_helpers import getHotKeyList
from skeletons.gui.shared.hangar_spaces_switcher import IHangarSpacesSwitcher
_logger = logging.getLogger(__name__)

def getEquipmentById(equipmentId):
    return vehicles.g_cache.equipments()[equipmentId]


def getSmokeDataByPredicate(smokesInfo, predicate):
    if smokesInfo is None or not predicate:
        return (None, None)
    else:
        activeSmokes = list(((sInfo['endTime'], sInfo['equipmentID']) for sInfo in smokesInfo if predicate(sInfo['equipmentID'])))
        if activeSmokes:
            maxEndTime, maxEndTimeEquipmentId = max(activeSmokes)
            return (maxEndTime, getEquipmentById(maxEndTimeEquipmentId))
        return (None, None)


def parseSmokeData(smokesInfo):
    if smokesInfo:
        maxEndTime, eqId = max(((smokeInfo['endTime'], smokeInfo['equipmentID']) for smokeInfo in smokesInfo))
        return (maxEndTime, getEquipmentById(eqId))
    else:
        return (None, None)


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
    if not hasattr(vehicle, 'coneVisibility'):
        _logger.warning('Vehicle attribute "coneVisibility" is not found!')
        return
    else:
        return math.degrees(vehicle.coneVisibility.circularVisionAngle)


def getHotKeyString(command):
    return ' +'.join(getHotKeyList(command))


def getHotKeyListByIndex(index):
    if index == 0:
        command = CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_LEFT
    else:
        command = CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_RIGHT
    return getHotKeyList(command)


def isIncorrectVehicle(vehicle):
    return vehicle is None or not vehicle.isOnlyForBattleRoyaleBattles


def isAdditionalModule(level, unlocks, moduleGetter):
    for unlockIntCD in unlocks:
        itemWhichUnlocks = moduleGetter(unlockIntCD)
        if itemWhichUnlocks.level == level:
            return True

    return False


@dependency.replace_none_kwargs(brCtrl=IBattleRoyaleController)
def canVehicleSpawnBot(vehicleName, brCtrl=None):
    equipmentIds = brCtrl.getBrVehicleEquipmentIds(vehicleName)
    if equipmentIds:
        spawnedBotID = vehicles.g_cache.equipmentIDs()['spawn_kamikaze']
        return spawnedBotID in equipmentIds
    return False


@dependency.replace_none_kwargs(hangarSwitcher=IHangarSpacesSwitcher)
def currentHangarIsSteelHunter(hangarSwitcher=None):
    return hangarSwitcher.currentItem == hangarSwitcher.itemsToSwitch.BATTLE_ROYALE
