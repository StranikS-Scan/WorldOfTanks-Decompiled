# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/states.py
from frameworks.state_machine import ConditionTransition, StringEventTransition
from frameworks.state_machine import State, StateFlags
from frameworks.state_machine import StringEvent
from gui.battle_pass.battle_pass_helpers import isPlayerVoted
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import LobbySimpleEvent

class FinalRewardStateID(object):
    LOBBY = 'lobby'
    LOBBY_START = 'lobby.start'
    LOBBY_WAIT = 'lobby.wait'
    LOBBY_FINAL = 'lobby.final'
    VIDEO_BEFORE = 'video.before'
    VIDEO_VOTED = 'video.voted'
    VOTING = 'voting'
    VOTING_SCREEN = 'voting.screen'
    VOTING_PREVIEW = 'voting.preview'
    REWARD = 'reward'
    REWARD_PART = 'reward.part'
    REWARD_FINAL = 'reward.final'


class FinalRewardEventID(object):
    PROGRESSION_COMPLETE = 'lobby.event.progression_complete'
    VOTING_OPENED = 'voting.event.voting_opened'
    OPEN_PREVIEW = 'voting.event.open_preview'
    CLOSE_PREVIEW = 'voting.event.close_preview'
    OPEN_HANGAR = 'voting.event.open_hangar'
    ESCAPE = 'escape'
    NEXT = 'next'


class LobbyState(State):
    __slots__ = ()

    def __init__(self):
        super(LobbyState, self).__init__(stateID=FinalRewardStateID.LOBBY, flags=StateFlags.SINGULAR | StateFlags.INITIAL)

    @property
    def startState(self):
        return self.getChildByIndex(0)

    @property
    def waitState(self):
        return self.getChildByIndex(1)

    @property
    def finalState(self):
        return self.getChildByIndex(2)

    def configure(self):
        start = State(stateID=FinalRewardStateID.LOBBY_START, flags=StateFlags.INITIAL)
        wait = State(stateID=FinalRewardStateID.LOBBY_WAIT)
        final = State(stateID=FinalRewardStateID.LOBBY_FINAL, flags=StateFlags.FINAL)
        start.addTransition(ConditionTransition(isPlayerVoted), target=final)
        start.addTransition(ConditionTransition(isPlayerVoted, invert=True), target=wait)
        self.addChildState(start)
        self.addChildState(wait)
        self.addChildState(final)


class VotingState(State):
    __slots__ = ()

    def __init__(self):
        super(VotingState, self).__init__(stateID=FinalRewardStateID.VOTING, flags=StateFlags.SINGULAR)

    @property
    def votingScreen(self):
        return self.getChildByIndex(0)

    @property
    def previewScreen(self):
        return self.getChildByIndex(1)

    def configure(self):
        voting = State(stateID=FinalRewardStateID.VOTING_SCREEN, flags=StateFlags.INITIAL)
        preview = PreviewState()
        voting.addTransition(StringEventTransition(FinalRewardEventID.OPEN_PREVIEW, priority=3), target=preview)
        preview.addTransition(StringEventTransition(FinalRewardEventID.CLOSE_PREVIEW, priority=2), target=voting)
        self.addChildState(voting)
        self.addChildState(preview)


class PreviewState(State):
    __slots__ = ()

    def __init__(self):
        super(PreviewState, self).__init__(stateID=FinalRewardStateID.VOTING_PREVIEW)

    def _onEntered(self):
        g_eventBus.addListener(LobbySimpleEvent.VEHICLE_PREVIEW_HIDDEN, self.__onHidePreview, EVENT_BUS_SCOPE.LOBBY)

    def _onExited(self):
        g_eventBus.removeListener(LobbySimpleEvent.VEHICLE_PREVIEW_HIDDEN, self.__onHidePreview, EVENT_BUS_SCOPE.LOBBY)

    def __onHidePreview(self, _):
        machine = self.getMachine()
        if machine:
            machine.post(StringEvent(FinalRewardEventID.OPEN_HANGAR))


class RewardState(State):
    __slots__ = ()

    def __init__(self):
        super(RewardState, self).__init__(stateID=FinalRewardStateID.REWARD, flags=StateFlags.SINGULAR)

    @property
    def rewardPartial(self):
        return self.getChildByIndex(0)

    @property
    def rewardFinal(self):
        return self.getChildByIndex(1)

    def configure(self):
        part = State(stateID=FinalRewardStateID.REWARD_PART, flags=StateFlags.INITIAL)
        final = State(stateID=FinalRewardStateID.REWARD_FINAL)
        self.addChildState(part)
        self.addChildState(final)
