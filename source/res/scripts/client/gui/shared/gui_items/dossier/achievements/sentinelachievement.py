# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/SentinelAchievement.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import SimpleProgressAchievement

class SentinelAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(SentinelAchievement, self).__init__('sentinelMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'sentinel')
