# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger_ingame_menu.py
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu
from gui.battle_control import avatar_getter
from gui.battle_control.battle_session import BattleExitResult
from story_mode.uilogging.story_mode.consts import LogWindows, LogButtons
from story_mode.uilogging.story_mode.loggers import WindowLogger
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from white_tiger.gui.white_tiger_gui_constants import VIEW_ALIAS

class WhiteTigerIngameMenu(IngameMenu):

    def __init__(self, ctx=None):
        super(WhiteTigerIngameMenu, self).__init__(ctx)
        self._uiLogger = WindowLogger(LogWindows.ESCAPE_MENU)

    def settingsClick(self):
        self._uiLogger.logClick(LogButtons.SETTINGS)
        g_eventBus.handleEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.WHITE_TIGER_SETTINGS_WINDOW)), scope=EVENT_BUS_SCOPE.BATTLE)

    def _getExitResult(self):
        prematureLeave = self._isWhiteTigerPrematureLeave()
        if prematureLeave:
            arenaDP = self.sessionProvider.getArenaDP()
            vInfo = arenaDP.getVehicleInfo()
            return BattleExitResult(prematureLeave, vInfo.player)
        return super(WhiteTigerIngameMenu, self)._getExitResult()

    def _isWhiteTigerPrematureLeave(self):
        return not avatar_getter.isVehicleAlive()
