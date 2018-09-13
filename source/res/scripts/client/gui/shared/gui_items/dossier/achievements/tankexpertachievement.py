# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/TankExpertAchievement.py
from dossiers2.custom.helpers import getTankExpertRequirements
from abstract import NationSpecificAchievement
from abstract.mixins import HasVehiclesList

class TankExpertAchievement(HasVehiclesList, NationSpecificAchievement):

    def __init__(self, nationID, block, dossier, value = None):
        self.__vehTypeCompDescrs = self._parseVehiclesDescrsList(NationSpecificAchievement.makeFullName('tankExpert', nationID), dossier)
        NationSpecificAchievement.__init__(self, 'tankExpert', nationID, block, dossier, value)
        HasVehiclesList.__init__(self)
        self.__achieved = dossier is not None and bool(dossier.getRecordValue(*self.getRecordName()))
        return

    def isActive(self):
        return self.__achieved

    def getVehiclesListTitle(self):
        return 'vehiclesToKill'

    def _readLevelUpValue(self, dossier):
        return len(self.getVehiclesData())

    def _getVehiclesDescrsList(self):
        return self.__vehTypeCompDescrs

    @classmethod
    def _parseVehiclesDescrsList(cls, name, dossier):
        if dossier is not None:
            return getTankExpertRequirements(dossier.getBlock('vehTypeFrags')).get(name, [])
        else:
            return []
