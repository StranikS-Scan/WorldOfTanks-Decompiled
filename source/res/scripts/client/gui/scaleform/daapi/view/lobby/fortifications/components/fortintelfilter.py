# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortIntelFilter.py
import constants
from gui.shared.formatters import text_styles
from helpers import i18n
from constants import FORT_SCOUTING_DATA_FILTER
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortIntelFilterMeta import FortIntelFilterMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import FortEvent
from shared_utils import findFirst

class FortIntelFilter(FortIntelFilterMeta, FortViewHelper):
    FILTER_TYPE_MAPPING = {None: FORT_SCOUTING_DATA_FILTER.DEFAULT,
     FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_ALL: FORT_SCOUTING_DATA_FILTER.FILTER,
     FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_BOOKMARKS: FORT_SCOUTING_DATA_FILTER.ELECT,
     FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_LASTSEARCH: FORT_SCOUTING_DATA_FILTER.RECENT}

    def onTryToSearchByClanAbbr(self, tag, searchType):
        self.applySearching(tag, searchType)

    def applySearching(self, tag, searchType):
        filterType = self.FILTER_TYPE_MAPPING[searchType]
        if searchType == FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_ALL:
            if not tag:
                filterType = FORT_SCOUTING_DATA_FILTER.DEFAULT
        self.__applyServerTypedFilter(tag, filterType)

    def onClearClanTagSearch(self):
        cache = self.fortCtrl.getPublicInfoCache()
        if cache:
            cache.resetClanAbbrev()
            self.__doCacheRequest(cache)

    def onFortPublicInfoReceived(self, hasResults):
        self.as_setSearchResultS('Error' if not hasResults else None)
        self.__updateFilterStatuses()
        return

    def onFortPublicInfoValidationError(self, reason):
        self.as_setSearchResultS('Error')
        self.__updateFilterStatuses()

    def _populate(self):
        super(FortIntelFilter, self)._populate()
        self.startFortListening()
        cache = self.fortCtrl.getPublicInfoCache()
        if cache is not None:
            rqIsInCooldown, _ = cache.getRequestCacheCooldownInfo()
            if not rqIsInCooldown:
                self.__resetFilter(True)
        self.__updateFilterStatuses()
        self.as_setDataS(self.__getData())
        self.addListener(FortEvent.ON_INTEL_FILTER_APPLY, self.__onIntelFilterApply, EVENT_BUS_SCOPE.FORT)
        self.addListener(FortEvent.ON_INTEL_FILTER_RESET, self.__onIntelFilterReset, EVENT_BUS_SCOPE.FORT)
        return

    def _dispose(self):
        self.stopFortListening()
        self.removeListener(FortEvent.ON_INTEL_FILTER_APPLY, self.__onIntelFilterApply, EVENT_BUS_SCOPE.FORT)
        self.removeListener(FortEvent.ON_INTEL_FILTER_RESET, self.__onIntelFilterReset, EVENT_BUS_SCOPE.FORT)
        super(FortIntelFilter, self)._dispose()

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
        cache = self.fortCtrl.getPublicInfoCache()
        if cache:
            status = ''
            if cache.hasResults():
                if self.__getSelectedFilterType() == FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_ALL:
                    if cache.getFilterType() == FORT_SCOUTING_DATA_FILTER.FILTER and cache.isFilterApplied():
                        status = FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_STATUS_APPLIEDFILTERANDCLAN
                    elif cache.isFilterApplied():
                        status = FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_STATUS_APPLIEDFILTER
                    elif cache.ifDefaultQueryResult():
                        status = FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_STATUS_ALL
                elif self.__getSelectedFilterType() == FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_BOOKMARKS:
                    status = FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_STATUS_APPLIEDBOOKMARKEDFILTER
                elif self.__getSelectedFilterType() == FORTIFICATION_ALIASES.CLAN_TYPE_FILTER_STATE_LASTSEARCH:
                    status = FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_STATUS_APPLIEDLASTFOUNDFILTER
            self.as_setClanAbbrevS(cache.getAbbrevPattern())
            status = text_styles.standard(i18n.makeString(status))
            self.as_setFilterStatusS(status)
            self.__setFilterButtonStatus(not cache.isFilterApplied())

    def __onIntelFilterApply(self, event):
        self.__updateFilterStatuses()

    def __onIntelFilterReset(self, event):
        self.__updateFilterStatuses()

    def __resetFilter(self, isDefaultRequest = False):
        cache = self.fortCtrl.getPublicInfoCache()
        if cache:
            if isDefaultRequest:
                cache.setDefaultRequestFilters()
                self.__doCacheRequest(cache)
                cache.reset()
            else:
                cache.reset()
                self.__doCacheRequest(cache)

    def __getData(self):
        tooltipI18nKeyPrefix = '#tooltips:fortification/intelligenceWindow/tagSearchTextInput'
        if constants.IS_CHINA:
            tooltipI18nKeyPrefix += '/CN'
        elif constants.IS_KOREA:
            tooltipI18nKeyPrefix += '/KR'
        return {'clanTypes': FORTIFICATIONS.FORTINTELLIGENCE_CLANTYPES_ENUM,
         'selectedFilterType': self.__getSelectedFilterType(),
         'tagTooltip': tooltipI18nKeyPrefix}

    def __setFilterButtonStatus(self, isMax):
        if isMax:
            status = i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_FILTERBUTTONSTATUS_MAX)
            status = text_styles.disabled(status)
        else:
            status = i18n.makeString(FORTIFICATIONS.FORTINTELLIGENCE_FORTINTELFILTER_FILTERBUTTONSTATUS_MIN)
            status = text_styles.neutral(status)
        self.as_setFilterButtonStatusS(status, not isMax)
