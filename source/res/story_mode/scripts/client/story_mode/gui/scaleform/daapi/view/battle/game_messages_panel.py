# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/game_messages_panel.py
from gui.Scaleform.daapi.view.battle.shared.game_messages_panel import GameMessagesPanel, PlayerMessageData
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R

class StoreModeGameMessagesPanel(GameMessagesPanel):

    def sendEndGameMessage(self, winningTeam, reason, extraData):
        messageType = GAME_MESSAGES_CONSTS.WIN if avatar_getter.getPlayerTeam() == winningTeam else GAME_MESSAGES_CONSTS.DRAW
        rReason = R.strings.sm_battle.battleResult.reason
        endGameMsgData = {'title': backport.text(R.strings.sm_battle.battleResult.resultLabel.dyn(messageType)()),
         'subTitle': backport.text(rReason.num(reason, rReason.default)())}
        msg = PlayerMessageData(messageType, GAME_MESSAGES_CONSTS.DEFAULT_MESSAGE_LENGTH, GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_END_GAME, endGameMsgData)
        self._addMessage(msg.getDict())
