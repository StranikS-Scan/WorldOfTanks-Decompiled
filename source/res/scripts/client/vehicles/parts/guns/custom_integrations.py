# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/custom_integrations.py
import typing
import weakref
import TriggersManager
from aih_constants import ShakeReason
from events_handler import eventHandler
from TriggersManager import TRIGGER_TYPE
from vehicles.components.component_events import ComponentListener
from vehicles.components.component_wrappers import ifAppearanceReady, ifPlayerVehicle
from vehicles.parts.guns.guns_interfaces import IGunShootingListener
from vehicle_systems.shake_helpers import shakeMultiGunPlayerDynamicCamera, shakeMultiGunsPlayerDynamicCamera
from vehicle_systems.shooting_helpers import processVehicleDiscreteShots
if typing.TYPE_CHECKING:
    import CGF
    from Avatar import PlayerAvatar
    from Vehicle import Vehicle
    from vehicles.parts.guns import IGunComponent, IGunShootingEvents

class GunShootingCustomIntegrations(ComponentListener, IGunShootingListener):

    def __init__(self, vehicle, component):
        self.__vehicle = weakref.proxy(vehicle)
        self.__component = weakref.proxy(component)
        self.__gunInstallationSlot = None
        return

    def isAppearanceReady(self):
        return self.__component.isAppearanceReady()

    def isPlayerVehicle(self, player):
        return self.__component.isPlayerVehicle(player)

    def getGunRootGameObject(self):
        return self.__component.getGunRootGameObject()

    @eventHandler
    def onComponentEventsDestroy(self, events):
        self.__gunInstallationSlot = self.__component = self.__vehicle = None
        super(GunShootingCustomIntegrations, self).onComponentEventsDestroy(events)
        return

    @eventHandler
    def onAppearanceReady(self):
        gunInstallationIndex = self.__component.getGunInstallationIndex()
        self.__gunInstallationSlot = self.__vehicle.typeDescriptor.gunInstallations[gunInstallationIndex]

    @eventHandler
    @ifAppearanceReady
    def onDiscreteShot(self, gunIndex):
        vehicle, gunInstallationSlot = self.__vehicle, self.__gunInstallationSlot
        processVehicleDiscreteShots(vehicle, gunInstallationSlot, self.getGunRootGameObject())
        shakeMultiGunPlayerDynamicCamera(vehicle, gunInstallationSlot, gunIndex, ShakeReason.OWN_SHOT_DELAYED)
        self.__processAvatarSingleDiscreteShot()

    @eventHandler
    @ifAppearanceReady
    def onMultiShot(self, gunIndexes):
        vehicle, gunInstallationSlot = self.__vehicle, self.__gunInstallationSlot
        processVehicleDiscreteShots(vehicle, gunInstallationSlot, self.getGunRootGameObject())
        shakeMultiGunsPlayerDynamicCamera(vehicle, gunInstallationSlot, gunIndexes, ShakeReason.OWN_SHOT_DELAYED)
        self.__processAvatarSingleDiscreteShot()

    @ifPlayerVehicle
    def __processAvatarSingleDiscreteShot(self, _=None):
        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_DISCRETE_SHOOT, gunInstallationIndex=self.__gunInstallationSlot.installationIndex)
