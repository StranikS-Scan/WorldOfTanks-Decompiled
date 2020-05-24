# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCBattleResultMeta.py
from gui.Scaleform.framework.entities.View import View

class BCBattleResultMeta(View):

    def click(self):
        self._printOverrideError('click')

    def onAnimationAwardStart(self, id):
        self._printOverrideError('onAnimationAwardStart')

    def onToolTipShow(self, rendererId):
        self._printOverrideError('onToolTipShow')

    def onVideoButtonClick(self):
        self._printOverrideError('onVideoButtonClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
