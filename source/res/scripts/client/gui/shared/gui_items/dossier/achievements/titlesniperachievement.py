# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/TitleSniperAchievement.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import SeriesAchievement

class TitleSniperAchievement(SeriesAchievement):

    def __init__(self, dossier, value = None):
        super(TitleSniperAchievement, self).__init__('titleSniper', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'sniperSeries'), (_AB.TOTAL, 'maxSniperSeries'))
