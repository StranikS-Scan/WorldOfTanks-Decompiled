# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/tabbed_full_stats.py
import logging
from enum import Enum
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from gui.Scaleform.daapi.view.meta.TabbedFullStatsMeta import TabbedFullStatsMeta
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class TabsAliases(Enum):
    STATS = 'stats'
    QUESTS_PROGRESS = 'quests_progress'
    BOOSTERS = 'boosters'


class TabbedFullStatsComponent(TabbedFullStatsMeta):

    def __init__(self):
        super(TabbedFullStatsComponent, self).__init__()
        self.__tabsMap = {}

    @property
    def hasTabs(self):
        return True

    def hasTab(self, alias):
        return alias in self.__tabsMap

    def setActiveTab(self, tabAlias):
        if tabAlias is None:
            self.as_resetActiveTabS()
        else:
            index = self.__tabsMap.get(tabAlias)
            if index is None:
                _logger.error("FullStatsComponent doesn't have %s tab", tabAlias)
            else:
                self.as_setActiveTabS(index)
        return

    def _populate(self):
        super(TabbedFullStatsComponent, self)._populate()
        tabs = self._buildTabs(_TabsBuilder())
        for idx, tabData in enumerate(tabs):
            self.__tabsMap[tabData['alias']] = idx
            tabData['alias'] = tabData['alias'].value

        self.as_updateTabsS(tabs)

    def _destroy(self):
        self.__tabsMap = {}
        super(TabbedFullStatsComponent, self)._destroy()

    @staticmethod
    def _buildTabs(builder):
        builder.addStatisticsTab()
        builder.addPersonalQuestsTab()
        builder.addBoostersTab()
        return builder.getTabs()


class _TabsBuilder(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__tabs = []

    def addStatisticsTab(self):
        self.__tabs.append({'label': backport.text(R.strings.ingame_gui.statistics.tab.line_up.header()),
         'alias': TabsAliases.STATS})

    def addPersonalQuestsTab(self):
        if self.__lobbyContext.getServerSettings().isPersonalMissionsEnabled():
            self.__tabs.append({'label': backport.text(R.strings.ingame_gui.statistics.tab.quests.header()),
             'alias': TabsAliases.QUESTS_PROGRESS})

    def addBoostersTab(self):
        if self.__isBoosterProcessingAvailable():
            self.__tabs.append({'label': backport.text(R.strings.ingame_gui.statistics.tab.personalReserves.header()),
             'alias': TabsAliases.BOOSTERS})

    def getTabs(self):
        return self.__tabs

    def __isBoosterProcessingAvailable(self):
        return self.__lobbyContext.getServerSettings().personalReservesConfig.isReservesInBattleActivationEnabled and ARENA_BONUS_TYPE_CAPS.checkAny(BigWorld.player().arena.bonusType, ARENA_BONUS_TYPE_CAPS.BOOSTERS)
