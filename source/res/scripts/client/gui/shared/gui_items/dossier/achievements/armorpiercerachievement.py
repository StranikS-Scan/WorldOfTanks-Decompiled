# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ArmorPiercerAchievement.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import SeriesAchievement

class ArmorPiercerAchievement(SeriesAchievement):

    def __init__(self, dossier, value = None):
        super(ArmorPiercerAchievement, self).__init__('armorPiercer', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'piercingSeries'), (_AB.TOTAL, 'maxPiercingSeries'))
