# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedCompleteViewMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class RankedCompleteViewMeta(WrapperViewMeta):

    def as_setRewardsDataS(self, awardData):
        """
        :param awardData: Represented by RibbonAwardsVO (AS)
        """
        return self.flashObject.as_setRewardsData(awardData) if self._isDAAPIInited() else None
