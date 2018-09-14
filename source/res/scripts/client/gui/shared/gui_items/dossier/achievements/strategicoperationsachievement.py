# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/StrategicOperationsAchievement.py
from abstract import ClassProgressAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB

class StrategicOperationsAchievement(ClassProgressAchievement):

    def __init__(self, dossier, value = None):
        super(StrategicOperationsAchievement, self).__init__('strategicOperations', _AB.RATED_7X7, dossier, value)

    def getNextLevelInfo(self):
        return ('winsLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.RATED_7X7, 'strategicOperations')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getTotalStats().getWinsCount()
