# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/vehicle_preview_20.py
import itertools
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from HeroTank import HeroTank
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PREVIEW_INFO_PANEL_IDX
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.items_kit_helper import getActiveOffer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled, getBuyVehiclesUrl
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.sound_constants import RESEARCH_PREVIEW_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import resolveStateTooltip
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.info.vehicle_preview_crew_tab import getUniqueMembers
from gui.Scaleform.daapi.view.meta.VehiclePreview20Meta import VehiclePreview20Meta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.STORE_TYPES import STORE_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.shared import event_dispatcher, events, event_bus_handlers, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showWebShop, showOldShop
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getTypeSmallIconPath
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IHeroTankController
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from gui.Scaleform.daapi.view.lobby.store.browser.sound_constants import INGAMESHOP_PREVIEW_SOUND_SPACE
from web_client_api.common import ItemPackTypeGroup, ItemPackEntry, ItemPackType
_BACK_BTN_LABELS = {VIEW_ALIAS.LOBBY_HANGAR: 'hangar',
 VIEW_ALIAS.LOBBY_STORE: 'shop',
 VIEW_ALIAS.LOBBY_STORAGE: 'storage',
 VIEW_ALIAS.LOBBY_RESEARCH: 'researchTree',
 VIEW_ALIAS.LOBBY_TECHTREE: 'researchTree',
 VIEW_ALIAS.VEHICLE_COMPARE: 'vehicleCompare',
 VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW: 'referralProgram',
 VIEW_ALIAS.EPIC_BATTLE_PAGE: 'frontline',
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
        self._backAlias = ctx.get('previewAlias', VIEW_ALIAS.LOBBY_HANGAR)
        self.__itemsPack = ctx.get('itemsPack')
        if self._backAlias == VIEW_ALIAS.LOBBY_STORE or self.__itemsPack is not None:
            self._COMMON_SOUND_SPACE = INGAMESHOP_PREVIEW_SOUND_SPACE
        elif self._backAlias in (VIEW_ALIAS.LOBBY_TECHTREE, VIEW_ALIAS.LOBBY_RESEARCH):
            self._COMMON_SOUND_SPACE = RESEARCH_PREVIEW_SOUND_SPACE
        super(VehiclePreview20, self).__init__(ctx)
        self._showCloseBtn = True
        self._vehicleCD = ctx['itemCD']
        self.__vehicleStrCD = ctx.get('vehicleStrCD')
        self._previousBackAlias = ctx.get('previousBackAlias')
        self._previewBackCb = ctx.get('previewBackCb')
        self.__isHeroTank = ctx.get('isHeroTank', False)
        vehParams = ctx.get('vehParams') or {}
        self.__customizationCD = vehParams.get('styleCD')
        self.__offers = ctx.get('offers')
        self.__price = ctx.get('price')
        self.__oldPrice = ctx.get('oldPrice')
        self.__title = ctx.get('title')
        self.__description = ctx.get('description')
        self.__endTime = ctx.get('endTime')
        self.__buyParams = ctx.get('buyParams')
        self._heroInteractive = not (self.__itemsPack or self.__offers or self._backAlias == VIEW_ALIAS.LOBBY_STORE)
        self.__haveCustomCrew = any((item.type == ItemPackType.CREW_CUSTOM for item in self.__itemsPack)) if self.__itemsPack else False
        if 'previewAppearance' in ctx:
            self.__vehAppearanceChanged = True
            g_currentPreviewVehicle.resetAppearance(ctx['previewAppearance'])
        else:
            self.__vehAppearanceChanged = False
        self.__keepVehicleSelectionEnabled = False
        self._needToResetAppearance = True
        if not self.__isHeroTank:
            self.hangarSpace.removeVehicle()
        g_currentPreviewVehicle.selectHeroTank(self.__isHeroTank)
        return

    def setBottomPanel(self):
        self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.BUYING_PANEL_LINKAGE)

    def _populate(self):
        self.addListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        self.setBottomPanel()
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
        if not self._heroInteractive:
            self.heroTanks.setInteractive(False)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.handleSelectedEntityUpdated)

    def _dispose(self):
        self.removeListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
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
        if not self._heroInteractive:
            self.heroTanks.setInteractive(True)
        if self.__vehAppearanceChanged:
            g_currentPreviewVehicle.resetAppearance()
        return

    def closeView(self):
        event_dispatcher.showHangar()

    def onBackClick(self):
        self._processBackClick()

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
                self._processBackClick({'entity': entity})
        return

    def _highlight3DEntityAndShowTT(self, entity):
        LobbySelectableView._highlight3DEntityAndShowTT(self, entity)
        itemId = entity.selectionId
        if itemId:
            self.as_show3DSceneTooltipS(TOOLTIPS_CONSTANTS.ENVIRONMENT, [itemId])

    def _fade3DEntityAndHideTT(self, entity):
        LobbySelectableView._fade3DEntityAndHideTT(self, entity)
        self.as_hide3DSceneTooltipS()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(VehiclePreview20, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VEHPREVIEW_CONSTANTS.BUYING_PANEL_PY_ALIAS:
            if self.__itemsPack:
                viewPy.setPackItems(self.__itemsPack, self.__price, self.__title)
                viewPy.setTimerData(self.__endTime, self.__oldPrice)
                viewPy.setBuyParams(self.__buyParams)
                viewPy.setBackAlias(self._backAlias)
            elif self.__offers:
                viewPy.setOffers(self.__offers, self.__title, self.__description)
        elif alias == VEHPREVIEW_CONSTANTS.CREW_LINKAGE:
            if self.__itemsPack:
                crewItems = tuple((item for item in self.__itemsPack if item.type in ItemPackTypeGroup.CREW))
                vehicleItems = tuple((item for item in self.__itemsPack if item.type in ItemPackTypeGroup.VEHICLE))
                viewPy.setVehicleCrews(vehicleItems, crewItems)
            elif self.__offers:
                offer = getActiveOffer(self.__offers)
                viewPy.setVehicleCrews((ItemPackEntry(id=g_currentPreviewVehicle.item.intCD, groupID=offer.crew.groupID),), (offer.crew,))
            else:
                viewPy.setVehicleCrews((ItemPackEntry(id=g_currentPreviewVehicle.item.intCD, groupID=1),), ())
        elif alias == VEHPREVIEW_CONSTANTS.BROWSE_LINKAGE:
            viewPy.setHeroTank(self.__isHeroTank)

    def __onVehicleLoading(self, ctxEvent):
        if self.__customizationCD is not None and not ctxEvent.ctx.get('started'):
            customizationItem = self.itemsCache.items.getItemByCD(self.__customizationCD)
            if customizationItem is None:
                return
            if customizationItem.itemTypeID == GUI_ITEM_TYPE.STYLE:
                g_currentPreviewVehicle.previewStyle(customizationItem)
            elif customizationItem.itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
                g_currentPreviewVehicle.previewCamouflage(customizationItem)
        return

    def __onServerSettingsChanged(self, diff):
        if not self.lobbyContext.getServerSettings().isIngamePreviewEnabled():
            event_dispatcher.showHangar()

    def __fullUpdate(self):
        self.__updateHeaderData()
        self.__updateTabsData()

    def __updateTabsData(self):
        selectedTabInd = AccountSettings.getSettings(PREVIEW_INFO_PANEL_IDX)
        if self.__haveCustomCrew or self.__offers:
            tab_ids = [ tab['id'] for tab in _TABS_DATA ]
            if VEHPREVIEW_CONSTANTS.CREW_LINKAGE in tab_ids:
                selectedTabInd = tab_ids.index(VEHPREVIEW_CONSTANTS.CREW_LINKAGE)
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
        crewCount += len(getUniqueMembers(g_currentPreviewVehicle.item))
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
        if vehicle.isPremium:
            vehicleTitle = '{} {},'.format(_ms(MENU.header_vehicletype_elite(vehicle.type)), _ms(VEHICLE_PREVIEW.INFOPANEL_LEVEL, level=_ms(MENU.header_level(vehicle.level))))
            vehicleName = makeHtmlString('html_templates:lobby/vehicle_preview', 'vehicleNamePremium', {'name': vehicle.descriptor.type.shortUserString.upper()})
        else:
            vehicleTitle = '{} {},'.format(_ms(MENU.header_vehicletype(vehicle.type)), _ms(VEHICLE_PREVIEW.INFOPANEL_LEVEL, level=_ms(MENU.header_level(vehicle.level))))
            vehicleName = makeHtmlString('html_templates:lobby/vehicle_preview', 'vehicleNameRegular', {'name': vehicle.descriptor.type.shortUserString.upper()})
        if vehicle.isPremiumIGR:
            vehicleTitle = makeHtmlString('html_templates:igr/premium-vehicle', 'name', {'vehicle': vehicleTitle})
        compareBtnEnabled, compareBtnTooltip = resolveStateTooltip(self.comparisonBasket, vehicle, VEH_COMPARE.STORE_COMPAREVEHICLEBTN_TOOLTIPS_ADDTOCOMPARE, VEH_COMPARE.STORE_COMPAREVEHICLEBTN_TOOLTIPS_DISABLED)
        result = {'closeBtnLabel': VEHICLE_PREVIEW.HEADER_CLOSEBTN_LABEL,
         'backBtnLabel': VEHICLE_PREVIEW.HEADER_BACKBTN_LABEL,
         'backBtnDescrLabel': self._getBackBtnLabel(),
         'vehicleTitle': vehicleTitle,
         'vehicleTypeIcon': getTypeSmallIconPath(vehicle.type, vehicle.isElite),
         'nationFlagIcon': RES_ICONS.getFilterNation(vehicle.nationName),
         'vehicleName': vehicleName,
         'nationName': MENU.nations(vehicle.nationName),
         'showCloseBtn': self._showCloseBtn,
         'compareBtnTooltip': compareBtnTooltip,
         'showCompareBtn': compareBtnEnabled,
         'listDesc': self.__getInfoPanelListDescription(vehicle)}
        return result

    @staticmethod
    def __getInfoPanelListDescription(vehicle):
        descriptions = (text_styles.main(VEHICLE_PREVIEW.INFOPANEL_TAB_LISTDESC_CREW),
         text_styles.main(VEHICLE_PREVIEW.INFOPANEL_TAB_LISTDESC_CREWSKILLS),
         text_styles.main(VEHICLE_PREVIEW.INFOPANEL_TAB_LISTDESC_CREWEQUIPS),
         text_styles.main(VEHICLE_PREVIEW.INFOPANEL_TAB_LISTDESC_CREWSKILLSEQUIPS))
        hasSkillBonuses = any((tMan.skills for _, tMan in vehicle.crew))
        hasEquipBonuses = any(itertools.chain(vehicle.optDevices, vehicle.equipment.battleAbilityConsumables, vehicle.equipment.battleBoosterConsumables, (rCons and rCons.kpi for rCons in vehicle.equipment.regularConsumables), (vehicle.hasOutfit(vehicle.getAnyOutfitSeason()),)))
        return descriptions[hasEquipBonuses << 1 | hasSkillBonuses]

    def _getBackBtnLabel(self):
        return VEHICLE_PREVIEW.getBackBtnLabel(_BACK_BTN_LABELS[self._backAlias]) if self._backAlias and self._backAlias in _BACK_BTN_LABELS else VEHICLE_PREVIEW.HEADER_BACKBTN_DESCRLABEL_HANGAR

    def __onHangarCreateOrRefresh(self):
        self.__keepVehicleSelectionEnabled = True
        self.__handleWindowClose()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_VEHICLE_PREVIEW, EVENT_BUS_SCOPE.LOBBY)
    def __handleWindowClose(self):
        self.onBackClick()
        self.destroy()

    def _processBackClick(self, ctx=None):
        if self._previewBackCb:
            self._previewBackCb()
        elif self._backAlias == VIEW_ALIAS.LOBBY_RESEARCH and g_currentPreviewVehicle.isPresent():
            event_dispatcher.showResearchView(self._vehicleCD, exitEvent=events.LoadViewEvent(VIEW_ALIAS.LOBBY_TECHTREE, ctx={'nation': g_currentPreviewVehicle.item.nationName}))
        elif self._backAlias == VIEW_ALIAS.VEHICLE_PREVIEW_20:
            entity = ctx.get('entity', None) if ctx else None
            if entity:
                descriptor = entity.typeDescriptor
                event_dispatcher.showVehiclePreview(descriptor.type.compactDescr, previewAlias=self._previousBackAlias)
            else:
                event_dispatcher.showHangar()
        elif self._backAlias == VIEW_ALIAS.LOBBY_STORE:
            if isIngameShopEnabled():
                showWebShop(getBuyVehiclesUrl())
            else:
                showOldShop(ctx={'tabId': STORE_TYPES.SHOP,
                 'component': STORE_CONSTANTS.VEHICLE})
        else:
            event = g_entitiesFactories.makeLoadEvent(self._backAlias, {'isBackEvent': True})
            self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)
        return
