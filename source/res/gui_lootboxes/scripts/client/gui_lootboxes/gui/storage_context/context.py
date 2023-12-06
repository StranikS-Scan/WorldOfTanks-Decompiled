# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/storage_context/context.py
import typing
from enum import IntEnum
import Event
from gui.Scaleform.Waiting import Waiting
from gui.shared.utils.decorators import adisp_process
from gui_lootboxes.gui.bonuses.bonuses_helpers import prepareOpenResult
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootboxes_storage_view_model import States
from gui_lootboxes.gui.storage_context.lootboxes_state_machine import LootBoxesStorageStateMachine, LootBoxesStorageStateObserver, LootBoxesStorageStateMachineDescription, LootBoxesStorageEventEnum
from frameworks.state_machine import StringEvent
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from helpers import dependency
from skeletons.gui.game_control import IGuiLootBoxesController
from wg_async import AsyncScope
if typing.TYPE_CHECKING:
    from gui.SystemMessages import ResultMsg
    from gui.shared.gui_items.loot_box import LootBox

class ViewEvents(IntEnum):
    ON_OPEN_CLICK = 1
    ON_OPENING_FINISH = 2
    ON_CHILD_VIEW_CLOSED = 3
    ON_CHILD_VIEW_SKIP = 4


class GlobalEvents(IntEnum):
    OPEN_RESPONSE_RECEIVED = 1


class ReturnPlaces(IntEnum):
    TO_HANGAR = 0
    TO_SHOP = 1
    TO_CUSTOM = 2
    TO_SHARDS = 3


def _handlerOnOpenClick(eventData):
    lootBox, count = eventData
    return StringEvent(LootBoxesStorageEventEnum.GOTO_REQUEST, lootBox=lootBox, count=count)


def _handlerOpenningFinished(eventData):
    uniqueRewardsHandler, rewards = eventData
    return StringEvent(LootBoxesStorageEventEnum.GOTO_UNIQUE_REWARDING, uniqueRewardsHandler=uniqueRewardsHandler, rewards=rewards) if uniqueRewardsHandler else StringEvent(LootBoxesStorageEventEnum.GOTO_REWARDING, rewards=rewards)


def _handlerResponseReceived(result):
    return StringEvent(LootBoxesStorageEventEnum.GOTO_OPENING, result=result) if result and result.success else StringEvent(LootBoxesStorageEventEnum.GOTO_ERROR)


_VIEW_EVENTS_HANDLERS_MAP = {(ViewEvents.ON_OPEN_CLICK, States.STORAGE_VIEWING): _handlerOnOpenClick,
 (ViewEvents.ON_OPENING_FINISH, States.OPENING): _handlerOpenningFinished,
 (ViewEvents.ON_CHILD_VIEW_CLOSED, States.OPENING_ERROR): lambda *_: StringEvent(LootBoxesStorageEventEnum.GOTO_STORAGE),
 (ViewEvents.ON_CHILD_VIEW_CLOSED, States.REWARDING): lambda *_: StringEvent(LootBoxesStorageEventEnum.GOTO_STORAGE),
 (ViewEvents.ON_CHILD_VIEW_CLOSED, States.UNIQUE_REWARDING): lambda rewards: StringEvent(LootBoxesStorageEventEnum.GOTO_REWARDING, rewards=rewards),
 (ViewEvents.ON_CHILD_VIEW_SKIP, States.REWARDING): lambda *_: StringEvent(LootBoxesStorageEventEnum.GOTO_STORAGE),
 (ViewEvents.ON_CHILD_VIEW_SKIP, States.UNIQUE_REWARDING): lambda rewards: StringEvent(LootBoxesStorageEventEnum.GOTO_REWARDING, rewards=rewards)}
_GLOBAL_EVENT_HANDLERS_MAP = {(GlobalEvents.OPEN_RESPONSE_RECEIVED, States.REQUEST_TO_OPEN): _handlerResponseReceived}

@adisp_process('lootboxOpeninig')
@dependency.replace_none_kwargs(eventLootBoxesCtrl=IGuiLootBoxesController)
def _handleRequestToOpen(context, event, eventLootBoxesCtrl=None):
    lootBox, count = event.getArgument('lootBox'), event.getArgument('count')
    result = None
    if eventLootBoxesCtrl.isEnabled() and lootBox is not None and lootBox.isEnabled:
        result = yield LootBoxOpenProcessor(lootBox, count).request()
        prepareOpenResult(result)
    context.postGlobalEvent(GlobalEvents.OPEN_RESPONSE_RECEIVED, result)
    return


_STATE_ENTERED_HANDLERS = {States.REQUEST_TO_OPEN: _handleRequestToOpen}

class LootBoxesContext(object):
    __guiLootBoxesCtr = dependency.descriptor(IGuiLootBoxesController)
    __slots__ = ('__stateMachine', '__stateMachineObserver', '__currentState', 'onStateChanged', '__asyncScope', '__returnPlace')

    def __init__(self):
        super(LootBoxesContext, self).__init__()
        self.onStateChanged = Event.Event()
        self.__stateMachineObserver = LootBoxesStorageStateObserver()
        self.__stateMachine = LootBoxesStorageStateMachine(self.__stateMachineObserver)
        self.__currentState = LootBoxesStorageStateMachineDescription.INIT_STATE
        self.__asyncScope = AsyncScope()
        self.__returnPlace = ReturnPlaces.TO_HANGAR

    def init(self):
        Waiting.show('loadLootboxesStorage')
        self.__stateMachineObserver.handleStateChanged += self.__handleStateChanged
        self.__stateMachine.run()

    def viewReady(self):
        self.__guiLootBoxesCtr.getHangarOptimizer().enable()
        Waiting.hide('loadLootboxesStorage')

    def fini(self):
        self.__guiLootBoxesCtr.getHangarOptimizer().disable(needShowHangar=self.__returnPlace == ReturnPlaces.TO_HANGAR)
        self.__asyncScope.destroy()
        self.onStateChanged.clear()
        self.__stateMachine.stop()
        self.__stateMachineObserver.handleStateChanged -= self.__handleStateChanged
        self.__stateMachineObserver.clear()
        if Waiting.isOpened('loadLootboxesStorage'):
            Waiting.hide('loadLootboxesStorage')

    def postViewEvent(self, event, eventData):
        transit = _VIEW_EVENTS_HANDLERS_MAP.get((event, self.__currentState), lambda *_: None)(eventData)
        if transit is not None:
            self.__stateMachine.transit(transit)
        return

    def postGlobalEvent(self, event, eventData):
        transit = _GLOBAL_EVENT_HANDLERS_MAP.get((event, self.__currentState), lambda *_: None)(eventData)
        if transit is not None:
            self.__stateMachine.transit(transit)
        return

    def getCurrentState(self):
        return self.__currentState

    def getAsyncScope(self):
        return self.__asyncScope

    def setReturnPlace(self, returnPlace):
        self.__returnPlace = returnPlace

    def __handleStateChanged(self, stateID, event):
        self.__currentState = States(stateID)
        self.onStateChanged(stateID, event)
        handler = _STATE_ENTERED_HANDLERS.get(self.__currentState, None)
        if handler is not None and event is not None:
            handler(self, event)
        return
