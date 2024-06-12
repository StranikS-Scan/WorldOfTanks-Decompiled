# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/shared/br_ingame_menu.py
import BigWorld
from BWUtil import AsyncReturn
from gui.battle_control import avatar_getter
from wg_async import wg_async
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu

@wg_async
def showBattleRoyaleLeaverAliveWindow():
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from battle_royale.gui.impl.battle.views.leave_battle_view import LeaveBattleView
    wrapper = FullScreenDialogWindowWrapper(LeaveBattleView(), doBlur=False)
    result = yield dialogs.showSimple(wrapper)
    raise AsyncReturn(result)


class BRIngameMenu(IngameMenu):

    @staticmethod
    def _showLeaverAliveWindow(isPlayerIGR):
        return showBattleRoyaleLeaverAliveWindow()

    def _getExitResult(self):
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        isLeaverWhileRespawning = not self.sessionProvider.isReplayPlaying and vehicle.dynamicComponents.get('vehicleBRRespawnComponent') and self.sessionProvider.arenaVisitor.hasFairplay()
        return isLeaverWhileRespawning or super(BRIngameMenu, self)._getExitResult()
