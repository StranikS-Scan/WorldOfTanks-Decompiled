# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/state_machine/states.py
import logging
import typing
from functools import partial
from adisp import adisp_process
from frameworks.state_machine import State, StateEvent, StateFlags, StringEvent, ConditionTransition, StringEventTransition
from one_time_gift.gui.messages import pushOTGNotActiveErrorNotification, pushOTGNotAvailableErrorNotification, pushOTGRewardReceivedErrorNotification
from one_time_gift.gui.shared import event_dispatcher as otg_event_dispatcher, processors as otg_processors
from one_time_gift.gui.state_machine import state_helpers as helpers
from one_time_gift_common.one_time_gift_constants import BranchListType, OTG_ERROR_CODES
if typing.TYPE_CHECKING:
    from one_time_gift.gui.state_machine.machine import OneTimeGiftStateMachine
    from typing import Optional
_logger = logging.getLogger(__name__)

class OTGEvent(object):
    ENTRY_POINT_CLICK = 'entry_point.click'
    INTRO_START = 'intro.start'
    INFO_CLICK = 'info.click'
    CONFIRM = 'confirm'
    ERROR = 'error'


class OTGStateID(object):
    ROOT = 'root'
    ROOT_START = 'root.start'
    ROOT_WAIT = 'root.wait'
    FINAL = 'final'
    ENTERED = 'entered'
    ENTERED_INITIAL = 'entered.initial'
    ERROR = 'error'
    INTRO = 'intro'
    INFO = 'info'
    SELECTION = 'bs'
    SELECTION_INITIAL = 'bs.initial'
    SELECTION_NEWBIE = 'bs.newbie'
    SELECTION_EMPTY = 'bs.newbie.empty'
    SELECTION_FULL = 'bs.full'
    SELECTION_HISTORY = 'bs.history'
    REWARD_BRANCH_NEWBIE = 'reward.branch.newbie'
    REWARD_BRANCH_FULL = 'reward.branch.full'
    REWARD_COLLECTOR = 'reward.collector'
    REWARD_ADDITIONAL = 'reward.additional'


class RouterState(State):

    def _onEntered(self, _):
        machine = self.getMachine()
        if machine is not None:
            machine.post(StateEvent())
        return


class RootState(State):

    def __init__(self):
        super(RootState, self).__init__(OTGStateID.ROOT, StateFlags.SINGULAR | StateFlags.INITIAL)

    @property
    def wait(self):
        return self.getChildByIndex(1)

    def configure(self):
        start = RouterState(OTGStateID.ROOT_START, StateFlags.INITIAL)
        wait = State(OTGStateID.ROOT_WAIT, StateFlags.SINGULAR)
        start.addTransition(ConditionTransition(lambda _: True), target=wait)
        self.addChildState(start)
        self.addChildState(wait)

    def _onEntered(self, event):
        machine = self.getMachine()
        if machine is not None:
            otg_event_dispatcher.closeOneTimeGiftWindow()
        super(RootState, self)._onEntered(event)
        return


class EnteredState(State):

    def __init__(self):
        super(EnteredState, self).__init__(OTGStateID.ENTERED, StateFlags.SINGULAR)

    @property
    def intro(self):
        return self.getChildByIndex(1)

    @property
    def rewardAdditional(self):
        return self.getChildByIndex(7)

    @property
    def error(self):
        return self.getChildByIndex(8)

    def configure(self, root):
        initial = RouterState(OTGStateID.ENTERED_INITIAL, StateFlags.INITIAL)
        intro = IntroState()
        info = InfoState()
        error = ErrorState()
        rewardBranchNewbie = NewbieBranchRewardState()
        rewardBranchFull = FullBranchRewardState()
        rewardCollector = CollectorsCompensationRewardState()
        rewardAdditional = AdditionalRewardsState()
        branchSelection = BranchSelectionRootState()
        branchSelection.configure(info, rewardBranchNewbie, rewardBranchFull, rewardAdditional)
        initial.addTransition(ConditionTransition(lambda _: helpers.isCollectorsCompensationReceived() or helpers.isFullListBranchReceived(), priority=2), target=rewardAdditional)
        initial.addTransition(ConditionTransition(helpers.isFullListPurchased, priority=1), target=rewardCollector)
        initial.addTransition(ConditionTransition(lambda _: True), target=branchSelection)
        rewardBranchNewbie.addTransition(ConditionTransition(helpers.isFullListBranchReceived, invert=True, priority=2), target=branchSelection.full)
        rewardBranchNewbie.addTransition(ConditionTransition(helpers.areAdditionalRewardsAvailable, priority=1), target=rewardAdditional)
        rewardBranchNewbie.addTransition(ConditionTransition(lambda _: True), target=self)
        rewardBranchFull.addTransition(ConditionTransition(helpers.areAdditionalRewardsAvailable, priority=1), target=rewardAdditional)
        rewardBranchFull.addTransition(ConditionTransition(lambda _: True), target=self)
        rewardCollector.addTransition(ConditionTransition(helpers.areAdditionalRewardsAvailable, priority=1), target=rewardAdditional)
        rewardCollector.addTransition(ConditionTransition(lambda _: True), target=self)
        rewardAdditional.addTransition(ConditionTransition(lambda _: True), target=root)
        intro.addTransition(ConditionTransition(lambda _: True), target=self)
        info.addTransition(ConditionTransition(lambda _: True), target=branchSelection.history)
        error.addTransition(ConditionTransition(lambda _: True), target=root)
        branchSelection.addTransition(ConditionTransition(lambda _: True), target=root)
        self.addChildState(initial)
        self.addChildState(intro)
        self.addChildState(info)
        self.addChildState(branchSelection)
        self.addChildState(rewardBranchNewbie)
        self.addChildState(rewardBranchFull)
        self.addChildState(rewardCollector)
        self.addChildState(rewardAdditional)
        self.addChildState(error)


