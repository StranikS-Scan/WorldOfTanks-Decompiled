# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/components_states/ammo/collections.py
from __future__ import absolute_import
import typing
from future.utils import viewvalues
from gui.battle_control.components_states.ammo.constants import AmmoShootPossibility
from gui.battle_control.components_states.ammo.shells import DefaultAmmoMode
from items.vehicle_mechanics_types import VehicleMechanicKeys
from shared_utils import findFirst
if typing.TYPE_CHECKING:
    from ChargeableBurstComponent import ChargeableBurstAmmoState
    from StationaryReloadController import StationaryReloadAmmoState
    from TemperatureGunController import TemperatureGunAmmoState
    from gui.battle_control.components_states.ammo.interfaces import IComponentAmmoState, IAmmoMode

class AmmoStatesROCollection(object):

    def __init__(self, ammoStates):
        self._ammoStates = ammoStates

    @property
    def ammoStates(self):
        return self._ammoStates.copy()

    @property
    def chargeableBurstAmmoState(self):
        return self._ammoStates.get(VehicleMechanicKeys.CHARGEABLE_BURST.uniqueName)

    @property
    def extraShotReloadState(self):
        extraShotState = self._ammoStates.get(VehicleMechanicKeys.EXTRA_SHOT_CLIP.uniqueName)
        return extraShotState.extraReloadState if extraShotState is not None else 0

    @property
    def stationaryReloadAmmoState(self):
        return self._ammoStates.get(VehicleMechanicKeys.STATIONARY_RELOAD.uniqueName)

    @property
    def temperatureGunAmmoState(self):
        return self._ammoStates.get(VehicleMechanicKeys.TEMPERATURE_GUN.uniqueName)

    def isReloadingBlocked(self):
        return any((state.isReloadingBlocked() for state in viewvalues(self._ammoStates)))

    def canChangeVehicleSetting(self, code):
        return not self._ammoStates or all((s.canChangeVehicleSetting(code) for s in viewvalues(self._ammoStates)))

    def canShootValidation(self, defaultError):
        return findFirst(lambda validationResult: not validationResult[0], (state.canShootValidation() for state in viewvalues(self._ammoStates)), default=(True, defaultError))

    def getSpecialReloadMessage(self):
        return findFirst(None, (state.getSpecialReloadMessage() for state in viewvalues(self._ammoStates)))

    def getAmmoMode(self):
        return findFirst(None, (state.getAmmoMode() for state in viewvalues(self._ammoStates)), default=DefaultAmmoMode())

    def getShotsAmount(self):
        return max((state.getShotsAmount() for state in viewvalues(self._ammoStates))) if self._ammoStates else -1

    def getShootPossibility(self, currentShells):
        return findFirst(lambda shootPossibility: shootPossibility != AmmoShootPossibility.NOT_DEFINED, (state.getShootPossibility(currentShells) for state in viewvalues(self._ammoStates)), default=AmmoShootPossibility.NOT_DEFINED)

    def getShellReloadTimes(self, currShell, shellChangeTime, shells):
        return findFirst(None, (state.getShellReloadTimes(currShell, shellChangeTime, shells) for state in viewvalues(self._ammoStates)))


class AmmoStatesRWCollection(AmmoStatesROCollection):

    @property
    def ammoStates(self):
        return self._ammoStates

    def getReadOnlyCopy(self):
        return AmmoStatesROCollection(self._ammoStates.copy())

    def setAmmoStates(self, ammoStates):
        self._ammoStates = ammoStates

    def clear(self):
        self._ammoStates = {}
