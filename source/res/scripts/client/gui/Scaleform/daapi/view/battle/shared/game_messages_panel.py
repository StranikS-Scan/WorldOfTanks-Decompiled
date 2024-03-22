# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/game_messages_panel.py
from collections import namedtuple
import BattleReplay
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.meta.GameMessagesPanelMeta import GameMessagesPanelMeta
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from gui.battle_control import avatar_getter
from gui.battle_results.components.common import makeRegularFinishResultLabel
from gui.shared.utils import toUpper

class PlayerMessageData(namedtuple('playerMessageData', ('messageType', 'length', 'priority', 'msgData'))):

    def getDict(self):
        return self._asdict()


class GameMessagesPanel(GameMessagesPanelMeta):

    def _populate(self):
        super(GameMessagesPanel, self)._populate()
        if BattleReplay.g_replayEvents.isPlaying:
            BattleReplay.g_replayEvents.onTimeWarpStart += self.as_clearMessagesS

    def _dispose(self):
        self.as_clearMessagesS()
        if BattleReplay.g_replayEvents.isPlaying:
            BattleReplay.g_replayEvents.onTimeWarpStart -= self.as_clearMessagesS
        super(GameMessagesPanel, self)._dispose()

    def _addMessage(self, msg):
        self.as_addMessageS(msg)

    def onMessageStarted(self, msgType, modificator, msgID):
        pass

    def onMessagePhaseStarted(self, type, modificator, id):
        pass

    def onMessageEnded(self, msgType, msgID):
        pass

    def onMessageHiding(self, msgType, msgID):
        pass

    def sendEndGameMessage(self, winningTeam, reason):
        isWinner = avatar_getter.getPlayerTeam() == winningTeam
        if winningTeam == 0:
            messageType = GAME_MESSAGES_CONSTS.DRAW
        elif isWinner:
            messageType = GAME_MESSAGES_CONSTS.WIN
        else:
            messageType = GAME_MESSAGES_CONSTS.DEFEAT
        endGameMsgData = {'title': toUpper(backport.text(R.strings.menu.finalStatistic.commonStats.resultlabel.dyn(messageType)())),
         'subTitle': makeRegularFinishResultLabel(reason, messageType)}
        msg = PlayerMessageData(messageType, GAME_MESSAGES_CONSTS.DEFAULT_MESSAGE_LENGTH, GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_END_GAME, endGameMsgData)
        self._addMessage(msg.getDict())

    def setFlashObject(self, movieClip, autoPopulate=True, setScript=True):
        if movieClip is None and BattleReplay.g_replayCtrl.isPlaying:
            return
        else:
            super(GameMessagesPanel, self).setFlashObject(movieClip, autoPopulate, setScript)
            return
