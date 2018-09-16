# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYChestsViewMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.View import View

class NYChestsViewMeta(View):

    def onOpenBtnClick(self):
        self._printOverrideError('onOpenBtnClick')

    def onCloseWindow(self):
        self._printOverrideError('onCloseWindow')

    def onPlaySound(self, soundType):
        self._printOverrideError('onPlaySound')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by NYChestsViewVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setRewardDataS(self, awardData):
        """
        :param awardData: Represented by RibbonAwardsVO (AS)
        """
        return self.flashObject.as_setRewardData(awardData) if self._isDAAPIInited() else None

    def as_setOpenBtnLabelS(self, label):
        return self.flashObject.as_setOpenBtnLabel(label) if self._isDAAPIInited() else None

    def as_setOpenBtnEnabledS(self, enabled):
        return self.flashObject.as_setOpenBtnEnabled(enabled) if self._isDAAPIInited() else None

    def as_setControlsEnabledS(self, enabled):
        return self.flashObject.as_setControlsEnabled(enabled) if self._isDAAPIInited() else None

    def as_showRewardRibbonS(self):
        return self.flashObject.as_showRewardRibbon() if self._isDAAPIInited() else None

    def as_hideRewardRibbonS(self):
        return self.flashObject.as_hideRewardRibbon() if self._isDAAPIInited() else None
