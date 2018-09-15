# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview/VehiclePreview.py
from collections import namedtuple
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PREVIEW_INFO_PANEL_IDX
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import resolveStateTooltip
from gui.Scaleform.daapi.view.meta.VehiclePreviewMeta import VehiclePreviewMeta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.customization.shared import getBonusIcon42x42
from gui.shared import event_dispatcher
from gui.shared.economics import getGUIPrice
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.money import Currency
from gui.shared.tooltips.formatters import getActionPriceData
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IVehicleComparisonBasket, ITradeInController, IRestoreController
from skeletons.gui.shared import IItemsCache
CREW_INFO_TAB_ID = 'crewInfoTab'
FACT_SHEET_TAB_ID = 'factSheetTab'
TAB_ORDER = [FACT_SHEET_TAB_ID, CREW_INFO_TAB_ID]
TAB_DATA_MAP = {FACT_SHEET_TAB_ID: (VEHPREVIEW_CONSTANTS.FACT_SHEET_LINKAGE, VEHICLE_PREVIEW.INFOPANEL_TAB_FACTSHEET_NAME),
 CREW_INFO_TAB_ID: (VEHPREVIEW_CONSTANTS.CREW_INFO_LINKAGE, VEHICLE_PREVIEW.INFOPANEL_TAB_CREWINFO_NAME)}
_ButtonState = namedtuple('_ButtonState', 'enabled, price, label, isAction, currencyIcon, actionType, action, tooltip')
_BACK_BTN_LABELS = {VIEW_ALIAS.LOBBY_HANGAR: 'hangar',
 VIEW_ALIAS.LOBBY_STORE: 'shop',
 VIEW_ALIAS.LOBBY_RESEARCH: 'researchTree',
 VIEW_ALIAS.LOBBY_TECHTREE: 'researchTree',
 VIEW_ALIAS.VEHICLE_COMPARE: 'vehicleCompare'}

def _buildBuyButtonTooltip(key):
    return makeTooltip(TOOLTIPS.vehiclepreview_buybutton_all(key, 'header'), TOOLTIPS.vehiclepreview_buybutton_all(key, 'body'))


