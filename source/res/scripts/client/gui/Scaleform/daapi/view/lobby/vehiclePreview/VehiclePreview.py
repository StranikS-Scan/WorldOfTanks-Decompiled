# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview/VehiclePreview.py
from collections import namedtuple
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from HeroTank import HeroTank
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PREVIEW_INFO_PANEL_IDX
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled, getBuyVehiclesUrl
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehiclePreview.vehicle_preview_dp import DefaultVehPreviewDataProvider
from gui.Scaleform.daapi.view.meta.VehiclePreviewMeta import VehiclePreviewMeta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.STORE_TYPES import STORE_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.ingame_shop import canBuyGoldForVehicleThroughWeb
from gui.shared import event_dispatcher, events, event_bus_handlers, EVENT_BUS_SCOPE
from gui.shared.gui_items.gui_item_economics import getPriceTypeAndValue
from gui.shared.event_dispatcher import showWebShop, showOldShop
from gui.shared.formatters import text_styles, icons, chooseItemPriceVO, getItemUnlockPricesVO, getMoneyVO
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IVehicleComparisonBasket, ITradeInController, IRestoreController, IHeroTankController, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
_ButtonState = namedtuple('_ButtonState', ('enabled', 'isMoneyEnough', 'itemPrice', 'label', 'isAction', 'tooltip', 'isUnlock'))
_BACK_BTN_LABELS = {VIEW_ALIAS.LOBBY_HANGAR: 'hangar',
 VIEW_ALIAS.LOBBY_STORE: 'shop',
 VIEW_ALIAS.LOBBY_RESEARCH: 'researchTree',
 VIEW_ALIAS.LOBBY_TECHTREE: 'researchTree',
 VIEW_ALIAS.VEHICLE_COMPARE: 'vehicleCompare',
 PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_AWARDS_VIEW_ALIAS: 'personalAwards'}

def _buildBuyButtonTooltip(key):
    return makeTooltip(TOOLTIPS.vehiclepreview_buybutton_all(key, 'header'), TOOLTIPS.vehiclepreview_buybutton_all(key, 'body'))


