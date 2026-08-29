# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/components_states/ammo/interfaces.py
from __future__ import absolute_import
import typing
if typing.TYPE_CHECKING:
    from gui.battle_control.components_states.ammo.constants import AmmoShootPossibility, ActiveAmmoMode, ShellMode

class IComponentAmmoState(object):

    def isReloadingBlocked(self):
        raise NotImplementedError

    def canChangeVehicleSetting(self, code):
        raise NotImplementedError

    def canShootValidation(self):
        raise NotImplementedError

    def getShotsAmount(self):
        raise NotImplementedError

    def getShootPossibility(self, currentShells):
        raise NotImplementedError

    def getSpecialReloadMessage(self):
        raise NotImplementedError

    def getAmmoMode(self):
        raise NotImplementedError

    def getShellReloadTimes(self, currShell, shellChangeTime, shells):
        raise NotImplementedError


class IAmmoMode(object):

    def getActiveMode(self):
        raise NotImplementedError

    def getModifiedShells(self):
        raise NotImplementedError

    def getShellMode(self, shellIntCD):
        raise NotImplementedError
