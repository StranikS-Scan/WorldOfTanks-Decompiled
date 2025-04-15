# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/play_streak/play_streak_facade.py
from constants import ARENA_GUI_TYPE_LABEL
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_view_model import DailyQuestsViewModel, DailyTabs
from gui.impl.lobby.play_streak.play_streak_subview import PlayStreakSubView
from gui.impl.lobby.play_streak.play_streak_tab_view import PlayStreakTabView
from gui.impl.lobby.daily.tooltips.mode_selector_tooltip import ModeSelectorTooltip
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from helpers import dependency
PLAY_STREAK_LAYOUT_ID = R.views.lobby.daily.PlayStreakView()
PLAY_STREAK_TAB_LAYOUT_ID = R.views.lobby.daily.PlayStreakTabView()

class PlayStreakFacade(object):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__playStreakSubView', '__tabs', '__tabsToSubview', '__battleTypes')

    def __init__(self, parentView, *args, **kwargs):
        self.__playStreakSubView = PlayStreakSubView(parentView, PLAY_STREAK_LAYOUT_ID)
        self.__tabsToSubview = {DailyTabs.SERIAL: (self.__playStreakSubView, PLAY_STREAK_LAYOUT_ID)}
        self.__tabs = {DailyTabs.SERIAL: (PlayStreakTabView(), PLAY_STREAK_TAB_LAYOUT_ID)}
        self.__battleTypes = None
        return

    def finalize(self):
        self.__tabs.clear()
        self.__tabsToSubview.clear()

    def getTabs(self):
        return self.__tabs

    def getSubviews(self):
        return self.__tabsToSubview

    def getToolTipContent(self, event, contentID):
        return ModeSelectorTooltip(event.contentID, self.__battleTypes) if event.contentID == R.views.lobby.daily.tooltips.ModeSelectorTooltip() else None

    def updateBattleModes(self, battleModes):
        battleModes.clear()
        quests = self.eventsCache.getDailyQuests().values()
        bonusTypes = quests[0].preBattleCond.getConditions().find('bonusTypes').getValue() if quests else []
        for bonusType in bonusTypes:
            bonusTypeLabel = ARENA_GUI_TYPE_LABEL.LABELS.get(bonusType)
            if bonusTypeLabel and bonusTypeLabel not in battleModes:
                battleModes.addString(str(bonusType))

        self.__battleTypes = battleModes
        battleModes.invalidate()
