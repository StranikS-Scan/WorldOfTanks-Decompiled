# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesUnreachableViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class RankedBattlesUnreachableViewMeta(WrapperViewMeta):

    def onCloseBtnClick(self):
        self._printOverrideError('onCloseBtnClick')

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def onLeaderboardBtnClick(self):
        self._printOverrideError('onLeaderboardBtnClick')

    def onVideoBtnClick(self):
        self._printOverrideError('onVideoBtnClick')

    def as_setDataS(self, data):
        """
        :param data: Represented by RankedBattlesUnreachableViewVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
