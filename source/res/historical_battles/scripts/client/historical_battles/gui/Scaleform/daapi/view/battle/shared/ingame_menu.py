# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/shared/ingame_menu.py
import BigWorld
from wg_async import wg_async, wg_await
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu
from historical_battles.gui.impl.battle.premature_leave import showExitWindow, showLeaverCanRespawnWindow, showLeaverAliveWindow

class HistoricalBattleIngameMenu(IngameMenu):

    @wg_async
    def _doLeaveArena(self):
        self.as_setVisibilityS(False)
        vehicleID = self.sessionProvider.getArenaDP().getPlayerVehicleID()
        teamLivesComponent = BigWorld.player().arena.teamInfo.dynamicComponents.get('teamLivesComponent')
        if teamLivesComponent:
            lives = teamLivesComponent.getLives(vehicleID) + teamLivesComponent.getLockedLives(vehicleID)
        else:
            lives = 0
        if lives > 0:
            inPostmortem = self.sessionProvider.shared.vehicleState.isInPostmortem
            if inPostmortem:
                result = yield wg_await(showLeaverCanRespawnWindow())
            else:
                result = yield wg_await(showLeaverAliveWindow())
        else:
            result = yield wg_await(showExitWindow())
        self.as_setVisibilityS(True)
        if result:
            self._doExit()
