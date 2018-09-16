# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RankedBattlesWidgetMeta(BaseDAAPIComponent):

    def onWidgetClick(self):
        self._printOverrideError('onWidgetClick')

    def onAnimationFinished(self):
        self._printOverrideError('onAnimationFinished')

    def onSoundTrigger(self, triggerName):
        self._printOverrideError('onSoundTrigger')

    def as_setDataS(self, states):
        return self.flashObject.as_setData(states) if self._isDAAPIInited() else None
