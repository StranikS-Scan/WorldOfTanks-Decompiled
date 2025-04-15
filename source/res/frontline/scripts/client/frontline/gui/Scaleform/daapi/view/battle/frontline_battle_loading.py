# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/frontline_battle_loading.py
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class FrontlineEpicBattleLoading(BattleLoading):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def _getBattlesCount(self):
        return self.lobbyContext.getEpicBattlesCount()
