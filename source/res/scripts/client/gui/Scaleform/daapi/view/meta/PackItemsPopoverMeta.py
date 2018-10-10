# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PackItemsPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class PackItemsPopoverMeta(SmartPopOverView):

    def as_setItemsS(self, title, items):
        return self.flashObject.as_setItems(title, items) if self._isDAAPIInited() else None
