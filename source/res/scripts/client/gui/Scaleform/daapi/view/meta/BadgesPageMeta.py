# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BadgesPageMeta.py
from gui.Scaleform.framework.entities.View import View

class BadgesPageMeta(View):

    def onCloseView(self):
        self._printOverrideError('onCloseView')

    def onSelectBadge(self, badgeID):
        self._printOverrideError('onSelectBadge')

    def onDummyButtonPress(self):
        self._printOverrideError('onDummyButtonPress')

    def as_setStaticDataS(self, data):
        """
        :param data: Represented by BadgesStaticDataVO (AS)
        """
        return self.flashObject.as_setStaticData(data) if self._isDAAPIInited() else None

    def as_setReceivedBadgesS(self, data):
        """
        :param data: Represented by BadgesGroupVO (AS)
        """
        return self.flashObject.as_setReceivedBadges(data) if self._isDAAPIInited() else None

    def as_setNotReceivedBadgesS(self, data):
        """
        :param data: Represented by BadgesGroupVO (AS)
        """
        return self.flashObject.as_setNotReceivedBadges(data) if self._isDAAPIInited() else None

    def as_setSelectedBadgeImgS(self, value):
        return self.flashObject.as_setSelectedBadgeImg(value) if self._isDAAPIInited() else None
