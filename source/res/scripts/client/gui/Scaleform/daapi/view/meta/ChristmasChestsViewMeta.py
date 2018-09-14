# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ChristmasChestsViewMeta.py
from gui.Scaleform.framework.entities.View import View

class ChristmasChestsViewMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    """

    def onOpenBtnClick(self):
        self._printOverrideError('onOpenBtnClick')

    def onCloseWindow(self):
        self._printOverrideError('onCloseWindow')

    def onPlaySound(self, soundType):
        self._printOverrideError('onPlaySound')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by ChestsViewVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setOpenBtnEnabledS(self, enabled):
        return self.flashObject.as_setOpenBtnEnabled(enabled) if self._isDAAPIInited() else None

    def as_showAwardRibbonS(self, showRibbon):
        return self.flashObject.as_showAwardRibbon(showRibbon) if self._isDAAPIInited() else None

    def as_setAwardDataS(self, awardData):
        """
        :param awardData: Represented by Vector.<AwardCarouselItemRendererVO> (AS)
        """
        return self.flashObject.as_setAwardData(awardData) if self._isDAAPIInited() else None

    def as_setBottomTextsS(self, chestsNum, openBtnLabel):
        return self.flashObject.as_setBottomTexts(chestsNum, openBtnLabel) if self._isDAAPIInited() else None

    def as_setControlsEnabledS(self, enabled):
        return self.flashObject.as_setControlsEnabled(enabled) if self._isDAAPIInited() else None
