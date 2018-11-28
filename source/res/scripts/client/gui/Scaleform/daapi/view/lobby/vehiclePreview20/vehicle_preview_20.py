# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/vehicle_preview_20.py
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from HeroTank import HeroTank
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PREVIEW_INFO_PANEL_IDX
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled, getBuyVehiclesUrl
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.STORE_TYPES import STORE_TYPES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import resolveStateTooltip
from gui.Scaleform.daapi.view.meta.VehiclePreview20Meta import VehiclePreview20Meta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.shared import event_dispatcher, events, event_bus_handlers, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showWebShop, showOldShop
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.game_control import IHeroTankController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from web_client_api.common import ItemPackTypeGroup
_BACK_BTN_LABELS = {VIEW_ALIAS.LOBBY_HANGAR: 'hangar',
 VIEW_ALIAS.LOBBY_STORE: 'shop',
 VIEW_ALIAS.LOBBY_RESEARCH: 'researchTree',
 VIEW_ALIAS.LOBBY_TECHTREE: 'researchTree',
 VIEW_ALIAS.VEHICLE_COMPARE: 'vehicleCompare',
 PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_AWARDS_VIEW_ALIAS: 'personalAwards'}
_TABS_DATA = ({'id': VEHPREVIEW_CONSTANTS.BROWSE_LINKAGE,
  'label': VEHICLE_PREVIEW.INFOPANEL_TAB_BROWSE_NAME,
  'linkage': VEHPREVIEW_CONSTANTS.BROWSE_LINKAGE}, {'id': VEHPREVIEW_CONSTANTS.MODULES_LINKAGE,
  'label': VEHICLE_PREVIEW.INFOPANEL_TAB_MODULES_NAME,
  'linkage': VEHPREVIEW_CONSTANTS.MODULES_LINKAGE}, {'id': VEHPREVIEW_CONSTANTS.CREW_LINKAGE,
  'label': VEHICLE_PREVIEW.INFOPANEL_TAB_CREWINFO_NAME,
  'linkage': VEHPREVIEW_CONSTANTS.CREW_LINKAGE})

