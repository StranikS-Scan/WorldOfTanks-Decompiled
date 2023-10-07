# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleDebuffBase.py
from collections import namedtuple
import BigWorld
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID
DebuffInfo = namedtuple('DebuffInfo', ('duration', 'animated'))

class HWVehicleDebuffBase(BigWorld.DynamicScriptComponent):
    _TIMER_ID = None

    def __init__(self):
        super(HWVehicleDebuffBase, self).__init__()
        self._guiSessionProvider = self.entity.guiSessionProvider
        self._guiFeedback = self.entity.guiSessionProvider.shared.feedback
        BigWorld.player().onVehicleLeaveWorld += self.__onVehicleLeaveWorld
        self._updateVisuals()

    def onDestroy(self):
        BigWorld.player().onVehicleLeaveWorld -= self.__onVehicleLeaveWorld
        self._updateVisuals(isShow=False)

    def onLeaveWorld(self, *args):
        self.onDestroy()

    def set_finishTime(self, _=None):
        self._updateVisuals()

    def __onVehicleLeaveWorld(self, v):
        if self.entity.id != v.id:
            return
        self.__updateMarker(isShow=False)

    def _updateVisuals(self, isShow=True):
        hasDebuff = False
        if hasattr(self.entity, 'hwVehicleAbilitiesManager'):
            hasDebuff = self.entity.hwVehicleAbilitiesManager.debuffsMask > 0
        if self.entity.id == BigWorld.player().playerVehicleID and self._TIMER_ID is not None:
            self.__updateTimer(isShow)
            self.__updateDamagePanel(hasDebuff)
        else:
            self.__updateMarker(hasDebuff)
        return

    def _getTimerData(self, isShow=True):
        data = {'duration': self._getDuration() if isShow else 0.0,
         'endTime': self.finishTime}
        return data

    def _getMarkerData(self, isShow=True):
        data = {'isShown': isShow,
         'isSourceVehicle': False,
         'duration': self._getDuration() if isShow else 0.0,
         'animated': True,
         'markerID': BATTLE_MARKER_STATES.HW_DEBUFF_STATE}
        return data

    def _getDuration(self):
        return self.finishTime - BigWorld.serverTime() if self.finishTime else 0.0

    def __updateTimer(self, isShow):
        data = self._getTimerData(isShow)
        self._guiSessionProvider.invalidateVehicleState(self._TIMER_ID, data)

    def __updateMarker(self, isShow):
        self._guiFeedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.VEHICLE_CUSTOM_MARKER, self.entity.id, self._getMarkerData(isShow))

    def __updateDamagePanel(self, isShow):
        playerDebuffInfo = DebuffInfo(duration=0.1 if isShow else 0, animated=isShow)
        self._guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DEBUFF, playerDebuffInfo)
