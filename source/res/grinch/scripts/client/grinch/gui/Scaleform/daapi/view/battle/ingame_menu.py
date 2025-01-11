# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/ingame_menu.py
from BWUtil import AsyncReturn
from grinch.gui.grinch_gui_constants import VIEW_ALIAS
from gui.battle_control.battle_session import BattleExitResult
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu
from gui.Scaleform.daapi.view.battle.shared.premature_leave import showResDialogWindow
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from wg_async import wg_await, wg_async

@wg_async
def _showLeaverAliveWindow():
    quitBattleLeaverR = R.strings.ingame_gui.grinchBattle.quit.leaver
    result = yield wg_await(showResDialogWindow(title=quitBattleLeaverR.title(), confirm=quitBattleLeaverR.submit(), cancel=quitBattleLeaverR.cancel(), description=quitBattleLeaverR.descriptionAlive(), icon=R.images.grinch.gui.maps.icons.battle.deserterLeaveBattle()))
    raise AsyncReturn(result)


class GrinchIngameMenu(IngameMenu):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def settingsClick(self):
        g_eventBus.handleEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.GRINCH_SETTINGS_WINDOW)), scope=EVENT_BUS_SCOPE.BATTLE)

    @staticmethod
    def _showLeaverAliveWindow(isPlayerIGR):
        return _showLeaverAliveWindow()

    def _getExitResult(self):
        if self.sessionProvider.isReplayPlaying:
            return BattleExitResult(False, None)
        else:
            arenaDP = self.sessionProvider.getArenaDP()
            vInfo = arenaDP.getVehicleInfo()
            return BattleExitResult(True, vInfo.player)
