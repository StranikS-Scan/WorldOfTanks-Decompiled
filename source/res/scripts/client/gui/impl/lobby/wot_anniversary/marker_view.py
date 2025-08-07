# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/marker_view.py
from CurrentVehicle import g_currentPreviewVehicle
from frameworks.wulf import ViewSettings
from frameworks.wulf import WindowLayer, WindowStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.marker_view_model import MarkerViewModel
from gui.impl.pub import ViewImpl
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.maps_training.pre_queue.entity import MapsTrainingEntity
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.wot_anniversary import IWotAnniversaryController

class WotAnniversaryMarkerView(ViewImpl):
    __wotAnniversaryController = dependency.descriptor(IWotAnniversaryController)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __LAYERS_WITHOUT_MARKERS = {WindowLayer.FULLSCREEN_WINDOW,
     WindowLayer.TOP_WINDOW,
     WindowLayer.OVERLAY,
     WindowLayer.TOP_SUB_VIEW}
    __ALIASES_WITHOUT_MARKERS = {PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY,
     PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY,
     PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY,
     PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY,
     VIEW_ALIAS.BATTLE_QUEUE,
     VIEW_ALIAS.LOBBY_CUSTOMIZATION,
     VIEW_ALIAS.STYLE_PREVIEW,
     VIEW_ALIAS.VEHICLE_PREVIEW,
     VIEW_ALIAS.HERO_VEHICLE_PREVIEW}
    __ACTIVE_WINDOW_STATUSES = (WindowStatus.LOADING, WindowStatus.LOADED)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wot_anniversary.MarkerView(), model=MarkerViewModel(), args=args, kwargs=kwargs)
        super(WotAnniversaryMarkerView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WotAnniversaryMarkerView, self)._onLoading(*args, **kwargs)
        self.__updateMarker()

    def _getEvents(self):
        events = super(WotAnniversaryMarkerView, self)._getEvents()
        return events + ((self.__guiLoader.windowsManager.onWindowStatusChanged, self.__onWindowStatusChanged),
         (g_currentPreviewVehicle.onSelected, self.__onPreviewVehicleSelected),
         (self.__wotAnniversaryController.onSettingsChanged, self.__onSettingsChanged),
         (self.__wotAnniversaryController.onStartDateReached, self.__onActionByDate),
         (self.__wotAnniversaryController.onNextEnvelopeArrived, self.__onActionByDate),
         (self.__wotAnniversaryController.onEndDateReached, self.__onActionByDate))

    def _getCallbacks(self):
        return (('tokens', self.__onTokenReceived),)

    def __setMarkerVisible(self, isVisible):
        with self.viewModel.transaction() as model:
            if model.getIsVisible() != isVisible:
                model.setIsVisible(isVisible)
                if isVisible:
                    self.__updateMarker()

    def __canShowMarkers(self):
        windowsManager = self.__guiLoader.windowsManager
        dispatcher = g_prbLoader.getDispatcher()
        blockedByGameMode = issubclass(type(dispatcher.getEntity()), (MapsTrainingEntity,))
        blockedByWindow = len(windowsManager.findWindows(lambda w: w.layer in self.__LAYERS_WITHOUT_MARKERS and w.windowStatus in self.__ACTIVE_WINDOW_STATUSES)) > 0
        blockedByAlias = len(windowsManager.findWindows(lambda w: w.layer == WindowLayer.SUB_VIEW and w.windowStatus in self.__ACTIVE_WINDOW_STATUSES and isinstance(w, SFWindow) and w.loadParams.viewKey.alias in self.__ALIASES_WITHOUT_MARKERS)) > 0
        return not blockedByWindow and not blockedByAlias and not blockedByGameMode

    def __updateMarker(self):
        availableEnvelops = self.__wotAnniversaryController.getAvailableEnvelops()
        with self.viewModel.transaction() as model:
            model.setIsVisible(availableEnvelops and self.__wotAnniversaryController.isEnabled() and self.__canShowMarkers())
            model.setAvailableEnvelopesAmount(availableEnvelops)

    def __onPreviewVehicleSelected(self):
        self.__setMarkerVisible(g_currentPreviewVehicle.item is None)
        return

    def __updateMarkerVisibility(self):
        self.__setMarkerVisible(self.__canShowMarkers())

    def __onWindowStatusChanged(self, _, newStatus):
        if newStatus in (WindowStatus.LOADING, WindowStatus.LOADED, WindowStatus.DESTROYING):
            self.__updateMarkerVisibility()

    def __onTokenReceived(self, diff):
        if self.__wotAnniversaryController.config.dayToken in diff:
            self.__updateMarker()

    def __onSettingsChanged(self):
        self.__updateMarker()

    def __onActionByDate(self):
        self.__updateMarker()
