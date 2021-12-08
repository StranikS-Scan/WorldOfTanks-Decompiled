# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/style_preview.py
import logging
from CurrentVehicle import g_currentPreviewVehicle
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.vehicle_preview.sound_constants import STYLE_PREVIEW_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.meta.VehicleBasePreviewMeta import VehicleBasePreviewMeta
from gui.shared import event_dispatcher, events, event_bus_handlers, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.formatters import text_styles
from gui.shared.gui_items.customization.c11n_items import getGroupFullNameResourceID
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.game_control import IHeroTankController
from gui.prb_control.events_dispatcher import g_eventDispatcher
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
        self._style = None
        self.__vehicleCD = None
        self.__styleDescr = None
        self.__backCallback = None
        self.__destroyCallback = None
        self.__backBtnDescrLabel = None
        self.__selectedVehicleEntityId = None
        self.__initialize(ctx)
        g_currentPreviewVehicle.selectHeroTank(False)
        return

    def closeView(self):
        event_dispatcher.showHangar()

    def onBackClick(self):
        self.__destroyCallback = None
        self.__backCallback()
        return

    def _populate(self):
        super(VehicleStylePreview, self)._populate()
        self.__subscribe()
        self.__selectVehicle()
        self.__updateData()

    def _dispose(self):
        self.__unsubscribe()
        self.__unselectVehicle()
        if self.__destroyCallback is not None:
            self.__destroyCallback()
            self.__destroyCallback = None
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.VEHICLE_PREVIEW_HIDDEN), scope=EVENT_BUS_SCOPE.LOBBY)
        super(VehicleStylePreview, self)._dispose()
        return

    def _invalidate(self, ctx):
        self.__initialize(ctx)
        self.__selectVehicle()
        self.__updateData()

    def _createSelectableLogic(self):
        from new_year.custom_selectable_logic import WithoutNewYearObjectsSelectableLogic
        return WithoutNewYearObjectsSelectableLogic()

    def __subscribe(self):
        self.__hangarSpace.onSpaceCreate += self.__onHangarCreateOrRefresh
        self.addListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)

    def __unsubscribe(self):
        self.removeListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        self.__hangarSpace.onSpaceCreate -= self.__onHangarCreateOrRefresh

    def __initialize(self, ctx):
        self._style = ctx['style']
        self.__vehicleCD = ctx['itemCD']
        self.__styleDescr = ctx.get('styleDescr') % {'insertion_open': '',
         'insertion_close': ''}
        self.__backCallback = ctx.get('backCallback', event_dispatcher.showHangar)
        self.__destroyCallback = ctx.get('destroyCallback', None)
        self.__backBtnDescrLabel = ctx.get('backBtnDescrLabel', backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.personalAwards()))
        return

    def __selectVehicle(self):
        g_currentPreviewVehicle.selectVehicle(self.__vehicleCD, style=self._style)
        self.__selectedVehicleEntityId = g_currentPreviewVehicle.vehicleEntityID
        if not g_currentPreviewVehicle.isPresent() or self._style is None:
            event_dispatcher.showHangar()
        self.__heroTanksControl.setInteractive(False)
        return

    def __unselectVehicle(self):
        self.__heroTanksControl.setInteractive(True)
        g_currentPreviewVehicle.selectNoVehicle()
        g_currentPreviewVehicle.resetAppearance()
        self.__selectedVehicleEntityId = None
        return

    def __updateData(self):
        self.as_setDataS({'closeBtnLabel': backport.text(R.strings.vehicle_preview.header.closeBtn.label()),
         'backBtnLabel': backport.text(R.strings.vehicle_preview.header.backBtn.label()),
         'backBtnDescrLabel': self.__backBtnDescrLabel,
         'showCloseBtn': _SHOW_CLOSE_BTN,
         'showBackButton': _SHOW_BACK_BTN})
        self.as_setAdditionalInfoS({'objectSubtitle': text_styles.main(backport.text(getGroupFullNameResourceID(self._style.groupID))),
         'objectTitle': self._style.userName,
         'descriptionTitle': backport.text(R.strings.tooltips.vehiclePreview.historicalReference.title()),
         'descriptionText': self.__styleDescr})

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
