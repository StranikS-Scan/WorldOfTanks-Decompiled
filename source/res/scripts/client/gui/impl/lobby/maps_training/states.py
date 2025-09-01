# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/maps_training/states.py
import typing
import WWISE
from WeakMethod import WeakMethodProxy
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.view.lobby.battle_queue.states import BattleQueueContainerState
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.maps_training.maps_training_queue_view import MapsTrainingQueueView
from gui.impl.lobby.maps_training.maps_training_view import MapsTrainingView
from gui.impl.lobby.maps_training.sound_constants import MapsTrainingSound
from gui.lobby_state_machine.states import GuiImplViewLobbyState, SubScopeSubLayerState, LobbyStateFlags, LobbyState, LobbyStateDescription
from gui.lobby_state_machine.transitions import HijackTransition
from helpers import dependency
from helpers.time_utils import getCurrentTimestamp
from skeletons.gui.game_control import IMapsTrainingController

def registerStates(machine):
    machine.addState(MapsTrainingState())
    machine.addState(MapsTrainingQueueState())


def registerTransitions(machine):
    pass


@SubScopeSubLayerState.parentOf
class MapsTrainingState(GuiImplViewLobbyState):
    STATE_ID = 'mapsTraining'
    VIEW_KEY = ViewKey(R.views.lobby.maps_training.MapsTrainingPage())
    __mapsTrainingCtrl = dependency.descriptor(IMapsTrainingController)

    def __init__(self, flags=LobbyStateFlags.UNDEFINED):
        super(MapsTrainingState, self).__init__(MapsTrainingView, flags=flags, scope=ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.maps_training.mapSelection.title()))

    def registerStates(self):
        self.addChildState(EntryState(LobbyStateFlags.INITIAL | LobbyStateFlags.HANGAR))
        self.addChildState(SelectedState(LobbyStateFlags.HANGAR))

    def registerTransitions(self):
        entry = self.getMachine().getStateByCls(EntryState)
        selected = self.getMachine().getStateByCls(SelectedState)
        queue = self.getMachine().getStateByCls(MapsTrainingQueueState)
        entry.addNavigationTransition(selected, record=True)
        selected.addNavigationTransition(queue, record=True)
        from gui.impl.lobby.hangar.states import HangarState
        self.getParent().addTransition(HijackTransition(HangarState, WeakMethodProxy(self.__shouldHijack), transitionType=TransitionType.EXTERNAL), self)

    def _onEntered(self, event):
        super(MapsTrainingState, self)._onEntered(event)
        WWISE.WW_setState(MapsTrainingSound.GAMEMODE_GROUP, MapsTrainingSound.GAMEMODE_STATE)
        if self.__mapsTrainingCtrl.isValid() and event.targetStateID != SelectedState.STATE_ID:
            SelectedState.goTo(**self.__mapsTrainingCtrl.getPageCtx())

    def _onExited(self):
        WWISE.WW_setState(MapsTrainingSound.GAMEMODE_GROUP, MapsTrainingSound.GAMEMODE_DEFAULT)
        super(MapsTrainingState, self)._onExited()

    def __shouldHijack(self, _):
        return self.__mapsTrainingCtrl.isMapsTrainingEnabled and self.__mapsTrainingCtrl.isMapsTrainingPrbActive


@MapsTrainingState.parentOf
class EntryState(LobbyState):
    STATE_ID = 'entry'


@MapsTrainingState.parentOf
class SelectedState(LobbyState):
    STATE_ID = 'selected'
    __mapsTrainingCtrl = dependency.descriptor(IMapsTrainingController)

    def serializeParams(self):
        return self.__mapsTrainingCtrl.getPageCtx()

    def _onEntered(self, event):
        super(SelectedState, self)._onEntered(event)
        MapsTrainingSound.onSelectedMap(True)

    def _onExited(self):
        super(SelectedState, self)._onExited()
        MapsTrainingSound.onSelectedMap(False)


@BattleQueueContainerState.parentOf
class MapsTrainingQueueState(GuiImplViewLobbyState):
    STATE_ID = 'mapsTrainingQueue'
    VIEW_KEY = ViewKey(R.views.lobby.maps_training.MapsTrainingQueue())

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(MapsTrainingQueueState, self).__init__(MapsTrainingQueueView, ScopeTemplates.LOBBY_SUB_SCOPE, flags=flags)
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
        super(MapsTrainingQueueState, self)._onEntered(event)

    def _onExited(self):
        self.__createTime = None
        super(MapsTrainingQueueState, self)._onExited()
        return