class IntroBaseState(State):
    stateID = None
    showIntroVideo = False

    def __init__(self):
        super(IntroBaseState, self).__init__(self.stateID, StateFlags.SINGULAR)

    def _onEntered(self, event):
        machine = self.getMachine()
        ctx = event.getArgument('ctx')
        _logger.debug('IntroState entered, ctx=%s', ctx)
        if machine is not None:
            event = StateEvent(ctx=ctx)
            otg_event_dispatcher.showIntroWindow(onConfirmCallback=lambda : machine.post(event), onCloseCallback=lambda : machine.post(event), onErrorCallback=lambda **kwargs: machine.post(StringEvent(OTGEvent.ERROR, **kwargs)), showIntroVideo=self.showIntroVideo)
        return


class IntroState(IntroBaseState):
    stateID = OTGStateID.INTRO
    showIntroVideo = True


class InfoState(IntroBaseState):
    stateID = OTGStateID.INFO


class BranchSelectionRootState(State):

    def __init__(self):
        super(BranchSelectionRootState, self).__init__(OTGStateID.SELECTION, StateFlags.SINGULAR)

    @property
    def full(self):
        return self.getChildByIndex(3)

    @property
    def history(self):
        return self.getChildByIndex(4)

    def configure(self, infoState, rewardBranchNewbie, rewardBranchFull, rewardAdditional):
        initial = RouterState(OTGStateID.SELECTION_INITIAL, StateFlags.INITIAL)
        newbie = NewbieBranchSelectionState()
        newbieEmpty = NewbieBranchSelectionEmptyState()
        full = FullBranchSelectionState()
        history = State(OTGStateID.SELECTION_HISTORY, StateFlags.SHALLOW_HISTORY)
        newbie.configure(onInfoClickTarget=infoState, onConfirmTarget=rewardBranchNewbie, onCancelTarget=rewardAdditional)
        newbieEmpty.configure(onInfoClickTarget=infoState, onConfirmTarget=full, onCancelTarget=rewardAdditional)
        full.configure(onInfoClickTarget=infoState, onConfirmTarget=rewardBranchFull, onCancelTarget=rewardAdditional)
        initial.addTransition(ConditionTransition(lambda _: not helpers.isNewbie() or helpers.isNewbieBranchReceived(), priority=2), target=full)
        initial.addTransition(ConditionTransition(helpers.isNewbieListPurchased, priority=1), target=newbieEmpty)
        initial.addTransition(ConditionTransition(lambda _: True), target=newbie)
        self.addChildState(initial)
        self.addChildState(newbie)
        self.addChildState(newbieEmpty)
        self.addChildState(full)
        self.addChildState(history)


class BranchSelectionBaseState(State):
    stateID = None
    branchListType = None
    allVehiclesPurchased = False

    def __init__(self):
        super(BranchSelectionBaseState, self).__init__(self.stateID, StateFlags.SINGULAR)

    def configure(self, onInfoClickTarget, onConfirmTarget, onCancelTarget):
        self.addTransition(StringEventTransition(OTGEvent.INFO_CLICK, priority=1), target=onInfoClickTarget)
        self.addTransition(StringEventTransition(OTGEvent.CONFIRM, priority=1), target=onConfirmTarget)
        self.addTransition(ConditionTransition(helpers.areAdditionalRewardsAvailable), target=onCancelTarget)

    def _onEntered(self, _):
        machine = self.getMachine()
        if machine is not None:
            error = helpers.getAvailabilityError()
            if error:
                machine.post(StringEvent(OTGEvent.ERROR, error=error))
                return
            otg_event_dispatcher.showBranchSelectionWindow(self.branchListType, allVehiclesPurchased=self.allVehiclesPurchased, onConfirmCallback=lambda **kwargs: machine.post(StringEvent(OTGEvent.CONFIRM, **kwargs)), onCloseCallback=lambda : machine.post(StateEvent()), onErrorCallback=lambda **kwargs: machine.post(StringEvent(OTGEvent.ERROR, **kwargs)))
        return


