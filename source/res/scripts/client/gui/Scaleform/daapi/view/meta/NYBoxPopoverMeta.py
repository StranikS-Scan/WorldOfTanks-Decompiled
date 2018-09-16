# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYBoxPopoverMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class NYBoxPopoverMeta(SmartPopOverView):

    def toShop(self):
        self._printOverrideError('toShop')

    def boxOpen(self, id):
        self._printOverrideError('boxOpen')

    def toEarn(self):
        self._printOverrideError('toEarn')

    def as_setDataS(self, data, isShowAd):
        """
        :param data: Represented by Vector.<NYPopoverBoxVo> (AS)
        """
        return self.flashObject.as_setData(data, isShowAd) if self._isDAAPIInited() else None
