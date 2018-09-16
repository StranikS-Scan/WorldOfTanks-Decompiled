# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalMissionsOperationAwardsScreenMeta.py
from gui.Scaleform.framework.entities.View import View

class PersonalMissionsOperationAwardsScreenMeta(View):

    def onCloseWindow(self):
        self._printOverrideError('onCloseWindow')

    def onPlaySound(self, soundType):
        self._printOverrideError('onPlaySound')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setAwardDataS(self, awardData):
        return self.flashObject.as_setAwardData(awardData) if self._isDAAPIInited() else None

    def as_setCloseBtnEnabledS(self, enabled):
        return self.flashObject.as_setCloseBtnEnabled(enabled) if self._isDAAPIInited() else None

    def as_playAwardsAnimationS(self):
        return self.flashObject.as_playAwardsAnimation() if self._isDAAPIInited() else None
