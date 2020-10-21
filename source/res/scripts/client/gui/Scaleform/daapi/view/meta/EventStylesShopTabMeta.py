# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventStylesShopTabMeta.py
from gui.Scaleform.framework.entities.View import View

class EventStylesShopTabMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def onTankClick(self, index):
        self._printOverrideError('onTankClick')

    def onBannerClick(self, index):
        self._printOverrideError('onBannerClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None
