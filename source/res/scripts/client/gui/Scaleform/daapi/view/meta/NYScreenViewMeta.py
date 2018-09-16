# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NYScreenViewMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class NYScreenViewMeta(BaseDAAPIComponent):

    def onSlotClick(self, slotID):
        self._printOverrideError('onSlotClick')

    def onHide(self):
        self._printOverrideError('onHide')

    def onShow(self):
        self._printOverrideError('onShow')

    def as_initS(self, slotsData):
        """
        :param slotsData: Represented by Vector.<NYToySlotVo> (AS)
        """
        return self.flashObject.as_init(slotsData) if self._isDAAPIInited() else None

    def as_slotsIDS(self):
        return self.flashObject.as_slotsID() if self._isDAAPIInited() else None

    def as_slotsPositionS(self, x1, x2):
        return self.flashObject.as_slotsPosition(x1, x2) if self._isDAAPIInited() else None

    def as_breakToyS(self, index):
        return self.flashObject.as_breakToy(index) if self._isDAAPIInited() else None
