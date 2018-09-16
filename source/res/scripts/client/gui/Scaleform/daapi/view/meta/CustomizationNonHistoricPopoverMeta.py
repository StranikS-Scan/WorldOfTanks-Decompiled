# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationNonHistoricPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class CustomizationNonHistoricPopoverMeta(SmartPopOverView):

    def remove(self, id):
        self._printOverrideError('remove')

    def removeAll(self):
        self._printOverrideError('removeAll')

    def as_setHeaderDataS(self, data):
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_getDPS(self):
        return self.flashObject.as_getDP() if self._isDAAPIInited() else None