class NewbieBranchSelectionState(BranchSelectionBaseState):
    stateID = OTGStateID.SELECTION_NEWBIE
    branchListType = BranchListType.NEWBIE


class NewbieBranchSelectionEmptyState(BranchSelectionBaseState):
    stateID = OTGStateID.SELECTION_EMPTY
    branchListType = BranchListType.NEWBIE
    allVehiclesPurchased = True


class FullBranchSelectionState(BranchSelectionBaseState):
    stateID = OTGStateID.SELECTION_FULL
    branchListType = BranchListType.ALL


class NewbieBranchRewardState(State):

    def __init__(self):
        super(NewbieBranchRewardState, self).__init__(stateID=OTGStateID.REWARD_BRANCH_NEWBIE, flags=StateFlags.SINGULAR)

    def _onEntered(self, event):
        machine = self.getMachine()
        rewards = event.getArgument('rewards')
        if machine is not None:
            if rewards:
                otg_event_dispatcher.showNewbieBranchRewardWindow(rewards=rewards, onCloseCallback=lambda : machine.post(StateEvent()))
            else:
                machine.post(StateEvent())
        return


class FullBranchRewardState(State):

    def __init__(self):
        super(FullBranchRewardState, self).__init__(stateID=OTGStateID.REWARD_BRANCH_FULL, flags=StateFlags.SINGULAR)

    def _onEntered(self, event):
        machine = self.getMachine()
        rewards = event.getArgument('rewards')
        if machine is not None:
            if rewards:
                otg_event_dispatcher.showFullBranchRewardWindow(rewards=rewards, onCloseCallback=lambda : machine.post(StateEvent()))
            else:
                machine.post(StateEvent())
        return


class CollectorsCompensationRewardState(State):

    def __init__(self):
        super(CollectorsCompensationRewardState, self).__init__(stateID=OTGStateID.REWARD_COLLECTOR, flags=StateFlags.SINGULAR)

    @adisp_process
    def _onEntered(self, _):
        result = yield otg_processors.OneTimeGiftCollectorsCompensationProcessor().request()
        machine = self.getMachine()
        if machine is None or not machine.isStateEntered(self.getStateID()):
            _logger.info('State %s was exited until additional reward screens could be shown', self.getStateID())
            return
        else:
            if result.success:
                otg_event_dispatcher.showCollectorsCompensationWindow(rewards=result.auxData, onCloseCallback=lambda : machine.post(StateEvent()))
            else:
                machine.post(StringEvent(OTGEvent.ERROR, error=result.userMsg))
            return


class AdditionalRewardsState(State):

    def __init__(self):
        super(AdditionalRewardsState, self).__init__(stateID=OTGStateID.REWARD_ADDITIONAL, flags=StateFlags.SINGULAR)

    @adisp_process
    def _onEntered(self, _):
        result = yield otg_processors.OneTimeGiftAdditionalRewardProcessor().request()
        machine = self.getMachine()
        if machine is None or not machine.isStateEntered(self.getStateID()):
            _logger.info('State %s was exited until additional reward screens could be shown', self.getStateID())
            return
        else:
            if result.success:
                self.__onRewardsReceived(result.auxData)
            else:
                machine.post(StringEvent(OTGEvent.ERROR, error=result.userMsg))
            return

    def __onRewardsReceived(self, rewards):
        if len(rewards) == 2 and rewards[0]:
            otg_event_dispatcher.showNewbieAdditionalRewardWindow(rewards=rewards[0], onCloseCallback=partial(self.__showFullAdditionalRewards, rewards[1]))
        else:
            self.__showFullAdditionalRewards(rewards[0])

    def __showFullAdditionalRewards(self, rewards):
        machine = self.getMachine()
        otg_event_dispatcher.showFullAdditionalRewardWindow(rewards=rewards, onCloseCallback=lambda : machine.post(StateEvent()))


class ErrorState(State):

    def __init__(self):
        super(ErrorState, self).__init__(OTGStateID.ERROR, StateFlags.SINGULAR)

    def _onEntered(self, event):
        machine = self.getMachine()
        if machine is None:
            return
        else:
            otg_event_dispatcher.closeOneTimeGiftWindow()
            errStr = event.getArgument('error')
            if errStr == OTG_ERROR_CODES.NOT_ACTIVE:
                pushOTGNotActiveErrorNotification()
            elif errStr == OTG_ERROR_CODES.REWARD_RECEIVED:
                pushOTGRewardReceivedErrorNotification()
            else:
                pushOTGNotAvailableErrorNotification()
            machine.post(StateEvent())
            return
