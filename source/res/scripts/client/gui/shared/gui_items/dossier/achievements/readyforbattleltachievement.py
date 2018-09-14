# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ReadyForBattleLTAchievement.py
from abstract import ClassProgressAchievement, getCompletedPotapovQuestsCount
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class ReadyForBattleLTAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(ReadyForBattleLTAchievement, self).__init__('readyForBattleLT', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('questsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'readyForBattleLT')

    def _readCurrentProgressValue(self, dossier):
        return getCompletedPotapovQuestsCount(1, {'lightTank'})
