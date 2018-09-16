# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesAwardsViewMeta.py
from gui.Scaleform.framework.entities.View import View

class RankedBattlesAwardsViewMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def onSoundTrigger(self, triggerName):
        self._printOverrideError('onSoundTrigger')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
