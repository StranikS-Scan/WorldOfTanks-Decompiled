# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/auxiliary/buy_and_exchange_state_machine.py
import logging
import weakref
import typing
from enum import Enum
from frameworks.state_machine import State, StateFlags, StateMachine, StringEventTransition, StringEvent, BaseStateObserver
_logger = logging.getLogger(__name__)

class BuyAndExchangeStateEnum(Enum):
    BUY_CONTENT = 'buyContent'
    NEED_EXCHANGE = 'needExchange'
    EXCHANGE_CONTENT = 'exchangeContent'
    EXCHANGE_IN_PROCESS = 'exchangeInProcess'
    BUY_NOT_REQUIRED = 'buyNotRequired'
    EXCHANGE_NOT_REQUIRED = 'exchangeNotRequired'
    CAN_NOT_BUY = 'canNotBuy'
    GOLD_NOT_ENOUGH = 'goldNotEnough'


class BuyAndExchangeEventEnum(Enum):
    ACCEPT_CLICKED = 'acceptClicked'
    NEED_EXCHANGE = 'needExchange'
    START_EXCHANGE = 'startExchange'
    EXCHANGE_COMPLETED = 'exchangeCompleted'
    EXCHANGE_VALIDATION_ERROR = 'exchangeValidationError'
    CAN_BUY = 'canBuy'
    CAN_NOT_BUY = 'canNotBuy'


class BuyAndExchangeStateObserver(BaseStateObserver):
    __slots__ = ('__proxy', '__currentState')

    def __init__(self, handler, startState):
        self.__proxy = weakref.proxy(handler)
        self.__currentState = startState

    def getStateIDs(self):
        return tuple(BuyAndExchangeStateEnum)

    def getCurrentState(self):
        return self.__currentState

    def onStateChanged(self, stateID, flag, event=None):
        if flag:
            self.__currentState = stateID
            try:
                self.__proxy.stateChanged(stateID)
            except ReferenceError:
                _logger.error('View already delete! Please stop state machine')


