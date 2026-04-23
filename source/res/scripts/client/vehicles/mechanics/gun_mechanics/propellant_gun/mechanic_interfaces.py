# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/propellant_gun/mechanic_interfaces.py
from __future__ import absolute_import
import typing
from vehicles.mechanics.mechanic_states import IMechanicState
if typing.TYPE_CHECKING:
    from items.components.shared_components import PropellantGunParams

class IPropellantGunComponentParams(object):

    @classmethod
    def fromMechanicParams(cls, params):
        raise NotImplementedError

    @property
    def chargePerSec(self):
        raise NotImplementedError

    @property
    def dischargePerSec(self):
        raise NotImplementedError

    @property
    def maxCharge(self):
        raise NotImplementedError

    @property
    def maxOvercharge(self):
        raise NotImplementedError

    @property
    def stages(self):
        raise NotImplementedError

    @property
    def forbiddenShells(self):
        raise NotImplementedError


class IPropellantGunMechanicState(IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status, params):
        raise NotImplementedError

    @property
    def state(self):
        raise NotImplementedError

    @property
    def currentStage(self):
        raise NotImplementedError

    @property
    def currentCharge(self):
        raise NotImplementedError

    @property
    def currentThreshold(self):
        raise NotImplementedError

    @property
    def isOvercharge(self):
        raise NotImplementedError

    @property
    def isAvailable(self):
        raise NotImplementedError

    @property
    def timeLeft(self):
        raise NotImplementedError

    @property
    def isLastStage(self):
        raise NotImplementedError

    @property
    def isUsableShell(self):
        raise NotImplementedError

    @property
    def lastShotTimestamp(self):
        raise NotImplementedError

    @property
    def lastShotCharge(self):
        raise NotImplementedError

    def getCurrentDamageFactor(self, progress=None):
        raise NotImplementedError
