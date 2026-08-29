# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/components_states/ammo/shells.py
from __future__ import absolute_import
import typing
from gui.battle_control.components_states.ammo.constants import ActiveAmmoMode, ShellMode
from gui.battle_control.components_states.ammo.interfaces import IAmmoMode

class DefaultAmmoMode(IAmmoMode):

    def getActiveMode(self):
        return ActiveAmmoMode.NOT_DEFINED

    def getModifiedShells(self):
        pass

    def getShellMode(self, shellIntCD):
        return ShellMode.NOT_DEFINED
