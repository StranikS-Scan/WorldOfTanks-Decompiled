# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicBattlesAfterBattleViewMeta.py
from gui.Scaleform.framework.entities.View import View

class EpicBattlesAfterBattleViewMeta(View):

    def onIntroStartsPlaying(self):
        self._printOverrideError('onIntroStartsPlaying')

    def onRibbonStartsPlaying(self):
        self._printOverrideError('onRibbonStartsPlaying')

    def onNextBtnClick(self):
        self._printOverrideError('onNextBtnClick')

    def onCloseBtnClick(self):
        self._printOverrideError('onCloseBtnClick')

    def onRewardsBtnClick(self):
        self._printOverrideError('onRewardsBtnClick')

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def onProgressBarStartAnim(self):
        self._printOverrideError('onProgressBarStartAnim')

    def onProgressBarCompleteAnim(self):
        self._printOverrideError('onProgressBarCompleteAnim')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
