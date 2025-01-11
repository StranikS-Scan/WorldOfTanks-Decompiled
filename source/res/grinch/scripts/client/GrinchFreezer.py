# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/GrinchFreezer.py
import BigWorld
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class GrinchFreezer(DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, *_, **__):
        super(GrinchFreezer, self).__init__(*_, **__)
        self.set_currFreezerVehID(-1)

    def set_currFreezerVehID(self, prevVal):
        if prevVal == -1 and self.currFreezerVehID != -1:
            self.__tryToShowNotification()
        if prevVal != -1 and self.currFreezerVehID == -1:
            self.__tryToCloseNotification()

    def onDestroy(self):
        self.__tryToCloseNotification()
        super(GrinchFreezer, self).onDestroy()

    def __isCurrPlayerVehUnderFreezing(self):
        vehicle = self.entity
        if not vehicle:
            return
        if not vehicle.isAlive():
            return
        return False if vehicle.id != getattr(BigWorld.player(), 'playerVehicleID', 0) else True

    def __tryToShowNotification(self):
        if self.__isCurrPlayerVehUnderFreezing():
            from gui.battle_control import battle_constants
            self.__guiSessionProvider.invalidateVehicleState(battle_constants.VEHICLE_VIEW_STATE.MAP_DEATH_ZONE, battle_constants.DestroyTimerViewState(battle_constants.VEHICLE_VIEW_STATE.MAP_DEATH_ZONE, 0.0, battle_constants.TIMER_VIEW_STATE.CRITICAL, startTime=0.0))

    def __tryToCloseNotification(self):
        if self.__isCurrPlayerVehUnderFreezing():
            from gui.battle_control import battle_constants
            self.__guiSessionProvider.invalidateVehicleState(battle_constants.VEHICLE_VIEW_STATE.MAP_DEATH_ZONE, battle_constants.DestroyTimerViewState.makeCloseTimerState(battle_constants.VEHICLE_VIEW_STATE.MAP_DEATH_ZONE))
