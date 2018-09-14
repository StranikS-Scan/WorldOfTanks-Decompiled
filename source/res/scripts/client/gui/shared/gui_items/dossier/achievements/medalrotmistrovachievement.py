# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/MedalRotmistrovAchievement.py
from abstract import ClassProgressAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class MedalRotmistrovAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(MedalRotmistrovAchievement, self).__init__('medalRotmistrov', _AB.CLAN, dossier, value)

    def getNextLevelInfo(self):
        return ('battlesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.CLAN, 'medalRotmistrov')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getGlobalMapStats().getBattlesCount()
