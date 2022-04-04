# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CommanderBattlePageMeta.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage

class CommanderBattlePageMeta(ClassicPage):

    def as_spawnPointWindowClosedS(self):
        return self.flashObject.as_spawnPointWindowClosed() if self._isDAAPIInited() else None
