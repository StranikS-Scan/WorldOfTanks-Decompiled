# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/MedalAbramsAchievement.py
from abstract import ClassProgressAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class MedalAbramsAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalAbramsAchievement, self).__init__('medalAbrams', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('battlesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalAbrams')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRandomStats().getWinAndSurvived() + dossier.getTeam7x7Stats().getWinAndSurvived() + dossier.getFortBattlesStats().getWinAndSurvived() + dossier.getFortSortiesStats().getWinAndSurvived() + dossier.getGlobalMapStats().getWinAndSurvived()
