# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/PopoverManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class PopoverManagerMeta(BaseDAAPIModule):

    def requestShowPopover(self, alias, data):
        self._printOverrideError('requestShowPopover')

    def requestHidePopover(self):
        self._printOverrideError('requestHidePopover')

    def as_onPopoverDestroyS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_onPopoverDestroy()
