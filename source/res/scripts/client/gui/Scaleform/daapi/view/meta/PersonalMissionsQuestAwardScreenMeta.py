# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalMissionsQuestAwardScreenMeta.py
from gui.Scaleform.framework.entities.View import View

class PersonalMissionsQuestAwardScreenMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def onNextQuestLinkClick(self):
        self._printOverrideError('onNextQuestLinkClick')

    def onNextQuestBtnClick(self):
        self._printOverrideError('onNextQuestBtnClick')

    def onRecruitBtnClick(self):
        self._printOverrideError('onRecruitBtnClick')

    def onContinueBtnClick(self):
        self._printOverrideError('onContinueBtnClick')

    def onOkBtnClick(self):
        self._printOverrideError('onOkBtnClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
