# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/game_messages_panel.py
import typing
import BattleReplay
from ReservesEvents import randomReservesEvents
from gui.Scaleform.daapi.view.meta.GameMessagesPanelMeta import GameMessagesPanelMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.battle_hints.controller import BattleHintComponent
from gui.battle_control.controllers.battle_hints.queues import BattleHintQueueParams
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from gui.Scaleform.daapi.view.battle.shared.game_messages_panel import PlayerMessageData
from gui.battle_results.components.common import makeEpicBattleFinishResultLabel
if typing.TYPE_CHECKING:
    from hints.battle.schemas.base import ClientHintModel

class EpicMessagePanel(BattleHintComponent, GameMessagesPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EpicMessagePanel, self).__init__(battleHintsQueueParams=BattleHintQueueParams(name='epic', withFadeOut=False))
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

    def onMessageStarted(self, messageType, modificator, id_):
        ctrl = self.sessionProvider.dynamic.gameNotifications
        if ctrl is not None:
            randomReservesEvents.hidePanel(True)
            ctrl.onMessagePlaybackStarted(messageType, {'id': id_,
             'modificator': modificator})
        return

    def onMessagePhaseStarted(self, messageType, modificator, id_):
        ctrl = self.sessionProvider.dynamic.gameNotifications
        if ctrl is not None:
            ctrl.onMessagePlaybackPhaseStarted(messageType, {'id': id_,
             'modificator': modificator})
        return

    def onMessageEnded(self, messageType, id_):
        ctrl = self.sessionProvider.dynamic.gameNotifications
        if ctrl is not None:
            ctrl.onMessagePlaybackEnded(messageType, {'id': id_})
        return

    def onMessageHiding(self, messageType, id_):
        ctrl = self.sessionProvider.dynamic.gameNotifications
        if ctrl is not None:
            randomReservesEvents.showPanel()
            ctrl.onMessagePlaybackHide(messageType, {'id': id_})
        return

    def _populate(self):
        super(EpicMessagePanel, self)._populate()
        ctrl = self.sessionProvider.dynamic.missions
        if ctrl is not None:
            ctrl.onIngameMessageReady += self.__onIngameMessageReady
        if BattleReplay.g_replayEvents.isPlaying:
            BattleReplay.g_replayEvents.onTimeWarpStart += self.as_clearMessagesS
        return

    def _dispose(self):
        super(EpicMessagePanel, self)._dispose()
        if BattleReplay.g_replayEvents.isPlaying:
            BattleReplay.g_replayEvents.onTimeWarpStart -= self.as_clearMessagesS
        ctrl = self.sessionProvider.dynamic.missions
        if ctrl is not None:
            ctrl.onIngameMessageReady -= self.__onIngameMessageReady
        return

    def _showHint(self, model, params):
        if model.uniqueName == 'epic.CaptureBase':
            ctrl = self.sessionProvider.dynamic.missions
            if ctrl is not None:
                params = params or {}
                ctrl.onSectorBaseCaptured(int(params.get('param1', 0)), params.get('param2', 'false') == 'true')
        return

    def _hideHint(self):
        pass

    def __onIngameMessageReady(self, msg):
        if not self.__blockNewMessages:
            self.as_addMessageS(msg.getDict())
