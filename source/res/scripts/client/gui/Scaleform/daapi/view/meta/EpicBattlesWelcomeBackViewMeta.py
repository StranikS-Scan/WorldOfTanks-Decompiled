# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicBattlesWelcomeBackViewMeta.py
from gui.Scaleform.framework.entities.View import View

class EpicBattlesWelcomeBackViewMeta(View):

    def onBackBtnClicked(self):
        self._printOverrideError('onBackBtnClicked')

    def onCloseBtnClicked(self):
        self._printOverrideError('onCloseBtnClicked')

    def onContinueBtnClicked(self):
        self._printOverrideError('onContinueBtnClicked')

    def onChangesLinkClicked(self):
        self._printOverrideError('onChangesLinkClicked')

    def playVideo(self):
        self._printOverrideError('playVideo')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None
