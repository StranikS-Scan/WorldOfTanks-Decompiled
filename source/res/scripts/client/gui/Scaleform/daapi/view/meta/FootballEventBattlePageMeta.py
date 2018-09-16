# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FootballEventBattlePageMeta.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage

class FootballEventBattlePageMeta(ClassicPage):

    def as_setCommentatorPanelVisibleS(self, name, role, icon):
        return self.flashObject.as_setCommentatorPanelVisible(name, role, icon) if self._isDAAPIInited() else None
