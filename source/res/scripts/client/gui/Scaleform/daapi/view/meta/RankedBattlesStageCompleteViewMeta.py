# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesStageCompleteViewMeta.py
from gui.Scaleform.daapi.view.meta.RankedCompleteViewMeta import RankedCompleteViewMeta

class RankedBattlesStageCompleteViewMeta(RankedCompleteViewMeta):

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
