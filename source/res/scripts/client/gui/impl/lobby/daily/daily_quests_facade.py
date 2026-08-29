# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_quests_facade.py
from frameworks.wulf import Array
from constants import ARENA_BONUS_TYPE
from gui.impl.gen import R
from gui.impl.lobby.daily import DailyTabs
from gui.impl.lobby.daily.daily_quests_subview import DailyQuestsSubview
from gui.impl.lobby.daily.daily_quests_tab_view import DailyQuestTabView, DailyQuestPremTabView
from gui.impl.lobby.daily.tooltips.mode_selector_tooltip import ModeSelectorTooltip
from gui.server_events.events_helpers import isDailyRegularQuestsEnabled
from skeletons.gui.game_control import IFunRandomController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from helpers import dependency
DAILY_LAYOUT_ID = R.views.lobby.daily.DailyQuestsRegularView()
DAILY_TAB_REGULAR_LAYOUT_ID = R.views.lobby.daily.DailyQuestRegularTabView()
DAILY_TAB_PREMIUM_LAYOUT_ID = R.views.lobby.daily.DailyQuestPremiumTabView()

class DailyQuestsFacade(object):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    __funRandomController = dependency.descriptor(IFunRandomController)
    __slots__ = ('__dailySubView', '__tabs', '__tabsToSubview', '__battleTypes')

    def __init__(self, parentView, *args, **kwargs):
        self.__dailySubView = DailyQuestsSubview(parentView, DAILY_LAYOUT_ID)
        self.__tabsToSubview = {DailyTabs.QUESTS: (self.__dailySubView, DAILY_LAYOUT_ID),
         DailyTabs.PREMIUM: (self.__dailySubView, DAILY_LAYOUT_ID)}
        self.__tabs = {DailyTabs.QUESTS: (DailyQuestTabView(), DAILY_TAB_REGULAR_LAYOUT_ID),
         DailyTabs.PREMIUM: (DailyQuestPremTabView(), DAILY_TAB_PREMIUM_LAYOUT_ID)}
        self.__battleTypes = None
        return

    def finalize(self):
        self.__tabs.clear()
        self.__tabsToSubview.clear()

    def getTabs(self):
        return self.__tabs

    def getSubviews(self):
        return self.__tabsToSubview

    def getUnseenQuests(self):
        return self.__dailySubView.viewModel.unseenQuests

    def getToolTipContent(self, event, contentID):
        return ModeSelectorTooltip(event.contentID, self.__battleTypes) if event.contentID == R.views.lobby.daily.tooltips.ModeSelectorTooltip() else None

    def updateBattleModes(self, battleModes):
        battleModes.clear()
        if isDailyRegularQuestsEnabled():
            quests = self.eventsCache.getDailyQuests().values()
        else:
            quests = self.eventsCache.getDailyPremiumQuests().values()
        bonusTypes = quests[0].preBattleCond.getConditions().find('bonusTypes').getValue() if quests else []
        self.__extendBonusTypes(bonusTypes)
        for bonusType in bonusTypes:
            battleModes.addString(str(bonusType))

        self.__battleTypes = battleModes
        battleModes.invalidate()

    def __extendBonusTypes(self, bonusTypes):
        if ARENA_BONUS_TYPE.FUN_RANDOM in bonusTypes:
            oldIDx = bonusTypes.index(ARENA_BONUS_TYPE.FUN_RANDOM)
            bonusTypes.pop(oldIDx)
            bonusTypes.insert(oldIDx, int(str(ARENA_BONUS_TYPE.FUN_RANDOM) + str(self.__funRandomController.getCurrentFunType())))
