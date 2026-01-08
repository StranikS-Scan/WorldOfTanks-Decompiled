# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/common/custom_integrations.py
from __future__ import absolute_import
import logging
import typing
import weakref
import TriggersManager
from aih_constants import ShakeReason
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from TriggersManager import TRIGGER_TYPE
from vehicles.components.component_wrappers import ifAppearanceReady, ifPlayerVehicle
from vehicles.parts.guns.common.guns_interfaces import IGunShootingListenerLogic
from vehicle_systems.shake_helpers import shakeMultiGunPlayerDynamicCamera, shakeMultiGunsPlayerDynamicCamera
from vehicle_systems.shooting_helpers import processVehicleDiscreteShots
if typing.TYPE_CHECKING:
    from Avatar import PlayerAvatar
    from Vehicle import Vehicle
    from vehicles.parts.guns.common import IGunComponent, IGunShootingEvents
_logger = logging.getLogger(__name__)

class GunShootingCustomIntegrations(ContainersListener, IGunShootingListenerLogic):

    def __init__(self, vehicle, component):
        self._vehicle = weakref.proxy(vehicle)
        self._component = weakref.proxy(component)
        self._gunInstallationSlot = None
        return

    def isAppearanceReady(self):
        return self._component.isAppearanceReady()

    def isPlayerVehicle(self, player):
        return self._component.isPlayerVehicle(player)

    def isObservedVehicle(self, player, vehicle):
        return self._component.isObservedVehicle(player, vehicle)

    @eventHandler
    def onEventsContainerDestroy(self, events):
        self._gunInstallationSlot = self._component = self._vehicle = None
        super(GunShootingCustomIntegrations, self).onEventsContainerDestroy(events)
        return

    @eventHandler
    def onAppearanceReady(self):
        gunInstallationIndex = self._component.getGunInstallationIndex()
        self._gunInstallationSlot = self._vehicle.typeDescriptor.gunInstallations[gunInstallationIndex]

    @eventHandler
    @ifAppearanceReady
    def onDiscreteShot(self, gunIndex):
        gunInstallationSlot = self._gunInstallationSlot
        processVehicleDiscreteShots(self._vehicle, gunInstallationSlot)
        shakeMultiGunPlayerDynamicCamera(self._vehicle, gunInstallationSlot, gunIndex, ShakeReason.OWN_SHOT_DELAYED)
        self._processAvatarSingleDiscreteShot()

    @eventHandler
    @ifAppearanceReady
    def onMultiShot(self, gunIndexes):
        gunInstallationSlot = self._gunInstallationSlot
        processVehicleDiscreteShots(self._vehicle, gunInstallationSlot)
        shakeMultiGunsPlayerDynamicCamera(self._vehicle, gunInstallationSlot, gunIndexes, ShakeReason.OWN_SHOT_DELAYED)
        self._processAvatarSingleDiscreteShot()

    @ifPlayerVehicle
    def _processAvatarSingleDiscreteShot(self, _=None):
        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_DISCRETE_SHOOT, gunInstallationIndex=self._gunInstallationSlot.installationIndex)
