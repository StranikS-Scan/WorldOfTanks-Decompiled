# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/style_preview.py
import logging
from CurrentVehicle import g_currentPreviewVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.lobby.vehicle_preview.sound_constants import STYLE_PREVIEW_SOUND_SPACE
from gui.Scaleform.daapi.view.meta.VehicleBasePreviewMeta import VehicleBasePreviewMeta
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared import EVENT_BUS_SCOPE, event_bus_handlers, event_dispatcher, events, g_eventBus
from gui.shared.formatters import text_styles
from gui.shared.gui_items.customization.c11n_items import getGroupFullNameResourceID
from helpers import dependency
from preview_selectable_logic import PreviewSelectableLogic
from skeletons.gui.game_control import IHeroTankController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
_SHOW_CLOSE_BTN = False
_SHOW_BACK_BTN = True
_logger = logging.getLogger(__name__)

class VehicleStylePreview(LobbySelectableView, VehicleBasePreviewMeta):
    __background_alpha__ = 0.0
    __metaclass__ = event_bus_handlers.EventBusListener
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __heroTanksControl = dependency.descriptor(IHeroTankController)
    _COMMON_SOUND_SPACE = STYLE_PREVIEW_SOUND_SPACE

    def __init__(self, ctx=None):
        super(VehicleStylePreview, self).__init__(ctx)
        self.__ctx = ctx
        self._style = ctx['style']
        self.__vehicleCD = ctx['itemCD']
        self.__styleDescr = (ctx.get('styleDescr') or self._style.getDescription()) % {'insertion_open': '',
         'insertion_close': ''}
        self.__backCallback = ctx.get('backCallback', event_dispatcher.showHangar)
        self.__backBtnDescrLabel = ctx.get('backBtnDescrLabel', backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.personalAwards()))
        self.__topPanelData = ctx.get('topPanelData') or {}
        self.__selectedVehicleEntityId = None
        g_currentPreviewVehicle.selectHeroTank(ctx.get('isHeroTank', False))
        return

    def closeView(self):
        event_dispatcher.showHangar()

    def onBackClick(self):
        self.__backCallback()

    def setTopPanel(self):
        self.as_setTopPanelS(self.__topPanelData.get('linkage', ''))

    def _populate(self):
        self.setTopPanel()
        super(VehicleStylePreview, self)._populate()
        g_currentPreviewVehicle.selectVehicle(self.__vehicleCD, style=self._style)
        g_eventBus.handleEvent(events.CameraMoveEvent(events.CameraMoveEvent.ON_HANGAR_VEHICLE), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__selectedVehicleEntityId = g_currentPreviewVehicle.vehicleEntityID
        if not g_currentPreviewVehicle.isPresent() or self._style is None:
            event_dispatcher.showHangar()
        self.__hangarSpace.onSpaceCreate += self.__onHangarCreateOrRefresh
        self.addListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        self.__heroTanksControl.setInteractive(False)
        self.as_setDataS({'closeBtnLabel': backport.text(R.strings.vehicle_preview.header.closeBtn.label()),
         'backBtnLabel': backport.text(R.strings.vehicle_preview.header.backBtn.label()),
         'backBtnDescrLabel': self.__backBtnDescrLabel,
         'showCloseBtn': _SHOW_CLOSE_BTN,
         'showBackButton': _SHOW_BACK_BTN})
        self.as_setAdditionalInfoS({'objectSubtitle': text_styles.main(backport.text(getGroupFullNameResourceID(self._style.groupID))),
         'objectTitle': self._style.userName,
         'descriptionTitle': backport.text(R.strings.tooltips.vehiclePreview.historicalReference.title()),
         'descriptionText': self.__styleDescr})
        return

    def _dispose(self):
        self.__selectedVehicleEntityId = None
        self.removeListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__hangarSpace.onSpaceCreate -= self.__onHangarCreateOrRefresh
        self.__heroTanksControl.setInteractive(True)
        g_currentPreviewVehicle.selectNoVehicle()
        g_currentPreviewVehicle.resetAppearance()
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.VEHICLE_PREVIEW_HIDDEN), scope=EVENT_BUS_SCOPE.LOBBY)
        super(VehicleStylePreview, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_PY_ALIAS:
            viewPy.setData(**self.__topPanelData)
            viewPy.setParentCtx(**self.__ctx)

    def _createSelectableLogic(self):
        return PreviewSelectableLogic()

    def __onVehicleLoading(self, ctxEvent):
        isVehicleLoadingStarted = ctxEvent.ctx['started']
        if isVehicleLoadingStarted:
            _logger.debug('Too early VEHICLE_LOADING handler call.')
            return
        elif ctxEvent.ctx['intCD'] != self.__vehicleCD:
            _logger.warning('VEHICLE_LOADING handler: incompatible "intCD" parameter.')
            return
        elif ctxEvent.ctx['vEntityId'] != self.__selectedVehicleEntityId:
            _logger.warning('VEHICLE_LOADING handler: incompatible "vEntityId" parameter.')
            return
        else:
            self.removeListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
            self.__selectedVehicleEntityId = None
            return

    def __onHangarCreateOrRefresh(self):
        self.__handleWindowClose()
        g_eventDispatcher.loadHangar()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_VEHICLE_PREVIEW, EVENT_BUS_SCOPE.LOBBY)
    def __handleWindowClose(self, event=None):
        if event is not None:
            if event.ctx.get('back', True):
                self.onBackClick()
            elif event.ctx.get('close', False):
                self.closeView()
        self.destroy()
        return
