# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/battle_results/composer.py
from collections import namedtuple
from gui import SystemMessages
from helpers import dependency
from gui.impl.gen import R
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.battle_results.composer import RegularStatsComposer
from gui.prb_control.dispatcher import g_prbLoader
from skeletons.gui.impl import IGuiLoader
BattleResult = namedtuple('BattleResult', ('results', 'reusable'))

def _showErrorMessage():
    SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error, priority='high')


def _isNavigationDisabled():
    prbDispatcher = g_prbLoader.getDispatcher()
    return prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled()


class GrinchBattleStatsComposer(RegularStatsComposer):

    def __init__(self, reusable):
        super(GrinchBattleStatsComposer, self).__init__(reusable)
        self._results = None
        return

    def setResults(self, results, reusable):
        self._results = BattleResult(results=results, reusable=reusable)

    def getVO(self):
        return self._results

    @staticmethod
    def onShowResults(arenaUniqueID):
        pass

    @staticmethod
    def onResultsPosted(arenaUniqueID):
        showGrinchResultsView(arenaUniqueID)


@dependency.replace_none_kwargs(uiLoader=IGuiLoader)
def showGrinchResultsView(arenaUniqueID, uiLoader=None):
    if _isNavigationDisabled():
        _showErrorMessage()
        return
    from grinch.gui.impl.lobby.post_battle.post_battle_view import PostBattleView
    contentID = R.views.grinch.lobby.post_battle.PostBattleView()
    currentView = uiLoader.windowsManager.getViewByLayoutID(contentID)
    if currentView:
        currentView.destroy()
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentID, viewClass=PostBattleView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), ctx={'arenaUniqueID': arenaUniqueID}), scope=EVENT_BUS_SCOPE.LOBBY)
