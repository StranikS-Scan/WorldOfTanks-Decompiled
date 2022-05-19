# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleFireCircleEffectComponent.py
from collections import namedtuple
import BigWorld
from battle_royale.gui.constants import BattleRoyaleEquipments
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from Event import EventsSubscriber
from Vehicle import DebuffInfo
FireCircleInfo = namedtuple('FireCircleInfo', ('endTime',))

class VehicleFireCircleEffectComponent(BigWorld.DynamicScriptComponent, EventsSubscriber):
    __CLASS_NAME = 'VehicleFireCircleEffectComponent'
    EQUIPMENT_NAME = BattleRoyaleEquipments.FIRE_CIRCLE

    def __init__(self):
        super(VehicleFireCircleEffectComponent, self).__init__()
        self.__elapsedTime = 0.0
        self.__calculateDebuffTime()
        self.__udateVisuals()
        self.subscribeToEvent(self.entity.guiSessionProvider.onUpdateObservedVehicleData, self.__onUpdateObservedVehicleData)
        self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.EQUIPMENT_NAME, self.entity.id, FireCircleInfo(self.finishTime))

    def set_finishTime(self, _):
        self.__calculateDebuffTime()
        self.__udateVisuals()
        self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.EQUIPMENT_NAME, self.entity.id, FireCircleInfo(self.finishTime))

    def onDestroy(self):
        self.unsubscribeFromAllEvents()
        self.__calculateDebuffTime(isIgnoreSelf=True)
        self.__udateVisuals()
        self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.EQUIPMENT_NAME, self.entity.id, FireCircleInfo(0))

    def onLeaveWorld(self, *args):
        self.unsubscribeFromAllEvents()
        if self.finishTime - BigWorld.serverTime() > 0.0:
            self.__hideMarker()
            ctrl = self.entity.guiSessionProvider.shared.feedback
            ctrl.invalidateDebuff(self.entity.id, DebuffInfo(0, animated=True))

    def __calculateDebuffTime(self, isIgnoreSelf=False):

        def isCandidate(key, comp):
            if isIgnoreSelf:
                if key:
                    return key.startswith(self.__CLASS_NAME) and comp is not self
                return comp is not self
            return key.startswith(self.__CLASS_NAME) if key else isinstance(comp, VehicleFireCircleEffectComponent)

        compItems = self.entity.dynamicComponents.items()
        allTimes = [ comp.finishTime for key, comp in compItems if isCandidate(key, comp) ]
        self.__elapsedTime = max(max(allTimes) - BigWorld.serverTime(), 0.0) if allTimes else 0.0

    def __udateVisuals(self):
        self.__updateFireCircleTimer()
        self.__updateFireCircleMarker()

    def __updateFireCircleTimer(self):
        if self.entity.id == BigWorld.player().getObservedVehicleID():
            self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.FIRE_CIRCLE, self.__elapsedTime)

    def __updateFireCircleMarker(self):
        if self.entity.id != BigWorld.player().getObservedVehicleID() and self.__elapsedTime:
            self.__showMarker(self.entity.id, self.__elapsedTime)
        else:
            self.__hideMarker()

    def __showMarker(self, vehicleID, elapsedTime):
        feedback = self.entity.guiSessionProvider.shared.feedback
        data = {'isShown': True,
         'isSourceVehicle': False,
         'duration': elapsedTime,
         'animated': True,
         'markerID': BATTLE_MARKER_STATES.FIRE_CIRCLE_STATE}
        feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.VEHICLE_CUSTOM_MARKER, vehicleID, data)

    def __hideMarker(self):
        feedback = self.entity.guiSessionProvider.shared.feedback
        data = {'isShown': False,
         'isSourceVehicle': False,
         'duration': 0.0,
         'animated': True,
         'markerID': BATTLE_MARKER_STATES.FIRE_CIRCLE_STATE}
        feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.VEHICLE_CUSTOM_MARKER, self.entity.id, data)

    def __onUpdateObservedVehicleData(self, *args, **kwargs):
        self.__calculateDebuffTime()
        self.__udateVisuals()
