# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/states.py
from functools import partial
import typing
from battle_pass_common import get3DStyleProgressToken, BattlePassRewardReason
from frameworks.state_machine import ConditionTransition, StringEventTransition
from frameworks.state_machine import State, StateFlags, StateEvent
from gui.battle_pass.battle_pass_helpers import getStyleInfoForChapter, showVideo
from gui.battle_pass.state_machine import lockNotificationManager
from gui.battle_pass.state_machine.state_machine_helpers import isProgressionComplete, packToken
from gui.impl.gen import R
from gui.server_events.events_dispatcher import showBattlePass3dStyleChoiceWindow
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.event_dispatcher import showBattlePassRewardChoiceWindow, showBattlePassAwardsWindow
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.impl import INotificationWindowController
if typing.TYPE_CHECKING:
    from gui.battle_pass.state_machine.machine import BattlePassStateMachine

class BattlePassRewardStateID(CONST_CONTAINER):
    LOBBY = 'lobby'
    LOBBY_START = 'lobby.start'
    LOBBY_WAIT = 'lobby.wait'
    LOBBY_FINAL = 'lobby.final'
    VIDEO = 'video'
    CHOICE = 'choice'
    CHOICE_ITEM = 'choice.item'
    CHOICE_STYLE = 'choice.style'
    CHOICE_PREVIEW = 'choice.preview'
    REWARD = 'reward'
    REWARD_STYLE = 'reward.style'
    REWARD_ANY = 'reward.any'


class StateMachineEventID(object):
    OPEN_PREVIEW = 'choice.event.open_preview'
    CLOSE_PREVIEW = 'choice.event.close_preview'


class LobbyState(State):
    __slots__ = ()
    __notificationManager = dependency.descriptor(INotificationWindowController)
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self):
        super(LobbyState, self).__init__(stateID=BattlePassRewardStateID.LOBBY, flags=StateFlags.SINGULAR | StateFlags.INITIAL)

    @property
    def lobbyStart(self):
        return self.getChildByIndex(0)

    @property
    def lobbyWait(self):
        return self.getChildByIndex(1)

    @property
    def lobbyFinal(self):
        return self.getChildByIndex(2)

    def configure(self):
        lobbyStart = State(stateID=BattlePassRewardStateID.LOBBY_START, flags=StateFlags.INITIAL)
        lobbyWait = State(stateID=BattlePassRewardStateID.LOBBY_WAIT)
        lobbyFinal = State(stateID=BattlePassRewardStateID.LOBBY_FINAL, flags=StateFlags.FINAL)
        lobbyStart.addTransition(ConditionTransition(isProgressionComplete, priority=1), target=lobbyFinal)
        lobbyStart.addTransition(ConditionTransition(lambda _: True, priority=0), target=lobbyWait)
        self.addChildState(lobbyStart)
        self.addChildState(lobbyWait)
        self.addChildState(lobbyFinal)

    def _onEntered(self):
        lockNotificationManager(False, notificationManager=self.__notificationManager)
        self.__battlePass.onRewardSelectChange()

    def _onExited(self):
        lockNotificationManager(True, notificationManager=self.__notificationManager)


class ChoiceState(State):
    __slots__ = ()

    def __init__(self):
        super(ChoiceState, self).__init__(stateID=BattlePassRewardStateID.CHOICE, flags=StateFlags.SINGULAR)

    @property
    def choiceItem(self):
        return self.getChildByIndex(0)

    @property
    def choiceStyle(self):
        return self.getChildByIndex(1)

    @property
    def previewScreen(self):
        return self.getChildByIndex(2)

    def configure(self):
        choiceItem = ChoiceItemState()
        choiceStyle = ChoiceStyleState()
        preview = PreviewState()
        choiceStyle.addTransition(StringEventTransition(StateMachineEventID.OPEN_PREVIEW, priority=2), target=preview)
        preview.addTransition(StringEventTransition(StateMachineEventID.CLOSE_PREVIEW, priority=1), target=choiceStyle)
        self.addChildState(choiceItem)
        self.addChildState(choiceStyle)
        self.addChildState(preview)

    def _onExited(self):
        machine = self.getMachine()
        if machine is not None:
            if machine.getChosenStyleChapter() is None and machine.hasStyleToChoose():
                machine.clearStylesToChoose()
        return


class ChoiceItemState(State):
    __slots__ = ()

    def __init__(self):
        super(ChoiceItemState, self).__init__(stateID=BattlePassRewardStateID.CHOICE_ITEM, flags=StateFlags.INITIAL)

    def _onEntered(self):
        machine = self.getMachine()
        if machine is not None:
            if machine.hasRewardToChoose():
                showBattlePassRewardChoiceWindow()
            else:
                machine.post(StateEvent())
        return


class ChoiceStyleState(State):
    __slots__ = ()

    def __init__(self):
        super(ChoiceStyleState, self).__init__(stateID=BattlePassRewardStateID.CHOICE_STYLE)

    def _onEntered(self):
        showBattlePass3dStyleChoiceWindow()


