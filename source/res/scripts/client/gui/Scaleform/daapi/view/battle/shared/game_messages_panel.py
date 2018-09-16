# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/game_messages_panel.py
from collections import namedtuple
from gui.Scaleform.daapi.view.meta.GameMessagesPanelMeta import GameMessagesPanelMeta
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from gui.battle_control import avatar_getter
from gui.battle_results.components.common import makeRegularFinishResultLabel, _FULL_RESULT_LABEL
from gui.shared.utils import toUpper
from helpers import i18n

class PlayerMessageData(namedtuple('playerMessageData', ('messageType', 'length', 'priority', 'msgData'))):

    def getDict(self):
        return self._asdict()


class GameMessagesPanel(GameMessagesPanelMeta):

    def _addMessage(self, msg):
        self.as_addMessageS(msg)

    def sendEndGameMessage(self, winningTeam, reason):
        messageType = GAME_MESSAGES_CONSTS.DRAW
        if winningTeam != 0:
            isWinner = avatar_getter.getPlayerTeam() == winningTeam
            if isWinner:
                messageType = GAME_MESSAGES_CONSTS.WIN
            else:
                messageType = GAME_MESSAGES_CONSTS.DEFEAT
        endGameMsgData = {'title': toUpper(i18n.makeString(_FULL_RESULT_LABEL.format(messageType))),
         'subTitle': toUpper(makeRegularFinishResultLabel(reason, messageType))}
        msg = PlayerMessageData(messageType, GAME_MESSAGES_CONSTS.DEFAULT_MESSAGE_LENGTH, GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_HIGH, endGameMsgData)
        self._addMessage(msg.getDict())
