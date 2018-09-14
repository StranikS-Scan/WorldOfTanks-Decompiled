# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ReadyForBattleHTAchievement.py
from abstract import ClassProgressAchievement, getCompletedPotapovQuestsCount
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class ReadyForBattleHTAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(ReadyForBattleHTAchievement, self).__init__('readyForBattleHT', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('questsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'readyForBattleHT')

    def _readCurrentProgressValue(self, dossier):
        return getCompletedPotapovQuestsCount(1, {'heavyTank'})
