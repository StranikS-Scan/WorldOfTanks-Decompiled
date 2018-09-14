# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ReadyForBattleALLAchievement.py
from abstract import ClassProgressAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class ReadyForBattleALLAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(ReadyForBattleALLAchievement, self).__init__('readyForBattleALL', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'readyForBattleALL')

    def _readCurrentProgressValue(self, dossier):
        return 0
