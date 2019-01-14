# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicBattlesInfoViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class EpicBattlesInfoViewMeta(WrapperViewMeta):

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def onCloseBtnClick(self):
        self._printOverrideError('onCloseBtnClick')

    def onManageAbilitiesBtnClick(self):
        self._printOverrideError('onManageAbilitiesBtnClick')

    def onPrestigeBtnClick(self):
        self._printOverrideError('onPrestigeBtnClick')

    def onGameRewardsBtnClick(self):
        self._printOverrideError('onGameRewardsBtnClick')

    def onInfoBtnClick(self):
        self._printOverrideError('onInfoBtnClick')

    def onShowRewardVehicleInGarageBtnClick(self):
        self._printOverrideError('onShowRewardVehicleInGarageBtnClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_showInfoLinesS(self, show):
        return self.flashObject.as_showInfoLines(show) if self._isDAAPIInited() else None

    def as_showFinalRewardClaimedS(self):
        return self.flashObject.as_showFinalRewardClaimed() if self._isDAAPIInited() else None
