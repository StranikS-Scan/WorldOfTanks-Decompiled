# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/historicalBattles/sf_settings.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.framework.managers.loaders import PackageBusinessHandler
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ViewSettings, ScopeTemplates
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowWindowEvent

class HB_VIEW_ALIAS(object):
    HISTORICAL_BATTLES_LIST_WINDOW = 'historicalBattles/HBListWindow'


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.historicalBattles.HistoricalBattlesListWindow import HistoricalBattlesListWindow
    return [GroupedViewSettings(HB_VIEW_ALIAS.HISTORICAL_BATTLES_LIST_WINDOW, HistoricalBattlesListWindow, 'historicalBattlesListWindow.swf', ViewTypes.WINDOW, '', ShowWindowEvent.SHOW_HISTORICAL_BATTLES_WINDOW, ScopeTemplates.DEFAULT_SCOPE)]


def getBusinessHandlers():
    return [HistoricalBattlesBusinessHandler()]


class HistoricalBattlesBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = [(ShowWindowEvent.SHOW_HISTORICAL_BATTLES_WINDOW, self.__showHBListWindow)]
        super(HistoricalBattlesBusinessHandler, self).__init__(listeners, EVENT_BUS_SCOPE.LOBBY)

    def __showHBListWindow(self, _):
        alias = name = HB_VIEW_ALIAS.HISTORICAL_BATTLES_LIST_WINDOW
        self.app.loadView(alias, name)
