# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/auto_shoot_guns/custom_integrations.py
import typing
import weakref
import InstantStatuses
import Statuses
import TriggersManager
from aih_constants import ShakeReason
from events_handler import eventHandler
from TriggersManager import TRIGGER_TYPE
from vehicles.mechanics.auto_shoot_guns.mechanic_interfaces import IAutoShootingListener
from vehicles.components.component_wrappers import ifAppearanceReady, ifPlayerVehicle
from vehicle_systems.shake_helpers import shakePlayerDynamicCamera
from vehicle_systems.shooting_helpers import processVehicleDiscreteShots
from vehicle_systems.instant_status_helpers import invokeInstantStatusForVehicle
if typing.TYPE_CHECKING:
    import CGF
    from Avatar import PlayerAvatar
    from AutoShootGunController import AutoShootGunController
    from Vehicle import Vehicle
    from vehicles.mechanics.auto_shoot_guns.mechanic_interfaces import IAutoShootingEvents

class AutoShootCustomIntegrations(IAutoShootingListener):

    def __init__(self, vehicle, controller):
        self.__vehicle = weakref.proxy(vehicle)
        self.__controller = weakref.proxy(controller)
        self.__gunInstallationSlot = None
        return

    def isAppearanceReady(self):
        return self.__controller.isAppearanceReady()

    def isPlayerVehicle(self, player):
        return self.__controller.isPlayerVehicle(player)

    def getGunRootGameObject(self):
        return self.__controller.getGunRootGameObject()

    @eventHandler
    def onDestroy(self, events):
        self.__processAvatarContinuousDeactivation()
        self.__gunInstallationSlot = self.__controller = self.__vehicle = None
        super(AutoShootCustomIntegrations, self).onDestroy(events)
        return

    @eventHandler
    def onAppearanceReady(self):
        gunInstallationIndex = self.__controller.getGunInstallationIndex()
        self.__vehicle.appearance.removeComponentByType(Statuses.ContinuousBurstComponent)
        self.__gunInstallationSlot = self.__vehicle.typeDescriptor.gunInstallations[gunInstallationIndex]

    @eventHandler
    def onContinuousBurstActivation(self):
        self.__vehicle.appearance.createComponent(Statuses.ContinuousBurstComponent)
        invokeInstantStatusForVehicle(self.__vehicle, InstantStatuses.StartContinuousBurstComponent)
        shakePlayerDynamicCamera(self.__vehicle, self.__gunInstallationSlot)
        self.__processAvatarContinuousActivation()

    @eventHandler
    def onContinuousBurstDeactivation(self):
        self.__vehicle.appearance.removeComponentByType(Statuses.ContinuousBurstComponent)
        invokeInstantStatusForVehicle(self.__vehicle, InstantStatuses.StopContinuousBurstComponent)
        self.__processAvatarContinuousDeactivation()

    @eventHandler
    def onContinuousBurstUpdate(self):
        shakePlayerDynamicCamera(self.__vehicle, self.__gunInstallationSlot)

    @eventHandler
    @ifAppearanceReady
    def onDiscreteShot(self):
        gunInstallationSlot = self.__gunInstallationSlot
        processVehicleDiscreteShots(self.__vehicle, gunInstallationSlot, self.getGunRootGameObject())
        shakePlayerDynamicCamera(self.__vehicle, gunInstallationSlot, ShakeReason.OWN_SHOT_DELAYED)
        self.__processAvatarSingleDiscreteShot()

    @ifPlayerVehicle
    def __processAvatarSingleDiscreteShot(self, _=None):
        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_DISCRETE_SHOOT)

    @ifPlayerVehicle
    def __processAvatarContinuousActivation(self, _=None):
        TriggersManager.g_manager.fireTriggerInstantly(TRIGGER_TYPE.PLAYER_CONTINUOUS_BURST_START)

    @ifPlayerVehicle
    def __processAvatarContinuousDeactivation(self, _=None):
        TriggersManager.g_manager.fireTriggerInstantly(TRIGGER_TYPE.PLAYER_CONTINUOUS_BURST_STOP)
