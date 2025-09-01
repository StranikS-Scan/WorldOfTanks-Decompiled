# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/playlists_states.py
from __future__ import absolute_import
import logging
from copy import deepcopy
import typing
from BWUtil import AsyncReturn
from WeakMethod import WeakMethodProxy
from frameworks.state_machine import StateFlags
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.hangar.dialogs.vehicle_playlists import showSaveBeforeLeavePlaylistDialog
from gui.impl.lobby.hangar.random.sound_manager import PLAY_LISTS_SOUND_SPACE
from gui.impl.lobby.hangar.states import HangarState, AllVehiclesState
from gui.lobby_state_machine.states import LobbyState, SubScopeSubLayerState, TopScopeTopLayerState, LobbyStateDescription
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.gui.game_control import IVehiclePlaylistsController
from sound_gui_manager import ViewSoundExtension
from wg_async import wg_async, BrokenPromiseError, AsyncEvent
from gui.shared.events import NavigationEvent
from gui.Scaleform.daapi.view.lobby.battle_queue.states import CommonBattleQueueState
_logger = logging.getLogger(__name__)

def registerStates(machine):
    machine.addState(EditVehiclePlaylistsState())


@TopScopeTopLayerState.parentOf
class SaveVehiclePlaylistConfirmState(LobbyState):
    STATE_ID = 'saveVehiclePlaylistConfirm'
    __vehiclePlaylistsCtrl = dependency.descriptor(IVehiclePlaylistsController)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(SaveVehiclePlaylistConfirmState, self).__init__(flags)
        self.__waitFuture = None
        self.onResultSet = AsyncEvent()
        return

    def registerTransitions(self):
        lsm = self.getMachine()
        self.addGuardTransition(lsm.getStateByCls(SaveVehiclePlaylistConfirmState), WeakMethodProxy(self.__preventTransition))

    def getNavigationDescription(self):
        return None

    @wg_async
    def waitForResult(self):
        self.__waitFuture = self.__waitFuture if self.__waitFuture is not None else showSaveBeforeLeavePlaylistDialog()
        try:
            self.onResultSet.clear()
            confirmed, data = yield self.__waitFuture
            action = None
            if data is not None:
                action = data.get('action', None)
            raise AsyncReturn((confirmed, action))
        finally:
            self.onResultSet.set()
            self.__waitFuture = None

        return

    @wg_async
    def _onEntered(self, event):
        try:
            confirmed, action = yield self.waitForResult()
            if confirmed:
                if action == 'save':
                    self.__vehiclePlaylistsCtrl.saveModifiedPlaylist()
                    self.__vehiclePlaylistsCtrl.clearModifiedPlaylist()
                    self.getMachine().post(event)
                elif action == 'discard':
                    self.__vehiclePlaylistsCtrl.discardModifiedPlaylist()
                    self.getMachine().post(event)
                else:
                    _logger.warning("Unsupported operation has been received'%s'!", action)
            else:
                TopScopeTopLayerState.goTo()
                return
            redirected = event.targetStateID != self.getStateID()
            if not redirected:
                TopScopeTopLayerState.goTo()
                return
        except BrokenPromiseError:
            _logger.debug('%r dialog closed without user decision.', self.__class__.__name__)
            TopScopeTopLayerState.goTo()

    def _onExited(self):
        self.onResultSet.set()
        if self.__waitFuture is not None:
            self.__waitFuture.cancel()
        return

    def __preventTransition(self, _):
        return self.__waitFuture is not None and self.__vehiclePlaylistsCtrl.isEnabled


@HangarState.parentOf
class EditVehiclePlaylistsState(LobbyState, EventsHandler):
    STATE_ID = 'editVehiclePlaylists'
    __vehiclePlaylistsCtrl = dependency.descriptor(IVehiclePlaylistsController)
    __soundExtension = ViewSoundExtension(PLAY_LISTS_SOUND_SPACE)
    __RESTRICTED_EVENTS = [events.PrbInvitesEvent.ACCEPT, events.PrbActionEvent.SELECT, events.PrbActionEvent.LEAVE]

    def __init__(self):
        super(EditVehiclePlaylistsState, self).__init__()
        self.__params = None
        self.__goOutForced = False
        return

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.editVehiclePlaylists()))

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(SaveVehiclePlaylistConfirmState())

    def registerTransitions(self):
        from gui.impl.lobby.vehicle_hub import OverviewState
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)
        lsm.getStateByCls(AllVehiclesState).addNavigationTransition(self, record=True)
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
        self.addGuardTransition(lsm.getStateByCls(SaveVehiclePlaylistConfirmState), WeakMethodProxy(self.__preventTransition))

    def serializeParams(self):
        return self.__params

    def _onEntered(self, event):
        super(EditVehiclePlaylistsState, self)._onEntered(event)
        self.__forceOut = False
        self._subscribe()
        playlistId = event.params.get('id')
        self.__params = deepcopy(event.params)
        self.__handleSwitchEnableFeature()
        playlistData = self.__vehiclePlaylistsCtrl.getPlaylistDataByID(playlistId)
        if playlistData:
            self.__vehiclePlaylistsCtrl.setInitialModifiedPlaylist(playlistId, playlistData)
        self.__soundExtension.initSoundManager()
        self.__soundExtension.startSoundSpace()

    def _onExited(self):
        self._unsubscribe()
        self.__soundExtension.destroySoundManager()
        self.__params = None
        super(EditVehiclePlaylistsState, self)._onExited()
        return

    def _getEvents(self):
        return ((self.__vehiclePlaylistsCtrl.onEnabledStatusChanged, self.__handleSwitchEnableFeature),)

    def _getRestrictions(self):
        return ((event, self.__handleRestrictedEvent, EVENT_BUS_SCOPE.LOBBY) for event in self.__RESTRICTED_EVENTS)

    def __preventTransition(self, event):
        if not self.__vehiclePlaylistsCtrl.isEnabled or self.__forceOut:
            return False
        if isinstance(event, NavigationEvent):
            if event.targetStateID in (self.getStateID(), CommonBattleQueueState.STATE_ID):
                return False
        return self.__vehiclePlaylistsCtrl.isModifiedPlaylistChanged

    def __handleSwitchEnableFeature(self, _=None):
        if not self.isEntered() or self.__vehiclePlaylistsCtrl.isEnabled:
            return
        HangarState.goTo()

    @wg_async
    def __handleRestrictedEvent(self, event=None):
        if not self.__preventTransition(event):
            SubScopeSubLayerState.goTo()
            raise AsyncReturn(True)
        SaveVehiclePlaylistConfirmState.goTo()
        state = self.getMachine().getStateByCls(SaveVehiclePlaylistConfirmState)
        if isinstance(state, SaveVehiclePlaylistConfirmState):
            yield state.onResultSet.wait()
        self.__forceOut = True
        SubScopeSubLayerState.goTo()
        raise AsyncReturn(True)
