# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/series.py
from regular import RegularAchievement
from gui.impl import backport

class SeriesAchievement(RegularAchievement):
    __slots__ = ()

    def getMaxSeriesInfo(self):
        return (self._getCounterRecordNames()[1], self.getValue())

    def getI18nValue(self):
        return backport.getIntegralFormat(self._value)

    def _getCounterRecordNames(self):
        return (None, None)

    def _readValue(self, dossier):
        record = self._getCounterRecordNames()[1]
        return dossier.getRecordValue(*record) if record is not None else 0

    def _readLevelUpTotalValue(self, dossier):
        return self._value + 1

    def _readLevelUpValue(self, dossier):
        record = self._getCounterRecordNames()[0]
        return self._lvlUpTotalValue - dossier.getRecordValue(*record) if record is not None else 0
