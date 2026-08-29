# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/generic_mechanics/sight_pointer/mechanic_events.py
from __future__ import absolute_import, division
import math
import typing
from cgf_events import gun_events
from cgf_events.mechanics_events import postSightPointerSectorEvent
from constants import SIGHT_POINTER_STATE, VISIBILITY
from events_containers.common.containers import ClientEventsContainerDebugger
from events_handler import eventHandler
from vehicles.components.component_events import VehicleComponentEventsCoreIntegration
from vehicles.mechanics.generic_mechanics.sight_pointer.mechanic_interfaces import ISightPointerStatesEvents
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic, MechanicStatesEvents
if typing.TYPE_CHECKING:
    from events_containers.common.containers.interfaces import IClientEventsContainer
    from SightPointerComponent import SightPointerState
_VAR_SECTOR_MINSIZE = 'sectorVision/minsize'
_LERP_DURATION = 0.3
_OPACITY_MIN = 0.06
_OPACITY_MAX = 0.15

class SightPointerStatesEvents(MechanicStatesEvents, ISightPointerStatesEvents):

    def _createCoreIntegration(self):
        return SightPointerStatesCoreIntegration(self, self._getComponent())

    def updateComponentParams(self, maxAngle, minAngle):
        if self._cgfIntegration is not None:
            self._cgfIntegration.updateComponentParams(maxAngle, minAngle)
        return

    def _createEventsDebugger(self):
        return SightPointerEventsDebugger(self)


class SightPointerEventsDebugger(ClientEventsContainerDebugger):
    IGNORED_EVENTS = ClientEventsContainerDebugger.IGNORED_EVENTS + ('onStateObservation', 'onStateTick')
    _EVENTS_DEBUG_PREFIX = 'SIGHT_POINTER'


class SightPointerStatesCoreIntegration(VehicleComponentEventsCoreIntegration, IMechanicStatesListenerLogic):

    def __init__(self, events, component):
        self.__lastAngle = 0.0
        self.__lastDistance = 0.0
        self.__maxAngle = 0.0
        self.__minAngle = 0.0
        self.__isActivated = False
        super(SightPointerStatesCoreIntegration, self).__init__(events, component)

    @eventHandler
    def onStatePrepared(self, state):
        self.__updateSector(state)

    @eventHandler
    def onStateObservation(self, state):
        self.__updateSector(state)

    @eventHandler
    def onEventsContainerDestroy(self, events):
        self.__postSectorLerpEvent(0.0, 0.0, 0.0)
        super(SightPointerStatesCoreIntegration, self).onEventsContainerDestroy(events)

    def updateComponentParams(self, maxAngle, minAngle):
        self.__maxAngle = maxAngle
        self.__minAngle = minAngle

    def __updateSector(self, state):
        if state.state != SIGHT_POINTER_STATE.ACTIVE:
            if self.__lastAngle != 0.0 or self.__lastDistance != 0.0:
                self.__lastAngle = 0.0
                self.__lastDistance = 0.0
                self.__isActivated = False
                self.__postSectorLerpEvent(0.0, 0.0, 0.0)
            return
        angleDeg = state.angle
        distance = state.distance
        if distance <= VISIBILITY.MIN_RADIUS:
            return
        if angleDeg == self.__lastAngle and distance == self.__lastDistance:
            return
        if not self.__isActivated and distance > 0.0:
            self.__isActivated = True
        if self.__isActivated:
            self.__postMinSizeEvent(distance)
        self.__lastAngle = angleDeg
        self.__lastDistance = distance
        targetWidth = 2.0 * distance * math.tan(math.radians(angleDeg / 2.0))
        targetOpacity = self.__calcOpacity(angleDeg)
        self.__postSectorLerpEvent(targetWidth, distance, targetOpacity)

    def __postMinSizeEvent(self, distance):
        minSize = distance * math.tan(math.radians(self.__minAngle / 2.0))
        gun_events.postVehicularVariablesChangedEvent(self._spaceID, self._vehicleID, self._slotName, {_VAR_SECTOR_MINSIZE: minSize})

    def __calcOpacity(self, angleDeg):
        if self.__maxAngle <= self.__minAngle or angleDeg <= 0.0:
            return _OPACITY_MIN
        t = max(0.0, min(1.0, (self.__maxAngle - angleDeg) / (self.__maxAngle - self.__minAngle)))
        return _OPACITY_MIN + (_OPACITY_MAX - _OPACITY_MIN) * t

    def __postSectorLerpEvent(self, targetWidth, targetDistance, targetOpacity):
        postSightPointerSectorEvent(self._spaceID, self._vehicleID, self._slotName, targetWidth, targetDistance, targetOpacity, _LERP_DURATION)