class BuyAndExchangeStateMachine(object):

    def __init__(self, handler, stateToContent, startState=None):
        self.__stateMachine = StateMachine()
        self.__initState = startState if startState in BuyAndExchangeStateEnum else BuyAndExchangeStateEnum.BUY_CONTENT
        self.__observer = BuyAndExchangeStateObserver(handler, self.__initState)
        self.__stateToContentMap = stateToContent
        self._configuredStates(self.__initState)

    def run(self):
        if not self.__stateMachine.isRunning():
            self.__stateMachine.start()
            self.__stateMachine.connect(self.__observer)

    def stop(self):
        if self.__stateMachine.isRunning():
            self.__stateMachine.disconnect(self.__observer)
            self.__stateMachine.stop()

    def getCurrentState(self):
        return self.__observer.getCurrentState()

    def isCurrentState(self, state):
        return self.getCurrentState() == state

    def getCurrentContentType(self):
        return self.__stateToContentMap.get(self.getCurrentState(), '')

    def transit(self, event, condition=lambda : True):
        if self.__stateMachine.isRunning() and condition():
            self.__stateMachine.post(StringEvent(event))

    def _configuredStates(self, startState):
        states = {}
        for stateName in BuyAndExchangeStateEnum:
            flags = StateFlags.SINGULAR
            if stateName == startState:
                flags |= StateFlags.INITIAL
            states[stateName] = State(stateName, flags)

        states[BuyAndExchangeStateEnum.BUY_CONTENT].addTransition(StringEventTransition(BuyAndExchangeEventEnum.NEED_EXCHANGE), target=states[BuyAndExchangeStateEnum.NEED_EXCHANGE])
        states[BuyAndExchangeStateEnum.CAN_NOT_BUY].addTransition(StringEventTransition(BuyAndExchangeEventEnum.NEED_EXCHANGE), target=states[BuyAndExchangeStateEnum.NEED_EXCHANGE])
        states[BuyAndExchangeStateEnum.GOLD_NOT_ENOUGH].addTransition(StringEventTransition(BuyAndExchangeEventEnum.NEED_EXCHANGE), target=states[BuyAndExchangeStateEnum.EXCHANGE_CONTENT])
        states[BuyAndExchangeStateEnum.EXCHANGE_NOT_REQUIRED].addTransition(StringEventTransition(BuyAndExchangeEventEnum.NEED_EXCHANGE), target=states[BuyAndExchangeStateEnum.EXCHANGE_CONTENT])
        states[BuyAndExchangeStateEnum.BUY_CONTENT].addTransition(StringEventTransition(BuyAndExchangeEventEnum.START_EXCHANGE), target=states[BuyAndExchangeStateEnum.EXCHANGE_CONTENT])
        states[BuyAndExchangeStateEnum.CAN_NOT_BUY].addTransition(StringEventTransition(BuyAndExchangeEventEnum.START_EXCHANGE), target=states[BuyAndExchangeStateEnum.EXCHANGE_CONTENT])
        states[BuyAndExchangeStateEnum.GOLD_NOT_ENOUGH].addTransition(StringEventTransition(BuyAndExchangeEventEnum.START_EXCHANGE), target=states[BuyAndExchangeStateEnum.EXCHANGE_CONTENT])
        states[BuyAndExchangeStateEnum.EXCHANGE_NOT_REQUIRED].addTransition(StringEventTransition(BuyAndExchangeEventEnum.START_EXCHANGE), target=states[BuyAndExchangeStateEnum.EXCHANGE_CONTENT])
        states[BuyAndExchangeStateEnum.NEED_EXCHANGE].addTransition(StringEventTransition(BuyAndExchangeEventEnum.ACCEPT_CLICKED), target=states[BuyAndExchangeStateEnum.EXCHANGE_CONTENT])
        states[BuyAndExchangeStateEnum.EXCHANGE_CONTENT].addTransition(StringEventTransition(BuyAndExchangeEventEnum.ACCEPT_CLICKED), target=states[BuyAndExchangeStateEnum.EXCHANGE_IN_PROCESS])
        states[BuyAndExchangeStateEnum.EXCHANGE_IN_PROCESS].addTransition(StringEventTransition(BuyAndExchangeEventEnum.EXCHANGE_COMPLETED), target=states[BuyAndExchangeStateEnum.BUY_CONTENT])
        states[BuyAndExchangeStateEnum.EXCHANGE_IN_PROCESS].addTransition(StringEventTransition(BuyAndExchangeEventEnum.EXCHANGE_VALIDATION_ERROR), target=states[BuyAndExchangeStateEnum.EXCHANGE_CONTENT])
        states[BuyAndExchangeStateEnum.BUY_CONTENT].addTransition(StringEventTransition(BuyAndExchangeEventEnum.CAN_NOT_BUY), target=states[BuyAndExchangeStateEnum.CAN_NOT_BUY])
        states[BuyAndExchangeStateEnum.NEED_EXCHANGE].addTransition(StringEventTransition(BuyAndExchangeEventEnum.CAN_NOT_BUY), target=states[BuyAndExchangeStateEnum.CAN_NOT_BUY])
        states[BuyAndExchangeStateEnum.EXCHANGE_CONTENT].addTransition(StringEventTransition(BuyAndExchangeEventEnum.CAN_NOT_BUY), target=states[BuyAndExchangeStateEnum.GOLD_NOT_ENOUGH])
        states[BuyAndExchangeStateEnum.EXCHANGE_NOT_REQUIRED].addTransition(StringEventTransition(BuyAndExchangeEventEnum.CAN_NOT_BUY), target=states[BuyAndExchangeStateEnum.GOLD_NOT_ENOUGH])
        states[BuyAndExchangeStateEnum.NEED_EXCHANGE].addTransition(StringEventTransition(BuyAndExchangeEventEnum.CAN_BUY), target=states[BuyAndExchangeStateEnum.BUY_CONTENT])
        states[BuyAndExchangeStateEnum.EXCHANGE_CONTENT].addTransition(StringEventTransition(BuyAndExchangeEventEnum.CAN_BUY), target=states[BuyAndExchangeStateEnum.EXCHANGE_NOT_REQUIRED])
        states[BuyAndExchangeStateEnum.CAN_NOT_BUY].addTransition(StringEventTransition(BuyAndExchangeEventEnum.CAN_BUY), target=states[BuyAndExchangeStateEnum.BUY_CONTENT])
        states[BuyAndExchangeStateEnum.GOLD_NOT_ENOUGH].addTransition(StringEventTransition(BuyAndExchangeEventEnum.CAN_BUY), target=states[BuyAndExchangeStateEnum.EXCHANGE_NOT_REQUIRED])
        for state in states.values():
            self.__stateMachine.addState(state)
