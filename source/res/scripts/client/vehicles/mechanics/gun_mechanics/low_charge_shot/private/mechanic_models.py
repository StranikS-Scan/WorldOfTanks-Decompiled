# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/low_charge_shot/private/mechanic_models.py
from __future__ import absolute_import
import typing
import BigWorld
from constants import LowChargeShotReloadingState
from gui.battle_control.battle_constants import CANT_SHOOT_ERROR
from gui.battle_control.components_states.ammo import DefaultComponentAmmoState, AmmoShootPossibility
from gui.battle_control.components_states.ammo.constants import ShellMode
from gui.battle_control.components_states.ammo.shells import DefaultAmmoMode
from gui.shared.utils.decorators import ReprInjector
from vehicles.mechanics.mechanic_states import IMechanicState
if typing.TYPE_CHECKING:
    from gui.battle_control.components_states.ammo.interfaces import IAmmoMode

@ReprInjector.simple('reloadingState', 'timeLeft', 'baseTime', 'endTime', 'lowChargeTime')
class LowChargeShotMechanicState(typing.NamedTuple('LowChargeShotMechanicState', (('reloadingState', LowChargeShotReloadingState),
 ('timeLeft', float),
 ('baseTime', float),
 ('endTime', float),
 ('lowChargeTime', float),
 ('almostFinishedTime', float),
 ('reloadTimeCoefficient', float))), IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status, params):
        return cls(status.reloadingState, status.timeLeft, status.baseTime, status.endTime, status.lowChargeTime, params.almostFinishedTime, params.reloadTimeCoefficient)

    @property
    def duration(self):
        timeLeftCalculated = self.calculateTimeLeft()
        if self.reloadingState == LowChargeShotReloadingState.INITIAL_RELOAD:
            return self.lowChargeTime - (self.baseTime - timeLeftCalculated)
        if self.reloadingState == LowChargeShotReloadingState.LOW_CHARGE:
            return timeLeftCalculated - self.almostFinishedTime
        if self.reloadingState == LowChargeShotReloadingState.ALMOST_FINISHED:
            return timeLeftCalculated
        return timeLeftCalculated if self.reloadingState == LowChargeShotReloadingState.QUICK_RELOAD else self.timeLeft

    def isTransition(self, other):
        return self.reloadingState != other.reloadingState

    def calculateTimeLeft(self):
        return max(0.0, self.endTime - BigWorld.serverTime())


class LowChargeShotAmmoMode(DefaultAmmoMode):

    def getShellMode(self, shellIntCD):
        return ShellMode.LOW_CHARGE_SHOT


class LowChargeShotAmmoState(DefaultComponentAmmoState):

    def __init__(self, mechanicState):
        self.__mechanicState = mechanicState
        self.__ammoMode = LowChargeShotAmmoMode()

    def canShootValidation(self):
        return (False, CANT_SHOOT_ERROR.LOW_CHARGE_SHOT_BLOCKING) if self.__mechanicState.reloadingState == LowChargeShotReloadingState.ALMOST_FINISHED else super(LowChargeShotAmmoState, self).canShootValidation()

    def getShootPossibility(self, currentShells):
        return AmmoShootPossibility.ALLOWED if currentShells[0] > 0 and self.__mechanicState.reloadingState in (LowChargeShotReloadingState.LOW_CHARGE, LowChargeShotReloadingState.FULL_CHARGE) else AmmoShootPossibility.DENIED

    def getAmmoMode(self):
        return self.__ammoMode
