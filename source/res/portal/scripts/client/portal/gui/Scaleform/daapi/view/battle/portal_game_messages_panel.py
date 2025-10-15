# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/portal_game_messages_panel.py
from gui.battle_control import avatar_getter
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from gui.Scaleform.daapi.view.battle.shared.game_messages_panel import PlayerMessageData, GameMessagesPanel
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils import toUpper
from constants import FINISH_REASON
from portal.sounds.sound_helpers import play2DSound
from portal_common.portal_constants import BattleState
from portal.sounds.sound_constants import PortalEndGameUISound
_FINISH_REASON = {FINISH_REASON.EXTERMINATION: 'boss',
 FINISH_REASON.BASE: 'base',
 FINISH_REASON.TIMEOUT: 'timeout'}

def _makePortalFinishResultLabel(finishReason, teamResult):
    finishReason = _FINISH_REASON.get(finishReason)
    battleState = avatar_getter.getArenaInfo().portalBattleStateComponent
    if battleState.battleState == BattleState.SUPER_BOSS_FIGHT:
        finishReason = 'super_boss'
    res = R.strings.portal_battle.finish.dyn(teamResult).reason.dyn(finishReason)()
    return backport.text(res)


class PortalMessagePanel(GameMessagesPanel):

    def onMessageStarted(self, msgType, modificator, msgID):
        if msgType == GAME_MESSAGES_CONSTS.WIN:
            play2DSound(PortalEndGameUISound.WIN)
        elif msgType == GAME_MESSAGES_CONSTS.DEFEAT:
            play2DSound(PortalEndGameUISound.DEFEAT)

    def sendEndGameMessage(self, winningTeam, reason, extraData):
        isWinner = avatar_getter.getPlayerTeam() == winningTeam
        if winningTeam == 0:
            messageType = GAME_MESSAGES_CONSTS.DRAW
        elif isWinner:
            messageType = GAME_MESSAGES_CONSTS.WIN
        else:
            messageType = GAME_MESSAGES_CONSTS.DEFEAT
        titleRes = R.strings.portal_battle.finalStatistics.commonStats.resultlabel.dyn(messageType)
        if not isWinner and reason == FINISH_REASON.TIMEOUT:
            titleRes = titleRes.timeout
        endGameMsgData = {'title': toUpper(backport.text(titleRes())),
         'subTitle': _makePortalFinishResultLabel(reason, messageType)}
        msg = PlayerMessageData(messageType, GAME_MESSAGES_CONSTS.DEFAULT_MESSAGE_LENGTH, GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_END_GAME, endGameMsgData)
        self._addMessage(msg.getDict())
