# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview/VehiclePreview.py
from collections import namedtuple
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PREVIEW_INFO_PANEL_IDX
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehiclePreview.vehicle_preview_dp import DefaultVehPreviewDataProvider
from gui.Scaleform.daapi.view.meta.VehiclePreviewMeta import VehiclePreviewMeta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.shared import event_dispatcher, events, event_bus_handlers, EVENT_BUS_SCOPE
from gui.shared.economics import getGUIPrice
from gui.shared.formatters import text_styles, icons
from gui.shared.money import Currency
from gui.shared.tooltips.formatters import getActionPriceData
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IVehicleComparisonBasket, ITradeInController, IRestoreController, IHeroTankController, IBootcampController
from skeletons.gui.shared import IItemsCache
from hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from HeroTank import HeroTank
CREW_INFO_TAB_ID = 'crewInfoTab'
FACT_SHEET_TAB_ID = 'factSheetTab'
TAB_ORDER = [FACT_SHEET_TAB_ID, CREW_INFO_TAB_ID]
TAB_DATA_MAP = {FACT_SHEET_TAB_ID: (VEHPREVIEW_CONSTANTS.FACT_SHEET_LINKAGE, VEHICLE_PREVIEW.INFOPANEL_TAB_FACTSHEET_NAME),
 CREW_INFO_TAB_ID: (VEHPREVIEW_CONSTANTS.CREW_INFO_LINKAGE, VEHICLE_PREVIEW.INFOPANEL_TAB_CREWINFO_NAME)}
