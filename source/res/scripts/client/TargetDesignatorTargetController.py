# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TargetDesignatorTargetController.py
import typing
from functools import partial
from PlayerEvents import g_playerEvents
from constants import DIRECT_DETECTION_TYPE
from gui.battle_control.avatar_getter import isFPV, getVehicleIDAttached
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, VEHICLE_VIEW_STATE
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from helpers.dependency import descriptor
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.components.vehicle_component import VehicleDynamicComponent
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
    from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import VehicleMarkerPlugin

class TargetDesignatorTargetController(VehicleDynamicComponent):
    session = descriptor(IBattleSessionProvider)

    def __init__(self):
        super(TargetDesignatorTargetController, self).__init__()
        g_eventBus.addListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        self.session.shared.vehicleState.onVehicleControlling += self.__onVehicleControlling
        self.isFPV = partial(isFPV, self.entity.id)
        self._initComponent()

    def __onMarkersManagerMarkersCreated(self, event):
        g_eventBus.removeListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        if not self.isAppearanceReady():
            return
        manager = event.getMarkersManager()
        plugin = manager.getPlugin('vehicles')
        vehID = self.entity.id
        handle = plugin.getVehicleMarkerID(vehID)
        plugin.updateTargetDesignatorSpottedMarkerTimer(vehID, handle, self)

    def onDestroy(self):
        g_eventBus.removeListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        self.session.shared.vehicleState.onVehicleControlling -= self.__onVehicleControlling
        super(TargetDesignatorTargetController, self).onDestroy()

    def set_spottedMarker(self, _):
        self._updateComponentAppearance()

    def set_hasUnspottedIndicator(self, _):
        if self.entity.id != getVehicleIDAttached():
            return
        g_playerEvents.onObservedByEnemy(DIRECT_DETECTION_TYPE.UNSPOTTED, bool(self.hasUnspottedIndicator))

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(TargetDesignatorTargetController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__update()

    def __onVehicleControlling(self, _):
        self._updateComponentAppearance()

    def __update(self):
        vehID = self.entity.id
        self.session.shared.feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.TARGET_DESIGNATOR_SPOTTED_MARKER, vehID, self)
        self.session.invalidateVehicleState(VEHICLE_VIEW_STATE.TARGET_DESIGNATOR, self, vehID)
