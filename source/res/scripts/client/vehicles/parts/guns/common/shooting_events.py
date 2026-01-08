# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/common/shooting_events.py
from __future__ import absolute_import
import typing
import weakref
from cgf_events import gun_events
from events_containers.common.containers import ClientEventsContainer
from events_containers.components.common import ClientComponentEventsDebugger
from events_handler import eventHandler
from vehicles.components.component_events import VehicleComponentEventsCGFIntegration
from vehicles.parts.guns.common.guns_interfaces import IGunShootingEventsLogic, IGunShootingListenerLogic
if typing.TYPE_CHECKING:
    from vehicles.parts.guns.common.guns_interfaces import IGunComponent, IGunShootingListener

class GunShootingEvents(ClientEventsContainer, IGunShootingEventsLogic):

    def __init__(self, component):
        super(GunShootingEvents, self).__init__()
        self.__componentRef = weakref.ref(component)
        self._isAppearanceReady = False
        self.onAppearanceReady = self._createLateEvent(self.__lateAppearanceReady)
        self.onDiscreteShot = self._createEvent()
        self.onMultiShot = self._createEvent()

    def destroy(self):
        self.__componentRef = None
        super(GunShootingEvents, self).destroy()
        return

    def lateSubscribe(self, listener):
        self._lateSubscribe(listener)
        super(GunShootingEvents, self).lateSubscribe(listener)

    def processAppearanceReady(self):
        self._isAppearanceReady = True
        self.onAppearanceReady()

    def processDiscreteShot(self, gunIndex):
        self.onDiscreteShot(gunIndex)

    def processMultiShot(self, gunIndexes):
        self.onMultiShot(gunIndexes)

    def _getComponent(self):
        return self.__componentRef() if self.__componentRef is not None else None

    def _createCGFIntegration(self):
        return GunShootingCGFIntegration(self, self._getComponent())

    def _createEventsDebugger(self):
        return GunShootingEventsDebugger(self, self._getComponent())

    def _lateSubscribe(self, listener):
        self.__lateAppearanceReady(listener.onAppearanceReady)

    def __lateAppearanceReady(self, handler):
        if self._isAppearanceReady:
            handler()


class GunShootingCGFIntegration(VehicleComponentEventsCGFIntegration, IGunShootingListenerLogic):

    @eventHandler
    def onDiscreteShot(self, gunIndex):
        gun_events.postVehicularSingleShotEvent(self._spaceID, self._vehicleID, self._slotName, gunIndex)

    @eventHandler
    def onMultiShot(self, gunIndexes):
        gun_events.postVehicularMultiShotEvent(self._spaceID, self._vehicleID, self._slotName, gunIndexes)


class GunShootingEventsDebugger(ClientComponentEventsDebugger):
    IGNORED_EVENTS = ClientComponentEventsDebugger.IGNORED_EVENTS + ('onAppearanceReady',)
    _EVENTS_DEBUG_PREFIX = 'GUN'
