# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/fallout/repair_timer.py
from gui.Scaleform.daapi.view.meta.RepairPointTimerMeta import RepairPointTimerMeta
from gui.battle_control.battle_constants import REPAIR_STATE_ID
from helpers import dependency
from helpers import time_utils
from skeletons.gui.battle_session import IBattleSessionProvider
_STATES_TO_SHOW_TIMES = {REPAIR_STATE_ID.REPAIRING: 'progress',
 REPAIR_STATE_ID.COOLDOWN: 'cooldown'}

class RepairPointTimer(RepairPointTimerMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RepairPointTimer, self).__init__()
        self.__isTimerShown = False
        self.__pointIndex = -1

    def _populate(self):
        super(RepairPointTimer, self)._populate()
        self.as_useActionScriptTimerS(False)
        ctrl = self.sessionProvider.dynamic.repair
        if ctrl is not None:
            for pointIndex, stateID, isInPoint in ctrl.getPointsStates():
                if isInPoint and stateID in _STATES_TO_SHOW_TIMES:
                    self.__showTimer(pointIndex, stateID)
                    break

            ctrl.onStateCreated += self.__onRepairPointStateCreated
            ctrl.onTimerUpdated += self.__onRepairPointTimerUpdated
            ctrl.onVehicleEntered += self.__onRepairPointVehicleEntered
            ctrl.onVehicleLeft += self.__onRepairPointVehicleLeft
        return

    def _dispose(self):
        ctrl = self.sessionProvider.dynamic.repair
        if ctrl is not None:
            ctrl.onStateCreated -= self.__onRepairPointStateCreated
            ctrl.onTimerUpdated -= self.__onRepairPointTimerUpdated
            ctrl.onVehicleEntered -= self.__onRepairPointVehicleEntered
            ctrl.onVehicleLeft -= self.__onRepairPointVehicleLeft
        super(RepairPointTimer, self)._dispose()
        return

    def __showTimer(self, pointIndex, stateID):
        self.__isTimerShown = True
        self.__pointIndex = pointIndex
        self.as_setStateS(_STATES_TO_SHOW_TIMES[stateID])

    def __hideTimer(self):
        if self.__isTimerShown:
            self.__isTimerShown = False
            self.__pointIndex = -1
            self.as_hideS()

    def __onRepairPointStateCreated(self, pointIndex, stateID):
        if stateID in _STATES_TO_SHOW_TIMES:
            self.__showTimer(pointIndex, stateID)
        else:
            self.__hideTimer()

    def __onRepairPointTimerUpdated(self, pointIndex, stateID, timeLeft):
        if self.__isTimerShown and self.__pointIndex == pointIndex:
            self.as_setTimeStringS(time_utils.getTimeLeftFormat(timeLeft))

    def __onRepairPointVehicleEntered(self, pointIndex, stateID):
        if stateID in _STATES_TO_SHOW_TIMES:
            self.__showTimer(pointIndex, stateID)

    def __onRepairPointVehicleLeft(self, pointIndex, stateID):
        self.__hideTimer()
