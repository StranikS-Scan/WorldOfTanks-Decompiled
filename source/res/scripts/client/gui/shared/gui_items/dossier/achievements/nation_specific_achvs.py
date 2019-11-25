# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/nation_specific_achvs.py
from dossiers2.custom.helpers import getMechanicEngineerRequirements
from dossiers2.custom.helpers import getTankExpertRequirements
from abstract import NationSpecificAchievement
from abstract.mixins import HasVehiclesList
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class MechEngineerAchievement(HasVehiclesList, NationSpecificAchievement):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, nationID, block, dossier, value=None):
        self.__vehTypeCompDescrs = self._parseVehiclesDescrsList(NationSpecificAchievement.makeFullName('mechanicEngineer', nationID), nationID, dossier)
        NationSpecificAchievement.__init__(self, 'mechanicEngineer', nationID, block, dossier, value)
        HasVehiclesList.__init__(self)

    def getVehiclesListTitle(self):
        pass

    def isActive(self):
        return not self.getVehiclesData()

    def _readLevelUpValue(self, dossier):
        return len(self.getVehiclesData())

    def _getVehiclesDescrsList(self):
        return self.__vehTypeCompDescrs

    @classmethod
    def _parseVehiclesDescrsList(cls, name, nationID, dossier):
        return getMechanicEngineerRequirements(set(), cls.itemsCache.items.stats.unlocks, nationID).get(name, []) if dossier is not None and dossier.isCurrentUser() else []


class TankExpertAchievement(HasVehiclesList, NationSpecificAchievement):

    def __init__(self, nationID, block, dossier, value=None):
        self.__vehTypeCompDescrs = self._parseVehiclesDescrsList(NationSpecificAchievement.makeFullName('tankExpert', nationID), dossier)
        NationSpecificAchievement.__init__(self, 'tankExpert', nationID, block, dossier, value)
        HasVehiclesList.__init__(self)
        self.__achieved = dossier is not None and bool(dossier.getRecordValue(*self.getRecordName()))
        return

    def isActive(self):
        return self.__achieved

    def getVehiclesListTitle(self):
        pass

    def _readLevelUpValue(self, dossier):
        return len(self.getVehiclesData())

    def _getVehiclesDescrsList(self):
        return self.__vehTypeCompDescrs

    @classmethod
    def _parseVehiclesDescrsList(cls, name, dossier):
        return getTankExpertRequirements(dossier.getBlock('vehTypeFrags')).get(name, []) if dossier is not None else []
