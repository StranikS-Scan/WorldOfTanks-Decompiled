# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TargetDesignatorTargetController.py
import logging
import typing
from functools import partial
from PlayerEvents import g_playerEvents
from aih_constants import CTRL_MODE_NAME
from gui.battle_control.avatar_getter import isFPV
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, VEHICLE_VIEW_STATE
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from helpers.dependency import descriptor
from math_utils import almostEqual
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.components.vehicle_component import VehicleDynamicComponent
if typing.TYPE_CHECKING:
    from typing import Optional
    from Avatar import PlayerAvatar
    from Vehicle import Vehicle
    from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
    from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import VehicleMarkerPlugin
_debug = logging.getLogger(__name__).debug

class TargetDesignatorTargetController(VehicleDynamicComponent):
    session = descriptor(IBattleSessionProvider)

    def __init__(self):
        super(TargetDesignatorTargetController, self).__init__()
        g_eventBus.addListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        g_playerEvents.onAihControlModeChanged += self.__onAihControlModeChanged
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
        g_playerEvents.onAihControlModeChanged -= self.__onAihControlModeChanged
        self.session.shared.vehicleState.onVehicleControlling -= self.__onVehicleControlling
        super(TargetDesignatorTargetController, self).onDestroy()

    def set_spottedMarker(self, _):
        self._updateComponentAppearance()

    def set_hasUnspottedIndicator(self, _):
        self._updateComponentAppearance()

    def _onComponentAppearanceUpdate(self):
        self.__update()

    def __onVehicleControlling(self, _):
        self._updateComponentAppearance()

    def __update(self):
        vehID = self.entity.id
        self.session.shared.feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.TARGET_DESIGNATOR_SPOTTED_MARKER, vehID, self)
        self.session.invalidateVehicleState(VEHICLE_VIEW_STATE.TARGET_DESIGNATOR, self, vehID)

    def __onAihControlModeChanged(self, oldEmode, newEmode, validPlayer, attachedVeh):
        if not validPlayer.isObserver() or attachedVeh.id != self.entity.id:
            return
        isToFpvTransition = oldEmode == CTRL_MODE_NAME.POSTMORTEM and validPlayer.isObserverFPV
        _debug('onAihControlModeChanged, isToFpvTransition=%s, hasUnspottedIndicator=%s, hasSpottedMarker=%s', isToFpvTransition, bool(self.hasUnspottedIndicator), bool(self.spottedMarker))
        self._updateComponentAppearance()


def _almostEqual(t1, t2):
    return t1 is None and t2 is None or t1 is not None and t2 is not None and almostEqual(t1, t2)
