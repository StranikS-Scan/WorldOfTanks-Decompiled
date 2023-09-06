# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AnimatedBattleHintMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class AnimatedBattleHintMeta(BaseDAAPIComponent):

    def animFinish(self):
        self._printOverrideError('animFinish')

    def as_showHintS(self, frame, msgStr, isCompleted):
        return self.flashObject.as_showHint(frame, msgStr, isCompleted) if self._isDAAPIInited() else None

    def as_hideHintS(self):
        return self.flashObject.as_hideHint() if self._isDAAPIInited() else None

    def as_closeHintS(self):
        return self.flashObject.as_closeHint() if self._isDAAPIInited() else None

    def as_setPenetrationS(self, penetrationType, isPurple):
        return self.flashObject.as_setPenetration(penetrationType, isPurple) if self._isDAAPIInited() else None
