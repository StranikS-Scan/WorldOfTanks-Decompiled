# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/game_messages_panel.py
from gui.Scaleform.daapi.view.battle.shared.game_messages_panel import GameMessagesPanel, PlayerMessageData
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R

class HWGameMessagesPanel(GameMessagesPanel):

    def sendEndGameMessage(self, winningTeam, reason, extraData):
        isWinner = avatar_getter.getPlayerTeam() == winningTeam
        if winningTeam == 0:
            messageType = GAME_MESSAGES_CONSTS.DRAW
            flashlightType = GAME_MESSAGES_CONSTS.DRAW
        elif isWinner:
            messageType = GAME_MESSAGES_CONSTS.WIN
            flashlightType = GAME_MESSAGES_CONSTS.WIN
        else:
            messageType = GAME_MESSAGES_CONSTS.DEFEAT
            flashlightType = GAME_MESSAGES_CONSTS.DRAW
        titleRes = R.strings.battle_results.hw_battle_result.status.dyn(messageType)()
        subTitleRes = R.strings.battle_results.finish.reason.dyn('c_{}{}'.format(reason, messageType))()
        endGameMsgData = {'title': backport.text(titleRes),
         'subTitle': backport.text(subTitleRes)}
        msg = PlayerMessageData(flashlightType, GAME_MESSAGES_CONSTS.DEFAULT_MESSAGE_LENGTH, GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_END_GAME, endGameMsgData)
        self._addMessage(msg.getDict())
