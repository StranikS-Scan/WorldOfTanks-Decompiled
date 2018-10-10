# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/game_messages_panel.py
from gui.Scaleform.daapi.view.meta.GameMessagesPanelMeta import GameMessagesPanelMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.battle_control import avatar_getter
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from gui.Scaleform.daapi.view.battle.shared.game_messages_panel import PlayerMessageData
from gui.battle_results.components.common import makeEpicBattleFinishResultLabel

class EpicMessagePanel(GameMessagesPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EpicMessagePanel, self).__init__()
        self.__blockNewMessages = False

    def sendEndGameMessage(self, winningTeam, reason):
        isWinner = avatar_getter.getPlayerTeam() == winningTeam
        if winningTeam == 0:
            messageType = GAME_MESSAGES_CONSTS.DRAW
            title = EPIC_BATTLE.GAME_DRAW
        else:
            messageType = GAME_MESSAGES_CONSTS.WIN if isWinner else GAME_MESSAGES_CONSTS.DEFEAT
            title = EPIC_BATTLE.GAME_VICTORY if isWinner else EPIC_BATTLE.GAME_DEFEAT
        endGameMsgData = {'title': title,
         'reason': reason,
         'subTitle': makeEpicBattleFinishResultLabel(reason, messageType)}
        msg = PlayerMessageData(messageType, GAME_MESSAGES_CONSTS.DEFAULT_MESSAGE_LENGTH, GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_END_GAME, endGameMsgData)
        self.__onIngameMessageReady(msg)
        self.__blockNewMessages = True

    def onMessageStarted(self, messageType, id_):
        ctrl = self.sessionProvider.dynamic.gameNotifications
        if ctrl:
            ctrl.onMessagePlaybackStarted(messageType, {'id': id_})

    def onMessageEnded(self, messageType, id_):
        ctrl = self.sessionProvider.dynamic.gameNotifications
        if ctrl:
            ctrl.onMessagePlaybackEnded(messageType, {'id': id_})

    def _populate(self):
        super(EpicMessagePanel, self)._populate()
        ctrl = self.sessionProvider.dynamic.missions
        if ctrl is not None:
            ctrl.onIngameMessageReady += self.__onIngameMessageReady
        return

    def _dispose(self):
        super(EpicMessagePanel, self)._dispose()
        ctrl = self.sessionProvider.dynamic.missions
        if ctrl is not None:
            ctrl.onIngameMessageReady -= self.__onIngameMessageReady
        return

    def __onIngameMessageReady(self, msg):
        if not self.__blockNewMessages:
            self.as_addMessageS(msg.getDict())
