# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/battle_results/composer.py
import logging
from collections import namedtuple
import BigWorld
import typing
from cosmic_event.gui.battle_results import CosmicBattleResultEvent
from gui import SystemMessages
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.battle_results import templates
from gui.battle_results.composer import StatsComposer
from gui.impl.gen import R
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    from typing import Dict
_logger = logging.getLogger(__name__)
BattleResult = namedtuple('BattleResult', ('results', 'reusable'))

def _showMessage():
    SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error, priority='high')


class CosmicEventBattleStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(CosmicEventBattleStatsComposer, self).__init__(reusable, templates.REGULAR_COMMON_STATS_BLOCK.clone(), templates.REGULAR_PERSONAL_STATS_BLOCK.clone(), templates.REGULAR_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.PROGRESSIVE_REWARD_VO.clone())
        self.battleResults = None
        return

    def getVO(self):
        return self.battleResults

    def setResults(self, results, reusable):
        self.battleResults = BattleResult(results=results, reusable=reusable)

    @staticmethod
    def onShowResults(arenaUniqueID):
        return None

    @staticmethod
    def onResultsPosted(arenaUniqueID):
        if CosmicEventBattleStatsComposer._canNavigate():
            g_eventBus.handleEvent(CosmicBattleResultEvent(CosmicBattleResultEvent.POST_BATTLE_SCREEN_OPENING, ctx={}), scope=EVENT_BUS_SCOPE.LOBBY)
            showCosmicResultsView(arenaUniqueID)

    @staticmethod
    def _canNavigate():
        from gui.prb_control.dispatcher import g_prbLoader
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled():
            BigWorld.callback(0.0, _showMessage)
            return False
        else:
            return True


@dependency.replace_none_kwargs(uiLoader=IGuiLoader)
def showCosmicResultsView(arenaUniqueID, uiLoader=None):
    from cosmic_event.gui.impl.lobby.cosmic_post_battle_view.cosmic_post_battle_view import CosmicPostBattleView
    contentID = R.views.cosmic_event.lobby.cosmic_post_battle.CosmicPostBattleView()
    currentView = uiLoader.windowsManager.getViewByLayoutID(contentID)
    if currentView:
        currentView.destroy()
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentID, viewClass=CosmicPostBattleView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), ctx={'arenaUniqueID': arenaUniqueID}), scope=EVENT_BUS_SCOPE.LOBBY)
