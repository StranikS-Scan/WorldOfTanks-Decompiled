# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/gameplay_logic_blocks.py
import logging
import typing
from inspect import getmembers
from skeletons.gameplay import GameplayStateID, IGameplayLogic
from visual_script import ASPECT
from visual_script.block import Meta, Block, InitParam
from visual_script.dependency import dependencyImporter
from visual_script.slot_types import SLOT_TYPE
from visual_script.type import VScriptEnum
shared, events, dependency, state_machine = dependencyImporter('gui.shared', 'gui.shared.events', 'helpers.dependency', 'frameworks_common.state_machine')
_logger = logging.getLogger(__name__)

class GameplayLogicMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GameplayStateIDEnum(VScriptEnum):

    @classmethod
    def vs_name(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return GameplayStateID

    @classmethod
    def nameToIndex(cls, value):
        for idx, (_, member) in enumerate(getmembers(cls.vs_enum())):
            if member == value:
                return idx

    @classmethod
    def indexToName(cls, value):
        for idx, (name, _) in enumerate(getmembers(cls.vs_enum())):
            if idx == value:
                return name

    @classmethod
    def _vs_collectEnumEntries(cls):
        entriesData = {}
        for idx, (name, _) in enumerate(getmembers(cls.vs_enum())):
            if not name.startswith('_'):
                entriesData[name] = idx

        return entriesData

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT]


class GSMState(Block, GameplayLogicMeta, state_machine.BaseStateObserver):
    __gameplayLogic = dependency.descriptor(IGameplayLogic)

    def __init__(self, *args, **kwargs):
        super(GSMState, self).__init__(*args, **kwargs)
        self._isStateActive = self._makeDataOutputSlot('isActive', SLOT_TYPE.BOOL, None)
        self._onEnterState = self._makeEventOutputSlot('onEnterState')
        self._onExitState = self._makeEventOutputSlot('onExitState')
        stateIdx = self._getInitParams()
        self._stateName = GameplayStateIDEnum.indexToName(stateIdx)
        self._state = getattr(GameplayStateIDEnum.vs_enum(), self._stateName)
        return

    def captionText(self):
        return 'Gameplay State: ' + self._stateName

    @classmethod
    def initParams(cls):
        return [InitParam('GSM State', GameplayStateIDEnum.slotType(), 0)]

    def onStartScript(self):
        self.__gameplayLogic.addStateObserver(self)

    def onFinishScript(self):
        self.__gameplayLogic.removeStateObserver(self)

    def isObservingState(self, state):
        return state.getStateID() == self._state

    def onEnterState(self, state, event):
        self._isStateActive.setValue(True)
        self._onEnterState.call()

    def onExitState(self, state, event):
        self._isStateActive.setValue(False)
        self._onExitState.call()


class OnPrebattleHighlights(Block, GameplayLogicMeta):

    def __init__(self, *args, **kwargs):
        super(OnPrebattleHighlights, self).__init__(*args, **kwargs)
        self._subscribe = self._makeEventInputSlot('subscribe', self.__subscribe)
        self._unsubscribe = self._makeEventInputSlot('unsubscribe', self.__unsubscribe)
        self._onStart = self._makeEventOutputSlot('onStart')
        self._onEnded = self._makeEventOutputSlot('onEnded')

    def onFinishScript(self):
        self.__unsubscribe()

    def __subscribe(self):
        _logger.debug('OnPrebattleHighlights.subscribed')
        shared.g_eventBus.addListener(events.PrebattleEvent.ANIMATION_STARTED, self.__onAnimationStarted, scope=shared.EVENT_BUS_SCOPE.BATTLE)
        shared.g_eventBus.addListener(events.PrebattleEvent.ANIMATION_ENDED, self.__onAnimationEnded, scope=shared.EVENT_BUS_SCOPE.BATTLE)

    def __unsubscribe(self):
        _logger.debug('OnPrebattleHighlights.unsubscribed')
        shared.g_eventBus.removeListener(events.PrebattleEvent.ANIMATION_STARTED, self.__onAnimationStarted, scope=shared.EVENT_BUS_SCOPE.BATTLE)
        shared.g_eventBus.removeListener(events.PrebattleEvent.ANIMATION_ENDED, self.__onAnimationEnded, scope=shared.EVENT_BUS_SCOPE.BATTLE)

    def __onAnimationStarted(self, _):
        self._onStart.call()

    def __onAnimationEnded(self, _):
        self._onEnded.call()
