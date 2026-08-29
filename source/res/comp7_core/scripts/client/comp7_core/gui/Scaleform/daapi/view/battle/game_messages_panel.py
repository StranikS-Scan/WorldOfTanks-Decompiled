# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/Scaleform/daapi/view/battle/game_messages_panel.py
from gui.battle_control import avatar_getter
from helpers import dependency
from gui.Scaleform.daapi.view.battle.shared.game_messages_panel import GameMessagesPanel
from gui.impl import backport
from gui.impl.gen import R
from skeletons.gui.battle_session import IBattleSessionProvider
from comp7_core_constants import FINISH_REASON

class Comp7GameMessagesPanel(GameMessagesPanel):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def sendEndGameMessage(self, winningTeam, reason):
        if reason in FINISH_REASON.DRAW_RESOLVED_REASONS:
            isWinner = avatar_getter.getPlayerTeam() == winningTeam
            params = None
            if reason == FINISH_REASON.SURVIVORS_LEFT:
                battleFieldCtrl = self.guiSessionProvider.dynamic.battleField
                params = sorted([ len(vehs) for vehs in battleFieldCtrl.getAliveVehicles() ], reverse=isWinner)
            elif reason == FINISH_REASON.DAMAGE_DEALT:
                arena = avatar_getter.getArena()
                teamsDamageDealt = arena.arenaInfo.comp7.teamsDamageDealt if arena and arena.arenaInfo else [0, 0]
                params = sorted([ damage for damage in teamsDamageDealt ], reverse=isWinner)
            messageType = self._getMessageType(winningTeam)
            reasonKey = 'c_{}{}'.format(reason, messageType)
            subTitle = backport.text(R.strings.battle_results.battle_finish.reason.dyn(reasonKey)())
            if params:
                subTitle = subTitle.format(*params)
            self._sendEndGameMessage(messageType, subTitle)
        super(Comp7GameMessagesPanel, self).sendEndGameMessage(winningTeam, reason)
        return
