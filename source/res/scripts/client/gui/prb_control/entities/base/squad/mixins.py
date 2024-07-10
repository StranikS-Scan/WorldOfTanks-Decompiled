# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/mixins.py
from gui.prb_control.entities.base.squad.components import RestrictedRoleTagDataProvider

class RestrictedRoleTagMixin(object):

    def __init__(self):
        self.__restrictedRoleTagDataProvider = self._createRestrictedRoleTagDataProvider()

    def initRestrictedRoleDataProvider(self, unit):
        self.__restrictedRoleTagDataProvider.init(unit)

    def finiRestrictedRoleDataProvider(self):
        self.__restrictedRoleTagDataProvider.fini()

    def getMaxRoleCount(self, roleTag):
        return self.__restrictedRoleTagDataProvider.getMaxPossibleVehicles(roleTag)

    def getMaxRoleLevels(self, roleTag):
        return self.__restrictedRoleTagDataProvider.getRestrictionLevels(roleTag)

    def hasSlotForRole(self, roleTag):
        return self.__restrictedRoleTagDataProvider.hasSlotForVehicle(roleTag)

    def isRoleRestrictionValid(self):
        return self.__restrictedRoleTagDataProvider.isValid()

    def isTagVehicleAvailable(self, tags):
        return self.__restrictedRoleTagDataProvider.isTagVehicleAvailable(tags)

    @property
    def squadRestrictions(self):
        raise NotImplementedError

    @classmethod
    def _createRestrictedRoleTagDataProvider(cls):
        return RestrictedRoleTagDataProvider()
