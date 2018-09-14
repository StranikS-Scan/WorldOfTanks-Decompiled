# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesStageCompleteViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class RankedBattlesStageCompleteViewMeta(WrapperViewMeta):

    def closeView(self):
        self._printOverrideError('closeView')

    def onSoundTrigger(self, trigerName):
        self._printOverrideError('onSoundTrigger')

    def as_setDataS(self, data):
        """
        :param data: Represented by RankedBattlesStageCompleteVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
