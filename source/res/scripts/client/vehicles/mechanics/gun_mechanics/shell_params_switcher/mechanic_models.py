# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/shell_params_switcher/mechanic_models.py
from __future__ import absolute_import
import typing
import BigWorld
from constants import SHELL_PARAMS_SWITCHER_MASK, SHELL_PARAMS_SWITCHER_STATE
from items import vehicles
from gui.shared.utils.decorators import ReprInjector
from gui.battle_control.components_states.ammo import DefaultComponentAmmoState
from gui.battle_control.components_states.ammo.constants import ActiveAmmoMode, ShellMode
from gui.battle_control.components_states.ammo.shells import DefaultAmmoMode
from vehicles.mechanics.gun_mechanics.shell_params_switcher.mechanic_interfaces import IShellParamsSwitcherMechanicState, IShellParamsSwitcherComponentParams
from vehicles.mechanics.mechanic_constants import VehicleMechanic
if typing.TYPE_CHECKING:
    from items.components.shared_components import ShellSwitcherParams

@ReprInjector.simple('shellSubtypes')
class ShellParamsSwitcherComponentParams(IShellParamsSwitcherComponentParams):

    def __init__(self, shellSubtypes):
        super(ShellParamsSwitcherComponentParams, self).__init__()
        self.__shellSubtypes = shellSubtypes

    @classmethod
    def fromMechanicParams(cls, params, vehIntCD):
        mechanicsCache = vehicles.g_cache.vehicleMechanics.get(vehIntCD, {}).get(VehicleMechanic.SHELL_PARAMS_SWITCHER.value, {})
        mechanicSubtypes = mechanicsCache.get('mechanicSubtypes', {})
        shellSubtypes = {shellCD:mechanicSubtypes.get(shellCD, {}) for shellCD in params.modifiedShells}
        return cls(shellSubtypes)

    @property
    def shellSubtypes(self):
        return self.__shellSubtypes


@ReprInjector.simple('baseState', 'isCritState', 'isNoAmmo', 'isActive', 'mechanicSubtype')
class ShellParamsSwitcherMechanicState(IShellParamsSwitcherMechanicState):

    def __init__(self, state, endTime, isActive, lastActiveShotTimestamp, params, shellCD):
        self.__state = state
        self.__mask = state >> 2
        self.__baseState = state & 3
        self.__endTime = endTime
        self.__lastActiveShotTimestamp = lastActiveShotTimestamp
        self.__isActive = isActive
        self.__params = params
        self.__shellCD = shellCD

    @classmethod
    def fromComponentStatus(cls, status, publicStatus, params, shellCD):
        return cls(status.state, status.endTime, bool(publicStatus.isActive), publicStatus.lastActiveShotTimestamp, params, shellCD)

    @property
    def state(self):
        return self.__state

    @property
    def baseState(self):
        return self.__baseState

    @property
    def isActive(self):
        return self.__isActive

    @property
    def lastActiveShotTimestamp(self):
        return self.__lastActiveShotTimestamp

    @property
    def mechanicSubtype(self):
        subtypes = self.__params.shellSubtypes.get(self.__shellCD, {})
        isModified = self.__baseState == SHELL_PARAMS_SWITCHER_STATE.CHARGED
        return subtypes.get('modified', '') if isModified else subtypes.get('basic', '')

    def isTransition(self, other):
        return self.state != other.state

    def isNoAmmo(self):
        return bool(self.__mask & SHELL_PARAMS_SWITCHER_MASK.NO_AMMO)

    def isCritState(self):
        return bool(self.__mask & SHELL_PARAMS_SWITCHER_MASK.MODULE_CRIT)

    def timeLeft(self):
        return max(0.0, self.__endTime - BigWorld.serverTime()) if self.__endTime > 0.0 else -self.__endTime


class ShellParamsSwitcherAmmoMode(DefaultAmmoMode):

    def __init__(self, mechanicState, modifiedShells):
        self.__mechanicState = mechanicState
        self.__modifiedShells = modifiedShells

    def getActiveMode(self):
        return ActiveAmmoMode.MODIFIED_SHELLS if self.__mechanicState.isActive else ActiveAmmoMode.DEFAULT_SHELLS

    def getModifiedShells(self):
        return self.__modifiedShells

    def getShellMode(self, shellIntCD):
        return ShellMode.SHELL_PARAMS_SWITCHER if shellIntCD in self.__modifiedShells else ShellMode.NOT_DEFINED


class ShellParamsSwitcherAmmoState(DefaultComponentAmmoState):

    def __init__(self, mechanicState, modifiedShells):
        super(ShellParamsSwitcherAmmoState, self).__init__()
        self.__ammoMode = ShellParamsSwitcherAmmoMode(mechanicState, modifiedShells)

    def getAmmoMode(self):
        return self.__ammoMode
