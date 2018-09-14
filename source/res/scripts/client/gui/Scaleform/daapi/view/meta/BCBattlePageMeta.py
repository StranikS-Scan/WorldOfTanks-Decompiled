# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCBattlePageMeta.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage

class BCBattlePageMeta(ClassicPage):

    def onAnimationsComplete(self):
        self._printOverrideError('onAnimationsComplete')

    def as_showAnimatedS(self, data):
        return self.flashObject.as_showAnimated(data) if self._isDAAPIInited() else None

    def as_setAppearConfigS(self, data):
        return self.flashObject.as_setAppearConfig(data) if self._isDAAPIInited() else None
