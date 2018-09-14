# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/EFC2016Achievement.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import SeriesAchievement
from abstract.mixins import Quest

class EFC2016Achievement(Quest, SeriesAchievement):

    def __init__(self, dossier, value=None):
        SeriesAchievement.__init__(self, 'EFC2016', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'EFC2016WinSeries'), (_AB.TOTAL, 'maxEFC2016WinSeries'))
