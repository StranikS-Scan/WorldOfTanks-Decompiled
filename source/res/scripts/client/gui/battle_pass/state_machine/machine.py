# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/machine.py
import typing
import logging
from frameworks.state_machine import ConditionTransition
from frameworks.state_machine import StateMachine
from gui.battle_pass.state_machine import states, lockNotificationManager
from gui.battle_pass.state_machine.state_machine_helpers import isProgressionComplete, packToken
from shared_utils import first
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class BattlePassStateMachine(StateMachine):
    __slots__ = ('__rewards', '__data', '__rewardsToChoose', '__stylesToChoose', '__chosenStyle', '__manualFlow')

    def __init__(self):
        super(BattlePassStateMachine, self).__init__()
        self.__rewards = None
        self.__data = None
        self.__rewardsToChoose = []
        self.__stylesToChoose = []
        self.__chosenStyle = None
        self.__manualFlow = False
        return

    def stop(self):
        self.clearSelf()
        lockNotificationManager(False)
        super(BattlePassStateMachine, self).stop()

    def post(self, event):
        if self.isRunning():
            super(BattlePassStateMachine, self).post(event)

    @property
    def lobby(self):
        return self.getChildByIndex(0)

    @property
    def video(self):
        return self.getChildByIndex(1)

    @property
    def choice(self):
        return self.getChildByIndex(2)

    @property
    def reward(self):
        return self.getChildByIndex(3)

    def configure(self):
        lobbyState = states.LobbyState()
        choiceState = states.ChoiceState()
        rewardState = states.RewardState()
        videoState = states.VideoState()
        lobbyState.configure()
        choiceState.configure()
        rewardState.configure()
        lobbyState.lobbyWait.addTransition(ConditionTransition(self.__hasChoiceOption, priority=2), target=choiceState.choiceItem)
        lobbyState.lobbyWait.addTransition(ConditionTransition(self.__hasStyleReward, priority=1), target=videoState)
        lobbyState.lobbyWait.addTransition(ConditionTransition(self.__hasAnyReward, priority=0), target=rewardState.rewardAny)
        choiceState.choiceItem.addTransition(ConditionTransition(self.__hasStyleOption, priority=2), target=choiceState.choiceStyle)
        choiceState.choiceItem.addTransition(ConditionTransition(self.__hasStyleReward, priority=1), target=videoState)
        choiceState.choiceItem.addTransition(ConditionTransition(lambda _: True, priority=0), target=rewardState.rewardAny)
        choiceState.choiceStyle.addTransition(ConditionTransition(self.__hasStyleReward, priority=1), target=videoState)
        choiceState.choiceStyle.addTransition(ConditionTransition(lambda _: True, priority=0), target=rewardState.rewardAny)
        choiceState.previewScreen.addTransition(ConditionTransition(lambda _: True, priority=0), target=rewardState.rewardAny)
        videoState.addTransition(ConditionTransition(lambda _: True, priority=0), target=rewardState.rewardStyle)
        rewardState.rewardStyle.addTransition(ConditionTransition(self.__hasStyleOption, priority=1), target=choiceState.choiceStyle)
        rewardState.rewardAny.addTransition(ConditionTransition(self.__hasStyleOption, priority=2), target=choiceState.choiceStyle)
        rewardState.rewardAny.addTransition(ConditionTransition(isProgressionComplete, priority=1), target=lobbyState.lobbyFinal)
        rewardState.rewardAny.addTransition(ConditionTransition(lambda _: True, priority=0), target=lobbyState.lobbyWait)
        self.addState(lobbyState)
        self.addState(videoState)
        self.addState(choiceState)
        self.addState(rewardState)

    def hasActiveFlow(self):
        return not self.isStateEntered(states.BattlePassRewardStateID.LOBBY)

    def saveRewards(self, rewardsToChoose, stylesToChoose, defaultRewards, chosenStyle, data):
        self.__rewardsToChoose = rewardsToChoose
        self.__stylesToChoose = stylesToChoose
        self.__rewards = defaultRewards
        self.__chosenStyle = chosenStyle
        self.__data = data

    def setManualFlow(self):
        self.__manualFlow = True

    def getRewardsData(self):
        return (self.__rewards, self.__data)

    def addRewards(self, rewards):
        if self.__rewards:
            self.__rewards.append(rewards)
        else:
            self.__rewards = [rewards]

    def getNextRewardToChoose(self):
        return first(self.__rewardsToChoose)

    def hasRewardToChoose(self):
        return bool(self.__rewardsToChoose)

    def removeRewardToChoose(self, tokenID, isTaken):
        if isTaken:
            if tokenID in self.__rewardsToChoose:
                self.__rewardsToChoose.remove(tokenID)
        else:
            if self.__rewards is None:
                self.__rewards = []
            if not self.__manualFlow:
                for token in self.__rewardsToChoose:
                    self.__rewards.append(packToken(token))

            self.__rewardsToChoose = []
        return

    def getChosenStyleChapter(self):
        return self.__chosenStyle

    def addStyleToChoose(self, chapter):
        self.__stylesToChoose.append(chapter)

    def markStyleChosen(self, chapter):
        self.__chosenStyle = chapter
        if chapter in self.__stylesToChoose:
            self.__stylesToChoose.remove(chapter)

    def hasStyleToChoose(self):
        return bool(self.__stylesToChoose)

    def getLeftRewardsCount(self):
        return len(self.__rewardsToChoose)

    def clearStylesToChoose(self):
        self.__stylesToChoose = []

    def clearChosenStyle(self):
        self.__chosenStyle = None
        return

    def clearSelf(self):
        self.__rewards = None
        self.__data = None
        self.__rewardsToChoose = []
        self.__stylesToChoose = []
        self.__chosenStyle = None
        self.__manualFlow = False
        return

    def __hasStyleReward(self, *_):
        return self.__chosenStyle is not None

    def __hasChoiceOption(self, *_):
        return bool(self.__rewardsToChoose) or bool(self.__stylesToChoose)

    def __hasStyleOption(self, *_):
        return bool(self.__stylesToChoose) and not bool(self.__rewardsToChoose)

    def __hasAnyReward(self, *_):
        return bool(self.__rewards)
