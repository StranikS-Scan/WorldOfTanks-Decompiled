# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/game_messages_panel.py
import BattleReplay
from gui.Scaleform.daapi.view.meta.GameMessagesPanelMeta import GameMessagesPanelMeta
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.battle_control import event_dispatcher
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import EVENT, FINISH_REASON

class GameMessagesPanel(GameMessagesPanelMeta, GameEventGetterMixin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    HINT_TIME_OUT = 'timeOut'
    HINT_FULL_COLLECTOR_EXTERMINATION = 'failedRunIntoCollector'
    HINT_ACTIVATION_FAILED = 'failedActivateCollector'
    HINT_BOSS_FIGHT_TIME_OUT = 'bossFightTimeOut'
    HINT_BOSS_FIGHT_EXTERMINATION = 'bossFightExtermination'

    def onMessageStarted(self, msgType, msgID):
        pass

    def onMessageEnded(self, msgType, msgID):
        pass

    def onMessageHiding(self, msgType, msgID):
        pass

    def sendEndGameMessage(self, winningTeam, reason):
        if winningTeam == EVENT.PLAYERS_TEAM:
            return
        else:
            isCollectorFull = False
            battleGoals = self.sessionProvider.dynamic.battleGoals
            if battleGoals:
                souls, capacity = battleGoals.getCurrentCollectorSoulsInfo()
                isCollectorFull = souls >= capacity > 0
            battleHints = self.sessionProvider.dynamic.battleHints
            if battleHints is None:
                return
            isBossFight = self._isBossFight
            hintName = self.HINT_ACTIVATION_FAILED
            if reason == FINISH_REASON.TIMEOUT:
                hintName = self.HINT_TIME_OUT if not isBossFight else self.HINT_BOSS_FIGHT_TIME_OUT
            elif reason == FINISH_REASON.EXTERMINATION:
                if isBossFight:
                    hintName = self.HINT_BOSS_FIGHT_EXTERMINATION
                elif isCollectorFull:
                    hintName = self.HINT_FULL_COLLECTOR_EXTERMINATION
            battleHints.showHint(hintName)
            event_dispatcher.onHideBossHealthBar()
            return

    def setFlashObject(self, movieClip, autoPopulate=True, setScript=True):
        if movieClip is None and BattleReplay.g_replayCtrl.isPlaying:
            return
        else:
            super(GameMessagesPanel, self).setFlashObject(movieClip, autoPopulate, setScript)
            return

    @property
    def _isBossFight(self):
        envData = self.environmentData
        return False if envData is None else envData.getCurrentEnvironmentID() == envData.getBossFightEnvironmentID()
