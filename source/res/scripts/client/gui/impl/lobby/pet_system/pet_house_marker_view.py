# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pet_system/pet_house_marker_view.py
from Event import Event
from frameworks.state_machine import BaseStateObserver
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer, WindowStatus
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.pet_system.pet_house_marker_model import PetHouseMarkerModel
from gui.impl.pub import ViewImpl
from gui.lobby_state_machine.states import LobbyStateFlags
from gui.pet_system.pet_item_helper import PetItem
from gui.pet_system.pet_ui_settings import PetUISettings
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events as events_constants
from helpers import dependency
from pet_system_common import pet_constants
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.pet_system import IPetSystemController
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.prb_control.dispatcher import g_prbLoader
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.prb_control.entities.maps_training.pre_queue.entity import MapsTrainingEntity
from gui.Scaleform.framework.entities.sf_window import SFWindow

class HangarMarkerStatesObserver(BaseStateObserver):

    def __init__(self):
        super(HangarMarkerStatesObserver, self).__init__()
        self._state = None
        self.onMarkerState = Event()
        return

    def isObservingState(self, state):
        return state.getFlags() & LobbyStateFlags.HANGAR

    def onEnterState(self, state, event):
        self._state = state
        self.onMarkerState()

    def onExitState(self, state, event):
        self._state = None
        self.onMarkerState()
        return

    @property
    def currentState(self):
        return self._state


class PetHangarMarkerView(ViewImpl):
    __guiLoader = dependency.descriptor(IGuiLoader)
    _settingsCore = dependency.descriptor(ISettingsCore)
    __LAYERS_WITHOUT_MARKERS = {WindowLayer.FULLSCREEN_WINDOW, WindowLayer.OVERLAY, WindowLayer.TOP_SUB_VIEW}
    __ALIASES_WITHOUT_MARKERS = {PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY,
     PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY,
     PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY,
     PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY,
     VIEW_ALIAS.BATTLE_QUEUE,
     VIEW_ALIAS.BATTLE_STRONGHOLDS_QUEUE,
     VIEW_ALIAS.LOBBY_CUSTOMIZATION,
     VIEW_ALIAS.STYLE_PREVIEW,
     VIEW_ALIAS.VEHICLE_PREVIEW,
     VIEW_ALIAS.HERO_VEHICLE_PREVIEW}
    __ACTIVE_WINDOW_STATUSES = (WindowStatus.LOADING, WindowStatus.LOADED)

    def __init__(self, settings):
        settings.flags = ViewFlags.VIEW
        self._statesObserver = HangarMarkerStatesObserver()
        super(PetHangarMarkerView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(PetHangarMarkerView, self)._onLoading(*args, **kwargs)
        self._updateMarkerVisibility()
        self.__guiLoader.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged
        lsm = getLobbyStateMachine()
        lsm.connect(self._statesObserver)
        self._statesObserver.onMarkerState += self._updateMarkerVisibility

    def _finalize(self):
        super(PetHangarMarkerView, self)._finalize()
        self.__guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        lsm = getLobbyStateMachine()
        lsm.disconnect(self._statesObserver)
        self._statesObserver.clear()
        self._statesObserver = None
        return

    def _setMarkerVisible(self, value):
        pass

    def _canShowMarkers(self):
        windowsManager = self.__guiLoader.windowsManager
        dispatcher = g_prbLoader.getDispatcher()
        blockedByGameMode = issubclass(type(dispatcher.getEntity()), (MapsTrainingEntity,))
        blockedByWindow = len(windowsManager.findWindows(lambda w: w.layer in self.__LAYERS_WITHOUT_MARKERS and w.windowStatus in self.__ACTIVE_WINDOW_STATUSES)) > 0
        blockedByAlias = len(windowsManager.findWindows(lambda w: w.layer == WindowLayer.SUB_VIEW and w.windowStatus in self.__ACTIVE_WINDOW_STATUSES and isinstance(w, SFWindow) and w.loadParams.viewKey.alias in self.__ALIASES_WITHOUT_MARKERS)) > 0
        return not blockedByWindow and not blockedByAlias and not blockedByGameMode if self._statesObserver.currentState else False

    def _updateMarkerVisibility(self, *args, **kwargs):
        self._setMarkerVisible(self._canShowMarkers())

    def __onWindowStatusChanged(self, uniqueID, newStatus):
        if newStatus in (WindowStatus.LOADING, WindowStatus.LOADED, WindowStatus.DESTROYING):
            self._updateMarkerVisibility()


class PetHouseMarkerView(PetHangarMarkerView):
    __petController = dependency.descriptor(IPetSystemController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.mono.pet_system.pet_house_marker())
        settings.model = PetHouseMarkerModel()
        settings.args = args
        settings.kwargs = kwargs
        super(PetHouseMarkerView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(PetHouseMarkerView, self)._onLoading(*args, **kwargs)
        self.__update()

    def _getEvents(self):
        events = super(PetHouseMarkerView, self)._getEvents()
        return events + ((self.__petController.onUpdateActivePet, self.__update), (self.__petController.onUpdateUnlockedPetsIDs, self.__update), (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def _getListeners(self):
        events = super(PetHouseMarkerView, self)._getListeners()
        return events + ((events_constants.PetSystemEvent.SEEN_IN_STORAGE_PET_IDS_UPDATED, self.__update, EVENT_BUS_SCOPE.LOBBY),)

    @property
    def viewModel(self):
        return super(PetHouseMarkerView, self).getViewModel()

    def _setMarkerVisible(self, isVisible):
        with self.viewModel.transaction() as model:
            if model.getIsVisible() != isVisible:
                model.setIsVisible(isVisible)

    def __update(self, *_):
        with self.getViewModel().transaction() as tx:
            activePetId = self.__petController.getActivePet()
            if activePetId:
                nameId = PetItem.getCurrentNameId(activePetId)
                tx.setPetNameID(nameId)
            else:
                tx.setPetNameID(0)
            seenPetIDs = PetUISettings.getSeenInStoragePetIDs()
            petIDs = self.__petController.getUnlockedAndPromoPets()
            tx.setHasUpdate(any((petID not in seenPetIDs for petID in petIDs)))

    def __onServerSettingsChanged(self, diff):
        sysDiff = diff.get(pet_constants.PETS_SYSTEM_CONFIG, {})
        if pet_constants.PetPromoConsts.CONFIG_NAME in sysDiff:
            self.__update()
