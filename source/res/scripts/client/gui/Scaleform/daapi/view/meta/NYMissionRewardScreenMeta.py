# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYMissionRewardScreenMeta.py
from gui.Scaleform.framework.entities.View import View

class NYMissionRewardScreenMeta(View):

    def onOpenBtnClick(self):
        self._printOverrideError('onOpenBtnClick')

    def onCloseWindow(self):
        self._printOverrideError('onCloseWindow')

    def onPlaySound(self, soundType):
        self._printOverrideError('onPlaySound')

    def onToyObtained(self, level):
        self._printOverrideError('onToyObtained')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by NYMissionRewardScreenVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setRewardDataS(self, awardData):
        """
        :param awardData: Represented by RibbonAwardsVO (AS)
        """
        return self.flashObject.as_setRewardData(awardData) if self._isDAAPIInited() else None

    def as_setVehicleDataS(self, data):
        """
        :param data: Represented by NYVehicleRewardVO (AS)
        """
        return self.flashObject.as_setVehicleData(data) if self._isDAAPIInited() else None

    def as_startAnimationS(self, boxAnimSource):
        return self.flashObject.as_startAnimation(boxAnimSource) if self._isDAAPIInited() else None

    def as_restartAnimationS(self, boxAnimSource):
        return self.flashObject.as_restartAnimation(boxAnimSource) if self._isDAAPIInited() else None

    def as_setOpenBtnLabelS(self, label):
        return self.flashObject.as_setOpenBtnLabel(label) if self._isDAAPIInited() else None

    def as_setOpenBtnEnabledS(self, enabled):
        return self.flashObject.as_setOpenBtnEnabled(enabled) if self._isDAAPIInited() else None

    def as_setCloseBtnEnabledS(self, enabled):
        return self.flashObject.as_setCloseBtnEnabled(enabled) if self._isDAAPIInited() else None
