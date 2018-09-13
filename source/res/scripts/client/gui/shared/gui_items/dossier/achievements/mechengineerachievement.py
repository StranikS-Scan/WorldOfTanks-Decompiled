# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/MechEngineerAchievement.py
from dossiers2.custom.helpers import getMechanicEngineerRequirements
from abstract import NationSpecificAchievement
from abstract.mixins import HasVehiclesList

class MechEngineerAchievement(HasVehiclesList, NationSpecificAchievement):

    def __init__(self, nationID, block, dossier, value = None):
        self.__vehTypeCompDescrs = self._parseVehiclesDescrsList(NationSpecificAchievement.makeFullName('mechanicEngineer', nationID), nationID, dossier)
        NationSpecificAchievement.__init__(self, 'mechanicEngineer', nationID, block, dossier, value)
        HasVehiclesList.__init__(self)

    def getVehiclesListTitle(self):
        return 'vehiclesToResearch'

    def isActive(self):
        return not len(self.getVehiclesData())

    def _readLevelUpValue(self, dossier):
        return len(self.getVehiclesData())

    def _getVehiclesDescrsList(self):
        return self.__vehTypeCompDescrs

    @classmethod
    def _parseVehiclesDescrsList(cls, name, nationID, dossier):
        if dossier is not None and dossier.isCurrentUser():
            from gui.shared import g_itemsCache
            return getMechanicEngineerRequirements(set(), g_itemsCache.items.stats.unlocks, nationID).get(name, [])
        else:
            return []
