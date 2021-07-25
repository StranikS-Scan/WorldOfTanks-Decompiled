# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicBattlePageMeta.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage

class EpicBattlePageMeta(ClassicPage):

    def as_setSelectReservesAvailableS(self, value):
        return self.flashObject.as_setSelectReservesAvailable(value) if self._isDAAPIInited() else None

    def as_setVehPostProgressionEnabledS(self, value):
        return self.flashObject.as_setVehPostProgressionEnabled(value) if self._isDAAPIInited() else None
