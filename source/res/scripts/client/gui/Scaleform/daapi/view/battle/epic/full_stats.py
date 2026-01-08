# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/full_stats.py
import BigWorld
from gui.Scaleform.daapi.view.meta.EpicFullStatsMeta import EpicFullStatsMeta
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import i18n

class EpicFullStatsComponent(EpicFullStatsMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(EpicFullStatsComponent, self)._populate()
        self.as_initializeTextS(i18n.makeString(EPIC_BATTLE.TAB_SCREEN_SHOW_MY_LANE).upper(), i18n.makeString(EPIC_BATTLE.TAB_SCREEN_SHOW_ALL_LANES).upper(), i18n.makeString(EPIC_BATTLE.TAB_SCREEN_SHOW_QUESTS).upper())
        BigWorld.player().arena.componentSystem.playerDataComponent.onCrewRolesFactorUpdated += self.__setGeneralBonus
        g_eventBus.addListener(GameEvent.FULL_STATS_QUEST_PROGRESS, self.__onToggleFullStatsQuest, EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        super(EpicFullStatsComponent, self)._dispose()
        g_eventBus.removeListener(GameEvent.FULL_STATS_QUEST_PROGRESS, self.__onToggleFullStatsQuest, EVENT_BUS_SCOPE.BATTLE)
        arena = BigWorld.player().arena if hasattr(BigWorld.player(), 'arena') else None
        if arena and hasattr(arena, 'componentSystem'):
            componentSystem = BigWorld.player().arena.componentSystem
            if componentSystem:
                componentSystem.playerDataComponent.onCrewRolesFactorUpdated -= self.__setGeneralBonus
        return

    def __setGeneralBonus(self, newFactor, allyVehID=None, allyNewRank=None):
        self.as_setGeneralBonusS(newFactor)

    def __onToggleFullStatsQuest(self, event):
        manager = self.app.containerManager
        if manager.isModalViewsIsExists():
            return
        self.as_toggleQuestsTabS(event.ctx['isDown'])
