# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_page.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR, RANKED_AWARDS_COUNTER, RANKED_INFO_COUNTER, RANKED_SHOP_COUNTER, RANKED_YEAR_RATING_COUNTER, RANKED_AWARDS_BUBBLE_YEAR_REACHED, RANKED_ENTITLEMENT_EVENTS_AMOUNT
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.ranked_battles.ranked_helpers.sound_manager import RANKED_MAIN_PAGE_SOUND_SPACE
from gui.ranked_battles.constants import RankedDossierKeys
from gui.ranked_battles.ranked_builders import main_page_vos
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.RankedBattlesPageMeta import RankedBattlesPageMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import time_utils, dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
_RANKED_BATTLES_VIEW_TO_ITEM_ID = {RANKEDBATTLES_ALIASES.RANKED_BATTLES_LEAGUES_VIEW_UI: RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_DIVISIONS_VIEW_UI: RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_GAP_VIEW_UI: RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_WEB_SEASON_GAP_ALIAS: RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI: RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_SEASON_OFF_ALIAS: RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_SHOP_ALIAS: RANKEDBATTLES_CONSTS.RANKED_BATTLES_SHOP_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_RAITING_ALIAS: RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_INFO_ALIAS: RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_YEAR_RAITING_ALIAS: RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID}
_RANKED_WEB_PAGES = (RANKEDBATTLES_ALIASES.RANKED_BATTLES_WEB_SEASON_GAP_ALIAS,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_SHOP_ALIAS,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_RAITING_ALIAS,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_INFO_ALIAS,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_YEAR_RAITING_ALIAS)

class IResetablePage(object):

    def reset(self):
        raise NotImplementedError


