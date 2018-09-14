# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesWelcomeViewMeta.py
from gui.Scaleform.framework.entities.View import View

class RankedBattlesWelcomeViewMeta(View):

    def onCloseBtnClick(self):
        self._printOverrideError('onCloseBtnClick')

    def onNextBtnClick(self):
        self._printOverrideError('onNextBtnClick')

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def onAnimationFinished(self, forced):
        self._printOverrideError('onAnimationFinished')

    def onSoundTrigger(self, trigerName):
        self._printOverrideError('onSoundTrigger')

    def as_setDataS(self, data):
        """
        :param data: Represented by WelcomeViewVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
