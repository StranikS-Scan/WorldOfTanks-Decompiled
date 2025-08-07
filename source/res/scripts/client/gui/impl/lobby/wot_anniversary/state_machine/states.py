# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/state_machine/states.py
import typing
from adisp import adisp_process
from frameworks.state_machine import StateFlags, State, StringEventTransition
from gui.impl.lobby.wot_anniversary.wot_anniversary_helpers import pushErrorSysMessage, showRegularRewardView, showProgressionRewardView
from gui.wot_anniversary.processors import WotAnniversaryOpenEnvelopeProcessor
from helpers import dependency
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from shared_utils import CONST_CONTAINER, nextTick
from skeletons.gui.system_messages import ISystemMessages
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.impl.lobby.wot_anniversary.state_machine.machine import WotAnniversaryStateMachine
    from gui.SystemMessages import ResultMsg

class WotAnniversaryStateID(CONST_CONTAINER):
    MAIN = 'main'
    MAIN_START = 'main.start'
    MAIN_REQUEST = 'main.request'
    MAIN_FINAL = 'main.final'
    ALBUM_REQUEST_SUCCESS = 'album.request.success'
    ALBUM_REQUEST_FAILED = 'album.request.failed'
    ALBUM_SLOT_UNLOCK = 'album.slot.unlock'
    ALBUM_PROGRESSION_INCREASE_COUNTER = 'album.progression.increase.counter'
    ALBUM_PROGRESSION_STAGE_UNLOCK = 'album.progression.stage.unlock'
    ALBUM_FIRST_PAGE_ENDED = 'album.first.page.ended'
    REWARD_REGULAR = 'reward.regular'
    REWARD_PROGRESSION = 'reward.progression'
    ENVELOPE_VIDEO = 'envelope.video'
    ENVELOPE_SKIP_VIDEO = 'envelope.skip.video'
    ENVELOPE_PREVIEW = 'envelope.preview'


class WotAnniversaryTransitionID(CONST_CONTAINER):
    MAIN_REQUEST = 'transition.main.request'
    ENVELOPE_PREVIEW = 'transition.envelope.preview'
    RESTART = 'transition.restart'


class MainState(State):

    def __init__(self):
        super(MainState, self).__init__(stateID=WotAnniversaryStateID.MAIN, flags=StateFlags.SINGULAR | StateFlags.INITIAL)

    @property
    def mainStart(self):
        return self.getChildByIndex(0)

    @property
    def mainRequest(self):
        return self.getChildByIndex(1)

    @property
    def mainFinal(self):
        return self.getChildByIndex(2)

    def configure(self):
        mainStart = State(stateID=WotAnniversaryStateID.MAIN_START, flags=StateFlags.INITIAL)
        mainRequest = MainRequestState()
        mainFinal = State(stateID=WotAnniversaryStateID.MAIN_FINAL, flags=StateFlags.FINAL)
        mainStart.addTransition(StringEventTransition(token=WotAnniversaryTransitionID.MAIN_REQUEST, priority=0), target=mainRequest)
        mainFinal.addTransition(StringEventTransition(token=WotAnniversaryTransitionID.RESTART, priority=0), target=mainStart)
        self.addChildState(mainStart)
        self.addChildState(mainRequest)
        self.addChildState(mainFinal)


class MainRequestState(State):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self):
        super(MainRequestState, self).__init__(stateID=WotAnniversaryStateID.MAIN_REQUEST)

    @adisp_process
    def _onEntered(self):
        machine = self.getMachine()
        if machine is None:
            return
        else:
            result = yield WotAnniversaryOpenEnvelopeProcessor().request()
            if result.success:
                self.__systemMessages.proto.serviceChannel.pushClientMessage(result.auxData, SCH_CLIENT_MSG_TYPE.WOT_ANNIVERSARY_REWARD)
            else:
                pushErrorSysMessage()
            machine.saveRequestResult(result)
            nextTick(machine.postStateEvent)()
            return


class AlbumRequestFailedState(State):

    def __init__(self):
        super(AlbumRequestFailedState, self).__init__(stateID=WotAnniversaryStateID.ALBUM_REQUEST_FAILED)

    def _onEntered(self):
        machine = self.getMachine()
        if machine is None:
            return
        else:
            nextTick(machine.postStateEvent)()
            return


class RewardRegularState(State):

    def __init__(self):
        super(RewardRegularState, self).__init__(stateID=WotAnniversaryStateID.REWARD_REGULAR)

    def _onEntered(self):
        machine = self.getMachine()
        if machine is None:
            return
        else:
            data = machine.getRequestResultData()
            bonuses = data.get('regularRewards')
            if not bonuses:
                return
            showRegularRewardView(bonuses=bonuses, parent=machine.albumView.getParentWindow(), closeCallback=machine.postStateEvent)
            return


class RewardProgressionState(State):

    def __init__(self):
        super(RewardProgressionState, self).__init__(stateID=WotAnniversaryStateID.REWARD_PROGRESSION)

    def _onEntered(self):
        machine = self.getMachine()
        if machine is None:
            return
        else:
            data = machine.getRequestResultData()
            bonuses = data.get('progressionRewards')
            reachedStageIdx = data.get('reachedStageIdx')
            if not bonuses or reachedStageIdx is None:
                return
            showProgressionRewardView(bonuses=bonuses, reachedStageIdx=reachedStageIdx, parent=machine.albumView.getParentWindow(), closeCallback=machine.postStateEvent)
            return


class AlbumSimpleState(State):

    def _onEntered(self):
        machine = self.getMachine()
        if machine is None:
            return
        else:
            nextTick(machine.postStateEvent)()
            return
