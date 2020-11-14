# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/observers.py
import typing
from frameworks.state_machine import SingleStateObserver, StateEvent, StateObserversContainer, StringEvent
from gui.Scaleform.Waiting import Waiting
from gui.battle_pass.battle_pass_helpers import showVideo, isBattlePassBought
from gui.battle_pass.state_machine.states import FinalRewardStateID, FinalRewardEventID
from gui.impl.gen import R
from gui.shared.event_dispatcher import showBattleVotingResultWindow, showBattlePassAwardsWindow
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
if typing.TYPE_CHECKING:
    from gui.battle_pass.state_machine.delegator import FinalRewardLogic

def showWaiting():
    Waiting.show('draw_research_items')


def stopWaiting():
    Waiting.hide('draw_research_items')


class VideoBeforeStateObserver(SingleStateObserver):

    def onEnterState(self, event=None):
        videoSource = R.videos.battle_pass.dyn('before_voting_{}'.format(1 if isBattlePassBought() else 0))
        if not videoSource.exists():
            videoSource = R.videos.battle_pass.before_voting
        showVideo(videoSource, isAutoClose=True)


class VotingStateObserver(SingleStateObserver):
    __battlePassController = dependency.descriptor(IBattlePassController)

    def onEnterState(self, event=None):
        isVotingOpen = False
        if event is not None:
            isVotingOpen = event.getArgument('isVotingOpen')
        if not isVotingOpen:
            showBattleVotingResultWindow(isOverlay=True)
        return

    def onExitState(self, event=None):
        if isinstance(event, StringEvent) and event.token == FinalRewardEventID.ESCAPE:
            self.__battlePassController.onFinalRewardStateChange()


class VideoVotedStateObserver(SingleStateObserver):

    def onEnterState(self, event=None):
        voteOption = 0
        if event is not None:
            voteOption = event.getArgument('voteOption')
        videoSource = self.__getVideoId(voteOption, isBattlePassBought())
        showVideo(videoSource, isAutoClose=True)
        return

    def onExitState(self, event=None):
        showWaiting()

    @staticmethod
    def __getVideoId(choise, isBought):
        return R.videos.battle_pass.dyn('c_{}_{}'.format(choise, 1 if isBought else 0))


class PartRewardScreenStateObserver(SingleStateObserver):
    __battlePassController = dependency.descriptor(IBattlePassController)

    def onEnterState(self, event=None):
        logic = self.__battlePassController.getFinalRewardLogic()
        rewards, data = logic.getRewardsData()
        showBattlePassAwardsWindow(rewards, data)

    def onExitState(self, event=None):
        logic = self.__battlePassController.getFinalRewardLogic()
        logic.clearRewardsData()
        self.__battlePassController.onFinalRewardStateChange()


class FinalRewardScreenStateObserver(SingleStateObserver):
    __battlePassController = dependency.descriptor(IBattlePassController)

    def onEnterState(self, event=None):
        logic = self.__battlePassController.getFinalRewardLogic()
        rewards, data = logic.getRewardsData()
        rewards, data = self.__addFinalRewardsData(rewards, data)
        data['isFinalReward'] = True
        showBattlePassAwardsWindow(rewards, data, callback=stopWaiting)

    def onExitState(self, event=None):
        logic = self.__battlePassController.getFinalRewardLogic()
        logic.clearRewardsData()
        self.__battlePassController.onFinalRewardStateChange()

    @classmethod
    def __addFinalRewardsData(cls, rewards, data):
        vote = cls.__battlePassController.getVoteOption()
        if not vote:
            return (rewards, data)
        else:
            finalReward = cls.__battlePassController.getFinalRewards()
            if vote not in finalReward:
                return (rewards, data)
            needMedal = False
            if rewards is None:
                rewards = []
                needMedal = True
            if data is None:
                data = {'reason': 0,
                 'newState': 1,
                 'newLevel': 0,
                 'prevLevel': cls.__battlePassController.getMaxLevel() - 1,
                 'prevState': 0}
            rewards.append(finalReward[vote]['shared'])
            rewards.append(finalReward[vote]['unique'])
            if cls.__battlePassController.isBought():
                for key in finalReward.keys():
                    if key == vote:
                        continue
                    rewards.append(finalReward[key]['shared'])

            elif needMedal:
                rewards.append(cls.__battlePassController.getFreeFinalRewardDict())
            return (rewards, data)


class FinalStateMachineObserver(StateObserversContainer):
    __slots__ = ()

    def __init__(self):
        super(FinalStateMachineObserver, self).__init__(SingleStateObserver(FinalRewardStateID.LOBBY_WAIT), SingleStateObserver(FinalRewardStateID.LOBBY_FINAL), VideoBeforeStateObserver(FinalRewardStateID.VIDEO_BEFORE), VotingStateObserver(FinalRewardStateID.VOTING_SCREEN), VideoVotedStateObserver(FinalRewardStateID.VIDEO_VOTED), PartRewardScreenStateObserver(FinalRewardStateID.REWARD_PART), FinalRewardScreenStateObserver(FinalRewardStateID.REWARD_FINAL))
