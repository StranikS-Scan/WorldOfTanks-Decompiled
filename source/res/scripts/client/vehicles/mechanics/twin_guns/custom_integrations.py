# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/twin_guns/custom_integrations.py
import typing
import weakref
import TriggersManager
from aih_constants import ShakeReason
from events_handler import eventHandler
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from TriggersManager import TRIGGER_TYPE
from vehicles.components.component_wrappers import ifAppearanceReady, ifPlayerVehicle, ifObservedVehicle
from vehicles.mechanics.twin_guns.mechanic_interfaces import ITwinShootingListener
from vehicle_systems.shake_helpers import shakeMultiGunPlayerDynamicCamera, shakeMultiGunsPlayerDynamicCamera
from vehicle_systems.shooting_helpers import processVehicleDiscreteShots
if typing.TYPE_CHECKING:
    import CGF
    from Avatar import PlayerAvatar
    from TwinGunController import TwinGunController
    from Vehicle import Vehicle
    from Vehicular import DetailedGunState
    from vehicles.mechanics.twin_guns.mechanic_interfaces import ITwinGunShootingEvents

class TwinGunCustomIntegrations(ITwinShootingListener):

    def __init__(self, vehicle, controller):
        self.__vehicle = weakref.proxy(vehicle)
        self.__controller = weakref.proxy(controller)
        self.__gunInstallationSlot = None
        return

    @property
    def detailedGunState(self):
        return self.__vehicle.appearance.detailedGunState

    def isAppearanceReady(self):
        return self.__controller.isAppearanceReady()

    def isPlayerVehicle(self, player):
        return self.__controller.isPlayerVehicle(player)

    def isObservedVehicle(self, player, vehicle):
        return self.__controller.isObservedVehicle(player, vehicle)

    def getGunRootGameObject(self):
        return self.__controller.getGunRootGameObject()

    @eventHandler
    def onDestroy(self, events):
        self.__gunInstallationSlot = self.__controller = self.__vehicle = None
        super(TwinGunCustomIntegrations, self).onDestroy(events)
        return

    @eventHandler
    def onAppearanceReady(self):
        gunInstallationIndex = self.__controller.getGunInstallationIndex()
        self.__gunInstallationSlot = self.__vehicle.typeDescriptor.gunInstallations[gunInstallationIndex]
        self.detailedGunState.activeGuns = self.__controller.getActiveGunIndexes()
        self.detailedGunState.animatedGuns = self.__controller.getNextGunIndexes()

    @eventHandler
    def onActiveGunsUpdate(self, gunIndexes):
        self.detailedGunState.activeGuns = gunIndexes
        self.__processAvatarActiveGunsUpdate(gunIndexes=gunIndexes)

    @eventHandler
    def onAnimatedGunsUpdate(self, gunIndexes):
        self.detailedGunState.animatedGuns = gunIndexes

    @eventHandler
    @ifAppearanceReady
    def onDiscreteShot(self, gunIndex):
        vehicle, gunInstallationSlot = self.__vehicle, self.__gunInstallationSlot
        processVehicleDiscreteShots(vehicle, gunInstallationSlot, self.getGunRootGameObject())
        shakeMultiGunPlayerDynamicCamera(vehicle, gunInstallationSlot, gunIndex, ShakeReason.OWN_SHOT_DELAYED)
        self.__processAvatarSingleDiscreteShot()

    @eventHandler
    @ifAppearanceReady
    def onDoubleShot(self, gunIndexes):
        vehicle, gunInstallationSlot = self.__vehicle, self.__gunInstallationSlot
        processVehicleDiscreteShots(vehicle, gunInstallationSlot, self.getGunRootGameObject())
        shakeMultiGunsPlayerDynamicCamera(vehicle, gunInstallationSlot, gunIndexes, ShakeReason.OWN_SHOT_DELAYED)
        self.__processAvatarSingleDiscreteShot()

    @ifObservedVehicle
    def __processAvatarActiveGunsUpdate(self, player=None, __=None, gunIndexes=()):
        player.updateMultiGunCollisions()
        feedback = dependency.instance(IBattleSessionProvider).shared.feedback
        if feedback is not None:
            feedback.invalidateActiveGunChanges(self.__vehicle.id, gunIndexes, 0.0)
        return

    @ifPlayerVehicle
    def __processAvatarSingleDiscreteShot(self, player=None):
        player.cancelWaitingForShot()
        player.getOwnVehicleShotDispersionAngle(player.gunRotator.turretRotationSpeed, withShot=1)
        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_DISCRETE_SHOOT)
