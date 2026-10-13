# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/game_messages_panel.py
from __future__ import absolute_import
from constants import FINISH_REASON
from gui.Scaleform.daapi.view.battle.shared.game_messages_panel import GameMessagesPanel, PlayerMessageData
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R

class FortRushGameMessagesPanel(GameMessagesPanel):

    def sendEndGameMessage(self, winningTeam, reason):
        isWinner = avatar_getter.getPlayerTeam() == winningTeam
        if winningTeam == 0:
            messageType = GAME_MESSAGES_CONSTS.DRAW
        elif isWinner:
            messageType = GAME_MESSAGES_CONSTS.WIN
        else:
            messageType = GAME_MESSAGES_CONSTS.DEFEAT
        if reason == FINISH_REASON.WIN_POINTS_CAP:
            reasonResource = R.strings.fort_rush.endGame.reason.num(reason).dyn(messageType)()
        else:
            reasonResource = R.strings.fort_rush.endGame.reason.num(reason)()
        endGameMsgData = {'title': backport.text(R.strings.menu.finalStatistic.commonStats.resultlabel.dyn(messageType)()),
         'subTitle': backport.text(reasonResource) if reasonResource else ''}
        msg = PlayerMessageData(messageType, GAME_MESSAGES_CONSTS.DEFAULT_MESSAGE_LENGTH, GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_END_GAME, endGameMsgData)
        self.as_clearMessagesS()
        self._addMessage(msg.getDict())
