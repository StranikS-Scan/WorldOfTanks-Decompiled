# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/storage_context/lootboxes_state_machine.py
import logging
import typing
from enum import Enum
import Event
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootboxes_storage_view_model import States
from frameworks.state_machine import State, StateFlags, StateMachine, StringEventTransition, BaseStateObserver
if typing.TYPE_CHECKING:
    from frameworks.state_machine import StringEvent
_logger = logging.getLogger(__name__)

class LootBoxesStorageEventEnum(str, Enum):
    GOTO_REQUEST = 'GOTO_REQUEST'
    GOTO_OPENING = 'GOTO_OPENING'
    GOTO_ERROR = 'GOTO_ERROR'
    GOTO_UNIQUE_REWARDING = 'GOTO_UNIQUE_REWARDING'
    GOTO_REWARDING = 'GOTO_REWARDING'
    GOTO_STORAGE = 'GOTO_STORAGE'


class LootBoxesStorageStateObserver(BaseStateObserver):

    def __init__(self):
        super(LootBoxesStorageStateObserver, self).__init__()
        self.handleStateChanged = Event.Event()

    def clear(self):
        self.handleStateChanged.clear()

    def getStateIDs(self):
        return tuple((state.value for state in States))

    def onStateChanged(self, stateID, flag, event=None):
        if flag:
            self.handleStateChanged(stateID, event)


class LootBoxesStorageStateMachine(object):

    def __init__(self, observer):
        self.__stateMachine = StateMachine()
        self.__observer = observer
        for state in LootBoxesStorageStateMachineDescription.getStates():
            self.__stateMachine.addState(state)

    def run(self):
        if not self.__stateMachine.isRunning():
            self.__stateMachine.start()
            self.__stateMachine.connect(self.__observer)

    def stop(self):
        if self.__stateMachine.isRunning():
            self.__stateMachine.disconnect(self.__observer)
            self.__stateMachine.stop()

    def transit(self, event):
        if self.__stateMachine.isRunning():
            self.__stateMachine.post(event)


class LootBoxesStorageStateMachineDescription(object):
    INIT_STATE = States.STORAGE_VIEWING.value

    @classmethod
    def __getStateFromStateId(cls, stateId):
        flags = StateFlags.SINGULAR
        if stateId == cls.INIT_STATE:
            flags = flags | StateFlags.INITIAL
        return State(stateId, flags)

    @classmethod
    def getStates(cls):
        storageViewing = cls.__getStateFromStateId(States.STORAGE_VIEWING.value)
        requestToOpen = cls.__getStateFromStateId(States.REQUEST_TO_OPEN.value)
        opening = cls.__getStateFromStateId(States.OPENING.value)
        openingError = cls.__getStateFromStateId(States.OPENING_ERROR.value)
        uniqueRewarding = cls.__getStateFromStateId(States.UNIQUE_REWARDING.value)
        rewarding = cls.__getStateFromStateId(States.REWARDING.value)
        storageViewing.addTransition(StringEventTransition(LootBoxesStorageEventEnum.GOTO_REQUEST), target=requestToOpen)
        requestToOpen.addTransition(StringEventTransition(LootBoxesStorageEventEnum.GOTO_OPENING), target=opening)
        requestToOpen.addTransition(StringEventTransition(LootBoxesStorageEventEnum.GOTO_ERROR), target=openingError)
        opening.addTransition(StringEventTransition(LootBoxesStorageEventEnum.GOTO_UNIQUE_REWARDING), target=uniqueRewarding)
        opening.addTransition(StringEventTransition(LootBoxesStorageEventEnum.GOTO_REWARDING), target=rewarding)
        rewarding.addTransition(StringEventTransition(LootBoxesStorageEventEnum.GOTO_STORAGE), target=storageViewing)
        uniqueRewarding.addTransition(StringEventTransition(LootBoxesStorageEventEnum.GOTO_STORAGE), target=storageViewing)
        uniqueRewarding.addTransition(StringEventTransition(LootBoxesStorageEventEnum.GOTO_REWARDING), target=rewarding)
        openingError.addTransition(StringEventTransition(LootBoxesStorageEventEnum.GOTO_STORAGE), target=storageViewing)
        return (storageViewing,
         requestToOpen,
         opening,
         openingError,
         uniqueRewarding,
         rewarding)
