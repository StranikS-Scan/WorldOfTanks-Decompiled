# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortOrderSelectPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortOrderSelectPopoverMeta(SmartPopOverView):

    def addOrder(self, orderID):
        self._printOverrideError('addOrder')

    def removeOrder(self, orderID):
        self._printOverrideError('removeOrder')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
