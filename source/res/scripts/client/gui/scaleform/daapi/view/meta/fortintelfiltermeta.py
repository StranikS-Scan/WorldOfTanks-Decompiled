# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelFilterMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortIntelFilterMeta(BaseDAAPIComponent):

    def onTryToSearchByClanAbbr(self, tag, searchType):
        self._printOverrideError('onTryToSearchByClanAbbr')

    def onClearClanTagSearch(self):
        self._printOverrideError('onClearClanTagSearch')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_setMaxClanAbbreviateLengthS(self, length):
        if self._isDAAPIInited():
            return self.flashObject.as_setMaxClanAbbreviateLength(length)

    def as_setSearchResultS(self, status):
        if self._isDAAPIInited():
            return self.flashObject.as_setSearchResult(status)

    def as_setFilterStatusS(self, filterStatus):
        if self._isDAAPIInited():
            return self.flashObject.as_setFilterStatus(filterStatus)

    def as_setFilterButtonStatusS(self, filterButtonStatus, showEffect):
        if self._isDAAPIInited():
            return self.flashObject.as_setFilterButtonStatus(filterButtonStatus, showEffect)

    def as_setupCooldownS(self, isOnCooldown):
        if self._isDAAPIInited():
            return self.flashObject.as_setupCooldown(isOnCooldown)

    def as_setClanAbbrevS(self, clanAbbrev):
        if self._isDAAPIInited():
            return self.flashObject.as_setClanAbbrev(clanAbbrev)
