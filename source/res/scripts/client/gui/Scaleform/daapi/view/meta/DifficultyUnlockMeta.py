# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DifficultyUnlockMeta.py
from gui.Scaleform.framework.entities.View import View

class DifficultyUnlockMeta(View):

    def onCloseClick(self):
        self._printOverrideError('onCloseClick')

    def onDifficultyChangeClick(self):
        self._printOverrideError('onDifficultyChangeClick')

    def as_setDifficultyS(self, value, btnEnable=True):
        return self.flashObject.as_setDifficulty(value, btnEnable) if self._isDAAPIInited() else None

    def as_blurOtherWindowsS(self, layer):
        return self.flashObject.as_blurOtherWindows(layer) if self._isDAAPIInited() else None
