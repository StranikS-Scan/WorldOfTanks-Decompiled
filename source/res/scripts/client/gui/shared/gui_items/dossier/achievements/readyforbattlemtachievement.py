# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ReadyForBattleMTAchievement.py
from abstract import ClassProgressAchievement, getCompletedPotapovQuestsCount
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class ReadyForBattleMTAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(ReadyForBattleMTAchievement, self).__init__('readyForBattleMT', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('questsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'readyForBattleMT')

    def _readCurrentProgressValue(self, dossier):
        return getCompletedPotapovQuestsCount(1, {'mediumTank'})
