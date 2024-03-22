# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SpectatorViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SpectatorViewMeta(BaseDAAPIComponent):

    def as_setFollowInfoTextS(self, folowText):
        return self.flashObject.as_setFollowInfoText(folowText) if self._isDAAPIInited() else None

    def as_changeModeS(self, mode):
        return self.flashObject.as_changeMode(mode) if self._isDAAPIInited() else None

    def as_focusOnVehicleS(self, focused):
        return self.flashObject.as_focusOnVehicle(focused) if self._isDAAPIInited() else None

    def as_setTimerS(self, time):
        return self.flashObject.as_setTimer(time) if self._isDAAPIInited() else None

    def as_setSpeedS(self, speed):
        return self.flashObject.as_setSpeed(speed) if self._isDAAPIInited() else None

    def as_setHintStringsS(self, movementHeadline, movementDescription, speedHeadline, speedDescription, heightHeadline, heightDescription, spectatorUpBtnText, spectatorDownBtnText):
        return self.flashObject.as_setHintStrings(movementHeadline, movementDescription, speedHeadline, speedDescription, heightHeadline, heightDescription, spectatorUpBtnText, spectatorDownBtnText) if self._isDAAPIInited() else None

    def as_showMovementHintS(self, shouldShow):
        return self.flashObject.as_showMovementHint(shouldShow) if self._isDAAPIInited() else None

    def as_showSpeedHeightHintS(self, shouldShow):
        return self.flashObject.as_showSpeedHeightHint(shouldShow) if self._isDAAPIInited() else None

    def as_showReturnHintS(self, shouldShow):
        return self.flashObject.as_showReturnHint(shouldShow) if self._isDAAPIInited() else None

    def as_showSpeedHintS(self, shouldShow):
        return self.flashObject.as_showSpeedHint(shouldShow) if self._isDAAPIInited() else None

    def as_toggleHintS(self, hintModeId):
        return self.flashObject.as_toggleHint(hintModeId) if self._isDAAPIInited() else None

    def as_handleAsReplayS(self):
        return self.flashObject.as_handleAsReplay() if self._isDAAPIInited() else None

    def as_updateMovementHintControlsS(self, forward, left, backward, right):
        return self.flashObject.as_updateMovementHintControls(forward, left, backward, right) if self._isDAAPIInited() else None
