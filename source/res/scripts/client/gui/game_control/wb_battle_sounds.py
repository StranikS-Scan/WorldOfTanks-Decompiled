# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wb_battle_sounds.py
import logging
import BigWorld
import WWISE
import BattleReplay
from gui.battle_control.battle_constants import UNDEFINED_VEHICLE_ID
from gui.battle_control.controllers.points_of_interest_ctrl import IPointOfInterestListener
from helpers import dependency
from items.vehicles import getItemByCompactDescr
from skeletons.gui.battle_session import IBattleSessionProvider
from weekend_brawl_common import POIActivityStatus
_logger = logging.getLogger(__name__)
_WB_ABILITY_SOUND_LIST = ('INSPIRE', 'RECON', 'BOMBER')

class WBEvents(object):
    ENEMY_CAPTURING_ON = 'wb_point_sirena_on'
    ENEMY_CAPTURING_OFF = 'wb_point_sirena_off'
    GUI_ENEMY_CAPTURING_ON = 'wb_point_sirena_gui_on'
    GUI_ENEMY_CAPTURING_OFF = 'wb_point_sirena_gui_off'
    POINT_CAPTURED_BY_PLAYER = 'wb_point_activated'
    POINT_CAPTURED_BY_ALLY = 'wb_point_activated'
    POINT_CAPTURED_BY_ENEMY = 'wb_point_lost'

    @staticmethod
    def playSound(eventName):
        if BattleReplay.g_replayCtrl.isPlaying and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        WWISE.WW_eventGlobal(eventName)


class WBBattleSoundController(object):

    def __init__(self):
        self.__soundPlayers = (AllyPoiSound(), EnemyPoiSound())

    def init(self):
        for player in self.__soundPlayers:
            player.init()

    def destroy(self):
        for player in self.__soundPlayers:
            player.destroy()

        self.__soundPlayers = None
        return


class _BasePoiSound(object):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def init(self):
        pass

    def destroy(self):
        pass

    def _getArenaDP(self):
        return self._sessionProvider.getArenaDP()


class EnemyPoiSound(_BasePoiSound, IPointOfInterestListener):

    def __init__(self):
        self.__isEnemySoundPlaying = False

    def destroy(self):
        self.__isEnemySoundPlaying = False

    def finishedCapturing(self, pointID, vehicleID):
        arenaDP = self._getArenaDP()
        if arenaDP is None:
            return
        else:
            if vehicleID == UNDEFINED_VEHICLE_ID or not arenaDP.isAlly(vehicleID):
                WBEvents.playSound(WBEvents.POINT_CAPTURED_BY_ENEMY)
            return

    def updateState(self, pointID, status, startTime, vehicleID=UNDEFINED_VEHICLE_ID):
        if status == POIActivityStatus.CAPTURING and vehicleID == UNDEFINED_VEHICLE_ID:
            self.__enemySoundsOn(pointID)
        else:
            self.__enemySoundsOff(pointID)

    def __enemySoundsOn(self, pointID):
        point = BigWorld.entity(pointID)
        if point is not None and not self.__isEnemySoundPlaying:
            point.playSound(WBEvents.ENEMY_CAPTURING_ON)
            WBEvents.playSound(WBEvents.GUI_ENEMY_CAPTURING_ON)
            self.__isEnemySoundPlaying = True
        return

    def __enemySoundsOff(self, pointID):
        point = BigWorld.entity(pointID)
        if point is None:
            return
        else:
            if self.__isEnemySoundPlaying:
                point.playSound(WBEvents.ENEMY_CAPTURING_OFF)
                WBEvents.playSound(WBEvents.GUI_ENEMY_CAPTURING_OFF)
                self.__isEnemySoundPlaying = False
            return


class AllyPoiSound(_BasePoiSound, IPointOfInterestListener):

    def finishedCapturing(self, pointID, vehicleID):
        arenaDP = self._getArenaDP()
        if arenaDP is None or vehicleID == UNDEFINED_VEHICLE_ID:
            return
        else:
            if vehicleID == arenaDP.getPlayerVehicleID():
                WBEvents.playSound(WBEvents.POINT_CAPTURED_BY_PLAYER)
            elif arenaDP.isAlly(vehicleID):
                WBEvents.playSound(WBEvents.POINT_CAPTURED_BY_ALLY)
            return


class UsedAbilitySound(_BasePoiSound, IPointOfInterestListener):

    def usedAbility(self, equipmentCD, vehicleID):
        battleCxt = self._sessionProvider.getCtx()
        if not battleCxt.isCurrentPlayer(vehicleID):
            return
        else:
            item = getItemByCompactDescr(equipmentCD)
            if item is None:
                return
            prefix = item.name.split('_')[0].upper()
            if prefix not in _WB_ABILITY_SOUND_LIST:
                return
            soundEvent = item.wwsoundEquipmentUsed
            if soundEvent:
                WBEvents.playSound(soundEvent)
            return
