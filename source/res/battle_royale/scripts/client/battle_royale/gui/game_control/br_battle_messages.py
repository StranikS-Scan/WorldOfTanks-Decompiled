# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/game_control/br_battle_messages.py
import BigWorld
from helpers import dependency, int2roman
from battle_royale.gui.battle_control.controllers.progression_ctrl import IProgressionListener
from skeletons.gui.battle_session import IBattleSessionProvider
import BattleReplay

class ProgressionMessagesPlayer(IProgressionListener):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def updateData(self, arenaLevelData):
        if BattleReplay.g_replayCtrl.isPlaying and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        elif arenaLevelData.level == 1 or not arenaLevelData.levelIsChanged:
            return
        else:
            ctrl = self._sessionProvider.shared.messages
            isObserver = BigWorld.player().isObserver()
            if ctrl is not None and not isObserver:
                ctrl.onShowPlayerMessageByKey('VEHICLE_LEVEL_UP', {'level': int2roman(arenaLevelData.level)})
            return

    def onMaxLvlAchieved(self):
        if BattleReplay.g_replayCtrl.isPlaying and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        else:
            ctrl = self._sessionProvider.shared.messages
            isObserver = BigWorld.player().isObserver()
            if ctrl is not None and not isObserver:
                ctrl.onShowPlayerMessageByKey('VEHICLE_LEVEL_MAXED')
            return
