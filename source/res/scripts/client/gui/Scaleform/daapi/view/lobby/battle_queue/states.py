# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_queue/states.py
import logging
from functools import partial
import typing
from frameworks.state_machine import StateFlags
from gui import SystemMessages
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import SFViewLobbyState, SubScopeSubLayerState, LobbyState, LobbyStateDescription, LobbyStateFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.prb_control import prbDispatcherProperty
from helpers.time_utils import getCurrentTimestamp
_logger = logging.getLogger(__name__)

def registerStates(machine):
    machine.addState(BattleQueueContainerState())


def registerTransitions(_):
    pass


@SubScopeSubLayerState.parentOf
class BattleQueueContainerState(LobbyState):
    STATE_ID = 'battleQueue'

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(InitialQueueState(StateFlags.INITIAL))
        lsm.addState(CommonBattleQueueState())
        lsm.addState(StrongholdsBattleQueueState())

    def registerTransitions(self):
        parent = self.getParent()
        for child in self.getChildrenStates():
            if isinstance(child, InitialQueueState):
                continue
            parent.addNavigationTransition(child)
            child.addGuardTransition(child, partial(self.__preventTransitionCheck, state=child))

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    def __preventTransitionCheck(self, event, state=None):
        from gui.impl.lobby.battle_results.states import PostBattleResultsEntryState
        allowedStates = [PostBattleResultsEntryState] + [ type(s) for s in self.getChildrenStates() ]
        if not state.isEntered():
            return False
        elif self.prbDispatcher is None or not self.prbDispatcher.getFunctionalState().isNavigationDisabled():
            return False
        else:
            targetID = event.targetStateID
            lsm = state.getMachine()
            target = lsm.getStateByID(targetID)
            prevent = not any((isinstance(target, cls) for cls in allowedStates))
            if prevent:
                SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error, priority='high')
            return prevent


@BattleQueueContainerState.parentOf
class InitialQueueState(LobbyState):
    STATE_ID = 'initial'

    def _onEntered(self, event):
        _logger.warning('%s state should never be entered. Enter specific battle queue states via .goTo method.', self.__class__.__name__)
        super(InitialQueueState, self)._onEntered(event)


@BattleQueueContainerState.parentOf
class CommonBattleQueueState(SFViewLobbyState):
    STATE_ID = VIEW_ALIAS.BATTLE_QUEUE
    VIEW_KEY = ViewKey(VIEW_ALIAS.BATTLE_QUEUE)

    def __init__(self, flags=LobbyStateFlags.UNDEFINED):
        super(CommonBattleQueueState, self).__init__(flags=flags)
        self.__createTime = None
        return

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.waiting.prebattle.battle_queue()))

    def serializeParams(self):
        return {'createTime': self.__createTime}

    def _getViewLoadCtx(self, event):
        return {'ctx': {'createTime': self.__createTime}}

    def _onEntered(self, event):
        self.__createTime = event.params.get('createTime', getCurrentTimestamp())
        super(CommonBattleQueueState, self)._onEntered(event)

    def _onExited(self):
        self.__createTime = None
        super(CommonBattleQueueState, self)._onExited()
        return


@BattleQueueContainerState.parentOf
class StrongholdsBattleQueueState(SFViewLobbyState):
    STATE_ID = VIEW_ALIAS.BATTLE_STRONGHOLDS_QUEUE
    VIEW_KEY = ViewKey(VIEW_ALIAS.BATTLE_STRONGHOLDS_QUEUE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.waiting.prebattle.battle_queue()))
