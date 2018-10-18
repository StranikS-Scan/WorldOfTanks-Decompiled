# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventShopViewMeta.py
from gui.Scaleform.framework.entities.View import View

class EventShopViewMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def onBuyItem(self, itemId):
        self._printOverrideError('onBuyItem')

    def as_setMaxBonusDataS(self, data):
        return self.flashObject.as_setMaxBonusData(data) if self._isDAAPIInited() else None

    def as_setProgressDataS(self, data):
        return self.flashObject.as_setProgressData(data) if self._isDAAPIInited() else None

    def as_setShopDataS(self, data):
        return self.flashObject.as_setShopData(data) if self._isDAAPIInited() else None

    def as_setProgressValueS(self, value, oldValue=-1):
        return self.flashObject.as_setProgressValue(value, oldValue) if self._isDAAPIInited() else None
