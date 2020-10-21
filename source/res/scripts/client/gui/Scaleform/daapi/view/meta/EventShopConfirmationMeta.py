# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventShopConfirmationMeta.py
from gui.Scaleform.framework.entities.View import View

class EventShopConfirmationMeta(View):

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def onBuyClick(self):
        self._printOverrideError('onBuyClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