class PreviewState(State):
    __slots__ = ()

    def __init__(self):
        super(PreviewState, self).__init__(stateID=BattlePassRewardStateID.CHOICE_PREVIEW)

    def _onEntered(self):
        g_eventBus.addListener(LobbySimpleEvent.VEHICLE_PREVIEW_HIDDEN, self.__onHidePreview, EVENT_BUS_SCOPE.LOBBY)

    def _onExited(self):
        g_eventBus.removeListener(LobbySimpleEvent.VEHICLE_PREVIEW_HIDDEN, self.__onHidePreview, EVENT_BUS_SCOPE.LOBBY)

    def __onHidePreview(self, _):
        machine = self.getMachine()
        if machine:
            machine.post(StateEvent())


class VideoState(State):
    __slots__ = ()

    def __init__(self):
        super(VideoState, self).__init__(stateID=BattlePassRewardStateID.VIDEO)

    def _onEntered(self):
        machine = self.getMachine()
        if machine is not None:
            chapter = machine.getChosenStyleChapter()
            intCD, level = getStyleInfoForChapter(chapter)
            videoSource = R.videos.battle_pass.dyn('c_{}_{}'.format(intCD, level))
            if not videoSource.exists():
                machine.post(StateEvent())
                return
            showVideo(videoSource, isAutoClose=True, onVideoClosed=partial(machine.post, StateEvent()))
        return


class RewardState(State):
    __slots__ = ()

    def __init__(self):
        super(RewardState, self).__init__(stateID=BattlePassRewardStateID.REWARD, flags=StateFlags.SINGULAR)

    @property
    def rewardStyle(self):
        return self.getChildByIndex(0)

    @property
    def rewardAny(self):
        return self.getChildByIndex(1)

    def configure(self):
        rewardStyle = RewardStyleState()
        rewardAny = RewardAnyState()
        rewardStyle.addTransition(ConditionTransition(lambda _: True, priority=0), target=rewardAny)
        self.addChildState(rewardStyle)
        self.addChildState(rewardAny)


class RewardStyleState(State):
    __slots__ = ()
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self):
        super(RewardStyleState, self).__init__(stateID=BattlePassRewardStateID.REWARD_STYLE, flags=StateFlags.INITIAL)

    def _onEntered(self):
        machine = self.getMachine()
        if machine is None:
            return
        else:
            chapter = machine.getChosenStyleChapter()
            _, machineData = machine.getRewardsData()
            if machineData is not None:
                oldLevel = machineData['prevLevel']
                newLevel = machineData['newLevel']
                oldChapter = self.__battlePass.getChapterByLevel(oldLevel)
                newChapter = self.__battlePass.getChapterByLevel(newLevel)
                isMaxLevel = newLevel == self.__battlePass.getMaxLevel()
                if chapter >= oldChapter and (oldChapter != newChapter or isMaxLevel):
                    machine.post(StateEvent())
                    return
            chapter = machine.getChosenStyleChapter()
            _, level = getStyleInfoForChapter(chapter)
            prevLevel, _ = self.__battlePass.getChapterLevelInterval(chapter)
            data = {'reason': BattlePassRewardReason.SELECT_STYLE,
             'prevLevel': prevLevel,
             'callback': partial(machine.post, StateEvent())}
            styleToken = get3DStyleProgressToken(self.__battlePass.getSeasonID(), chapter, level)
            rewards = packToken(styleToken)
            machine.clearChosenStyle()
            showBattlePassAwardsWindow([rewards], data)
            return


class RewardAnyState(State):
    __slots__ = ()
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self):
        super(RewardAnyState, self).__init__(stateID=BattlePassRewardStateID.REWARD_ANY)

    def _onEntered(self):
        machine = self.getMachine()
        if machine is None:
            return
        else:
            rewards, data = machine.getRewardsData()
            if rewards is None:
                machine.clearSelf()
                machine.post(StateEvent())
                return
            if data is None:
                data = {'reason': BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS,
                 'prevLevel': self.__battlePass.getCurrentLevel()}
            data['callback'] = partial(machine.post, StateEvent())
            chapter = machine.getChosenStyleChapter()
            _, level = getStyleInfoForChapter(chapter)
            if chapter is None:
                chapter = self.__battlePass.getChapterByLevel(data['prevLevel'])
                if 'newLevel' in data:
                    newLevel = data['newLevel'] + 1
                    if level is None and newLevel > self.__battlePass.getChapterLevelInterval(chapter)[1]:
                        level = self.__battlePass.getChapterStyleProgress(chapter)
            if level is not None:
                styleToken = get3DStyleProgressToken(self.__battlePass.getSeasonID(), chapter, level)
                rewards.append(packToken(styleToken))
                machine.clearChosenStyle()
            if not rewards:
                machine.clearSelf()
                machine.post(StateEvent())
                return
            if chapter and self.__battlePass.isFinalLevel(data.get('newLevel', 0)) and chapter < len(self.__battlePass.getChapterConfig()):
                machine.clearSelf()
                machine.addStyleToChoose(chapter + 1)
            showBattlePassAwardsWindow(rewards, data)
            return

    def _onExited(self):
        machine = self.getMachine()
        if machine is None:
            return
        else:
            if not machine.hasStyleToChoose():
                machine.clearSelf()
            return
