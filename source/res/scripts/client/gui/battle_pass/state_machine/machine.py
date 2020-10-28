# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/machine.py
import logging
from battle_pass_common import BattlePassRewardReason as RewardReason
from frameworks.state_machine import ConditionTransition, StringEventTransition
from frameworks.state_machine import State
from frameworks.state_machine import StateMachine
from gui.battle_pass.state_machine import states
from gui.battle_pass.state_machine.states import FinalRewardStateID, FinalRewardEventID
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class FinalRewardStateMachine(StateMachine):
    __slots__ = ('__rewards', '__data')

    def __init__(self):
        super(FinalRewardStateMachine, self).__init__()
        self.__rewards = None
        self.__data = None
        return

    @property
    def lobby(self):
        return self.getChildByIndex(0)

    @property
    def beforeVideo(self):
        return self.getChildByIndex(1)

    @property
    def voting(self):
        return self.getChildByIndex(2)

    @property
    def votedVideo(self):
        return self.getChildByIndex(3)

    @property
    def reward(self):
        return self.getChildByIndex(4)

    def configure(self):
        lobbyState = states.LobbyState()
        votingState = states.VotingState()
        rewardState = states.RewardState()
        beforeVideoState = State(stateID=FinalRewardStateID.VIDEO_BEFORE)
        votedVideoState = State(stateID=FinalRewardStateID.VIDEO_VOTED)
        lobbyState.configure()
        votingState.configure()
        rewardState.configure()
        lobbyState.waitState.addTransition(StringEventTransition(FinalRewardEventID.PROGRESSION_COMPLETE), target=beforeVideoState)
        lobbyState.waitState.addTransition(StringEventTransition(FinalRewardEventID.VOTING_OPENED), target=votingState.votingScreen)
        beforeVideoState.addTransition(StringEventTransition(FinalRewardEventID.NEXT), target=votingState.votingScreen)
        votingState.votingScreen.addTransition(ConditionTransition(self.__hasVoteOption, priority=2), target=votedVideoState)
        votingState.votingScreen.addTransition(ConditionTransition(self.__hasRewardsAfterPurchase, priority=1), target=rewardState.rewardPartial)
        votingState.votingScreen.addTransition(StringEventTransition(FinalRewardEventID.ESCAPE), target=lobbyState.waitState)
        votingState.previewScreen.addTransition(StringEventTransition(FinalRewardEventID.OPEN_HANGAR), target=lobbyState.waitState)
        votingState.previewScreen.addTransition(ConditionTransition(self.__hasRewardsAfterPurchase, priority=1), target=rewardState.rewardPartial)
        votedVideoState.addTransition(StringEventTransition(FinalRewardEventID.NEXT), target=rewardState.rewardFinal)
        rewardState.rewardPartial.addTransition(StringEventTransition(FinalRewardEventID.ESCAPE), target=lobbyState.waitState)
        rewardState.rewardFinal.addTransition(StringEventTransition(FinalRewardEventID.ESCAPE), target=lobbyState.finalState)
        self.addState(lobbyState)
        self.addState(beforeVideoState)
        self.addState(votingState)
        self.addState(votedVideoState)
        self.addState(rewardState)

    def saveRewards(self, rewards, data):
        self.__rewards = rewards
        self.__data = data

    def getRewardsData(self):
        return (self.__rewards, self.__data)

    def clearRewardsData(self):
        self.__rewards = None
        self.__data = None
        return

    def __hasRewardsAfterPurchase(self, _):
        if self.__data:
            startingMachineAfterPurchase = self.__data.get('reason') == RewardReason.PURCHASE_BATTLE_PASS_LEVELS
        else:
            startingMachineAfterPurchase = False
        return startingMachineAfterPurchase and self.__isEnoughDataForAwardsScreen(self.__rewards)

    @staticmethod
    def __hasVoteOption(event):
        return event and event.getArgument('voteOption')

    @staticmethod
    def __isEnoughDataForAwardsScreen(rewards=None):
        if rewards is None:
            return False
        else:
            for reward in rewards:
                for bonus in reward.iterkeys():
                    if bonus != 'dossier':
                        return True

            return False
