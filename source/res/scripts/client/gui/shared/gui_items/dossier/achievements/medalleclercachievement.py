# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/MedalLeClercAchievement.py
from abstract import ClassProgressAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class MedalLeClercAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalLeClercAchievement, self).__init__('medalLeClerc', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('capturePointsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'medalLeClerc')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRandomStats().getCapturePoints() - dossier.getClanStats().getCapturePoints() + dossier.getTeam7x7Stats().getCapturePoints() + dossier.getFortBattlesStats().getCapturePoints() + dossier.getFortSortiesStats().getCapturePoints() + dossier.getGlobalMapStats().getCapturePoints()
