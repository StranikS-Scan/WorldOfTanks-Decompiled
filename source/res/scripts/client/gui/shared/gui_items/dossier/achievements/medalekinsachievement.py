# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/MedalEkinsAchievement.py
from abstract import ClassProgressAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class MedalEkinsAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalEkinsAchievement, self).__init__('medalEkins', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalEkins')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRandomStats().getFrags8p() + dossier.getTeam7x7Stats().getFrags8p() + dossier.getFortBattlesStats().getFrags8p() + dossier.getFortSortiesStats().getFrags8p() + dossier.getGlobalMapStats().getFrags8p()
