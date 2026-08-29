# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/generic_mechanics/shell_calibration/mechanic_models.py
from __future__ import absolute_import, division
from gui.battle_control.components_states.ammo import DefaultComponentAmmoState
from gui.battle_control.components_states.ammo.constants import ShellMode
from gui.battle_control.components_states.ammo.shells import DefaultAmmoMode

class ShellCalibrationAmmoMode(DefaultAmmoMode):

    def __init__(self, calibrationShells):
        self.__calibrationShells = frozenset(calibrationShells)

    def getShellMode(self, shellIntCD):
        return ShellMode.SHELL_CALIBRATION if shellIntCD in self.__calibrationShells else ShellMode.NOT_DEFINED


class ShellCalibrationAmmoState(DefaultComponentAmmoState):

    def __init__(self, calibrationShells):
        super(ShellCalibrationAmmoState, self).__init__()
        self.__ammoMode = ShellCalibrationAmmoMode(calibrationShells)

    def getAmmoMode(self):
        return self.__ammoMode
