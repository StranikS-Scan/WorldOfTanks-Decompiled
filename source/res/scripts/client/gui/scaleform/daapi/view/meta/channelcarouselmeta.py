# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ChannelCarouselMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ChannelCarouselMeta(BaseDAAPIComponent):

    def channelOpenClick(self, itemID):
        self._printOverrideError('channelOpenClick')

    def closeAll(self):
        self._printOverrideError('closeAll')

    def channelCloseClick(self, itemID):
        self._printOverrideError('channelCloseClick')

    def as_getDataProviderS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getDataProvider()

    def as_getBattlesDataProviderS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getBattlesDataProvider()
