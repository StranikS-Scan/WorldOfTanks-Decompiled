# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/game_messages_panel.py
from gui.Scaleform.daapi.view.battle.shared.game_messages_panel import GameMessagesPanel, PlayerMessageData
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils import toUpper

class EventGameMessagesPanel(GameMessagesPanel):

    def sendEndGameMessage(self, winningTeam, reason, extraData):
        playerTeam = avatar_getter.getPlayerTeam()
        isWinner = playerTeam == winningTeam
        messageType = GAME_MESSAGES_CONSTS.WIN if isWinner else GAME_MESSAGES_CONSTS.DEFEAT
        state = 'victory' if isWinner else 'defeat'
        subTitle = R.strings.event.pbt.dyn(state)
        teamSubTitle = subTitle.num(playerTeam)
        endGameMsgData = {'title': toUpper(backport.text(R.strings.menu.finalStatistic.commonStats.resultlabel.dyn(messageType)())),
         'subTitle': backport.text(teamSubTitle.num(reason)())}
        msg = PlayerMessageData(messageType, GAME_MESSAGES_CONSTS.DEFAULT_MESSAGE_LENGTH, GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_END_GAME, endGameMsgData)
        self._addMessage(msg.getDict())