class RankedMainPage(LobbySubView, RankedBattlesPageMeta):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx):
        super(RankedMainPage, self).__init__(ctx)
        self._selectedItemID = RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID
        self._selectedAlias = RANKEDBATTLES_ALIASES.RANKED_BATTLES_LEAGUES_VIEW_UI
        self._processContext(ctx)

    def onClose(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def onPageChanged(self, viewId):
        newSelectedID = _RANKED_BATTLES_VIEW_TO_ITEM_ID.get(viewId, self._selectedItemID)
        isOtherSelected = self._selectedItemID != newSelectedID
        if isOtherSelected or viewId in _RANKED_WEB_PAGES:
            self._selectedItemID = newSelectedID
            self._selectedAlias = viewId
            self._updateSounds()
            self.__resetComponent(viewId)
        if isOtherSelected:
            self._updateHeader()
            self.__resetCounters(newSelectedID)
        self.__rankedController.clearWebOpenPageCtx()

    def _checkOverlayDestroy(self, onClose=False):
        isShopPage = self._selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_SHOP_ID
        isYearLBPage = self._selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID
        isShopEnabled = self.__rankedController.isRankedShopEnabled()
        isYearLBEnabled = self.__rankedController.isYearLBEnabled()
        if onClose or isShopPage and not isShopEnabled or isYearLBPage and not isYearLBEnabled:
            self.__rankedController.onKillWebOverlays()

    def _dispose(self):
        self._updateSounds(True)
        self._checkOverlayDestroy(True)
        self.__rankedController.clearWebOpenPageCtx()
        self.__rankedController.onUpdated -= self._update
        self.__rankedController.onEntitlementEvent -= self.__onEntitlementEvent
        self.__rankedController.onYearPointsChanges -= self.__onYearAwardPointsUpdate
        super(RankedMainPage, self)._dispose()

    def _getSelectedIdx(self, menuItems):
        for idx, item in enumerate(menuItems):
            if item['id'] == self._selectedItemID and item.get('enabled', True):
                return idx

    def _processContext(self, ctx):
        self._selectedItemID = ctx.get('selectedItemID', self._selectedItemID)
        if self._selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID and ctx.get('showedFromWeb', False):
            stateFlags = self.__getShowStateFlags()
            stateFlags['isRankedWelcomeViewShowed'] = True
            self.__setShowStateFlags(stateFlags)

    def _populate(self):
        super(RankedMainPage, self)._populate()
        self.__rankedController.onYearPointsChanges += self.__onYearAwardPointsUpdate
        self.__rankedController.onEntitlementEvent += self.__onEntitlementEvent
        self.__rankedController.onUpdated += self._update
        self.__onYearAwardPointsUpdate()
        self.__onEntitlementEvent()
        self.__resetCounters(self._selectedItemID)
        self._updateSounds()
        self._update()

    def _invalidate(self, ctx=None):
        self._processContext(ctx)
        self.__resetCounters(self._selectedItemID)
        self._updateSounds()
        self._update()
        if _RANKED_BATTLES_VIEW_TO_ITEM_ID.get(self._selectedAlias) == self._selectedItemID:
            self.onPageChanged(self._selectedAlias)

    def _update(self):
        self._checkOverlayDestroy()
        self._updateHeader()
        self._updateMenuItems(self.__rankedController.isRankedShopEnabled(), self.__rankedController.isYearLBEnabled(), self.__rankedController.isYearRewardEnabled(), self.__rankedController.getYearLBSize())

    def _updateHeader(self):
        raise NotImplementedError

    def _updateMenuItems(self, isRankedShopEnabled, isYearLBEnabled, isYearRewardEnabled, yearLBSize):
        raise NotImplementedError

    def _updateSounds(self, onClose=False):
        self.__rankedController.getSoundManager().setAmbient()

    def __getShowStateFlags(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        return self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)

    def __onEntitlementEvent(self):
        currEventsCount = self.__rankedController.getEntitlementEvents()
        oldEventsCount = AccountSettings.getCounters(RANKED_ENTITLEMENT_EVENTS_AMOUNT)
        AccountSettings.setCounters(RANKED_ENTITLEMENT_EVENTS_AMOUNT, currEventsCount)
        if currEventsCount > oldEventsCount:
            AccountSettings.setCounters(RANKED_SHOP_COUNTER, 1)
            self.__resetCounters(self._selectedItemID)
            self.__updateCounters()

    def __onYearAwardPointsUpdate(self):
        if not AccountSettings.getSettings(RANKED_AWARDS_BUBBLE_YEAR_REACHED):
            points = self.__rankedController.getYearRewardPoints()
            for minPoints, maxPoints in self.__rankedController.getYearAwardsPointsMap().itervalues():
                if maxPoints >= points >= minPoints:
                    AccountSettings.setCounters(RANKED_AWARDS_COUNTER, 1)
                    AccountSettings.setSettings(RANKED_AWARDS_BUBBLE_YEAR_REACHED, True)
                    self.__resetCounters(self._selectedItemID)
                    self.__updateCounters()
                    break

    def __resetCounters(self, selectedItemID):
        if selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID:
            if AccountSettings.getCounters(RANKED_AWARDS_COUNTER) > 0:
                AccountSettings.setCounters(RANKED_AWARDS_COUNTER, 0)
        elif selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID:
            AccountSettings.setCounters(RANKED_INFO_COUNTER, 0)
        elif selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID:
            AccountSettings.setCounters(RANKED_YEAR_RATING_COUNTER, 0)
        elif selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_SHOP_ID:
            AccountSettings.setCounters(RANKED_SHOP_COUNTER, 0)
        self.__updateCounters()

    def __resetComponent(self, viewId):
        viewComponent = self.getComponent(viewId)
        if viewComponent is not None:
            viewComponent.reset()
        return

    def __setShowStateFlags(self, filters):
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, filters)

    def __updateCounters(self):
        awardsCounter = main_page_vos.getBubbleLabel(AccountSettings.getCounters(RANKED_AWARDS_COUNTER))
        infoCounter = main_page_vos.getBubbleLabel(AccountSettings.getCounters(RANKED_INFO_COUNTER))
        yearRatingCounter = main_page_vos.getBubbleLabel(AccountSettings.getCounters(RANKED_YEAR_RATING_COUNTER))
        shopCounter = main_page_vos.getBubbleLabel(AccountSettings.getCounters(RANKED_SHOP_COUNTER))
        self.as_setCountersS(main_page_vos.getCountersData(self.__rankedController, awardsCounter, infoCounter, yearRatingCounter, shopCounter))


