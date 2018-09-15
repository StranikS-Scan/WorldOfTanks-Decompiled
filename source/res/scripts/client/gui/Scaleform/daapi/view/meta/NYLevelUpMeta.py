# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYLevelUpMeta.py
from gui.Scaleform.framework.entities.View import View

class NYLevelUpMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onOpenClick(self):
        self._printOverrideError('onOpenClick')

    def onAnimFinished(self, isBoxOpened):
        self._printOverrideError('onAnimFinished')

    def onPlaySound(self, soundType):
        self._printOverrideError('onPlaySound')

    def as_setDataS(self, data):
        """
        :param data: Represented by NYLevelUpDataVo (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_boxOpenS(self, isApprove):
        return self.flashObject.as_boxOpen(isApprove) if self._isDAAPIInited() else None
