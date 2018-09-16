# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedCompleteViewViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class RankedCompleteViewViewMeta(WrapperViewMeta):

    def as_setRewardsS(self, awardData):
        """
        :param awardData: Represented by RibbonAwardsVO (AS)
        """
        return self.flashObject.as_setRewards(awardData) if self._isDAAPIInited() else None
