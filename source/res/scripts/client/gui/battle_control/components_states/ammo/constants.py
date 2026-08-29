# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/components_states/ammo/constants.py
from __future__ import absolute_import
from enum import Enum, IntEnum
from vehicles.mechanics.mechanic_constants import VehicleMechanic

class AmmoShootPossibility(IntEnum):
    NOT_DEFINED = 0
    ALLOWED = 1
    DENIED = 2


class ActiveAmmoMode(IntEnum):
    NOT_DEFINED = 0
    DEFAULT_SHELLS = 1
    MODIFIED_SHELLS = 2


class ShellMode(Enum):
    NOT_DEFINED = ''
    LOW_CHARGE_SHOT = VehicleMechanic.LOW_CHARGE_SHOT.value
    BUSTLE_FEED = VehicleMechanic.BUSTLE_FEED.value
    SHELL_PARAMS_SWITCHER = VehicleMechanic.SHELL_PARAMS_SWITCHER.value
    AUXILIARY_ROCKET_LAUNCHER = VehicleMechanic.AUXILIARY_ROCKET_LAUNCHER.value
    SHELL_CALIBRATION = VehicleMechanic.SHELL_CALIBRATION.value
