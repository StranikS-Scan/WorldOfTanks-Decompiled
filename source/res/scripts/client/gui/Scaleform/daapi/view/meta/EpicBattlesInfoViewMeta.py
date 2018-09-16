# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicBattlesInfoViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class EpicBattlesInfoViewMeta(WrapperViewMeta):

    def onCloseBtnClick(self):
        self._printOverrideError('onCloseBtnClick')

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def onManageAbilitiesBtnClick(self):
        self._printOverrideError('onManageAbilitiesBtnClick')

    def onPrestigeBtnClick(self):
        self._printOverrideError('onPrestigeBtnClick')

    def onSeeRewardsBtnClick(self):
        self._printOverrideError('onSeeRewardsBtnClick')

    def onReadIntroBtnClick(self):
        self._printOverrideError('onReadIntroBtnClick')

    def onButtonWelcomeAnimationDone(self):
        self._printOverrideError('onButtonWelcomeAnimationDone')

    def onButtonsElementWelcomeAnimationDone(self):
        self._printOverrideError('onButtonsElementWelcomeAnimationDone')

    def onMetaElementWelcomeAnimationDone(self):
        self._printOverrideError('onMetaElementWelcomeAnimationDone')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
