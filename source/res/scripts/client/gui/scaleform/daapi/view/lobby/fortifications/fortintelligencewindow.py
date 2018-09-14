# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortIntelligenceWindow.py
import BigWorld
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import FortEvent
from helpers import i18n
from constants import FORT_SCOUTING_DATA_FILTER
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.fortifications.components import sorties_dps
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.fort_formatters import getTextLevel
from gui.Scaleform.daapi.view.meta.FortIntelligenceWindowMeta import FortIntelligenceWindowMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS

class FortIntelligenceWindow(FortIntelligenceWindowMeta, FortViewHelper):

    def __init__(self, _ = None):
        super(FortIntelligenceWindow, self).__init__()
        self._searchDP = None
        self.__cooldownCB = None
        self._wasDefaultStatusShown = False
        return

    def onWindowClose(self):
        self.destroy()

    def requestClanFortInfo(self, index):
        vo = self._searchDP.getVO(index)
        if vo is not None:
            cache = self.fortCtrl.getPublicInfoCache()
            if cache is not None and not cache.isRequestInProcess:
                if not cache.setSelectedID(vo['clanID']):
                    cache.clearSelectedID()
                    self._searchDP.refresh()
                else:
                    Waiting.show('fort/card/get')
                    self._searchDP.setSelectedID(vo['clanID'])
        return

    def onFortPublicInfoReceived(self, hasResults):
        cache = self.fortCtrl.getPublicInfoCache()
        if cache is not None:
            cache.clearSelectedID()
            self._searchDP.rebuildList(cache)
            self.__setStatus(hasResults)
            self._wasDefaultStatusShown = True
        self.__updateCooldowns()
        return

    def onFortPublicInfoValidationError(self, reason):
        cache = self.fortCtrl.getPublicInfoCache()
        if cache is not None:
            cache.clearSelectedID()
            cache.clear()
            self._searchDP.rebuildList(cache)
        self.as_setStatusTextS(i18n.makeString('#menu:validation/%s' % reason))
        self.__updateCooldowns()
        return

    def onEnemyClanCardReceived(self, card):
        Waiting.hide('fort/card/get')
        self._searchDP.refresh()

    def onEnemyClanCardRemoved(self):
        Waiting.hide('fort/card/get')
        self.as_selectByIndexS(-1)
        self._searchDP.setSelectedID(None)
        return

    def onFavoritesChanged(self, clanDBID):
        cache = self.fortCtrl.getPublicInfoCache()
        if cache is not None:
            dropSelection = self._searchDP.refreshItem(cache, clanDBID)
            if dropSelection:
                cache.clearSelectedID()
            self._searchDP.refresh()
            self.__setStatus(cache.hasResults())
        return

    def getLevelColumnIcons(self):
        minLevelIcon = getTextLevel(FORTIFICATION_ALIASES.CLAN_FILTER_MIN_LEVEL)
        maxLevelIcon = getTextLevel(FORTIFICATION_ALIASES.CLAN_FILTER_MAX_LEVEL)
        return '%s - %s' % (minLevelIcon, maxLevelIcon)

    def getFilters(self):
        return self.components.get(FORTIFICATION_ALIASES.FORT_INTEL_FILTER_ALIAS)

    def _populate(self):
        super(FortIntelligenceWindow, self)._populate()
        self.startFortListening()
        self._searchDP = sorties_dps.IntelligenceDataProvider()
        self._searchDP.setFlashObject(self.as_getSearchDPS())
        cache = self.fortCtrl.getPublicInfoCache()
        if cache is not None:
            rqIsInCooldown, _ = cache.getRequestCacheCooldownInfo()
            if rqIsInCooldown:
                cache.clearSelectedID()
                self._searchDP.rebuildList(cache)
            self.__setStatus(cache.hasResults())
        self.addListener(FortEvent.ON_INTEL_FILTER_DO_REQUEST, self.__onDoInfoCacheRequest, EVENT_BUS_SCOPE.FORT)
        self._initTable()
        return

    def _initTable(self):
        self.as_setTableHeaderS({'tableHeader': [self._createHeader(self.getLevelColumnIcons(), 'clanLvl', 64, 0, TOOLTIPS.FORTIFICATION_INTELLIGENCEWINDOW_SORTBTN_LEVEL),
                         self._createHeader(FORTIFICATIONS.FORTINTELLIGENCE_SORTBTNS_CLANTAG, 'clanTag', 132, 1, TOOLTIPS.FORTIFICATION_INTELLIGENCEWINDOW_SORTBTN_CLANTAG),
                         self._createHeader(FORTIFICATIONS.FORTINTELLIGENCE_SORTBTNS_DEFENCETIME, 'defenceStartTime', 203, 2, TOOLTIPS.FORTIFICATION_INTELLIGENCEWINDOW_SORTBTN_DEFENCETIME),
                         self._createHeader(FORTIFICATIONS.FORTINTELLIGENCE_SORTBTNS_BUILDINGS, 'avgBuildingLvl', 195, 3, TOOLTIPS.FORTIFICATION_INTELLIGENCEWINDOW_SORTBTN_BUILDINGS)]})

    def _createHeader(self, label, iconId, buttonWidth, sortOrder, toolTip):
        return {'label': label,
         'sortOrder': sortOrder,
         'buttonWidth': buttonWidth,
         'toolTip': toolTip,
         'id': iconId}

    def _dispose(self):
        self.removeListener(FortEvent.ON_INTEL_FILTER_DO_REQUEST, self.__onDoInfoCacheRequest, EVENT_BUS_SCOPE.FORT)
        self.__clearCooldownCB()
        if self._searchDP is not None:
            self._searchDP.fini()
            self._searchDP = None
        self.stopFortListening()
        super(FortIntelligenceWindow, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(FortIntelligenceWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == FORTIFICATION_ALIASES.FORT_INTEL_FILTER_ALIAS:
            self.__updateCooldowns()

    def __onDoInfoCacheRequest(self, event):
        self.__updateCooldowns()

    def __updateCooldowns(self):
        cache = self.fortCtrl.getPublicInfoCache()
        if cache:
            isInProcess, timeLeft = cache.getRequestCacheCooldownInfo()
            self.__setCooldownComponents(isInProcess)
            self.__loadCooldownUnlockTimer(timeLeft)

    def __cooldownUnlockHandler(self):
        self.__clearCooldownCB()
        self.__setCooldownComponents(False)

    def __loadCooldownUnlockTimer(self, timeLeft):
        self.__clearCooldownCB()
        self.__cooldownCB = BigWorld.callback(max(timeLeft, 0), self.__cooldownUnlockHandler)

    def __clearCooldownCB(self):
        if self.__cooldownCB is not None:
            BigWorld.cancelCallback(self.__cooldownCB)
            self.__cooldownCB = None
        return

    def __setCooldownComponents(self, isInProcess):
        filters = self.getFilters()
        if filters:
            filters.as_setupCooldownS(isInProcess)

    def __setStatus(self, hasResults):
        cache = self.fortCtrl.getPublicInfoCache()
        if cache is not None and not hasResults:
            status = FORTIFICATIONS.FORTINTELLIGENCE_STATUS_EMPTY
            if cache:
                if cache.getFilterType() == FORT_SCOUTING_DATA_FILTER.RECENT:
                    status = FORTIFICATIONS.FORTINTELLIGENCE_STATUS_EMPTYRECENT
                elif cache.getFilterType() == FORT_SCOUTING_DATA_FILTER.ELECT:
                    status = FORTIFICATIONS.FORTINTELLIGENCE_STATUS_EMPTYFAVORITE
                elif cache.getFilterType() == FORT_SCOUTING_DATA_FILTER.FILTER:
                    status = FORTIFICATIONS.FORTINTELLIGENCE_STATUS_EMPTYABBREV
            if not self._wasDefaultStatusShown and status == FORTIFICATIONS.FORTINTELLIGENCE_STATUS_EMPTY:
                status = FORTIFICATIONS.FORTINTELLIGENCE_STATUS_DEFAULTREQUEST_EMPTY
            self.as_setStatusTextS(status)
        return
