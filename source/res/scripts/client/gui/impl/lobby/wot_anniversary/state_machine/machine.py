# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/state_machine/machine.py
import logging
import typing
from account_helpers.AccountSettings import WotAnniversary15
from frameworks.state_machine import StateMachine, ConditionTransition, StateEvent, StringEvent, StringEventTransition, State
from gui.impl.lobby.wot_anniversary.state_machine import states
from gui.impl.lobby.wot_anniversary.state_machine.states import WotAnniversaryTransitionID, WotAnniversaryStateID
from gui.impl.lobby.wot_anniversary.wot_anniversary_helpers import getWotAnniversarySetting
if typing.TYPE_CHECKING:
    from typing import Optional, Dict
    from frameworks.wulf import View
    from gui.SystemMessages import ResultMsg
_logger = logging.getLogger(__name__)

class WotAnniversaryStateMachine(StateMachine):

    def __init__(self, mainView, firstPageLastDayID):
        super(WotAnniversaryStateMachine, self).__init__()
        self.__albumView = mainView
        self.__firstPageLastDayID = firstPageLastDayID
        self.__requestResult = None
        self.__envelopePreviewDayID = None
        return

    @property
    def albumView(self):
        return self.__albumView

    def stop(self):
        self.__albumView = None
        self.clearParams()
        super(WotAnniversaryStateMachine, self).stop()
        return

    def post(self, event):
        if self.isRunning():
            super(WotAnniversaryStateMachine, self).post(event)

    def clearParams(self):
        self.__requestResult = None
        self.__envelopePreviewDayID = None
        return

    def configure(self):
        mainState = states.MainState()
        envelopeVideoState = State(stateID=WotAnniversaryStateID.ENVELOPE_VIDEO)
        envelopeSkipVideoState = State(stateID=WotAnniversaryStateID.ENVELOPE_SKIP_VIDEO)
        envelopePreviewState = State(stateID=WotAnniversaryStateID.ENVELOPE_PREVIEW)
        rewardBasicState = states.RewardRegularState()
        rewardProgressionState = states.RewardProgressionState()
        albumRequestSuccessState = State(stateID=WotAnniversaryStateID.ALBUM_REQUEST_SUCCESS)
        albumRequestFailedState = states.AlbumRequestFailedState()
        albumSlotUnlockState = states.AlbumSimpleState(stateID=WotAnniversaryStateID.ALBUM_SLOT_UNLOCK)
        albumProgressionIncreaseCounterState = states.AlbumSimpleState(stateID=WotAnniversaryStateID.ALBUM_PROGRESSION_INCREASE_COUNTER)
        albumProgressionStageUnlockState = states.AlbumSimpleState(stateID=WotAnniversaryStateID.ALBUM_PROGRESSION_STAGE_UNLOCK)
        albumFirstPageEnded = State(stateID=WotAnniversaryStateID.ALBUM_FIRST_PAGE_ENDED)
        mainState.configure()
        mainState.mainRequest.addTransition(ConditionTransition(self.__isRequestResultSuccess, invert=True, priority=1), target=albumRequestFailedState)
        mainState.mainRequest.addTransition(ConditionTransition(self.__isRequestResultSuccess, priority=0), target=albumRequestSuccessState)
        albumRequestFailedState.addTransition(ConditionTransition(lambda _: True, priority=0), target=mainState.mainFinal)
        albumRequestSuccessState.addTransition(ConditionTransition(lambda _: True, priority=0), target=rewardBasicState)
        rewardBasicState.addTransition(ConditionTransition(self.__isAnimationsEnabled, priority=1), target=envelopeVideoState)
        rewardBasicState.addTransition(ConditionTransition(self.__isAnimationsEnabled, invert=True, priority=0), target=envelopeSkipVideoState)
        envelopeVideoState.addTransition(StringEventTransition(token=WotAnniversaryTransitionID.ENVELOPE_PREVIEW, priority=0), target=envelopePreviewState)
        envelopeSkipVideoState.addTransition(StringEventTransition(token=WotAnniversaryTransitionID.ENVELOPE_PREVIEW, priority=0), target=envelopePreviewState)
        envelopePreviewState.addTransition(ConditionTransition(self.__isProgressionIncreased, priority=2), target=albumProgressionIncreaseCounterState)
        envelopePreviewState.addTransition(ConditionTransition(self.__isFirstPageLastDayReached, priority=1), target=albumFirstPageEnded)
        envelopePreviewState.addTransition(ConditionTransition(lambda _: True, priority=0), target=albumSlotUnlockState)
        albumProgressionIncreaseCounterState.addTransition(ConditionTransition(self.__isProgressionRewardReceived, priority=2), target=rewardProgressionState)
        albumProgressionIncreaseCounterState.addTransition(ConditionTransition(self.__isFirstPageLastDayReached, priority=1), target=albumFirstPageEnded)
        albumProgressionIncreaseCounterState.addTransition(ConditionTransition(lambda _: True, priority=0), target=albumSlotUnlockState)
        rewardProgressionState.addTransition(ConditionTransition(self.__isFirstPageLastDayReached, priority=1), target=albumFirstPageEnded)
        rewardProgressionState.addTransition(ConditionTransition(lambda _: True, priority=0), target=albumProgressionStageUnlockState)
        albumProgressionStageUnlockState.addTransition(ConditionTransition(lambda _: True, priority=0), target=albumSlotUnlockState)
        albumSlotUnlockState.addTransition(ConditionTransition(lambda _: True, priority=0), target=mainState.mainFinal)
        albumFirstPageEnded.addTransition(ConditionTransition(self.__isProgressionRewardReceived, priority=1), target=albumProgressionStageUnlockState)
        albumFirstPageEnded.addTransition(ConditionTransition(lambda _: True, priority=0), target=albumSlotUnlockState)
        for state in (mainState,
         envelopeVideoState,
         envelopeSkipVideoState,
         envelopePreviewState,
         rewardBasicState,
         rewardProgressionState,
         albumRequestSuccessState,
         albumRequestFailedState,
         albumSlotUnlockState,
         albumProgressionIncreaseCounterState,
         albumProgressionStageUnlockState,
         albumFirstPageEnded):
            self.addState(state)

    def isFinalStateReached(self):
        return self.isStateEntered(WotAnniversaryStateID.MAIN_FINAL)

    def postStateEvent(self):
        self.post(StateEvent())

    def postMainRequestEvent(self):
        self.post(StringEvent(states.WotAnniversaryTransitionID.MAIN_REQUEST))

    def postEnvelopePreviewEvent(self, dayID):
        self.__envelopePreviewDayID = dayID
        self.post(StringEvent(states.WotAnniversaryTransitionID.ENVELOPE_PREVIEW))

    def restart(self):
        if not self.isFinalStateReached():
            _logger.info('Can not restart Wot Anniversary State Machine, current state is not Final.')
            return
        self.clearParams()
        self.post(StringEvent(states.WotAnniversaryTransitionID.RESTART))

    def getEnvelopePreviewDayID(self):
        return self.__envelopePreviewDayID

    def saveRequestResult(self, result):
        self.__requestResult = result

    def __isRequestResultSuccess(self, _):
        return False if self.__requestResult is None else self.__requestResult.success

    def getRequestResultData(self):
        return {} if self.__requestResult is None or self.__requestResult.auxData is None else self.__requestResult.auxData

    def __isProgressionRewardReceived(self, _):
        data = self.getRequestResultData()
        return bool(data.get('progressionRewards'))

    def __isProgressionIncreased(self, _):
        data = self.getRequestResultData()
        return data.get('isProgressionIncreased', False)

    def __isFirstPageLastDayReached(self, _):
        return self.__envelopePreviewDayID is not None and self.__envelopePreviewDayID == self.__firstPageLastDayID

    @staticmethod
    def __isAnimationsEnabled(_):
        return not getWotAnniversarySetting(WotAnniversary15.IS_ALBUM_ANIMATIONS_DISABLED)
