# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/style_preview.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_helpers.sound_manager import RANKED_OVERLAY_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.lobby.store.browser.sound_constants import INGAMESHOP_PREVIEW_SOUND_SPACE
from gui.Scaleform.daapi.view.meta.VehicleBasePreviewMeta import VehicleBasePreviewMeta
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import event_dispatcher, events, event_bus_handlers, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.customization.c11n_items import STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.game_control import IBobSoundController
_SHOW_CLOSE_BTN = False
_SHOW_BACK_BTN = True

class VehicleStylePreview(LobbySelectableView, VehicleBasePreviewMeta):
    __background_alpha__ = 0.0
    __metaclass__ = event_bus_handlers.EventBusListener
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __bobSounds = dependency.descriptor(IBobSoundController)

    def __init__(self, ctx=None):
        self.__vehicleCD = ctx['itemCD']
        self.__style = ctx['style']
        self.__styleDescr = ctx.get('styleDescr')
        self.__backCallback = ctx.get('backCallback', event_dispatcher.showHangar)
        self.__backBtnDescrLabel = ctx.get('backBtnDescrLabel', backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.personalAwards()))
        if ctx.get('backAlias', VIEW_ALIAS.LOBBY_HANGAR) == VIEW_ALIAS.LOBBY_STORE:
            self._COMMON_SOUND_SPACE = INGAMESHOP_PREVIEW_SOUND_SPACE
        else:
            self._COMMON_SOUND_SPACE = RANKED_OVERLAY_SOUND_SPACE
        super(VehicleStylePreview, self).__init__(ctx)

    def closeView(self):
        event_dispatcher.showHangar()

    def onBackClick(self):
        self.__backCallback()

    def _populate(self):
        super(VehicleStylePreview, self)._populate()
        g_currentPreviewVehicle.selectVehicle(self.__vehicleCD)
        if not g_currentPreviewVehicle.isPresent() or self.__style is None:
            event_dispatcher.showHangar()
        self.__hangarSpace.onSpaceCreate += self.__onHangarCreateOrRefresh
        self.addListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        self.as_setDataS({'closeBtnLabel': backport.text(R.strings.vehicle_preview.header.closeBtn.label()),
         'backBtnLabel': backport.text(R.strings.vehicle_preview.header.backBtn.label()),
         'backBtnDescrLabel': self.__backBtnDescrLabel,
         'showCloseBtn': _SHOW_CLOSE_BTN,
         'showBackButton': _SHOW_BACK_BTN})
        self.as_setAdditionalInfoS({'objectSubtitle': text_styles.main(STYLE_GROUP_ID_TO_FULL_GROUP_NAME_MAP[self.__style.groupID]),
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
        self.__bobSounds.onStylePreviewClose()
        super(VehicleStylePreview, self)._dispose()

    def __onVehicleLoading(self, ctxEvent):
        g_currentPreviewVehicle.previewStyle(self.__style)

    def __onHangarCreateOrRefresh(self):
        self.__handleWindowClose()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_VEHICLE_PREVIEW, EVENT_BUS_SCOPE.LOBBY)
    def __handleWindowClose(self):
        self.onBackClick()
        self.destroy()
