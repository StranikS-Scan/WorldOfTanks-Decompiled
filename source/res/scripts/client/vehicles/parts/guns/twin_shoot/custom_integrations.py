# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/twin_shoot/custom_integrations.py
from __future__ import absolute_import
import logging
import typing
from events_handler import eventHandler
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.components.component_wrappers import ifPlayerVehicle, ifObservedVehicle
from vehicles.parts.guns.common import GunShootingCustomIntegrations
from vehicles.parts.guns.twin_shoot.guns_interfaces import ITwinShootingListenerLogic
if typing.TYPE_CHECKING:
    from Vehicular import DetailedGunState
_logger = logging.getLogger(__name__)

class TwinShootCustomIntegrations(GunShootingCustomIntegrations, ITwinShootingListenerLogic):

    @property
    def detailedGunState(self):
        return self._vehicle.appearance.detailedGunState

    @eventHandler
    def onAppearanceReady(self):
        super(TwinShootCustomIntegrations, self).onAppearanceReady()
        self.detailedGunState.activeGuns = self._component.getActiveGunIndexes()
        self.detailedGunState.animatedGuns = self._component.getNextGunIndexes()

    @eventHandler
    def onActiveGunsUpdate(self, gunIndexes):
        self.detailedGunState.activeGuns = gunIndexes
        self.__processAvatarActiveGunsUpdate(gunIndexes=gunIndexes)

    @eventHandler
    def onAnimatedGunsUpdate(self, gunIndexes):
        self.detailedGunState.animatedGuns = gunIndexes

    @ifPlayerVehicle
    def _processAvatarSingleDiscreteShot(self, player=None):
        player.cancelWaitingForShot()
        player.getOwnVehicleShotDispersionAngle(player.gunRotator.turretRotationSpeed, withShot=1)
        super(TwinShootCustomIntegrations, self)._processAvatarSingleDiscreteShot()

    @ifObservedVehicle
    def __processAvatarActiveGunsUpdate(self, player=None, __=None, gunIndexes=()):
        player.updateMultiGunCollisions()
        feedback = dependency.instance(IBattleSessionProvider).shared.feedback
        if feedback is not None:
            feedback.invalidateActiveGunChanges(self._vehicle.id, gunIndexes, 0.0)
        return
