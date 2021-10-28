# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBattlePageMeta.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage

class EventBattlePageMeta(ClassicPage):

    def as_updateDamageScreenS(self, isVisible):
        return self.flashObject.as_updateDamageScreen(isVisible) if self._isDAAPIInited() else None
