# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ChannelCarouselMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ChannelCarouselMeta(DAAPIModule):

    def channelOpenClick(self, itemID):
        self._printOverrideError('channelOpenClick')

    def minimizeAllChannels(self):
        self._printOverrideError('minimizeAllChannels')

    def closeAll(self):
        self._printOverrideError('closeAll')

    def closeAllExceptCurrent(self, itemID):
        self._printOverrideError('closeAllExceptCurrent')

    def channelCloseClick(self, itemID):
        self._printOverrideError('channelCloseClick')

    def as_getDataProviderS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getDataProvider()

    def as_getBattlesDataProviderS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getBattlesDataProvider()
