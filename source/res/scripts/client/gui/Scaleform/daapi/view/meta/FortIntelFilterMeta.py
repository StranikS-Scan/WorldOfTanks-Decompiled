# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelFilterMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortIntelFilterMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def onTryToSearchByClanAbbr(self, tag, searchType):
        """
        :param tag:
        :param searchType:
        :return String:
        """
        self._printOverrideError('onTryToSearchByClanAbbr')

    def onClearClanTagSearch(self):
        """
        :return :
        """
        self._printOverrideError('onClearClanTagSearch')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setMaxClanAbbreviateLengthS(self, length):
        """
        :param length:
        :return :
        """
        return self.flashObject.as_setMaxClanAbbreviateLength(length) if self._isDAAPIInited() else None

    def as_setSearchResultS(self, status):
        """
        :param status:
        :return :
        """
        return self.flashObject.as_setSearchResult(status) if self._isDAAPIInited() else None

    def as_setFilterStatusS(self, filterStatus):
        """
        :param filterStatus:
        :return :
        """
        return self.flashObject.as_setFilterStatus(filterStatus) if self._isDAAPIInited() else None

    def as_setFilterButtonStatusS(self, filterButtonStatus, showEffect):
        """
        :param filterButtonStatus:
        :param showEffect:
        :return :
        """
        return self.flashObject.as_setFilterButtonStatus(filterButtonStatus, showEffect) if self._isDAAPIInited() else None

    def as_setupCooldownS(self, isOnCooldown):
        """
        :param isOnCooldown:
        :return :
        """
        return self.flashObject.as_setupCooldown(isOnCooldown) if self._isDAAPIInited() else None

    def as_setClanAbbrevS(self, clanAbbrev):
        """
        :param clanAbbrev:
        :return :
        """
        return self.flashObject.as_setClanAbbrev(clanAbbrev) if self._isDAAPIInited() else None
