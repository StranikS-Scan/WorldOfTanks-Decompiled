# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelFilterMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortIntelFilterMeta(BaseDAAPIComponent):

    def onTryToSearchByClanAbbr(self, tag, searchType):
        self._printOverrideError('onTryToSearchByClanAbbr')

    def onClearClanTagSearch(self):
        self._printOverrideError('onClearClanTagSearch')

    def as_setDataS(self, data):
        """
        :param data: Represented by FortIntelFilterVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setMaxClanAbbreviateLengthS(self, length):
        return self.flashObject.as_setMaxClanAbbreviateLength(length) if self._isDAAPIInited() else None

    def as_setSearchResultS(self, status):
        return self.flashObject.as_setSearchResult(status) if self._isDAAPIInited() else None

    def as_setFilterStatusS(self, filterStatus):
        return self.flashObject.as_setFilterStatus(filterStatus) if self._isDAAPIInited() else None

    def as_setFilterButtonStatusS(self, filterButtonStatus, showEffect):
        return self.flashObject.as_setFilterButtonStatus(filterButtonStatus, showEffect) if self._isDAAPIInited() else None

    def as_setupCooldownS(self, isOnCooldown):
        return self.flashObject.as_setupCooldown(isOnCooldown) if self._isDAAPIInited() else None

    def as_setClanAbbrevS(self, clanAbbrev):
        return self.flashObject.as_setClanAbbrev(clanAbbrev) if self._isDAAPIInited() else None
