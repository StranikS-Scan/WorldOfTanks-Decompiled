# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/auxiliary_rocket_launcher/mechanic_models.py
from __future__ import absolute_import, division
import typing
from collections import namedtuple
import BigWorld
from constants import SECONDARY_GUN_STATE
from gui.battle_control.components_states.ammo import ActiveAmmoMode, DefaultAmmoMode, DefaultComponentAmmoState, ShellMode
from vehicles.mechanics.mechanic_states import IMechanicState
if typing.TYPE_CHECKING:
    from gui.battle_control.components_states.ammo.interfaces import IAmmoMode

class AuxiliaryRocketLauncherState(namedtuple('AuxiliaryRocketLauncherState', ('gunInstallationIndex', 'state', 'baseTime', 'endTime', 'isReloaded', 'reloadStartTime', 'isInAimingMode')), IMechanicState):

    @property
    def progress(self):
        return 1.0 - self.timeLeft / self.baseTime if self.baseTime > 0 else 1.0

    @property
    def timeLeft(self):
        return max(0.0, self.endTime - BigWorld.serverTime() if self.endTime >= 0 else self.baseTime)

    def isTransition(self, other):
        return self.state != other.state or self.isInAimingMode != other.isInAimingMode

    def isValidForAimingMode(self):
        return self.state in (SECONDARY_GUN_STATE.READY, SECONDARY_GUN_STATE.DISABLED)


class AuxiliaryRocketLauncherAmmoMode(DefaultAmmoMode):

    def __init__(self, isInAimingMode):
        self.__isInAimingMode = isInAimingMode

    def getActiveMode(self):
        return ActiveAmmoMode.MODIFIED_SHELLS if self.__isInAimingMode else ActiveAmmoMode.DEFAULT_SHELLS

    def getShellMode(self, shellIntCD):
        return ShellMode.AUXILIARY_ROCKET_LAUNCHER


class AuxiliaryRocketLauncherAmmoState(DefaultComponentAmmoState):

    def __init__(self, isInAimingMode):
        super(AuxiliaryRocketLauncherAmmoState, self).__init__()
        self.__ammoMode = AuxiliaryRocketLauncherAmmoMode(isInAimingMode)

    def getAmmoMode(self):
        return self.__ammoMode
