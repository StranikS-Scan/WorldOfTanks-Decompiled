# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/shared/br_ingame_menu.py
import BigWorld
from BWUtil import AsyncReturn
from gui.battle_control import avatar_getter
from gui.battle_control.battle_session import BattleExitResult
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
        arenaDP = self.sessionProvider.getArenaDP()
        vInfo = arenaDP.getVehicleInfo()
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        vehicleBRRespawnComponent = vehicle.dynamicComponents.get('vehicleBRRespawnComponent')
        isRespawning = vehicleBRRespawnComponent is not None
        isAlive = avatar_getter.isVehicleAlive()
        return BattleExitResult(isAlive or isRespawning, vInfo.player)