class RankedMainSeasonOffPage(RankedMainPage):
    _COMMON_SOUND_SPACE = RANKED_MAIN_PAGE_SOUND_SPACE
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, ctx):
        super(RankedMainSeasonOffPage, self).__init__(ctx)
        self.__nextSeason = None
        return

    def _dispose(self):
        self.__rankedController.getSoundManager().onSoundModeChanged(False)
        super(RankedMainSeasonOffPage, self)._dispose()

    def _populate(self):
        super(RankedMainSeasonOffPage, self)._populate()
        self.__rankedController.getSoundManager().onSoundModeChanged(True)

    def _processContext(self, ctx):
        super(RankedMainSeasonOffPage, self)._processContext(ctx)
        self.__prevSeason = ctx['prevSeason']
        self.__achievedRankID = self.__itemsCache.items.getAccountDossier().getSeasonRankedStats(RankedDossierKeys.SEASON % self.__prevSeason.getNumber(), self.__prevSeason.getSeasonID()).getAchievedRank()

    def _update(self):
        self.__checkDestroy()
        self.__nextSeason = self.__rankedController.getNextSeason()
        super(RankedMainSeasonOffPage, self)._update()

    def _updateHeader(self):
        self.as_setHeaderDataS(main_page_vos.getRankedMainSeasonOffHeader(self.__prevSeason, self.__nextSeason, self.__isYearGap(), self._selectedItemID))

    def _updateMenuItems(self, isRankedShopEnabled, isYearLBEnabled, isYearRewardEnabled, yearLBSize):
        menuItems = main_page_vos.getRankedMainSeasonOffItems(isRankedShopEnabled, isYearLBEnabled, isYearRewardEnabled, yearLBSize)
        self.as_setDataS({'menuItems': menuItems,
         'selectedIndex': self._getSelectedIdx(menuItems)})

    def _updateSounds(self, onClose=False):
        super(RankedMainSeasonOffPage, self)._updateSounds()
        soundManager = self.__rankedController.getSoundManager()
        if onClose:
            soundManager.setDefaultProgressSound()
        elif self.__rankedController.getMaxPossibleRank() == self.__achievedRankID or self.__isYearGap():
            soundManager.setProgressSound()
        else:
            soundManager.setProgressSound(self.__rankedController.getDivision(self.__achievedRankID).getUserID())

    def __checkDestroy(self):
        ctrlPrevSeason = self.__rankedController.getPreviousSeason()
        isPrevValid = ctrlPrevSeason is not None and ctrlPrevSeason.getSeasonID() == self.__prevSeason.getSeasonID()
        if not self.__rankedController.isEnabled() or self.__rankedController.getCurrentSeason() or not isPrevValid:
            self.onClose()
        return

    def __isYearGap(self):
        return self.__rankedController.isYearGap()


class RankedMainSeasonOnPage(RankedMainPage):
    _COMMON_SOUND_SPACE = RANKED_MAIN_PAGE_SOUND_SPACE
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx):
        super(RankedMainSeasonOnPage, self).__init__(ctx)
        self.__currentSeason = None
        self.__periodicNotifier = PeriodicNotifier(self.__getTimeTillCurrentSeasonEnd, self._updateHeader)
        return

    def _dispose(self):
        self.__periodicNotifier.stopNotification()
        self.__periodicNotifier.clear()
        super(RankedMainSeasonOnPage, self)._dispose()

    def _populate(self):
        super(RankedMainSeasonOnPage, self)._populate()
        self.__periodicNotifier.startNotification()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI and self.__selectedRewardsItemID is not None:
            viewPy.setActiveTab(self.__selectedRewardsItemID)
            self.__selectedRewardsItemID = None
        return

    def _update(self):
        self.__currentSeason = self.__rankedController.getCurrentSeason()
        self.__periodicNotifier.startNotification()
        super(RankedMainSeasonOnPage, self)._update()

    def _updateHeader(self):
        self.as_setHeaderDataS(main_page_vos.getRankedMainSeasonOnHeader(self.__currentSeason, self._selectedItemID))

    def _updateMenuItems(self, isRankedShopEnabled, isYearLBEnabled, isYearRewardEnabled, yearLBSize):
        isMastered = self.__rankedController.isAccountMastered()
        menuItems = main_page_vos.getRankedMainSeasonOnItems(isRankedShopEnabled, isYearLBEnabled, isYearRewardEnabled, yearLBSize, isMastered)
        self.as_setDataS({'menuItems': menuItems,
         'selectedIndex': self._getSelectedIdx(menuItems)})

    def _updateSounds(self, onClose=False):
        super(RankedMainSeasonOnPage, self)._updateSounds()
        soundManager = self.__rankedController.getSoundManager()
        if self.__rankedController.isAccountMastered():
            soundManager.setProgressSound()
        elif onClose:
            soundManager.setDefaultProgressSound()
        else:
            soundManager.setProgressSound(self.__rankedController.getCurrentDivision().getUserID())

    def _processContext(self, ctx):
        super(RankedMainSeasonOnPage, self)._processContext(ctx)
        self.__selectedRewardsItemID = ctx.get('rewardsSelectedTab', None)
        return

    def __getTimeTillCurrentSeasonEnd(self):
        return time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(self.__currentSeason.getEndDate())) if self.__currentSeason else time_utils.ONE_MINUTE
