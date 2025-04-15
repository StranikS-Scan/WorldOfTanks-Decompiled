# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_control/controllers/fall_tanks_battle_ctrl.py
import typing
import CommandMapping
import Event
from constants import ARENA_PERIOD
from gui import g_keyEventHandlers
from helpers import dependency
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from skeletons.gui.battle_session import IBattleSessionProvider
from FallTanksController import getPlayerVehicleFallTanksController
from fall_tanks.gui.battle_control.arena_info.interfaces import IFallTanksBattleController
from fall_tanks.gui.battle_control.arena_info.arena_vos import FallTanksKeys, FallTanksVehicleInfo
from fall_tanks.gui.fall_tanks_gui_constants import BATTLE_CTRL_ID
if typing.TYPE_CHECKING:
    from skeletons.gui.battle_session import IArenaDataProvider, IBattleContext, IClientArenaVisitor
    from Vehicle import Vehicle
    from fall_tanks.gui.battle_control.arena_info.interfaces import IFallTanksVehicleInfo
_UNKNOWN_VEHICLE_ID = 0

class FallTanksBattleController(IFallTanksBattleController):
    __slots__ = ('__playerVehicleID', '__currentVehicleID', '__fallTanksAttachedInfo', '__eManager', 'onFallTanksAttachedInfoUpdate')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__playerVehicleID = _UNKNOWN_VEHICLE_ID
        self.__currentVehicleID = _UNKNOWN_VEHICLE_ID
        self.__fallTanksAttachedInfo = FallTanksVehicleInfo()
        self.__eManager = Event.EventManager()
        self.onFallTanksAttachedInfoUpdate = Event.SafeEvent(self.__eManager)

    def getControllerID(self):
        return BATTLE_CTRL_ID.FALL_TANKS_BATTLE_CTRL

    def getCtrlScope(self):
        return _SCOPE.VEHICLES

    def getFallTanksAttachedVehicleInfo(self):
        return self.__fallTanksAttachedInfo

    def getFallTanksPlayerVehicleInfo(self):
        return self.__getFallTanksVehicleInfo(self.__playerVehicleID)

    def startControl(self, battleCtx, arenaVisitor):
        vStateCtrl = self.__sessionProvider.shared.vehicleState
        self.__currentVehicleID = vStateCtrl.getControllingVehicleID() if vStateCtrl else _UNKNOWN_VEHICLE_ID
        self.__playerVehicleID = avatar_getter.getPlayerVehicleID()
        self.__addListeners()

    def stopControl(self):
        self.__fallTanksAttachedInfo = FallTanksVehicleInfo()
        self.__currentVehicleID = _UNKNOWN_VEHICLE_ID
        self.__playerVehicleID = _UNKNOWN_VEHICLE_ID
        self.__removeListeners()
        self.__eManager.clear()

    def invalidateArenaInfo(self):
        self.__updateFallTanksAttachedVehicleInfo()

    def updateVehiclesStats(self, updated, arenaDP):
        if any((vStatsVO.vehicleID == self.__currentVehicleID for _, vStatsVO in updated)):
            self.__updateFallTanksAttachedVehicleInfo(arenaDP)

    def __addListeners(self):
        vStateCtrl = self.__sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        g_keyEventHandlers.add(self.__handleKeyEvent)
        return

    def __removeListeners(self):
        vStateCtrl = self.__sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        g_keyEventHandlers.discard(self.__handleKeyEvent)
        return

    def __handleKeyEvent(self, event):
        if not CommandMapping.g_instance.isFired(CommandMapping.CMD_REQUEST_RECOVERY, event.key) or event.isRepeatedEvent():
            return False
        else:
            component = getPlayerVehicleFallTanksController()
            if self.__sessionProvider.shared.arenaPeriod.getPeriod() == ARENA_PERIOD.BATTLE and component is not None:
                if event.isKeyDown():
                    component.startVehicleEvacuation()
                else:
                    component.stopVehicleEvacuation()
            return True

    def __onVehicleControlling(self, vehicle):
        self.__currentVehicleID = vehicle.id
        self.__updateFallTanksAttachedVehicleInfo()

    def __onVehicleStateUpdated(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.PLAYER_INFO:
            self.__playerVehicleID = value
            self.__updateFallTanksAttachedVehicleInfo()

    def __getFallTanksVehicleInfo(self, vehicleID, arenaDP=None):
        arenaDP = arenaDP or self.__sessionProvider.getArenaDP()
        vehicleStatsVO = arenaDP.getVehicleStats(vehicleID)
        fallTanksInfo = vehicleStatsVO.gameModeSpecific
        return FallTanksVehicleInfo(vehicleID == self.__playerVehicleID, fallTanksInfo.getValue(FallTanksKeys.CHECKPOINT), fallTanksInfo.getValue(FallTanksKeys.FINISH_TIME), fallTanksInfo.getValue(FallTanksKeys.RACE_POSITION), vehicleStatsVO.frags)

    def __updateFallTanksAttachedVehicleInfo(self, arenaDP=None):
        currentVehicleID = self.__currentVehicleID or self.__playerVehicleID
        self.__fallTanksAttachedInfo = self.__getFallTanksVehicleInfo(currentVehicleID, arenaDP)
        self.onFallTanksAttachedInfoUpdate(self.__fallTanksAttachedInfo)


def createFallTanksBattleController():
    return FallTanksBattleController()
