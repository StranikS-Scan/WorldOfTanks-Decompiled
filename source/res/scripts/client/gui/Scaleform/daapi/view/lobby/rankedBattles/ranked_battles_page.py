# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_page.py
import BigWorld
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR, RANKED_AWARDS_COUNTER, RANKED_INFO_COUNTER, RANKED_AWARDS_BUBBLE_WAS_SHOWN
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_helpers.sound_manager import RANKED_MAIN_PAGE_SOUND_SPACE
from gui.ranked_battles.constants import YEAR_AWARDS_POINTS_MAP
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.RankedBattlesPageMeta import RankedBattlesPageMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils.functions import makeTooltip
from helpers import time_utils, dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IRankedBattlesController
_RANKED_BATTLES_VIEW_TO_ITEM_ID = {RANKEDBATTLES_ALIASES.RANKED_BATTLES_LEAGUES_VIEW_UI: RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_DIVISIONS_VIEW_UI: RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI: RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_RAITING_ALIAS: RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_INFO_ALIAS: RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID}

def _getBubbleLabel(settingsKey):
    counter = AccountSettings.getCounters(settingsKey)
    return '' if not bool(counter) else backport.text(R.strings.ranked_battles.rankedBattleMainView.emptyBubble())


class IResetablePage(object):

    def reset(self):
        raise NotImplementedError


