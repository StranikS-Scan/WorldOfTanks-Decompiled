# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventStylesTradeMeta.py
from gui.Scaleform.framework.entities.View import View

class EventStylesTradeMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def onBackClick(self):
        self._printOverrideError('onBackClick')

    def onBuyClick(self):
        self._printOverrideError('onBuyClick')

    def onUseClick(self):
        self._printOverrideError('onUseClick')

    def showBlur(self):
        self._printOverrideError('showBlur')

    def hideBlur(self):
        self._printOverrideError('hideBlur')

    def onBannerClick(self, index):
        self._printOverrideError('onBannerClick')

    def onSelect(self, index):
        self._printOverrideError('onSelect')

    def onBundleClick(self):
        self._printOverrideError('onBundleClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_getDataProviderS(self):
        return self.flashObject.as_getDataProvider() if self._isDAAPIInited() else None

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None
