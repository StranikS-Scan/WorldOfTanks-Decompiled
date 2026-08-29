# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/IlluminationFlareTargetController.py
from __future__ import absolute_import
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, VEHICLE_VIEW_STATE
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from helpers.dependency import descriptor
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.components.vehicle_component import VehicleDynamicComponent

class IlluminationFlareTargetController(VehicleDynamicComponent):
    session = descriptor(IBattleSessionProvider)

    def __init__(self):
        super(IlluminationFlareTargetController, self).__init__()
        g_eventBus.addListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        self.session.shared.vehicleState.onVehicleControlling += self.__onVehicleControlling
        self._initComponent()
        if self.spottedMarker is not None:
            self.__update()
        return

    def __onMarkersManagerMarkersCreated(self, event):
        g_eventBus.removeListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        if not self.isAppearanceReady():
            return
        self.__update()

    def onDestroy(self):
        try:
            g_eventBus.removeListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
            self.session.shared.vehicleState.onVehicleControlling -= self.__onVehicleControlling
        except Exception:
            LOG_CURRENT_EXCEPTION()

        super(IlluminationFlareTargetController, self).onDestroy()

    def set_spottedMarker(self, _):
        self.__update()

    def __onVehicleControlling(self, _):
        self.__update()

    def __update(self):
        vehID = self.entity.id
        self.session.shared.feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.ILLUMINATION_FLARE_SPOTTED_MARKER, vehID, self)
        vehicleState = self.session.shared.vehicleState
        if vehicleState is not None and vehID == vehicleState.getControllingVehicleID():
            self.session.invalidateVehicleState(VEHICLE_VIEW_STATE.ILLUMINATION_FLARE_SPOTTED, self)
        return