class RankedBattlesPage(LobbySubView, RankedBattlesPageMeta):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    _COMMON_SOUND_SPACE = RANKED_MAIN_PAGE_SOUND_SPACE

    def __init__(self, ctx):
        super(RankedBattlesPage, self).__init__(ctx)
        self.__rewardsSelectedTab = None
        self.__selectedItemID = RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID
        self.__processContext(ctx)
        self.__updateStateFlags()
        return

    def onClose(self):
        soundManager = self.__rankedController.getSoundManager()
        if self.__rankedController.isAccountMastered():
            soundManager.setProgressSound()
        else:
            soundManager.setDefaultProgressSound()
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def onPageChanged(self, viewId):
        newSelectedID = _RANKED_BATTLES_VIEW_TO_ITEM_ID.get(viewId, self.__selectedItemID)
        if self.__selectedItemID != newSelectedID:
            self.__selectedItemID = newSelectedID
            viewComponent = self.getComponent(viewId)
            if viewComponent is not None:
                viewComponent.reset()
            self.__update()
            self.__resetCounter(newSelectedID)
        return

    def _populate(self):
        super(RankedBattlesPage, self)._populate()
        self.__rankedController.onYearPointsChanges += self.__onYearAwardPointsUpdate
        self.__rankedController.onUpdated += self.__update
        self.__onYearAwardPointsUpdate()
        self.__updateCounters()
        self.__update()

    def _dispose(self):
        self.__rankedController.onYearPointsChanges -= self.__onYearAwardPointsUpdate
        self.__rankedController.onUpdated -= self.__update
        super(RankedBattlesPage, self)._dispose()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI and self.__rewardsSelectedTab is not None:
            viewPy.setActiveTab(self.__rewardsSelectedTab)
            self.__rewardsSelectedTab = None
        return

    def __getSelectedIdx(self, menuItems):
        for idx, item in enumerate(menuItems):
            if item['id'] == self.__selectedItemID:
                return idx

    def __onYearAwardPointsUpdate(self):
        wasShown = AccountSettings.getSettings(RANKED_AWARDS_BUBBLE_WAS_SHOWN)
        if AccountSettings.getCounters(RANKED_AWARDS_COUNTER) == 0 and not wasShown:
            points = self.__rankedController.getYearRewardPoints()
            for minPoints, maxPoints in YEAR_AWARDS_POINTS_MAP.itervalues():
                if maxPoints >= points >= minPoints:
                    AccountSettings.setCounters(RANKED_AWARDS_COUNTER, 1)
                    self.__updateCounters()
                    return

    def __processContext(self, ctx=None):
        if ctx is not None:
            self.__selectedItemID = ctx.get('selectedItemID', self.__selectedItemID)
            self.__rewardsSelectedTab = ctx.get('rewardsSelectedTab')
            self.__showedFromWeb = ctx.get('showedFromWeb', False)
            self.__resetCounter(self.__selectedItemID)
        return

    def __resetCounter(self, itemId):
        if itemId == RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID:
            if AccountSettings.getCounters(RANKED_AWARDS_COUNTER) > 0:
                AccountSettings.setCounters(RANKED_AWARDS_COUNTER, 0)
                AccountSettings.setSettings(RANKED_AWARDS_BUBBLE_WAS_SHOWN, True)
        elif itemId == RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID:
            AccountSettings.setCounters(RANKED_INFO_COUNTER, 0)
        self.__updateCounters()

    def __update(self):
        self.__updateHeader()
        self.__updateMenuItems()
        self.__updateSound()

    def __updateCounters(self):
        awardsCounter = _getBubbleLabel(RANKED_AWARDS_COUNTER)
        infoCounter = _getBubbleLabel(RANKED_INFO_COUNTER)
        countersData = [{'componentId': RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
          'count': awardsCounter}, {'componentId': RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID,
          'count': infoCounter}]
        self.as_setCountersS(countersData)

    def __updateHeader(self):
        currentSeason = self.__rankedController.getCurrentSeason()
        leftSideText = ''
        rightSideText = ''
        tooltip = TOOLTIPS_CONSTANTS.RANKED_CALENDAR_DAY_INFO
        if self.__selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID:
            leftSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.infoPage.header())
            tooltip = ''
        elif currentSeason is not None:
            startDate = currentSeason.getStartDate()
            endDate = currentSeason.getEndDate()
            timeDelta = time_utils.getTimeDeltaFromNow(endDate)
            if timeDelta > time_utils.ONE_WEEK:
                leftSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.date.period(), start=BigWorld.wg_getLongDateFormat(startDate), finish=BigWorld.wg_getLongDateFormat(endDate))
            else:
                leftSideText = backport.getTillTimeStringByRClass(timeDelta, R.strings.ranked_battles.rankedBattleMainView.date)
            rightSideText = backport.text(R.strings.ranked_battles.rankedBattleMainView.season(), season=currentSeason.getUserName())
        self.as_setHeaderDataS({'title': backport.text(R.strings.ranked_battles.rankedBattle.title()),
         'leftSideText': leftSideText,
         'rightSideText': rightSideText,
         'tooltip': tooltip})
        return

    def __updateMenuItems(self):
        if self.__rankedController.isAccountMastered():
            mainMenuLinkage = RANKEDBATTLES_ALIASES.RANKED_BATTLES_LEAGUES_VIEW_UI
        else:
            mainMenuLinkage = RANKEDBATTLES_ALIASES.RANKED_BATTLES_DIVISIONS_VIEW_UI
        menuItems = [{'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
          'viewId': mainMenuLinkage,
          'linkage': mainMenuLinkage,
          'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
          'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.ranks.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.ranks.body()))},
         {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
          'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI,
          'linkage': RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI,
          'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
          'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.rewards.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.rewards.body()))},
         {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID,
          'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_RAITING_ALIAS,
          'linkage': 'BrowserViewStackExPaddingUI',
          'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.main()),
          'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.rating.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.rating.body()))},
         {'id': RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID,
          'viewId': RANKEDBATTLES_ALIASES.RANKED_BATTLES_INFO_ALIAS,
          'linkage': 'BrowserViewStackExPaddingUI',
          'background': backport.image(R.images.gui.maps.icons.rankedBattles.bg.rewards()),
          'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.rankedBattlesView.info.header()), body=backport.text(R.strings.tooltips.rankedBattlesView.info.body()))}]
        self.as_setDataS({'menuItems': menuItems,
         'selectedIndex': self.__getSelectedIdx(menuItems)})

    def __updateSound(self):
        soundManager = self.__rankedController.getSoundManager()
        if self.__rankedController.isAccountMastered():
            soundManager.setProgressSound()
        else:
            soundManager.setProgressSound(self.__rankedController.getCurrentDivision().getUserID())

    def __updateStateFlags(self):
        if self.__selectedItemID == RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID and self.__showedFromWeb:
            stateFlags = self.__getShowStateFlags()
            stateFlags['isRankedWelcomeViewShowed'] = True
            self.__setShowStateFlags(stateFlags)

    def __getShowStateFlags(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        return self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)

    def __setShowStateFlags(self, filters):
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, filters)
