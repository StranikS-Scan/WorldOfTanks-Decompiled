# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TankCarouselFilterPopoverMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class TankCarouselFilterPopoverMeta(SmartPopOverView):

    def changeFilter(self, groupId, itemId):
        self._printOverrideError('changeFilter')

    def changeSearchNameVehicle(self, inputText):
        self._printOverrideError('changeSearchNameVehicle')

    def switchCarouselType(self, selected):
        self._printOverrideError('switchCarouselType')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by FilterCarouseInitVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setStateS(self, data):
        """
        :param data: Represented by FiltersStateVO (AS)
        """
        return self.flashObject.as_setState(data) if self._isDAAPIInited() else None

    def as_showCounterS(self, countText):
        return self.flashObject.as_showCounter(countText) if self._isDAAPIInited() else None
