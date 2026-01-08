# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/common/guns_interfaces.py
from __future__ import absolute_import
import typing
from events_containers.common.containers import IClientEventsContainer, IClientEventsContainerListener
from vehicles.components.component_interfaces import IVehicleGunSlotComponent

class IGunComponent(IVehicleGunSlotComponent):

    @property
    def shootingEvents(self):
        raise NotImplementedError


class IGunShootingEventsLogic(object):
    onAppearanceReady = None
    onDiscreteShot = None
    onMultiShot = None

    def processAppearanceReady(self):
        raise NotImplementedError

    def processDiscreteShot(self, gunIndex):
        raise NotImplementedError

    def processMultiShot(self, gunIndexes):
        raise NotImplementedError


class IGunShootingEvents(IClientEventsContainer, IGunShootingEventsLogic):
    pass


class IGunShootingListenerLogic(object):

    def onAppearanceReady(self):
        pass

    def onDiscreteShot(self, gunIndex):
        pass

    def onMultiShot(self, gunIndexes):
        pass


class IGunShootingListener(IClientEventsContainerListener, IGunShootingListenerLogic):
    pass
