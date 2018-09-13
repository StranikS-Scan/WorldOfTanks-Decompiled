# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/GuerrillaAchievement.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import SimpleProgressAchievement

class GuerrillaAchievement(SimpleProgressAchievement):

    def __init__(self, dossier, value = None):
        super(GuerrillaAchievement, self).__init__('guerrillaMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'guerrilla')
