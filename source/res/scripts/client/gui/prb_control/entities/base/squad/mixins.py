# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/mixins.py
from gui.prb_control.entities.base.squad.components import SquadRestrictionsProvider

class SquadRestrictionsMixin(object):

    def __init__(self):
        self.__squadRestrictionsProvider = self._createSquadRestrictionsProvider()

    def initRestrictedRoleDataProvider(self, unit):
        self.__squadRestrictionsProvider.init(unit)

    def finiRestrictedRoleDataProvider(self):
        self.__squadRestrictionsProvider.fini()

    def isSquadRestrictionValid(self):
        return self.__squadRestrictionsProvider.isValid()

    def isVehicleSuitableForSquad(self, vehicle):
        hasSlot, _ = self.__squadRestrictionsProvider.hasSlotForVehicle(vehicle, ignoreOwnVehiclesInUnit=True)
        return hasSlot

    def hasSlotForVehicle(self, vehicle):
        return self.__squadRestrictionsProvider.hasSlotForVehicle(vehicle)

    @property
    def squadRestrictions(self):
        raise NotImplementedError

    @classmethod
    def _createSquadRestrictionsProvider(cls):
        return SquadRestrictionsProvider()
