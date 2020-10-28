# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/game_messages_panel.py
import BattleReplay
from gui.Scaleform.daapi.view.meta.GameMessagesPanelMeta import GameMessagesPanelMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import EVENT, FINISH_REASON

class GameMessagesPanel(GameMessagesPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onMessageStarted(self, msgType, msgID):
        pass

    def onMessageEnded(self, msgType, msgID):
        pass

    def onMessageHiding(self, msgType, msgID):
        pass

    def sendEndGameMessage(self, winningTeam, reason):
        isCollectorFull = False
        battleGoals = self.sessionProvider.dynamic.battleGoals
        if battleGoals:
            souls, capacity = battleGoals.getCurrentCollectorSoulsInfo()
            isCollectorFull = True if souls >= capacity else False
        if winningTeam != EVENT.PLAYERS_TEAM:
            battleHints = self.sessionProvider.dynamic.battleHints
            if battleHints:
                if reason == FINISH_REASON.TIMEOUT:
                    battleHints.showHint('timeOut')
                elif reason == FINISH_REASON.EXTERMINATION and isCollectorFull:
                    battleHints.showHint('failedRunIntoCollector')
                else:
                    battleHints.showHint('failedActivateCollector')

    def setFlashObject(self, movieClip, autoPopulate=True, setScript=True):
        if movieClip is None and BattleReplay.g_replayCtrl.isPlaying:
            return
        else:
            super(GameMessagesPanel, self).setFlashObject(movieClip, autoPopulate, setScript)
            return
