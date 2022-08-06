# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationItemsPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class CustomizationItemsPopoverMeta(SmartPopOverView):

    def remove(self, id, itemsList):
        self._printOverrideError('remove')

    def removeAll(self):
        self._printOverrideError('removeAll')

    def onFilterChanged(self, showHistoric, showNonHistoric, showFantastic):
        self._printOverrideError('onFilterChanged')

    def as_setHeaderDataS(self, data):
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_getDPS(self):
        return self.flashObject.as_getDP() if self._isDAAPIInited() else None

    def as_showClearMessageS(self, isClear, message):
        return self.flashObject.as_showClearMessage(isClear, message) if self._isDAAPIInited() else None