class VehiclePreview(LobbySubView, VehiclePreviewMeta):
    __background_alpha__ = 0.0
    itemsCache = dependency.descriptor(IItemsCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    tradeIn = dependency.descriptor(ITradeInController)
    restores = dependency.descriptor(IRestoreController)

    def __init__(self, ctx=None, skipConfirm=False):
        super(VehiclePreview, self).__init__(ctx)
        self._actionType = None
        self._showVehInfoPanel = True
        self._showHeaderCloseBtn = True
        self.__vehicleCD = ctx.get('itemCD')
        self.__vehicleStrCD = ctx.get('vehicleStrCD')
        self.__backAlias = ctx.get('previewAlias', VIEW_ALIAS.LOBBY_HANGAR)
        self._skipConfirm = skipConfirm
        self._disableBuyButton = False
        return

    def _populate(self):
        g_currentPreviewVehicle.selectVehicle(self.__vehicleCD, self.__vehicleStrCD)
        super(VehiclePreview, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self._updateBtnState)
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self._updateBtnState})
        g_currentPreviewVehicle.onComponentInstalled += self.__updateStatus
        g_currentPreviewVehicle.onVehicleUnlocked += self._updateBtnState
        g_currentPreviewVehicle.onVehicleInventoryChanged += self.__onInventoryChanged
        g_currentPreviewVehicle.onChanged += self.__onVehicleChanged
        self.comparisonBasket.onChange += self.__onCompareBasketChanged
        self.comparisonBasket.onSwitchChange += self.__updateHeaderData
        self.restores.onRestoreChangeNotify += self.__onRestoreChanged
        if g_currentPreviewVehicle.isPresent():
            self.__updateHeaderData()
            self.__fullUpdate()
        else:
            event_dispatcher.showHangar()

    def _dispose(self):
        super(VehiclePreview, self)._dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentPreviewVehicle.onComponentInstalled -= self.__updateStatus
        g_currentPreviewVehicle.onVehicleUnlocked -= self._updateBtnState
        g_currentPreviewVehicle.onVehicleInventoryChanged -= self.__onInventoryChanged
        g_currentPreviewVehicle.onChanged -= self.__onVehicleChanged
        self.comparisonBasket.onChange -= self.__onCompareBasketChanged
        self.comparisonBasket.onSwitchChange -= self.__updateHeaderData
        self.restores.onRestoreChangeNotify -= self.__onRestoreChanged
        g_currentPreviewVehicle.selectNoVehicle()

    def closeView(self):
        self.onBackClick()

    def onBackClick(self):
        if self.__backAlias == VIEW_ALIAS.LOBBY_RESEARCH:
            event_dispatcher.showResearchView(self.__vehicleCD)
        else:
            event = g_entitiesFactories.makeLoadEvent(self.__backAlias)
            self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)

    def onOpenInfoTab(self, index):
        AccountSettings.setSettings(PREVIEW_INFO_PANEL_IDX, index)

    def onBuyOrResearchClick(self):
        if self._actionType == ItemsActionsFactory.UNLOCK_ITEM:
            unlockProps = g_techTreeDP.getUnlockProps(self.__vehicleCD)
            ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, self.__vehicleCD, unlockProps.parentID, unlockProps.unlockIdx, unlockProps.xpCost, skipConfirm=self._skipConfirm)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, self.__vehicleCD, skipConfirm=self._skipConfirm)

    def onCompareClick(self):
        """
        Add to compare button click handler
        """
        self.comparisonBasket.addVehicle(self.__vehicleCD, initParameters={'strCD': g_currentPreviewVehicle.item.descriptor.makeCompactDescr()})

    def _updateBtnState(self, *args):
        if g_currentPreviewVehicle.isPresent():
            btnData = self.__getBtnData()
            isAction = btnData.isAction
            self._actionType = btnData.actionType
            self.as_updateBuyButtonS({'enabled': btnData.enabled,
             'label': btnData.label,
             'tooltip': btnData.tooltip})
            self.as_updatePriceS({'value': btnData.price,
             'icon': btnData.currencyIcon,
             'showAction': isAction,
             'actionTooltipType': TOOLTIPS_CONSTANTS.ACTION_PRICE if isAction else None,
             'actionData': btnData.action})
        return

    def __fullUpdate(self):
        selectedTabInd = AccountSettings.getSettings(PREVIEW_INFO_PANEL_IDX)
        self.__updateHeaderData()
        self.as_updateInfoDataS(self.__getInfoData(selectedTabInd))
        self._updateBtnState()
        self.__updateStatus()

    def __onVehicleChanged(self, *args):
        if g_currentPreviewVehicle.isPresent():
            self.__vehicleCD = g_currentPreviewVehicle.item.intCD
            self.__fullUpdate()

    def __getVehiclePanelData(self):
        vehicle = g_currentPreviewVehicle.item
        data = {'info': text_styles.main(TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO_BODY),
         'infoTooltip': TOOLTIPS.VEHICLEPREVIEW_VEHICLEPANEL_INFO,
         'vehCompareData': self.__getVehCompareData(vehicle),
         'isVisible': self._showVehInfoPanel}
        return data

    def __getVehCompareData(self, vehicle):
        state, tooltip = resolveStateTooltip(self.comparisonBasket, vehicle, enabledTooltip=None, fullTooltip=VEH_COMPARE.STORE_COMPAREVEHICLEBTN_TOOLTIPS_DISABLED)
        return {'modeAvailable': self.comparisonBasket.isEnabled(),
         'btnEnabled': state,
         'btnTooltip': tooltip,
         'label': text_styles.main(VEH_COMPARE.VEHPREVIEW_COMPAREINFO_ADDTOCOMPARE)}

    def __onCompareBasketChanged(self, changedData):
        """
        gui.game_control.VehComparisonBasket.onChange event handler
        :param changedData: instance of gui.game_control.veh_comparison_basket._ChangedData
        """
        if changedData.isFullChanged:
            self.__updateHeaderData()

    def __onInventoryChanged(self, *arg):
        if not g_currentPreviewVehicle.isPresent():
            event_dispatcher.selectVehicleInHangar(self.__vehicleCD)

    def __onRestoreChanged(self, vehicles):
        if g_currentPreviewVehicle.isPresent():
            if self.__vehicleCD in vehicles:
                self._updateBtnState()

    def __updateStatus(self):
        if g_currentPreviewVehicle.hasModulesToSelect():
            if g_currentPreviewVehicle.isModified():
                icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, 16, 16, -3, 0)
                text = text_styles.neutral('%s %s' % (icon, _ms(VEHICLE_PREVIEW.MODULESPANEL_STATUS_TEXT)))
            else:
                text = text_styles.main(VEHICLE_PREVIEW.MODULESPANEL_LABEL)
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
            mayObtainForMoney = vehicle.mayObtainWithMoneyExchange(money, exchangeRate)
            if currency == Currency.GOLD:
                currencyIcon = RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICONBIG
                if mayObtainForMoney:
                    formatter = text_styles.goldTextBig
                else:
                    formatter = text_styles.errCurrencyTextBig
                    tooltip = _buildBuyButtonTooltip('notEnoughGold')
            else:
                currencyIcon = RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICONBIG
                formatter = text_styles.creditsTextBig if mayObtainForMoney else text_styles.errCurrencyTextBig
                if not mayObtainForMoney:
                    tooltip = _buildBuyButtonTooltip('notEnoughCredits')
            if self._disableBuyButton:
                mayObtainForMoney = False
            return _ButtonState(mayObtainForMoney, formatter(BigWorld.wg_getIntegralFormat(price.getSignValue(currency))), VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_RESTORE if vehicle.isRestorePossible() else VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_BUY, action is not None, currencyIcon, ItemsActionsFactory.BUY_VEHICLE, action, tooltip)
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
                elif any(map(lambda cd: cd in unlocks, g_techTreeDP.getTopLevel(nodeCD))):
                    tooltip = _buildBuyButtonTooltip('parentModuleIsLocked')
                else:
                    tooltip = _buildBuyButtonTooltip('parentVehicleIsLocked')
            return _ButtonState(isAvailableToUnlock, formatter(BigWorld.wg_getIntegralFormat(xpCost)), VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_RESEARCH, False, currencyIcon, ItemsActionsFactory.UNLOCK_ITEM, None, tooltip)
            return None

    def __getStaticData(self):
        return {'header': self.__getHeaderData(),
         'bottomPanel': self.__getBottomPanelData(),
         'tabButtonsData': self.__packTabButtonsData(),
         'vehicleInfo': self.__getVehiclePanelData()}

    def __getHeaderData(self):
        vehicle = g_currentPreviewVehicle.item
        return {'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
         'tankInfo': text_styles.concatStylesToMultiLine(text_styles.promoSubTitle(vehicle.shortUserName), text_styles.stats(MENU.levels_roman(vehicle.level))),
         'closeBtnLabel': VEHICLE_PREVIEW.HEADER_CLOSEBTN_LABEL,
         'backBtnLabel': VEHICLE_PREVIEW.HEADER_BACKBTN_LABEL,
         'backBtnDescrLabel': self.__getBackBtnLabel(),
         'titleText': text_styles.promoTitle(VEHICLE_PREVIEW.HEADER_TITLE),
         'isPremiumIGR': vehicle.isPremiumIGR,
         'showCloseBtn': self._showHeaderCloseBtn}

    def __getBackBtnLabel(self):
        key = _BACK_BTN_LABELS.get(self.__backAlias, 'hangar')
        return '#vehicle_preview:header/backBtn/descrLabel/%s' % key

    def __getBottomPanelData(self):
        item = g_currentPreviewVehicle.item
        isBuyingAvailable = not item.isHidden or item.isRentable or item.isRestorePossible()
        if isBuyingAvailable:
            if item.canTradeIn:
                buyingLabel = text_styles.main(VEHICLE_PREVIEW.BUYINGPANEL_TRADEINLABEL)
            else:
                buyingLabel = text_styles.main(VEHICLE_PREVIEW.BUYINGPANEL_LABEL)
        else:
            buyingLabel = text_styles.alert(VEHICLE_PREVIEW.BUYINGPANEL_ALERTLABEL)
        if item.hasModulesToSelect:
            modulesLabel = VEHICLE_PREVIEW.MODULESPANEL_TITLE
        else:
            modulesLabel = VEHICLE_PREVIEW.MODULESPANEL_NOMODULESOPTIONS
        return {'buyingLabel': buyingLabel,
         'modulesLabel': text_styles.middleTitle(modulesLabel),
         'isBuyingAvailable': isBuyingAvailable,
         'isCanTrade': item.canTradeIn,
         'vehicleId': item.intCD}

    def __getInfoData(self, selectedTabInd):
        return {'selectedTab': selectedTabInd,
         'tabData': self.__packTabData(),
         'nation': g_currentPreviewVehicle.item.nationName}

    def __packTabButtonsData(self):
        data = []
        for id in TAB_ORDER:
            linkage, label = TAB_DATA_MAP[id]
            data.append({'label': label,
             'linkage': linkage})

        return data

    def __packTabData(self):
        return [self.__packDataItem(VEHPREVIEW_CONSTANTS.FACT_SHEET_DATA_CLASS_NAME, self.__packFactSheetData()), self.__packDataItem(VEHPREVIEW_CONSTANTS.CREW_INFO_DATA_CLASS_NAME, self.__packCrewInfoData())]

    def __packCrewInfoData(self):
        crewData = []
        for idx, tankman in g_currentPreviewVehicle.item.crew:
            role = tankman.descriptor.role
            crewData.append({'icon': getBonusIcon42x42(role),
             'name': text_styles.middleTitle(ITEM_TYPES.tankman_roles(role)),
             'tooltip': TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_CREW_MEMBER,
             'role': role})

        return {'listDesc': text_styles.main(VEHICLE_PREVIEW.INFOPANEL_TAB_CREWINFO_LISTDESC_TEXT),
         'crewList': crewData,
         'showNationFlag': False}

    def __packFactSheetData(self):
        return {'historicReferenceTxt': text_styles.main(g_currentPreviewVehicle.item.fullDescription),
         'showNationFlag': True}

    def __packDataItem(self, className, data):
        return {'voClassName': className,
         'voData': data}
