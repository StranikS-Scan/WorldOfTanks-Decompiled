# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/StormLordAchievement.py
from abstract import ClassProgressAchievement
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract.mixins import Deprecated, NoProgressBar

class StormLordAchievement(Deprecated, NoProgressBar, ClassProgressAchievement):

    def __init__(self, dossier, value=None):
        super(StormLordAchievement, self).__init__('stormLord', _AB.FALLOUT, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.FALLOUT, 'stormLord')

    def _readCurrentProgressValue(self, dossier):
        return dossier.getFalloutStats().getConsumablesFragsCount()
