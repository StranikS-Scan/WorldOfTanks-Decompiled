# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/game_messages_panel.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.game_messages_panel import GameMessagesPanel, PlayerMessageData
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R
from constants import ARENA_BONUS_TYPE_IDS

class LSGameMessagesPanel(GameMessagesPanel):

    def sendEndGameMessage(self, winningTeam, reason):
        isWinner = avatar_getter.getPlayerTeam() == winningTeam
        if isWinner:
            if BigWorld.player() is None:
                return
            arenaBonusType = BigWorld.player().arena.bonusType
            difficulty = ARENA_BONUS_TYPE_IDS.get(arenaBonusType, '').lower()
            messageType = GAME_MESSAGES_CONSTS.WIN
            flashlightType = GAME_MESSAGES_CONSTS.WIN
            subTitleRes = R.strings.last_stand_battle_results.ls_finish.reason.dyn(difficulty).num(reason).dyn(messageType)()
        else:
            messageType = GAME_MESSAGES_CONSTS.DEFEAT
            flashlightType = GAME_MESSAGES_CONSTS.DRAW
            subTitleRes = R.strings.last_stand_battle_results.ls_finish.reason.num(reason).dyn(messageType)()
        titleRes = R.strings.last_stand_battle_results.status.dyn(messageType)()
        endGameMsgData = {'title': backport.text(titleRes),
         'subTitle': backport.text(subTitleRes)}
        msg = PlayerMessageData(flashlightType, GAME_MESSAGES_CONSTS.DEFAULT_MESSAGE_LENGTH, GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_END_GAME, endGameMsgData)
        self._addMessage(msg.getDict())
        return
