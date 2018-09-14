# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortOrderSelectPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortOrderSelectPopoverMeta(SmartPopOverView):

    def addOrder(self, orderID):
        self._printOverrideError('addOrder')

    def removeOrder(self, orderID):
        self._printOverrideError('removeOrder')

    def as_setDataS(self, data):
        """
        :param data: Represented by OrderSelectPopoverVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
