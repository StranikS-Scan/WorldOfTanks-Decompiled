# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BadgesPageMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class BadgesPageMeta(WrapperViewMeta):

    def onBackClick(self):
        self._printOverrideError('onBackClick')

    def onSelectBadge(self, badgeID):
        self._printOverrideError('onSelectBadge')

    def onDeselectBadge(self):
        self._printOverrideError('onDeselectBadge')

    def onSelectSuffixBadge(self, badgeID):
        self._printOverrideError('onSelectSuffixBadge')

    def onDeselectSuffixBadge(self):
        self._printOverrideError('onDeselectSuffixBadge')

    def onDummyButtonPress(self):
        self._printOverrideError('onDummyButtonPress')

    def as_setStaticDataS(self, data):
        return self.flashObject.as_setStaticData(data) if self._isDAAPIInited() else None

    def as_setReceivedBadgesS(self, data):
        return self.flashObject.as_setReceivedBadges(data) if self._isDAAPIInited() else None

    def as_setNotReceivedBadgesS(self, data):
        return self.flashObject.as_setNotReceivedBadges(data) if self._isDAAPIInited() else None

    def as_setSelectedBadgeS(self, data, selected):
        return self.flashObject.as_setSelectedBadge(data, selected) if self._isDAAPIInited() else None

    def as_setBadgeSuffixS(self, data):
        return self.flashObject.as_setBadgeSuffix(data) if self._isDAAPIInited() else None
