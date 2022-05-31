# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleThunderStrikeComponent.py
from collections import namedtuple
import BigWorld
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from Event import EventsSubscriber
ThunderStrikeDebuffInfo = namedtuple('ThunderStrikeDebuffInfo', 'id, elapsedTime')

class VehicleThunderStrikeComponent(BigWorld.DynamicScriptComponent, EventsSubscriber):

    def __init__(self):
        super(VehicleThunderStrikeComponent, self).__init__()
        self.__id = id(self)
        self.__elapsedTime = 0.0
        self.__calculateElapsedTime()
        self.__updateVisuals()
        self.subscribeToEvent(self.entity.guiSessionProvider.onUpdateObservedVehicleData, self.__onUpdateObservedVehicleData)

    def set_finishTime(self, prev):
        self.__calculateElapsedTime()
        self.__updateVisuals()

    def onDestroy(self):
        self.__destroy()

    def onLeaveWorld(self, *args):
        self.__destroy()

    def __destroy(self):
        self.unsubscribeFromAllEvents()
        self.__elapsedTime = 0.0
        self.__updateTimer()
        self.__hideMarker()

    def __onUpdateObservedVehicleData(self, *args, **kwargs):
        self.__calculateElapsedTime()
        self.__updateVisuals()

    def __updateVisuals(self):
        self.__updateTimer()
        self.__updateMarker()

    def __calculateElapsedTime(self):
        self.__elapsedTime = self.finishTime - BigWorld.serverTime() if self.finishTime else 0.0

    def __updateTimer(self):
        if self.entity.id == BigWorld.player().getObservedVehicleID():
            data = ThunderStrikeDebuffInfo(self.__id, self.__elapsedTime)
            self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.THUNDER_STRIKE, data)

    def __updateMarker(self):
        if self.entity.id != BigWorld.player().getObservedVehicleID():
            self.__showMarker(self.__elapsedTime)

    def __showMarker(self, elapsedTime):
        data = {'isShown': True,
         'isSourceVehicle': False,
         'duration': elapsedTime,
         'animated': True,
         'markerID': BATTLE_MARKER_STATES.THUNDER_STRIKE_STATE}
        feedback = self.entity.guiSessionProvider.shared.feedback
        feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.VEHICLE_CUSTOM_MARKER, self.entity.id, data)

    def __hideMarker(self):
        data = {'isShown': False,
         'isSourceVehicle': False,
         'duration': 0.0,
         'animated': True,
         'markerID': BATTLE_MARKER_STATES.THUNDER_STRIKE_STATE}
        feedback = self.entity.guiSessionProvider.shared.feedback
        feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.VEHICLE_CUSTOM_MARKER, self.entity.id, data)