class VehiclePreview(LobbySelectableView, VehiclePreviewMeta):
    __background_alpha__ = 0.0
    __metaclass__ = event_bus_handlers.EventBusListener
    itemsCache = dependency.descriptor(IItemsCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    tradeIn = dependency.descriptor(ITradeInController)
    restores = dependency.descriptor(IRestoreController)
    heroTanks = dependency.descriptor(IHeroTankController)
    bootcamp = dependency.descriptor(IBootcampController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, ctx=None, skipConfirm=False):
        LobbySelectableView.__init__(self, ctx)
        self._actionType = None
        self._showHeaderCloseBtn = True
        self._vehicleCD = ctx['itemCD']
        self.__vehicleStrCD = ctx.get('vehicleStrCD')
        self._previousBackAlias = ctx.get('previousBackAlias')
        self._previewBackCb = ctx.get('previewBackCb')
        self._backAlias = ctx.get('previewAlias', VIEW_ALIAS.LOBBY_HANGAR)
        self.__manageVehicleModel = ctx.get('manageVehicleModel', False)
        if 'previewAppearance' in ctx:
            self.__vehAppearanceChanged = True
            g_currentPreviewVehicle.resetAppearance(ctx['previewAppearance'])
        else:
            self.__vehAppearanceChanged = False
        self.__previewDP = ctx.get('previewDP', DefaultVehPreviewDataProvider())
        self.__isHeroTank = ctx.get('isHeroTank', False)
        self._skipConfirm = skipConfirm
        self._disableBuyButton = False
        self.__keepVehicleSelectionEnabled = False
        self._needToResetAppearance = True
        if not self.__isHeroTank:
            self.hangarSpace.removeVehicle()
        g_currentPreviewVehicle.selectHeroTank(self.__isHeroTank)
        return

    def closeView(self):
        if self._previewBackCb:
            self._previewBackCb()
        else:
            event_dispatcher.showHangar()

    def onBackClick(self):
        self.__processBackClick()

    def onOpenInfoTab(self, index):
        AccountSettings.setSettings(PREVIEW_INFO_PANEL_IDX, index)

    def onBuyOrResearchClick(self):
        if self.__isHeroTank:
            url = self.heroTanks.getCurrentRelatedURL()
            self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.SPECIFIED, url=url))
        else:
            vehicle = g_currentPreviewVehicle.item
            level = vehicle.level
            if canBuyGoldForVehicleThroughWeb(vehicle):
                event_dispatcher.showVehicleBuyDialog(vehicle, previousAlias=VIEW_ALIAS.VEHICLE_PREVIEW)
            else:
                self.__previewDP.buyAction(self._actionType, self._vehicleCD, self._skipConfirm, level)

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
                    event_dispatcher.showHeroTankPreview(descriptor.type.compactDescr, previewAlias=VIEW_ALIAS.VEHICLE_PREVIEW, previousBackAlias=self._backAlias)
            elif entity.id == self.hangarSpace.space.vehicleEntityId:
                self.__processBackClick({'entity': entity})
        return

    def _populate(self):
        g_currentPreviewVehicle.selectVehicle(self._vehicleCD, self.__vehicleStrCD)
        LobbySelectableView._populate(self)
        g_clientUpdateManager.addMoneyCallback(self._updateBtnState)
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self._updateBtnState,
         'serverSettings.blueprints_config': self.__onBlueprintsModeChanged})
        g_currentPreviewVehicle.onComponentInstalled += self.__updateStatus
        g_currentPreviewVehicle.onVehicleUnlocked += self._updateBtnState
        g_currentPreviewVehicle.onVehicleInventoryChanged += self.__onInventoryChanged
        g_currentPreviewVehicle.onChanged += self.__onVehicleChanged
        self.comparisonBasket.onChange += self.__onCompareBasketChanged
        self.comparisonBasket.onSwitchChange += self.__updateHeaderData
        self.restores.onRestoreChangeNotify += self.__onRestoreChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.hangarSpace.onSpaceCreate += self.__onHangarCreateOrRefresh
        self.hangarSpace.setVehicleSelectable(True)
        if g_currentPreviewVehicle.isPresent():
            self.__fullUpdate()
        else:
            event_dispatcher.showHangar()
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.handleSelectedEntityUpdated)

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentPreviewVehicle.onComponentInstalled -= self.__updateStatus
        g_currentPreviewVehicle.onVehicleUnlocked -= self._updateBtnState
        g_currentPreviewVehicle.onVehicleInventoryChanged -= self.__onInventoryChanged
        g_currentPreviewVehicle.onChanged -= self.__onVehicleChanged
        self.comparisonBasket.onChange -= self.__onCompareBasketChanged
        self.comparisonBasket.onSwitchChange -= self.__updateHeaderData
        self.restores.onRestoreChangeNotify -= self.__onRestoreChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.hangarSpace.onSpaceCreate -= self.__onHangarCreateOrRefresh
        self.hangarSpace.setVehicleSelectable(self.__keepVehicleSelectionEnabled)
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.handleSelectedEntityUpdated)
        if self._needToResetAppearance:
            g_currentPreviewVehicle.selectNoVehicle()
            g_currentPreviewVehicle.resetAppearance()
        if self._backAlias == VIEW_ALIAS.VEHICLE_PREVIEW:
            g_currentVehicle.refreshModel()
        self._previewBackCb = None
        self.__previewDP = None
        LobbySelectableView._dispose(self)
        if self.__vehAppearanceChanged:
            g_currentPreviewVehicle.resetAppearance()
        return

    def _updateBtnState(self, *args):
        item = g_currentPreviewVehicle.item
        if item is None:
            return
        else:
            btnData = self.__getBtnData()
            self._actionType = self.__previewDP.getBuyType(item)
            self.as_updateBuyingPanelS(self.__previewDP.getBuyingPanelData(item, btnData, self.__isHeroTank))
            return

    def __fullUpdate(self):
        selectedTabInd = AccountSettings.getSettings(PREVIEW_INFO_PANEL_IDX)
        self.__updateHeaderData()
        self.as_updateInfoDataS(self.__getInfoData(selectedTabInd))
        self._updateBtnState()
        self.__updateStatus()

    def __onVehicleChanged(self, *args):
        if g_currentPreviewVehicle.isPresent():
            self._vehicleCD = g_currentPreviewVehicle.item.intCD
            self.__fullUpdate()

    def __onCompareBasketChanged(self, changedData):
        if changedData.isFullChanged:
            self.__updateHeaderData()

    def __onInventoryChanged(self, *arg):
        g_currentPreviewVehicle.selectNoVehicle()
        if self.bootcamp.isInBootcamp():
            event_dispatcher.selectVehicleInHangar(self._vehicleCD)

    def __onRestoreChanged(self, vehicles):
        if g_currentPreviewVehicle.isPresent():
            if self._vehicleCD in vehicles:
                self._updateBtnState()

    def __onServerSettingsChanged(self, diff):
        if self.lobbyContext.getServerSettings().isIngameDataChangedInDiff(diff, 'isEnabled'):
            self._updateBtnState()
        if self.lobbyContext.getServerSettings().isIngamePreviewEnabled():
            self.__processBackClick()

    def __onBlueprintsModeChanged(self, _):
        self._updateBtnState()

    def __updateStatus(self):
        if g_currentPreviewVehicle.hasModulesToSelect():
            if g_currentPreviewVehicle.isModified():
                icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INFO_YELLOW, 24, 24, -7, -4)
                text = text_styles.neutral(''.join((_ms(VEHICLE_PREVIEW.MODULESPANEL_STATUS_TEXT), icon)))
            else:
                icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INFO, 24, 24, -7, -4)
                text = text_styles.stats(''.join((_ms(VEHICLE_PREVIEW.MODULESPANEL_LABEL), icon)))
        else:
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INFO, 24, 24, -7, -4)
            text = text_styles.stats(''.join((_ms(VEHICLE_PREVIEW.MODULESPANEL_NOMODULESOPTIONS), icon)))
        self.as_updateVehicleStatusS(text)

    def __updateHeaderData(self):
        self.as_setStaticDataS(self.__getStaticData())

    def __getBtnData(self):
        vehicle = g_currentPreviewVehicle.item
        stats = self.itemsCache.items.stats
        tooltip = ''
        if vehicle.isUnlocked:
            money = stats.money
            money = self.tradeIn.addTradeInPriceIfNeeded(vehicle, money)
            exchangeRate = self.itemsCache.items.shop.exchangeRate
            priceType, price = getPriceTypeAndValue(vehicle, money, exchangeRate)
            currency = price.getCurrency(byWeight=True)
            isAction = False
            minRentPricePackage = vehicle.getRentPackage()
            if minRentPricePackage:
                isAction = minRentPricePackage['rentPrice'] != minRentPricePackage['defaultRentPrice']
            elif not vehicle.isRestoreAvailable() and not self.bootcamp.isInBootcamp():
                isAction = vehicle.buyPrices.getSum().isActionPrice()
            if self.bootcamp.isInBootcamp():
                itemPrice = [{'price': getMoneyVO(price.price)}]
            else:
                itemPrice = chooseItemPriceVO(priceType, price)
            mayObtainForMoney = self.__isHeroTank or vehicle.mayObtainWithMoneyExchange(money, exchangeRate)
            isBuyingAvailable = not vehicle.isHidden or vehicle.isRentable or vehicle.isRestorePossible()
            isMoneyEnough = mayObtainForMoney
            if not mayObtainForMoney and isBuyingAvailable:
                if currency == Currency.GOLD:
                    tooltip = _buildBuyButtonTooltip('notEnoughGold')
                    if isIngameShopEnabled():
                        mayObtainForMoney = True
                else:
                    tooltip = _buildBuyButtonTooltip('notEnoughCredits')
            if self._disableBuyButton:
                mayObtainForMoney = False
            return _ButtonState(mayObtainForMoney, isMoneyEnough, itemPrice, VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_RESTORE if vehicle.isRestorePossible() else VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_BUY, isAction, tooltip, isUnlock=False)
        else:
            nodeCD = vehicle.intCD
            isNextToUnlock, isXpEnough = g_techTreeDP.isVehicleAvailableToUnlock(nodeCD, vehicle.level)
            isAvailableToUnlock = isNextToUnlock and isXpEnough
            isXPEnough = True
            unlocks = self.itemsCache.items.stats.unlocks
            next2Unlock, unlockProps = g_techTreeDP.isNext2Unlock(nodeCD, unlocked=set(unlocks), xps=stats.vehiclesXPs, freeXP=stats.freeXP, level=vehicle.level)
            if not isAvailableToUnlock:
                if next2Unlock:
                    isXPEnough = False
                    tooltip = _buildBuyButtonTooltip('notEnoughXp')
                elif any((bool(cd in unlocks) for cd in g_techTreeDP.getTopLevel(nodeCD))):
                    tooltip = _buildBuyButtonTooltip('parentModuleIsLocked')
                else:
                    tooltip = _buildBuyButtonTooltip('parentVehicleIsLocked')
            unlockPriceVO = getItemUnlockPricesVO(unlockProps)
            return _ButtonState(isAvailableToUnlock, isXPEnough, unlockPriceVO, VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_RESEARCH, unlockProps.discount > 0, tooltip, isUnlock=True)

    def __getStaticData(self):
        result = {'header': self.__getHeaderData(),
         'bottomPanel': self.__getBottomPanelData()}
        result.update(self.__previewDP.getCrewInfo(g_currentPreviewVehicle.item))
        return result

    def __getHeaderData(self):
        vehicle = g_currentPreviewVehicle.item
        return {'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
         'tankInfo': text_styles.concatStylesToMultiLine(text_styles.promoSubTitle(vehicle.userName), text_styles.stats(MENU.levels_roman(vehicle.level))),
         'closeBtnLabel': VEHICLE_PREVIEW.HEADER_CLOSEBTN_LABEL,
         'backBtnLabel': VEHICLE_PREVIEW.HEADER_BACKBTN_LABEL,
         'backBtnDescrLabel': self.__getBackBtnLabel(),
         'titleText': text_styles.promoTitle(VEHICLE_PREVIEW.HERO_HEADER_TITLE) if self.__isHeroTank else text_styles.promoTitle(VEHICLE_PREVIEW.HEADER_TITLE),
         'isPremiumIGR': vehicle.isPremiumIGR,
         'showCloseBtn': self._showHeaderCloseBtn}

    def __getBackBtnLabel(self):
        key = _BACK_BTN_LABELS.get(self._backAlias, 'hangar')
        return '#vehicle_preview:header/backBtn/descrLabel/%s' % key

    def __getBottomPanelData(self):
        item = g_currentPreviewVehicle.item
        isBootCamp = self.bootcamp.isInBootcamp()
        return self.__previewDP.getBottomPanelData(item, isHeroTank=self.__isHeroTank, isBootCamp=isBootCamp)

    def __getInfoData(self, selectedTabInd):
        return {'selectedTab': selectedTabInd,
         'tabData': self.__packTabData(),
         'nation': g_currentPreviewVehicle.item.nationName}

    def __packTabData(self):
        item = g_currentPreviewVehicle.item
        isPremium = item.isPremium and (not item.isHidden or item.isRentable) and not item.isSpecial
        if isPremium:
            info = self.__packDataItem(VEHPREVIEW_CONSTANTS.ELITE_FACT_SHEET_DATA_CLASS_NAME, self.__packEliteFactSheetData())
        else:
            info = self.__packDataItem(VEHPREVIEW_CONSTANTS.FACT_SHEET_DATA_CLASS_NAME, self.__packFactSheetData())
        return [info, self.__packDataItem(VEHPREVIEW_CONSTANTS.CREW_INFO_DATA_CLASS_NAME, self.__packCrewInfoData())]

    def __packCrewInfoData(self):
        crewData = []
        for _, tankman in g_currentPreviewVehicle.item.crew:
            role = tankman.descriptor.role
            crewData.append({'icon': RES_ICONS.getItemBonus42x42(role),
             'name': text_styles.middleTitle(ITEM_TYPES.tankman_roles(role)),
             'tooltip': TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_CREW_MEMBER,
             'role': role})

        return {'listDesc': text_styles.main(VEHICLE_PREVIEW.INFOPANEL_TAB_LISTDESC_CREW),
         'crewList': crewData}

    def __packFactSheetData(self):
        return {'historicReferenceTxt': text_styles.main(g_currentPreviewVehicle.item.fullDescription)}

    def __packEliteFactSheetData(self):
        icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INFO, 24, 24, -7, -4)
        return {'title': _ms(VEHICLE_PREVIEW.INFOPANEL_TAB_ELITEFACTSHEET_TITLE),
         'info': '%s%s' % (_ms(VEHICLE_PREVIEW.INFOPANEL_TAB_ELITEFACTSHEET_INFO), icon)}

    def __packDataItem(self, className, data):
        return {'voClassName': className,
         'voData': data}

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
        elif self._backAlias == VIEW_ALIAS.VEHICLE_PREVIEW:
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
