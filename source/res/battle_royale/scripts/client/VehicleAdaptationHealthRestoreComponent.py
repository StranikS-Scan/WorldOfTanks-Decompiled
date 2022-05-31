# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleAdaptationHealthRestoreComponent.py
import BigWorld
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID
from Event import EventsSubscriber
from script_component.DynamicScriptComponent import DynamicScriptComponent

class VehicleAdaptationHealthRestoreComponent(EventsSubscriber, DynamicScriptComponent):

    def __init__(self):
        super(VehicleAdaptationHealthRestoreComponent, self).__init__()
        self.__timeLeft = 0.0
        self.subscribeToEvent(self.entity.guiSessionProvider.onUpdateObservedVehicleData, self.__onUpdateObservedVehicleData)

    def _onAvatarReady(self):
        self.set_finishTime()
        self.set_restoreHealth()

    def set_finishTime(self, _=None):
        self.__calculateElapsedTime()
        self.__updateVisuals()

    def set_restoreHealth(self, _=None):
        data = {'type': 'additionInfo',
         'value': self.restoreHealth}
        self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.ADAPTATION_HEALTH_RESTORE, data)

    def onDestroy(self):
        self.__destroy()

    def onLeaveWorld(self, *args):
        self.__destroy()

    def __destroy(self):
        self.unsubscribeFromAllEvents()
        self.__timeLeft = 0.0
        self.__updateTimer()
        self.__hideMarker()

    def __calculateElapsedTime(self):
        self.__timeLeft = self.finishTime - BigWorld.serverTime() if self.finishTime else 0.0

    def __updateVisuals(self):
        self.__updateTimer()
        self.__updateMarker()

    def __updateTimer(self):
        if self.entity.id == BigWorld.player().getObservedVehicleID():
            data = {'type': 'time',
             'value': self.__timeLeft}
            self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.ADAPTATION_HEALTH_RESTORE, data)

    def __onUpdateObservedVehicleData(self, *args, **kwargs):
        self.__calculateElapsedTime()
        self.__updateVisuals()

    def __updateMarker(self):
        if self.entity.id != BigWorld.player().getObservedVehicleID():
            self.__showMarker()

    def __showMarker(self):
        data = {'isShown': True,
         'isSourceVehicle': True,
         'duration': self.__timeLeft,
         'animated': True,
         'markerID': BATTLE_MARKER_STATES.ADAPTATION_HEALTH_RESTORE_STATE}
        feedback = self.entity.guiSessionProvider.shared.feedback
        feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.VEHICLE_CUSTOM_MARKER, self.entity.id, data)

    def __hideMarker(self):
        data = {'isShown': False,
         'isSourceVehicle': True,
         'duration': 0.0,
         'animated': True,
         'markerID': BATTLE_MARKER_STATES.ADAPTATION_HEALTH_RESTORE_STATE}
        feedback = self.entity.guiSessionProvider.shared.feedback
        feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.VEHICLE_CUSTOM_MARKER, self.entity.id, data)
