# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/generic_mechanics/spec_boost_mode/mechanic_interfaces.py
from __future__ import absolute_import
import typing
from vehicles.mechanics.common.mechanic_interfaces import IMechanicWithVariants
from vehicles.mechanics.mechanic_states import IMechanicState
if typing.TYPE_CHECKING:
    from items.components.shared_components import SpecBoostModeParams

class ISpecBoostModeMechanicParams(IMechanicWithVariants):

    @classmethod
    def fromMechanicParams(cls, params):
        raise NotImplementedError


class ISpecBoostModeMechanicState(IMechanicState):

    @classmethod
    def fromComponentStatus(cls, status):
        raise NotImplementedError

    @property
    def progress(self):
        raise NotImplementedError

    @property
    def timeLeft(self):
        raise NotImplementedError

    @property
    def state(self):
        raise NotImplementedError
