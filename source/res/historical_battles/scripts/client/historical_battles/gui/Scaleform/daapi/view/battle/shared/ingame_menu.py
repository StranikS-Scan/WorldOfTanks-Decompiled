# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/shared/ingame_menu.py
import typing
import BigWorld
from BWUtil import AsyncReturn
from th_async import th_async, th_await
from gui.battle_control import avatar_getter
from gui.Scaleform.daapi.view.battle.shared.ingame_menu import IngameMenu
from historical_battles.gui.impl.battle.premature_leave import showExitWindow, showLeaverAliveWindow
if typing.TYPE_CHECKING:
    from HBAvatarRespawnComponent import HBAvatarRespawnComponent

class HistoricalBattleIngameMenu(IngameMenu):

    def _setServerStats(self):
        pass

    @th_async
    def _doLeaveArena(self):
        avatar = BigWorld.player()
        respawnComponent = avatar.HBAvatarRespawnComponent
        lives = respawnComponent.getAliveVehicleCount()
        if lives > 0 or avatar_getter.isVehicleAlive():
            result = yield th_await(showLeaverAliveWindow())
        else:
            result = yield th_await(showExitWindow())
        raise AsyncReturn(result)
