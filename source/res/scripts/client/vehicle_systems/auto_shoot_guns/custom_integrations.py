# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/auto_shoot_guns/custom_integrations.py
import typing
import weakref
import InstantStatuses
import Statuses
import TriggersManager
from aih_constants import ShakeReason
from events_handler import eventHandler
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from TriggersManager import TRIGGER_TYPE
from vehicle_systems.auto_shoot_guns.system_interfaces import IAutoShootingListener
from vehicle_systems.entity_components.vehicle_mechanic_component import ifPlayerVehicle
from vehicle_systems.shake_helpers import shakePlayerDynamicCamera
from vehicle_systems.instant_status_helpers import invokeInstantStatusForVehicle
if typing.TYPE_CHECKING:
    from AutoShootGunController import AutoShootGunController
    from Vehicle import Vehicle
    from vehicle_systems.auto_shoot_guns.system_interfaces import IAutoShootingEvents

class AutoShootCustomIntegrations(IAutoShootingListener):

    def __init__(self, vehicle, controller):
        self.__vehicle = weakref.proxy(vehicle)
        self.__controller = weakref.proxy(controller)

    def isPlayerVehicle(self, player):
        return self.__controller.isPlayerVehicle(player)

    @eventHandler
    def onDestroy(self, events):
        self.__processAvatarContinuousDeactivation()
        self.__controller = self.__vehicle = None
        super(AutoShootCustomIntegrations, self).onDestroy(events)
        return

    @eventHandler
    def onAppearanceReady(self):
        self.__vehicle.appearance.removeComponentByType(Statuses.ContinuousBurstComponent)

    @eventHandler
    def onContinuousBurstActivation(self):
        self.__vehicle.appearance.createComponent(Statuses.ContinuousBurstComponent)
        invokeInstantStatusForVehicle(self.__vehicle, InstantStatuses.StartContinuousBurstComponent)
        shakePlayerDynamicCamera(self.__vehicle)
        self.__processAvatarContinuousActivation()

    @eventHandler
    def onContinuousBurstDeactivation(self):
        self.__vehicle.appearance.removeComponentByType(Statuses.ContinuousBurstComponent)
        invokeInstantStatusForVehicle(self.__vehicle, InstantStatuses.StopContinuousBurstComponent)
        self.__processAvatarContinuousDeactivation()

    @eventHandler
    def onContinuousBurstUpdate(self):
        shakePlayerDynamicCamera(self.__vehicle)

    @eventHandler
    def onDiscreteShot(self):
        invokeInstantStatusForVehicle(self.__vehicle, InstantStatuses.ShotsDoneComponent)
        shakePlayerDynamicCamera(self.__vehicle, ShakeReason.OWN_SHOT_DELAYED)
        self.__processAvatarSingleDiscreteShot()

    @ifPlayerVehicle
    def __processAvatarSingleDiscreteShot(self, player=None):
        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_DISCRETE_SHOOT, aimingInfo=player.aimingInfo)
        feedback = dependency.instance(IBattleSessionProvider).shared.feedback
        if feedback is not None:
            feedback.onDiscreteShotDone()
        return

    @ifPlayerVehicle
    def __processAvatarContinuousActivation(self, _=None):
        TriggersManager.g_manager.fireTriggerInstantly(TRIGGER_TYPE.PLAYER_CONTINUOUS_BURST_START)

    @ifPlayerVehicle
    def __processAvatarContinuousDeactivation(self, _=None):
        TriggersManager.g_manager.fireTriggerInstantly(TRIGGER_TYPE.PLAYER_CONTINUOUS_BURST_STOP)
