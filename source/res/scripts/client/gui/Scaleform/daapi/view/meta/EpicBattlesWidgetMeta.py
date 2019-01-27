# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicBattlesWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EpicBattlesWidgetMeta(BaseDAAPIComponent):

    def onWidgetClick(self):
        self._printOverrideError('onWidgetClick')

    def onAnimationFinished(self):
        self._printOverrideError('onAnimationFinished')

    def onSoundTrigger(self, trigerName):
        self._printOverrideError('onSoundTrigger')

    def onChangeServerClick(self):
        self._printOverrideError('onChangeServerClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
