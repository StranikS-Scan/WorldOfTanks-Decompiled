# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortIntelFilter.py
from helpers import i18n
from debug_utils import LOG_DEBUG
from constants import FORT_SCOUTING_DATA_FILTER
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortIntelFilterMeta import FortIntelFilterMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import FortEvent
from gui.shared.utils import findFirst

class FortIntelFilter(FortIntelFilterMeta, FortViewHelper):
    FILTER_TYPE_MAPPING = {None: FORT_SCOUTING_DATA_FILTER.DEFAULT,
     FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_ALL: FORT_SCOUTING_DATA_FILTER.FILTER,
     FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_BOOKMARKS: FORT_SCOUTING_DATA_FILTER.ELECT,
     FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_LASTSEARCH: FORT_SCOUTING_DATA_FILTER.RECENT}

    def __init__(self):
        super(FortIntelFilter, self).__init__()
        self.__filterApplied = False
        self.__clanTagApplied = False
        self.__resultsIsEmpty = False

    def _populate(self):
        super(FortIntelFilter, self)._populate()
        self.startFortListening()
        cache = self.fortCtrl.getPublicInfoCache()
        if cache is not None:
            rqIsInCooldown, _ = cache.getRequestCacheCooldownInfo()
            if not rqIsInCooldown:
                self.__resetFilter(True)
        self.as_setDataS(self.__getData())
        self.addListener(FortEvent.ON_INTEL_FILTER_APPLY, self.__onIntelFilterApply, EVENT_BUS_SCOPE.FORT)
        self.addListener(FortEvent.ON_INTEL_FILTER_RESET, self.__onIntelFilterReset, EVENT_BUS_SCOPE.FORT)
        return

    def _dispose(self):
        self.stopFortListening()
        self.removeListener(FortEvent.ON_INTEL_FILTER_APPLY, self.__onIntelFilterApply, EVENT_BUS_SCOPE.FORT)
        self.removeListener(FortEvent.ON_INTEL_FILTER_RESET, self.__onIntelFilterReset, EVENT_BUS_SCOPE.FORT)
        super(FortIntelFilter, self)._dispose()

    def onTryToSearchByClanAbbr(self, tag, searchType):
        self.applySearching(tag, searchType)

    def applySearching(self, tag, searchType):
        filterType = self.FILTER_TYPE_MAPPING[searchType]
        if searchType == FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_ALL:
            if tag != '':
                self.__clanTagApplied = True
            else:
                self.__clanTagApplied = False
                filterType = FORT_SCOUTING_DATA_FILTER.DEFAULT
        self.__applyServerTypedFilter(tag, filterType)

    def onClearClanTagSearch(self):
        self.__resetFilter()

    def onFortPublicInfoReceived(self, hasResults):
        self.__resultsIsEmpty = not hasResults
        self.as_setSearchResultS('Error' if not hasResults else None)
        self.__updateFilterStatuses()
        return

    def onFortPublicInfoValidationError(self, reason):
        self.__resultsIsEmpty = True
        self.as_setSearchResultS('Error')
        self.__updateFilterStatuses()

    def __getSelectedFilterType(self):
        cache = self.fortCtrl.getPublicInfoCache()
        if cache:
            uiMapping = findFirst(lambda k: self.FILTER_TYPE_MAPPING[k] == cache.getFilterType(), self.FILTER_TYPE_MAPPING)
            return uiMapping or FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_ALL

    def __applyServerTypedFilter(self, tag, filterType):
        cache = self.fortCtrl.getPublicInfoCache()
        if cache:
            cache.setAbbrevPattern(tag)
            cache.setFilterType(filterType)
            self.__doCacheRequest(cache)

    def __doCacheRequest(self, cache):
        cache.request()
        self.fireEvent(FortEvent(FortEvent.ON_INTEL_FILTER_DO_REQUEST), EVENT_BUS_SCOPE.FORT)

    def __updateFilterStatuses(self):
        if self.__resultsIsEmpty:
            status = ''
        elif self.__getSelectedFilterType() == FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_ALL:
            if self.__filterApplied and self.__clanTagApplied:
                status = FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_STATUS_APPLIEDFILTERANDCLAN
            elif self.__filterApplied:
                status = FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_STATUS_APPLIEDFILTER
            else:
                status = FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_STATUS_ALL
        elif self.__getSelectedFilterType() == FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_BOOKMARKS:
            status = FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_STATUS_APPLIEDBOOKMARKEDFILTER
        else:
            status = FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_STATUS_APPLIEDLASTFOUNDFILTER
        status = fort_text.getText(fort_text.STANDARD_TEXT, i18n.makeString(status))
        self.as_setFilterStatusS(status)
        self.__setFilterButtonStatus(not self.__filterApplied)

    def __onIntelFilterApply(self, event):
        self.__filterApplied = True
        self.__updateFilterStatuses()

    def __onIntelFilterReset(self, event):
        self.__filterApplied = False
        self.__updateFilterStatuses()

    def __resetFilter(self, isDefaultRequest = False):
        self.__filterApplied = False
        self.__clanTagApplied = False
        self.__resultsIsEmpty = False
        status = fort_text.getText(fort_text.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_STATUS_ALL))
        self.as_setFilterStatusS(status)
        cache = self.fortCtrl.getPublicInfoCache()
        if cache:
            if isDefaultRequest:
                cache.setDefaultRequestFilters()
                self.__doCacheRequest(cache)
                cache.resetFilters()
            else:
                cache.resetFilters()
                self.__doCacheRequest(cache)

    def __getData(self):
        outcome = {'clanTypes': FORTIFICATIONS.FORTINTELLIGENCE_CLANTYPES_ENUM,
         'selectedFilterType': self.__getSelectedFilterType()}
        return outcome

    def __setFilterButtonStatus(self, isMax):
        if isMax:
            status = i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_FILTERBUTTONSTATUS_MAX)
            status = fort_text.getText(fort_text.DISABLE_TEXT, status)
        else:
            status = i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_FILTERBUTTONSTATUS_MIN)
            status = fort_text.getText(fort_text.NEUTRAL_TEXT, status)
        self.as_setFilterButtonStatusS(status, not isMax)
