# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/states.py
from functools import partial
import typing
from battle_pass_common import BattlePassRewardReason, get3DStyleProgressToken
from frameworks.state_machine import ConditionTransition, State, StateEvent, StateFlags
from gui.battle_pass.battle_pass_helpers import asBPVideoName, getStyleForChapter, getStyleInfoForChapter, makeChapterMediaName, makeProgressionStyleMediaName, showBPFullscreenVideo
from gui.battle_pass.state_machine import lockNotificationManager
from gui.battle_pass.state_machine.state_machine_helpers import isProgressionComplete, packToken, processRewardsToChoose
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.battle_pass_buy_view import WINDOW_IS_NOT_OPENED, g_BPBuyViewStates
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.event_dispatcher import showBattlePassAwardsWindow, showBattlePassBuyWindow, showBattlePassRewardsSelectionWindow
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.impl import INotificationWindowController
if typing.TYPE_CHECKING:
    from gui.battle_pass.state_machine.machine import BattlePassStateMachine
    from typing import Dict, List, Optional

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
        if g_BPBuyViewStates.chapterID != WINDOW_IS_NOT_OPENED:
            showBattlePassBuyWindow()

    def _onExited(self):
        lockNotificationManager(True, notificationManager=self.__notificationManager)


class ChoiceState(State):
    __slots__ = ()

    def __init__(self):
        super(ChoiceState, self).__init__(stateID=BattlePassRewardStateID.CHOICE, flags=StateFlags.SINGULAR)

    @property
    def choiceItem(self):
        return self.getChildByIndex(0)

    def configure(self):
        choiceItem = ChoiceItemState()
        self.addChildState(choiceItem)


class ChoiceItemState(State):
    __slots__ = ()

    def __init__(self):
        super(ChoiceItemState, self).__init__(stateID=BattlePassRewardStateID.CHOICE_ITEM, flags=StateFlags.INITIAL)

    def _onEntered(self):
        machine = self.getMachine()
        if machine is not None:
            _, data, _ = machine.getRewardsData()
            if machine.hasRewardToChoose():

                def onCloseCallback():
                    for token, isTaken in processRewardsToChoose(machine.getRewardsToChoose()).iteritems():
                        machine.removeRewardToChoose(token, isTaken)

                    machine.post(StateEvent())

                showBattlePassRewardsSelectionWindow(chapterID=data.get('chapter', 0), level=data.get('level', 0), onRewardsReceivedCallback=machine.extendRewards, onCloseCallback=onCloseCallback)
            else:
                machine.post(StateEvent())
        return


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
    __battlePass = dependency.descriptor(IBattlePassController)
    __slots__ = ()

    def __init__(self):
        super(VideoState, self).__init__(stateID=BattlePassRewardStateID.VIDEO)

    def _onEntered(self):
        machine = self.getMachine()
        if machine is not None:
            chapter = machine.getChosenStyleChapter()
            if chapter is not None:
                _, level = getStyleInfoForChapter(chapter)
                mediaName = makeProgressionStyleMediaName(chapter, level)
                showBPFullscreenVideo(asBPVideoName(mediaName), mediaName, partial(machine.post, StateEvent()))
            else:
                _, data, _ = machine.getRewardsData()
                chapterID = data.get('chapter')
                if self.__battlePass.isExtraChapter(chapterID):
                    mediaName = makeChapterMediaName(chapterID)
                    showBPFullscreenVideo(asBPVideoName(mediaName), mediaName, partial(machine.post, StateEvent()))
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
            chapterID = machine.getChosenStyleChapter()
            _, level = getStyleInfoForChapter(chapterID)
            style = getStyleForChapter(chapterID)
            additionalRewards, _, _ = machine.getRewardsData()
            needNotifyClosing = not additionalRewards
            if style is not None and style.getProgressionLevel() == style.getMaxProgressionLevel():
                machine.post(StateEvent())
                return
            prevLevel, _ = self.__battlePass.getChapterLevelInterval(chapterID)
            data = {'reason': BattlePassRewardReason.STYLE_UPGRADE,
             'chapter': chapterID,
             'prevLevel': prevLevel,
             'callback': partial(machine.post, StateEvent())}
            styleToken = get3DStyleProgressToken(self.__battlePass.getSeasonID(), chapterID, level)
            rewards = packToken(styleToken)
            machine.clearChapterStyle()
            showBattlePassAwardsWindow([rewards], data, needNotifyClosing=needNotifyClosing)
            return


class RewardAnyState(State):
    __slots__ = ('__needShowBuy',)
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self):
        self.__needShowBuy = False
        super(RewardAnyState, self).__init__(stateID=BattlePassRewardStateID.REWARD_ANY)

    def _onEntered(self):
        machine = self.getMachine()
        if machine is None:
            return
        else:
            rewards, data, packageRewards = machine.getRewardsData()
            if rewards is None and packageRewards is None:
                machine.clearSelf()
                machine.post(StateEvent())
                return
            if data is None:
                data = {'reason': BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS}
            data['callback'] = partial(self.__onAwardClose, data.get('chapter'), data.get('reason'))
            data['showBuyCallback'] = self.__onShowBuy
            chapter = machine.getChosenStyleChapter()
            if chapter is not None:
                _, level = getStyleInfoForChapter(chapter)
                styleToken = get3DStyleProgressToken(self.__battlePass.getSeasonID(), chapter, level)
                rewards.append(packToken(styleToken))
                machine.clearChapterStyle()
            if not rewards and not packageRewards:
                machine.clearSelf()
                machine.post(StateEvent())
                return
            showBattlePassAwardsWindow(rewards, data, packageRewards=packageRewards)
            return

    def _onExited(self):
        machine = self.getMachine()
        if machine is None:
            return
        else:
            chapterID = self.__battlePass.getCurrentChapterID()
            currentLevel = self.__battlePass.getCurrentLevel()
            if self.__battlePass.isFinalLevel(chapterID, currentLevel):
                machine.clearSelf()
                if not self.__battlePass.isDisabled() and not self.__needShowBuy:
                    showMissionsBattlePass(R.views.lobby.battle_pass.ChapterChoiceView())
            machine.clearManualFlow()
            return

    def __onAwardClose(self, chapterID, reason):
        machine = self.getMachine()
        if machine is not None:
            machine.post(StateEvent())
        if not self.__battlePass.isDisabled() and reason == BattlePassRewardReason.PURCHASE_BATTLE_PASS:
            showMissionsBattlePass(R.views.lobby.battle_pass.BattlePassProgressionsView(), chapterID)
        return

    def __onShowBuy(self):
        self.__needShowBuy = True
        machine = self.getMachine()
        if machine is not None:
            machine.clearSelf()
            machine.post(StateEvent())
        showBattlePassBuyWindow()
        return