_ButtonState = namedtuple('_ButtonState', 'enabled, price, label, isAction, currencyIcon, action, tooltip')
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

    def __init__(self, ctx=None, skipConfirm=False):
        LobbySelectableView.__init__(self, ctx)
        self._actionType = None
        self._showHeaderCloseBtn = True
        self._vehicleCD = ctx['itemCD']
        self.__vehicleStrCD = ctx.get('vehicleStrCD')
        self._previousBackAlias = ctx.get('previousBackAlias')
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
        if 'objectSelectionEnabled' in ctx:
            self._objectSelectionEnabled = ctx.get('objectSelectionEnabled')
        return

    def _populate(self):
        g_currentPreviewVehicle.selectVehicle(self._vehicleCD, self.__vehicleStrCD)
        LobbySelectableView._populate(self)
        g_clientUpdateManager.addMoneyCallback(self._updateBtnState)
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self._updateBtnState})
        g_currentPreviewVehicle.onComponentInstalled += self.__updateStatus
        g_currentPreviewVehicle.onVehicleUnlocked += self._updateBtnState
        g_currentPreviewVehicle.onVehicleInventoryChanged += self.__onInventoryChanged
        g_currentPreviewVehicle.onChanged += self.__onVehicleChanged
        self.comparisonBasket.onChange += self.__onCompareBasketChanged
        self.comparisonBasket.onSwitchChange += self.__updateHeaderData
        self.restores.onRestoreChangeNotify += self.__onRestoreChanged
        g_hangarSpace.onSpaceCreate += self.__onHangarCreateOrRefresh
        g_hangarSpace.setVehicleSelectable(True)
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
        g_hangarSpace.onSpaceCreate -= self.__onHangarCreateOrRefresh
        g_hangarSpace.setVehicleSelectable(self.__keepVehicleSelectionEnabled)
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.handleSelectedEntityUpdated)
        if self._needToResetAppearance:
            g_currentPreviewVehicle.selectNoVehicle()
            g_currentPreviewVehicle.resetAppearance()
        if self._backAlias == VIEW_ALIAS.VEHICLE_PREVIEW:
            g_currentVehicle.refreshModel()
        self.__previewDP = None
        LobbySelectableView._dispose(self)
        if self.__vehAppearanceChanged:
            g_currentPreviewVehicle.resetAppearance()
        return

    def closeView(self):
        self.__processBackClick()

    def onBackClick(self):
        self.__processBackClick()

    def onOpenInfoTab(self, index):
        AccountSettings.setSettings(PREVIEW_INFO_PANEL_IDX, index)

    def onBuyOrResearchClick(self):
        if self.__isHeroTank:
            url = self.heroTanks.getLinkByTankName()
            self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.SPECIFIED, url=url))
        else:
            self.__previewDP.buyAction(self._actionType, self._vehicleCD, self._skipConfirm)

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
            elif entity.id == g_hangarSpace.space.vehicleEntityId:
                self.__processBackClick({'entity': entity})
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
        if not g_currentPreviewVehicle.isPresent():
            event_dispatcher.selectVehicleInHangar(self._vehicleCD)

    def __onRestoreChanged(self, vehicles):
        if g_currentPreviewVehicle.isPresent():
            if self._vehicleCD in vehicles:
                self._updateBtnState()

    def __updateStatus(self):
        if g_currentPreviewVehicle.hasModulesToSelect():
            if g_currentPreviewVehicle.isModified():
                icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INFO_YELLOW, 24, 24, -7, -4)
                text = text_styles.neutral('%s%s' % (_ms(VEHICLE_PREVIEW.MODULESPANEL_STATUS_TEXT), icon))
            else:
                icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INFO, 24, 24, -7, -4)
                text = text_styles.stats('%s%s' % (_ms(VEHICLE_PREVIEW.MODULESPANEL_LABEL), icon))
        else:
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_INFO, 24, 24, -7, -4)
            text = text_styles.stats('%s%s' % (_ms(VEHICLE_PREVIEW.MODULESPANEL_NOMODULESOPTIONS), icon))
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
            price = getGUIPrice(vehicle, money, exchangeRate)
            currency = price.getCurrency(byWeight=True)
            action = getActionPriceData(vehicle)
            mayObtainForMoney = self.__isHeroTank or vehicle.mayObtainWithMoneyExchange(money, exchangeRate)
            isBuyingAvailable = not vehicle.isHidden or vehicle.isRentable or vehicle.isRestorePossible()
            if currency == Currency.GOLD:
                currencyIcon = RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICONBIG
                if mayObtainForMoney:
                    formatter = text_styles.goldTextBig
                else:
                    formatter = text_styles.errCurrencyTextBig
                    if isBuyingAvailable:
                        tooltip = _buildBuyButtonTooltip('notEnoughGold')
            else:
                currencyIcon = RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICONBIG
                formatter = text_styles.creditsTextBig if mayObtainForMoney else text_styles.errCurrencyTextBig
                if not mayObtainForMoney and isBuyingAvailable:
                    tooltip = _buildBuyButtonTooltip('notEnoughCredits')
            if self._disableBuyButton:
                mayObtainForMoney = False
            return _ButtonState(mayObtainForMoney, formatter(BigWorld.wg_getIntegralFormat(price.getSignValue(currency))), VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_RESTORE if vehicle.isRestorePossible() else VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_BUY, action is not None, currencyIcon, action, tooltip)
        else:
            nodeCD = vehicle.intCD
            currencyIcon = RES_ICONS.MAPS_ICONS_LIBRARY_XPCOSTICONBIG
            isAvailableToUnlock, xpCost, possibleXp = g_techTreeDP.isVehicleAvailableToUnlock(nodeCD)
            formatter = text_styles.creditsTextBig if possibleXp >= xpCost else text_styles.errCurrencyTextBig
            if not isAvailableToUnlock:
                unlocks = self.itemsCache.items.stats.unlocks
                next2Unlock, _ = g_techTreeDP.isNext2Unlock(nodeCD, unlocked=set(unlocks), xps=stats.vehiclesXPs, freeXP=stats.freeXP)
                if next2Unlock:
                    tooltip = _buildBuyButtonTooltip('notEnoughXp')
                elif any((bool(cd in unlocks) for cd in g_techTreeDP.getTopLevel(nodeCD))):
                    tooltip = _buildBuyButtonTooltip('parentModuleIsLocked')
                else:
                    tooltip = _buildBuyButtonTooltip('parentVehicleIsLocked')
            return _ButtonState(isAvailableToUnlock, formatter(BigWorld.wg_getIntegralFormat(xpCost)), VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_RESEARCH, False, currencyIcon, None, tooltip)
            return None

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
        isPremium = item.isPremium and (not item.isHidden or item.isRentable or item.isRestorePossible())
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

        return {'listDesc': text_styles.main(VEHICLE_PREVIEW.INFOPANEL_TAB_CREWINFO_LISTDESC_TEXT),
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
        if self._backAlias == VIEW_ALIAS.LOBBY_RESEARCH:
            event_dispatcher.showResearchView(self._vehicleCD)
        elif self._backAlias == VIEW_ALIAS.VEHICLE_PREVIEW:
            entity = ctx.get('entity', None) if ctx else None
            if entity:
                descriptor = entity.typeDescriptor
                event_dispatcher.showVehiclePreview(descriptor.type.compactDescr, previewAlias=self._previousBackAlias)
            else:
                event_dispatcher.showHangar()
        else:
            event = g_entitiesFactories.makeLoadEvent(self._backAlias, {'isBackEvent': True})
            self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)
        return
