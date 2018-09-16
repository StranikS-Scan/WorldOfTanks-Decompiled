# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleCompareCartPopoverMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class VehicleCompareCartPopoverMeta(SmartPopOverView):

    def remove(self, id):
        self._printOverrideError('remove')

    def removeAll(self):
        self._printOverrideError('removeAll')

    def gotoCompareView(self):
        self._printOverrideError('gotoCompareView')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by VehicleCompareCartPopoverInitDataVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_getDPS(self):
        return self.flashObject.as_getDP() if self._isDAAPIInited() else None

    def as_updateToCmpBtnPropsS(self, data):
        """
        :param data: Represented by ButtonPropertiesVO (AS)
        """
        return self.flashObject.as_updateToCmpBtnProps(data) if self._isDAAPIInited() else None

    def as_updateClearBtnPropsS(self, data):
        """
        :param data: Represented by ButtonPropertiesVO (AS)
        """
        return self.flashObject.as_updateClearBtnProps(data) if self._isDAAPIInited() else None
