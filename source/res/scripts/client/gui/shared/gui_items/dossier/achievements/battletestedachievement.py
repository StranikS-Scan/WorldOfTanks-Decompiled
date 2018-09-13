# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/BattleTestedAchievement.py
from abstract import ClassProgressAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class BattleTestedAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(BattleTestedAchievement, self).__init__('battleTested', _AB.TEAM_7X7, dossier, value)

    def getNextLevelInfo(self):
        return ('achievesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'battleTested')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'awardCount')
