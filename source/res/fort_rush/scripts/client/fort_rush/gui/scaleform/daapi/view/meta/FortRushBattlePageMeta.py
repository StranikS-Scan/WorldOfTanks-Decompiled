# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/meta/FortRushBattlePageMeta.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage

class FortRushBattlePageMeta(ClassicPage):

    def as_setRespawnModeS(self, value):
        return self.flashObject.as_setRespawnMode(value) if self._isDAAPIInited() else None
