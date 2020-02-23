# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/final_reward_state_machine.py
import logging
import weakref
import typing
from battle_pass_common import BattlePassRewardReason
from gui.impl.gen import R
from gui.battle_pass.battle_pass_helpers import showVideo
from gui.shared.event_dispatcher import showBattleVotingResultWindow, showBattlePassAwardsWindow
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import LobbySimpleEvent
if typing.TYPE_CHECKING:
    from skeletons.gui.game_control import IBattlePassController
_logger = logging.getLogger(__name__)
_LOCK_SOURCE_NAME = 'finalRewardStateMachine'

class _FinalStates(object):
    STOP = 0
    STARTED = 1
    IN_MIDDLE = 2
    PRE_FINAL = 3
    FINAL = 4
    PREVIEW = 5
    INTERRUPTED = 6


class FinalRewardStateMachine(object):
    __slots__ = ('__battlePassController', '__rewards', '__data', '__state')

    def __init__(self, battlePassController):
        super(FinalRewardStateMachine, self).__init__()
        self.__battlePassController = weakref.proxy(battlePassController)
        self.__rewards = None
        self.__data = None
        self.__state = _FinalStates.STOP
        return

    def init(self):
        if self.__battlePassController.isPlayerVoted():
            self.__state = _FinalStates.FINAL
        elif self.__state in (_FinalStates.FINAL, _FinalStates.INTERRUPTED):
            self.__state = _FinalStates.STOP

    def startFlow(self, rewards, data):
        if self.__state == _FinalStates.FINAL:
            return
        self.__rewards = rewards
        self.__data = data
        self.__state = _FinalStates.STARTED
        self.__lockOverlays()
        videoSource = self.__getVideoBeforeVoting()
        showVideo(videoSource, onVideoClosed=self.continueFlow, isAutoClose=True)

    def continueFlow(self, **kwargs):
        if self.__state == _FinalStates.STARTED:
            self.__state = _FinalStates.IN_MIDDLE
            showBattleVotingResultWindow(isOverlay=True)
        elif self.__state in (_FinalStates.IN_MIDDLE, _FinalStates.STOP):
            vote = kwargs.get('voteOption', 0)
            if vote == 0:
                self.__state = _FinalStates.STOP
                if self.__rewards is not None and self.__data is not None:
                    rewards, data = self.__rewards, self.__data
                    self.__rewards, self.__data = (None, None)
                    if data.get('reason') == BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS and self.__isEnoughDataForAwardsScreen(rewards):
                        data['callback'] = self.__unlockOverlays
                        showBattlePassAwardsWindow(rewards, data)
                    else:
                        self.__unlockOverlays()
                else:
                    self.__unlockOverlays()
            else:
                self.__state = _FinalStates.PRE_FINAL
                hasBattlePass = self.__battlePassController.isBought()
                video = self.__getVideoId(vote, hasBattlePass)
                showVideo(video, onVideoClosed=self.continueFlow, isAutoClose=True)
        elif self.__state == _FinalStates.PRE_FINAL:
            self.__addFinalRewardsData()
            rewards, data = self.__rewards, self.__data
            self.__rewards, self.__data = (None, None)
            data['callback'] = self.__unlockOverlays
            data['isFinalReward'] = True
            showBattlePassAwardsWindow(rewards, data)
            self.__state = _FinalStates.FINAL
        return

    def pauseFlow(self):
        if self.__state == _FinalStates.IN_MIDDLE:
            self.__state = _FinalStates.PREVIEW
            g_eventBus.addListener(LobbySimpleEvent.VEHICLE_PREVIEW_HIDDEN, self.__onHidePreview, EVENT_BUS_SCOPE.LOBBY)

    def unpauseFlow(self):
        if self.__state == _FinalStates.PREVIEW:
            self.__state = _FinalStates.IN_MIDDLE
            g_eventBus.removeListener(LobbySimpleEvent.VEHICLE_PREVIEW_HIDDEN, self.__onHidePreview, EVENT_BUS_SCOPE.LOBBY)

    def interruptFlow(self):
        self.__unlockOverlays()
        self.__state = _FinalStates.INTERRUPTED
        self.__rewards = None
        self.__data = None
        return

    @staticmethod
    def __getVideoId(choise, hasBattlePass):
        res = R.videos.battle_pass.dyn('c_{}_{}'.format(choise, 1 if hasBattlePass else 0))
        return res() if res.exists() else None

    @staticmethod
    def __getVideoBeforeVoting():
        return R.videos.battle_pass.before_voting()

    @staticmethod
    def __lockOverlays():
        ctx = {'source': _LOCK_SOURCE_NAME}
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.LOCK_OVERLAY_SCREEN, ctx), EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __unlockOverlays():
        ctx = {'source': _LOCK_SOURCE_NAME}
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.UNLOCK_OVERLAY_SCREEN, ctx), EVENT_BUS_SCOPE.LOBBY)

    def __addFinalRewardsData(self):
        vote = self.__battlePassController.getVoteOption()
        if not vote:
            return
        else:
            finalReward = self.__battlePassController.getFinalRewards()
            if vote not in finalReward:
                return
            needMedal = False
            if self.__rewards is None:
                self.__rewards = []
                needMedal = True
            if self.__data is None:
                self.__data = {'reason': 0,
                 'newState': 1,
                 'newLevel': 0,
                 'prevLevel': self.__battlePassController.getMaxLevel() - 1,
                 'prevState': 0}
            self.__rewards.append(finalReward[vote]['shared'])
            self.__rewards.append(finalReward[vote]['unique'])
            if self.__battlePassController.isBought():
                for key in finalReward.keys():
                    if key == vote:
                        continue
                    self.__rewards.append(finalReward[key]['shared'])

            elif needMedal:
                self.__rewards.append(self.__battlePassController.getFreeFinalRewardDict())
            return

    def __isEnoughDataForAwardsScreen(self, rewards=None):
        rewards = rewards or self.__rewards
        for reward in rewards:
            for bonus in reward.iterkeys():
                if bonus != 'dossier':
                    return True

        return False

    def __onHidePreview(self, _):
        g_eventBus.removeListener(LobbySimpleEvent.VEHICLE_PREVIEW_HIDDEN, self.__onHidePreview, EVENT_BUS_SCOPE.LOBBY)
        self.__state = _FinalStates.STOP
        self.continueFlow()