class VehiclePreview20(LobbySelectableView, VehiclePreview20Meta):
    __background_alpha__ = 0.0
    __metaclass__ = event_bus_handlers.EventBusListener
    itemsCache = dependency.descriptor(IItemsCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    tradeIn = dependency.descriptor(ITradeInController)
    restores = dependency.descriptor(IRestoreController)
    heroTanks = dependency.descriptor(IHeroTankController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, ctx=None):
        super(VehiclePreview20, self).__init__(ctx)
        self._showCloseBtn = True
        self._vehicleCD = ctx['itemCD']
        self.__vehicleStrCD = ctx.get('vehicleStrCD')
        self._previousBackAlias = ctx.get('previousBackAlias')
        self._previewBackCb = ctx.get('previewBackCb')
        self._backAlias = ctx.get('previewAlias', VIEW_ALIAS.LOBBY_HANGAR)
        self.__isHeroTank = ctx.get('isHeroTank', False)
        self.__itemsPack = ctx.get('itemsPack')
        self.__price = ctx.get('price')
        self.__oldPrice = ctx.get('oldPrice')
        self.__title = ctx.get('title')
        self.__endTime = ctx.get('endTime')
        self.__buyParams = ctx.get('buyParams')
        if 'previewAppearance' in ctx:
            self.__vehAppearanceChanged = True
            g_currentPreviewVehicle.resetAppearance(ctx['previewAppearance'])
        else:
            self.__vehAppearanceChanged = False
        self.__keepVehicleSelectionEnabled = False
        self._needToResetAppearance = True

    def _populate(self):
        g_currentPreviewVehicle.selectVehicle(self._vehicleCD, self.__vehicleStrCD)
        super(VehiclePreview20, self)._populate()
        g_currentPreviewVehicle.onChanged += self.__onVehicleChanged
        self.comparisonBasket.onChange += self.__onCompareBasketChanged
        self.comparisonBasket.onSwitchChange += self.__updateHeaderData
        self.hangarSpace.onSpaceCreate += self.__onHangarCreateOrRefresh
        self.hangarSpace.setVehicleSelectable(True)
        serverSettings = self.lobbyContext.getServerSettings()
        serverSettings.onServerSettingsChange += self.__onServerSettingsChanged
        if not g_currentPreviewVehicle.isPresent():
            event_dispatcher.showHangar()
        if self.__itemsPack or self._backAlias == VIEW_ALIAS.LOBBY_STORE:
            self.heroTanks.setInteractive(False)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.handleSelectedEntityUpdated)

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentPreviewVehicle.onChanged -= self.__onVehicleChanged
        self.comparisonBasket.onChange -= self.__onCompareBasketChanged
        self.comparisonBasket.onSwitchChange -= self.__updateHeaderData
        self.hangarSpace.onSpaceCreate -= self.__onHangarCreateOrRefresh
        self.hangarSpace.setVehicleSelectable(self.__keepVehicleSelectionEnabled)
        serverSettings = self.lobbyContext.getServerSettings()
        serverSettings.onServerSettingsChange -= self.__onServerSettingsChanged
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.handleSelectedEntityUpdated)
        if self._needToResetAppearance:
            g_currentPreviewVehicle.selectNoVehicle()
            g_currentPreviewVehicle.resetAppearance()
        if self._backAlias == VIEW_ALIAS.VEHICLE_PREVIEW_20:
            g_currentVehicle.refreshModel()
        self._previewBackCb = None
        super(VehiclePreview20, self)._dispose()
        if self.__itemsPack or self._backAlias == VIEW_ALIAS.LOBBY_STORE:
            self.heroTanks.setInteractive(True)
        if self.__vehAppearanceChanged:
            g_currentPreviewVehicle.resetAppearance()
        return

    def closeView(self):
        event_dispatcher.showHangar()

    def onBackClick(self):
        self.__processBackClick()

    def onOpenInfoTab(self, index):
        AccountSettings.setSettings(PREVIEW_INFO_PANEL_IDX, index)

    def onCompareClick(self):
        self.comparisonBasket.addVehicle(self._vehicleCD, initParameters={'strCD': g_currentPreviewVehicle.item.descriptor.makeCompactDescr()})

    def handleSelectedEntityUpdated(self, event):
        ctx = event.ctx
        entity = BigWorld.entities.get(ctx['entityId'], None)
        if ctx['state'] == CameraMovementStates.MOVING_TO_OBJECT:
            if isinstance(entity, HeroTank):
                descriptor = entity.typeDescriptor
                if descriptor:
                    self._needToResetAppearance = False
                    event_dispatcher.showHeroTankPreview(descriptor.type.compactDescr, previewAlias=VIEW_ALIAS.VEHICLE_PREVIEW_20, previousBackAlias=self._backAlias)
            elif entity.id == self.hangarSpace.space.vehicleEntityId:
                self.__processBackClick({'entity': entity})
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(VehiclePreview20, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VEHPREVIEW_CONSTANTS.BUYING_PANEL_PY_ALIAS:
            viewPy.setCallSource(self._backAlias)
            if self.__itemsPack:
                viewPy.setPackItems(self.__itemsPack, self.__price, self.__title)
                viewPy.setTimerData(self.__endTime, self.__oldPrice)
                viewPy.setBuyParams(self.__buyParams)
        elif alias == VEHPREVIEW_CONSTANTS.CREW_LINKAGE and self.__itemsPack:
            crewItems = [ item for item in self.__itemsPack if item.type in ItemPackTypeGroup.CREW ]
            vehicleItems = [ item for item in self.__itemsPack if item.type in ItemPackTypeGroup.VEHICLE ]
            viewPy.setVehicleCrews(vehicleItems, crewItems)
        elif alias == VEHPREVIEW_CONSTANTS.BROWSE_LINKAGE:
            viewPy.setHeroTank(self.__isHeroTank)

    def __onServerSettingsChanged(self, diff):
        if not self.lobbyContext.getServerSettings().isIngamePreviewEnabled():
            event_dispatcher.showHangar()

    def __fullUpdate(self):
        self.__updateHeaderData()
        self.__updateTabsData()

    def __updateTabsData(self):
        selectedTabInd = AccountSettings.getSettings(PREVIEW_INFO_PANEL_IDX)
        for idx, tab in enumerate(_TABS_DATA):
            tab['selected'] = selectedTabInd == idx

        self.as_setTabsDataS(_TABS_DATA)

    def __onVehicleChanged(self, *args):
        if g_currentPreviewVehicle.isPresent():
            self._vehicleCD = g_currentPreviewVehicle.item.intCD
            self.__updateCrewTabLabel()
            self.__fullUpdate()

    def __updateCrewTabLabel(self):
        crewCount = len(g_currentPreviewVehicle.item.crew)
        for tab in _TABS_DATA:
            if tab['linkage'] == VEHPREVIEW_CONSTANTS.CREW_LINKAGE:
                tab['label'] = _ms(VEHICLE_PREVIEW.INFOPANEL_TAB_CREWINFO_NAME, crewCount=crewCount)

    def __onCompareBasketChanged(self, changedData):
        if changedData.isFullChanged:
            self.__updateHeaderData()

    def __updateHeaderData(self):
        self.as_setDataS(self.__getData())

    def __getData(self):
        vehicle = g_currentPreviewVehicle.item
        if vehicle.isElite:
            vehicleTitle = text_styles.bonusPreviewText('%s %s, %s' % (_ms(MENU.header_vehicletype_elite(vehicle.type)), _ms(VEHICLE_PREVIEW.INFOPANEL_LEVEL, level=_ms(MENU.header_level(vehicle.level))), _ms(MENU.nations(vehicle.nationName))))
        else:
            vehicleTitle = text_styles.playerOnline('%s %s, %s' % (_ms(MENU.header_vehicletype(vehicle.type)), _ms(VEHICLE_PREVIEW.INFOPANEL_LEVEL, level=_ms(MENU.header_level(vehicle.level))), _ms(MENU.nations(vehicle.nationName))))
        if vehicle.isPremiumIGR:
            vehicleTitle = makeHtmlString('html_templates:igr/premium-vehicle', 'name', {'vehicle': vehicleTitle})
        compareBtnEnabled, compareBtnTooltip = resolveStateTooltip(self.comparisonBasket, vehicle, VEH_COMPARE.STORE_COMPAREVEHICLEBTN_TOOLTIPS_ADDTOCOMPARE, VEH_COMPARE.STORE_COMPAREVEHICLEBTN_TOOLTIPS_DISABLED)
        result = {'closeBtnLabel': VEHICLE_PREVIEW.HEADER_CLOSEBTN_LABEL,
         'backBtnLabel': VEHICLE_PREVIEW.HEADER_BACKBTN_LABEL,
         'backBtnDescrLabel': self.__getBackBtnLabel(),
         'vehicleTitle': vehicleTitle,
         'vehicleName': vehicle.descriptor.type.shortUserString.upper(),
         'showCloseBtn': self._showCloseBtn,
         'compareBtnTooltip': compareBtnTooltip,
         'showCompareBtn': compareBtnEnabled}
        return result

    def __getBackBtnLabel(self):
        key = _BACK_BTN_LABELS.get(self._backAlias, 'hangar')
        return '#vehicle_preview:header/backBtn/descrLabel/%s' % key

    def __onHangarCreateOrRefresh(self):
        self.__keepVehicleSelectionEnabled = True
        self.__handleWindowClose()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_VEHICLE_PREVIEW, EVENT_BUS_SCOPE.LOBBY)
    def __handleWindowClose(self):
        self.onBackClick()
        self.destroy()

    def __processBackClick(self, ctx=None):
        if self._previewBackCb:
            self._previewBackCb()
        elif self._backAlias == VIEW_ALIAS.LOBBY_RESEARCH:
            event_dispatcher.showResearchView(self._vehicleCD)
        elif self._backAlias == VIEW_ALIAS.VEHICLE_PREVIEW_20:
            entity = ctx.get('entity', None) if ctx else None
            if entity:
                descriptor = entity.typeDescriptor
                event_dispatcher.showVehiclePreview(descriptor.type.compactDescr, previewAlias=self._previousBackAlias)
            else:
                event_dispatcher.showHangar()
        elif self._backAlias == VIEW_ALIAS.LOBBY_STORE:
            if isIngameShopEnabled():
                showWebShop(url=getBuyVehiclesUrl())
            else:
                showOldShop(ctx={'tabId': STORE_TYPES.SHOP,
                 'component': STORE_CONSTANTS.VEHICLE})
        else:
            event = g_entitiesFactories.makeLoadEvent(self._backAlias, {'isBackEvent': True})
            self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)
        return
