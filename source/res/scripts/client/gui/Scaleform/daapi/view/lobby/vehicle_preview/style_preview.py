# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/style_preview.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
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
from preview_selectable_logic import PreviewSelectableLogic
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
_SHOW_CLOSE_BTN = False
_SHOW_BACK_BTN = True

class VehicleStylePreview(LobbySelectableView, VehicleBasePreviewMeta):
    __background_alpha__ = 0.0
    __metaclass__ = event_bus_handlers.EventBusListener
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    _COMMON_SOUND_SPACE = STYLE_PREVIEW_SOUND_SPACE

    def __init__(self, ctx=None):
        super(VehicleStylePreview, self).__init__(ctx)
        self.__vehicleCD = ctx['itemCD']
        self.__style = ctx['style']
        self.__styleDescr = ctx.get('styleDescr')
        self.__backCallback = ctx.get('backCallback', event_dispatcher.showHangar)
        self.__backBtnDescrLabel = ctx.get('backBtnDescrLabel', backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.personalAwards()))

    def closeView(self):
        event_dispatcher.showHangar()

    def onBackClick(self):
        self.__backCallback()

    def _populate(self):
        super(VehicleStylePreview, self)._populate()
        g_currentPreviewVehicle.selectVehicleWithoutHeroTankUpdate(self.__vehicleCD)
        if not g_currentPreviewVehicle.isPresent() or self.__style is None:
            event_dispatcher.showHangar()
        self.__hangarSpace.onSpaceCreate += self.__onHangarCreateOrRefresh
        self.addListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        self.as_setDataS({'closeBtnLabel': backport.text(R.strings.vehicle_preview.header.closeBtn.label()),
         'backBtnLabel': backport.text(R.strings.vehicle_preview.header.backBtn.label()),
         'backBtnDescrLabel': self.__backBtnDescrLabel,
         'showCloseBtn': _SHOW_CLOSE_BTN,
         'showBackButton': _SHOW_BACK_BTN})
        self.as_setAdditionalInfoS({'objectSubtitle': text_styles.main(backport.text(getGroupFullNameResourceID(self.__style.groupID))),
         'objectTitle': self.__style.userName,
         'descriptionTitle': backport.text(R.strings.tooltips.vehiclePreview.historicalReference.title()),
         'descriptionText': self.__styleDescr})
        return

    def _dispose(self):
        self.removeListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__hangarSpace.onSpaceCreate -= self.__onHangarCreateOrRefresh
        g_currentPreviewVehicle.selectNoVehicle()
        g_currentPreviewVehicle.resetAppearance()
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.VEHICLE_PREVIEW_HIDDEN), scope=EVENT_BUS_SCOPE.LOBBY)
        super(VehicleStylePreview, self)._dispose()

    def _createSelectableLogic(self):
        return PreviewSelectableLogic()

    def __onVehicleLoading(self, ctxEvent):
        self.removeListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        g_currentPreviewVehicle.previewStyle(self.__style)

    def __onHangarCreateOrRefresh(self):
        self.__handleWindowClose()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_VEHICLE_PREVIEW, EVENT_BUS_SCOPE.LOBBY)
    def __handleWindowClose(self, event=None):
        if event is not None and not event.ctx.get('noCallback', False):
            self.onBackClick()
        self.destroy()
        return
