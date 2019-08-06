# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventPostmortemPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import PostmortemPanel

class EventPostmortemPanelMeta(PostmortemPanel):

    def switchShowDogtagAnimation(self, value):
        self._printOverrideError('switchShowDogtagAnimation')

    def onDogtagRollover(self):
        self._printOverrideError('onDogtagRollover')

    def onDogtagRollout(self):
        self._printOverrideError('onDogtagRollout')

    def onDogtagStartAnim(self):
        self._printOverrideError('onDogtagStartAnim')

    def onDogtagHideAnim(self):
        self._printOverrideError('onDogtagHideAnim')

    def as_setDogtagInfoS(self, basisImg, emblemImg, titleImg, rankStr, nickStr, isAnimEnabled, basisSmallImg, emblemSmallImg, translateStr, basisBackImg, truncateEndingStr, animEnabledTooltip, animDisabledTooltip):
        return self.flashObject.as_setDogtagInfo(basisImg, emblemImg, titleImg, rankStr, nickStr, isAnimEnabled, basisSmallImg, emblemSmallImg, translateStr, basisBackImg, truncateEndingStr, animEnabledTooltip, animDisabledTooltip) if self._isDAAPIInited() else None

    def as_toggleCtrlPressFlagS(self, isCtrlPressed):
        return self.flashObject.as_toggleCtrlPressFlag(isCtrlPressed) if self._isDAAPIInited() else None
