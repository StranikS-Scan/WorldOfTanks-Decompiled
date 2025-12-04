# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_quests_facade.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.lobby.daily import DailyTabs, NYTabs
from gui.impl.lobby.daily.daily_quests_subview import DailyQuestsSubview
from gui.impl.lobby.daily.daily_quests_tab_view import DailyQuestTabView, DailyQuestPremTabView
from gui.impl.lobby.daily.ny_quests_tab_view import NYQuestTabView
from gui.impl.lobby.daily.tooltips.mode_selector_tooltip import ModeSelectorTooltip
from gui.server_events.events_helpers import isDailyRegularQuestsEnabled
from shared_utils import findFirst
from new_year_common.items.components.ny_constants import CurrentNYConstants
from new_year.gui.impl.lobby.new_year.tooltips.ny_currency_tooltip import NyCurrencyTooltip
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from helpers import dependency
DAILY_LAYOUT_ID = R.views.lobby.daily.DailyQuestsRegularView()
DAILY_TAB_REGULAR_LAYOUT_ID = R.views.lobby.daily.DailyQuestRegularTabView()
DAILY_TAB_PREMIUM_LAYOUT_ID = R.views.lobby.daily.DailyQuestPremiumTabView()
NY_TAB_LAYOUT_ID = R.views.lobby.daily.NyQuestsTabView()

class DailyQuestsFacade(object):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__dailySubView', '__tabs', '__tabsToSubview', '__battleTypes', '__nyBattleTypes')

    def __init__(self, parentView, *args, **kwargs):
        self.__dailySubView = DailyQuestsSubview(parentView, DAILY_LAYOUT_ID)
        self.__tabsToSubview = {DailyTabs.QUESTS: (self.__dailySubView, DAILY_LAYOUT_ID),
         DailyTabs.PREMIUM: (self.__dailySubView, DAILY_LAYOUT_ID)}
        self.__tabs = {DailyTabs.QUESTS: (DailyQuestTabView(), DAILY_TAB_REGULAR_LAYOUT_ID),
         DailyTabs.PREMIUM: (DailyQuestPremTabView(), DAILY_TAB_PREMIUM_LAYOUT_ID),
         NYTabs.DAILY: (NYQuestTabView(), NY_TAB_LAYOUT_ID)}
        self.__battleTypes = None
        self.__nyBattleTypes = None
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
        if event.contentID == R.views.lobby.daily.tooltips.ModeSelectorTooltip():
            if event.getArgument('isInNy'):
                return ModeSelectorTooltip(event.contentID, self.__nyBattleTypes)
            return ModeSelectorTooltip(event.contentID, self.__battleTypes)
        else:
            return NyCurrencyTooltip(NyCurrencyType.NYGIFTMACHINETOKEN) if contentID == R.views.new_year.lobby.new_year.tooltips.NyCurrencyTooltip() else None

    def updateBattleModes(self, battleModes):
        battleModes.clear()
        if isDailyRegularQuestsEnabled():
            quests = self.eventsCache.getDailyQuests().values()
        else:
            quests = self.eventsCache.getDailyPremiumQuests().values()
        bonusTypes = quests[0].preBattleCond.getConditions().find('bonusTypes').getValue() if quests else []
        for bonusType in bonusTypes:
            battleModes.addString(str(bonusType))

        self.__battleTypes = battleModes
        battleModes.invalidate()

    def updateNyBattleModes(self, battleModes):
        battleModes.clear()
        allQuests = sorted(self.eventsCache.getAllQuests().iteritems())
        _, nyQuest = findFirst(lambda (questID, quest): questID.startswith(CurrentNYConstants.NY_DAILY_QUESTS_PREFIX), allQuests, ('', None))
        if nyQuest is not None:
            bonusTypes = nyQuest.preBattleCond.getConditions().find('bonusTypes').getValue()
            for bonusType in bonusTypes:
                battleModes.addString(str(bonusType))

            self.__nyBattleTypes = battleModes
            battleModes.invalidate()
        return
