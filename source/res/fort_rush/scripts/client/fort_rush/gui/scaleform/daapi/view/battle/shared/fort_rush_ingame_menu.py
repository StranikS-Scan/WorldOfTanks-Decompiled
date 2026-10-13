# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/shared/fort_rush_ingame_menu.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu
from gui.Scaleform.daapi.view.battle.shared.premature_leave import showResDialogWindow
from gui.battle_control.battle_session import BattleExitResult
import BattleReplay
from wg_async import wg_await, wg_async
from BWUtil import AsyncReturn
from gui.impl.gen import R

@wg_async
def _showLeaverAliveWindow(quitR):
    title = quitR.leaver.title()
    confirm = quitR.leaver.submit()
    cancel = quitR.leaver.cancel()
    description = quitR.leaver.descriptionAlive()
    icon = R.images.gui.maps.icons.battle.deserterLeaveBattle()
    result = yield wg_await(showResDialogWindow(title, confirm=confirm, cancel=cancel, description=description, icon=icon))
    raise AsyncReturn(result)


class FortRushIngameMenu(IngameMenu):

    def _getExitResult(self):
        arenaDP = self.sessionProvider.getArenaDP()
        vInfo = arenaDP.getVehicleInfo()
        arenaVisitor = self.sessionProvider.arenaVisitor
        isLeaveAllowed = arenaVisitor.isArenaLeaveAllowed() if not BattleReplay.isPlaying() else True
        return BattleExitResult(not isLeaveAllowed, vInfo.player) if isLeaveAllowed is not None else super(FortRushIngameMenu, self)._getExitResult()

    @staticmethod
    def _showLeaverAliveWindow(isPlayerIGR):
        return _showLeaverAliveWindow(R.strings.dialogs.quitBattle if isPlayerIGR else R.strings.fort_rush.quitBattle)
