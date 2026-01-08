# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/temperature/overheat_gun/mechanic_models.py
from __future__ import absolute_import, division
import math
import typing
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from constants import OVERHEAT_GUN_STATE
from gui.battle_control.battle_constants import CANT_SHOOT_ERROR
from gui.battle_control.components_states.ammo import DefaultComponentAmmoState
from gui.shared.utils.decorators import ReprInjector
from helpers import dependency
from messenger_common_chat2 import messageArgs
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.mechanics.gun_mechanics.temperature.overheat_gun.mechanic_interfaces import IOverheatGunComponentParams, IOverheatGunMechanicState
if typing.TYPE_CHECKING:
    from items.components.shared_components import OverheatGunParams
    from vehicles.mechanics.gun_mechanics.temperature.temperature_gun import ITemperatureGunMechanicState

@ReprInjector.simple('overheatWarnPercent', 'overheatOffPercent', 'overheatOffThreshold')
class OverheatGunComponentParams(IOverheatGunComponentParams):

    def __init__(self, overheatWarnPercent, overheatOffPercent, overheatOffThreshold):
        self.__overheatWarnPercent = overheatWarnPercent
        self.__overheatOffPercent = overheatOffPercent
        self.__overheatOffThreshold = overheatOffThreshold

    @classmethod
    def fromMechanicParams(cls, params):
        return cls(params.tempOverheatWarnThreshold / params.tempOverheatOnThreshold, params.tempOverheatOffThreshold / params.tempOverheatOnThreshold, params.tempOverheatOffThreshold)

    @property
    def overheatWarnPercent(self):
        return self.__overheatWarnPercent

    @property
    def overheatOffPercent(self):
        return self.__overheatOffPercent

    @property
    def overheatOffThreshold(self):
        return self.__overheatOffThreshold


@ReprInjector.simple('overheatState')
class OverheatGunMechanicState(IOverheatGunMechanicState):

    def __init__(self, overheatState, params):
        self.__overheatState = overheatState
        self.__params = params

    @classmethod
    def fromComponentStatus(cls, state, params):
        return cls(state, params)

    @property
    def isOverheated(self):
        return self.__overheatState == OVERHEAT_GUN_STATE.OVERHEATING

    @property
    def overheatState(self):
        return self.__overheatState

    def isTransition(self, other):
        return self.overheatState != other.overheatState

    def overheatTimeLeft(self, temperatureState):
        return temperatureState.getCoolingTime(self.__params.overheatOffThreshold) if self.isOverheated else -1.0


class OverheatGunAmmoState(DefaultComponentAmmoState):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, mechanicState):
        self.__mechanicState = mechanicState

    def canShootValidation(self):
        return (False, CANT_SHOOT_ERROR.GUN_OVERHEATED) if self.__mechanicState.isOverheated else super(OverheatGunAmmoState, self).canShootValidation()

    def getSpecialReloadMessage(self):
        if not self.__mechanicState.isOverheated:
            return
        else:
            temperatureAmmoState = self.__sessionProvider.shared.ammo.ammoStatesInfo.temperatureGunAmmoState
            if temperatureAmmoState is None:
                return
            cooldownTime = self.__mechanicState.overheatTimeLeft(temperatureAmmoState.mechanicState)
            return (BATTLE_CHAT_COMMAND_NAMES.OVERHEATEDGUN, messageArgs(floatArg1=math.ceil(cooldownTime)))
