# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventShopTabMeta.py
from gui.Scaleform.framework.entities.View import View

class EventShopTabMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def onItemsBannerClick(self):
        self._printOverrideError('onItemsBannerClick')

    def onMainBannerClick(self):
        self._printOverrideError('onMainBannerClick')

    def onPackBannerClick(self, id):
        self._printOverrideError('onPackBannerClick')

    def as_setPackBannersDataS(self, dataPack1, dataPack2):
        return self.flashObject.as_setPackBannersData(dataPack1, dataPack2) if self._isDAAPIInited() else None

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None

    def as_setExpireDateS(self, value):
        return self.flashObject.as_setExpireDate(value) if self._isDAAPIInited() else None
