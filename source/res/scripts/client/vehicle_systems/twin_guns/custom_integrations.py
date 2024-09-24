# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/twin_guns/custom_integrations.py
import typing
import weakref
import TriggersManager
from aih_constants import ShakeReason
from events_handler import eventHandler
from helpers import dependency
from items.vehicles import MultiGunInstance
from skeletons.gui.battle_session import IBattleSessionProvider
from TriggersManager import TRIGGER_TYPE
from vehicle_systems.instant_status_helpers import invokeShotsDoneStatus
from vehicle_systems.entity_components.vehicle_mechanic_component import ifPlayerVehicle, ifObservedVehicle
from vehicle_systems.twin_guns.system_interfaces import ITwinShootingListener
from vehicle_systems.shake_helpers import shakeMultiGunPlayerDynamicCamera
if typing.TYPE_CHECKING:
    from Avatar import PlayerAvatar
    from TwinGunController import TwinGunController
    from Vehicle import Vehicle
    from Vehicular import DetailedGunState
    from vehicle_systems.twin_guns.system_interfaces import ITwinGunShootingEvents

class TwinGunCustomIntegrations(ITwinShootingListener):

    def __init__(self, vehicle, controller):
        self.__vehicle = weakref.proxy(vehicle)
        self.__controller = weakref.proxy(controller)
        self.__multiGun = []

    @property
    def detailedGunState(self):
        return self.__vehicle.appearance.detailedGunState

    def isPlayerVehicle(self, player):
        return self.__controller.isPlayerVehicle(player)

    def isObservedVehicle(self, player, vehicle):
        return self.__controller.isObservedVehicle(player, vehicle)

    @eventHandler
    def onDestroy(self, events):
        self.__controller = self.__vehicle = None
        super(TwinGunCustomIntegrations, self).onDestroy(events)
        return

    @eventHandler
    def onAppearanceReady(self):
        self.__multiGun = self.__vehicle.typeDescriptor.turret.multiGun
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
    def onDiscreteShot(self, gunIndex):
        invokeShotsDoneStatus(self.__vehicle)
        shakeMultiGunPlayerDynamicCamera(self.__vehicle, self.__multiGun[gunIndex], ShakeReason.OWN_SHOT_DELAYED)
        self.__processAvatarSingleDiscreteShot()

    @eventHandler
    def onDoubleShot(self, _):
        invokeShotsDoneStatus(self.__vehicle)
        shakeMultiGunPlayerDynamicCamera(self.__vehicle, self.__multiGun[0], ShakeReason.OWN_SHOT_DELAYED)
        shakeMultiGunPlayerDynamicCamera(self.__vehicle, self.__multiGun[1], ShakeReason.OWN_SHOT_DELAYED)
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
        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_DISCRETE_SHOOT, aimingInfo=player.aimingInfo)
        feedback = dependency.instance(IBattleSessionProvider).shared.feedback
        if feedback is not None:
            feedback.onDiscreteShotDone()
        return
