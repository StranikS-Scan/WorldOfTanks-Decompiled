# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedCompleteViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class RankedCompleteViewMeta(WrapperViewMeta):

    def as_setRewardsDataS(self, awardData):
        return self.flashObject.as_setRewardsData(awardData) if self._isDAAPIInited() else None
