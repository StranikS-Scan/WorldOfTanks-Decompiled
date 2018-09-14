# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/historicalBattles/sf_settings.py
from gui.Scaleform.framework.managers.loaders import PackageBusinessHandler
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.shared import EVENT_BUS_SCOPE

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.historicalBattles.HistoricalBattlesListWindow import HistoricalBattlesListWindow
    return [GroupedViewSettings(PREBATTLE_ALIASES.HISTORICAL_BATTLES_LIST_WINDOW_PY, HistoricalBattlesListWindow, 'historicalBattlesListWindow.swf', ViewTypes.WINDOW, '', PREBATTLE_ALIASES.HISTORICAL_BATTLES_LIST_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True)]


def getBusinessHandlers():
    return [HistoricalBattlesBusinessHandler()]


class HistoricalBattlesBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = [(PREBATTLE_ALIASES.HISTORICAL_BATTLES_LIST_WINDOW_PY, self.__showHBListWindow)]
        super(HistoricalBattlesBusinessHandler, self).__init__(listeners, EVENT_BUS_SCOPE.LOBBY)

    def __showHBListWindow(self, _):
        alias = name = PREBATTLE_ALIASES.HISTORICAL_BATTLES_LIST_WINDOW_PY
        self.app.loadView(alias, name)
