# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/legacy/repair_timer.py
import weakref
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_constants import REPAIR_STATE_ID
from gui.shared.utils.plugins import IPlugin
from helpers import time_utils
_CALLBACK_NAME = 'battle.onLoadRepairTimer'

class _RepairTimer(object):

    def __init__(self, battleUI):
        self.__flashObject = weakref.proxy(battleUI.movie.repairTimer.instance)

    def destroy(self):
        self.__flashObject = None
        return

    def showTimer(self, state, title, description):
        self.__flashObject.as_show(state, title, description)

    def updateTime(self, timeLeft):
        self.__flashObject.as_update(time_utils.getTimeLeftFormat(timeLeft))

    def hideTimer(self):
        self.__flashObject.as_hide()


class RepairTimerPlugin(IPlugin):

    def __init__(self, parentObj):
        super(RepairTimerPlugin, self).__init__(parentObj)
        self.__repairTimer = None
        self.__isTimerShown = False
        self.__pointIndex = -1
        self.__stateID = REPAIR_STATE_ID.UNRESOLVED
        return

    def init(self):
        super(RepairTimerPlugin, self).init()
        self._parentObj.addExternalCallback(_CALLBACK_NAME, self.__onLoad)

    def fini(self):
        self._parentObj.removeExternalCallback(_CALLBACK_NAME)
        super(RepairTimerPlugin, self).fini()

    def start(self):
        ctrl = g_sessionProvider.dynamic.repair
        if ctrl is not None:
            ctrl.onStateCreated += self.__onRepairPointStateCreated
            ctrl.onTimerUpdated += self.__onRepairPointTimerUpdated
            ctrl.onVehicleEntered += self.__onRepairPointVehicleEntered
            ctrl.onVehicleLeft += self.__onRepairPointVehicleLeft
        super(RepairTimerPlugin, self).start()
        self._parentObj.movie.falloutItems.as_loadRepairTimer()
        return

    def stop(self):
        ctrl = g_sessionProvider.dynamic.repair
        if ctrl is not None:
            ctrl.onStateCreated -= self.__onRepairPointStateCreated
            ctrl.onTimerUpdated -= self.__onRepairPointTimerUpdated
            ctrl.onVehicleEntered -= self.__onRepairPointVehicleEntered
            ctrl.onVehicleLeft -= self.__onRepairPointVehicleLeft
        if self.__repairTimer is not None:
            self.__repairTimer.destroy()
            self.__repairTimer = None
        super(RepairTimerPlugin, self).stop()
        return

    def __showRepairingTimer(self):
        if self.__repairTimer is not None:
            self.__isTimerShown = True
            self.__repairTimer.showTimer('progress', INGAME_GUI.REPAIRPOINT_TITLE, None)
        return

    def __showCooldownTimer(self):
        if self.__repairTimer is not None:
            self.__isTimerShown = True
            self.__repairTimer.showTimer('cooldown', INGAME_GUI.REPAIRPOINT_TITLE, INGAME_GUI.REPAIRPOINT_UNAVAILABLE)
        return

    def __hideTimer(self):
        if self.__repairTimer is not None:
            self.__isTimerShown = False
            self.__repairTimer.hideTimer()
        return

    def __onLoad(self, _):
        self.__repairTimer = _RepairTimer(self._parentObj)
        self.__onRepairPointStateCreated(self.__pointIndex, self.__stateID)

    def __onRepairPointStateCreated(self, pointIndex, stateID):
        self.__stateID = stateID
        self.__pointIndex = pointIndex
        if stateID == REPAIR_STATE_ID.REPAIRING:
            self.__showRepairingTimer()
        elif stateID == REPAIR_STATE_ID.COOLDOWN:
            self.__showCooldownTimer()
        else:
            self.__hideTimer()

    def __onRepairPointTimerUpdated(self, _, __, timeLeft):
        if self.__isTimerShown and self.__repairTimer is not None:
            self.__repairTimer.updateTime(timeLeft)
        return

    def __onRepairPointVehicleEntered(self, _, stateID):
        self.__stateID = stateID
        if stateID == REPAIR_STATE_ID.REPAIRING:
            self.__showRepairingTimer()
        elif stateID == REPAIR_STATE_ID.COOLDOWN:
            self.__showCooldownTimer()

    def __onRepairPointVehicleLeft(self, _, __):
        self.__hideTimer()
