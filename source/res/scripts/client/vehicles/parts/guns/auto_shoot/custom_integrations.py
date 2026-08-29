# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/auto_shoot/custom_integrations.py
from __future__ import absolute_import
import logging
import TriggersManager
from events_handler import eventHandler
from TriggersManager import TRIGGER_TYPE
from vehicles.components.component_wrappers import ifPlayerVehicle
from vehicles.parts.guns.common import GunShootingCustomIntegrations
from vehicles.parts.guns.auto_shoot.guns_interfaces import IAutoShootingListenerLogic
from vehicle_systems.shake_helpers import shakePlayerDynamicCamera
from vehicle_systems.shooting_helpers import notifyArenaVehicleShot
_logger = logging.getLogger(__name__)

class AutoShootCustomIntegrations(GunShootingCustomIntegrations, IAutoShootingListenerLogic):

    @eventHandler
    def onContinuousBurstActivation(self):
        shakePlayerDynamicCamera(self._vehicle, self._gunInstallationSlot)
        notifyArenaVehicleShot(self._vehicle)
        self.__processAvatarContinuousActivation()

    @eventHandler
    def onContinuousBurstDeactivation(self):
        self.__processAvatarContinuousDeactivation()

    @eventHandler
    def onContinuousBurstUpdate(self):
        shakePlayerDynamicCamera(self._vehicle, self._gunInstallationSlot)

    @ifPlayerVehicle
    def __processAvatarContinuousActivation(self, _=None):
        TriggersManager.g_manager.fireTriggerInstantly(TRIGGER_TYPE.PLAYER_CONTINUOUS_BURST_START, gunInstallationIndex=self._gunInstallationSlot.installationIndex)

    @ifPlayerVehicle
    def __processAvatarContinuousDeactivation(self, _=None):
        TriggersManager.g_manager.fireTriggerInstantly(TRIGGER_TYPE.PLAYER_CONTINUOUS_BURST_STOP, gunInstallationIndex=self._gunInstallationSlot.installationIndex)
