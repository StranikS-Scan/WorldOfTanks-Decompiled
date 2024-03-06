# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/fitting_select_popover.py
import logging
import typing
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.shared.fitting_select.module_extenders import ModuleParamsExtender, fittingSelectModuleExtenders
from gui.Scaleform.daapi.view.meta.FittingSelectPopoverMeta import FittingSelectPopoverMeta
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters import text_styles, getItemPricesVOWithReason
from gui.shared.formatters.text_styles import builder as str_builder
from gui.shared.gui_items import GUI_ITEM_TYPE_INDICES, GUI_ITEM_TYPE, GUI_ITEM_ECONOMY_CODE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.fitting_item import FittingItem
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.items_parameters import params_helper
from gui.shared.items_parameters.formatters import formatModuleParamName, formatParameter
from gui.shared.utils import EXTRA_MODULE_INFO
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency, i18n
from helpers.i18n import makeString as _ms
from items import getTypeInfoByName
from items.vehicles import VehicleDescriptor
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.vehicle_modules import VehicleGun, VehicleRadio, VehicleEngine, VehicleTurret, VehicleChassis
_logger = logging.getLogger(__name__)
FITTING_MODULES = (GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CHASSIS],
 GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.TURRET],
 GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.GUN],
 GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.ENGINE],
 GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.RADIO])
_PARAMS_LISTS = {GUI_ITEM_TYPE.RADIO: ('radioDistance',),
 GUI_ITEM_TYPE.CHASSIS: ('maxLoad', 'rotationSpeed', 'maxSteeringLockAngle', 'chassisRepairTime'),
 GUI_ITEM_TYPE.ENGINE: ('enginePower', 'fireStartingChance'),
 GUI_ITEM_TYPE.TURRET: ('armor', 'rotationSpeed', 'circularVisionRadius'),
 GUI_ITEM_TYPE.GUN: ('avgDamageList', 'avgPiercingPower', 'reloadTime')}
_POPOVER_FIRST_TAB_IDX = 0
_POPOVER_SECOND_TAB_IDX = 1
_TAB_IDS = (_POPOVER_FIRST_TAB_IDX, _POPOVER_SECOND_TAB_IDX)

def _extendByModuleData(targetData, vehicleModule, vehDescr, extenders):
    moduleType = vehicleModule.itemTypeID
    paramsList = _PARAMS_LISTS[moduleType]
    if moduleType == GUI_ITEM_TYPE.GUN and vehicleModule.isDamageMutable():
        paramsList = ('maxAvgMutableDamageList', 'minAvgMutableDamageList', 'avgPiercingPower', 'reloadTime')
    values, names = [], []
    paramsData = params_helper.getParameters(vehicleModule, vehDescr)
    serverSettings = dependency.instance(ISettingsCore).serverSettings
    for ext in extenders:
        if ext.check(vehicleModule, vehDescr):
            paramsList, indexes = ext.extendParamList(paramsList)
            if ext.highlightCheck(serverSettings) and indexes:
                targetData['highlightedParameterIdx'] = indexes[0]
                ext.updatedHighlightSettings(serverSettings)

    for paramName in paramsList:
        value = paramsData.get(paramName)
        if value is not None:
            values.append(_formatValuesString(formatParameter(paramName, value)))
            names.append(formatModuleParamName(paramName, vehDescr))

    targetData['level'] = vehicleModule.level
    targetData['paramValues'] = '\n'.join(values)
    targetData['paramNames'] = '\n'.join(names)
    targetData['name'] = text_styles.middleTitle(vehicleModule.userName)
    targetData[EXTRA_MODULE_INFO] = vehicleModule.getExtraIconInfo(vehDescr)
    return


def _getInstallReason(module, vehicle, reason, slotIdx=None):
    _, installReason = module.mayInstall(vehicle, slotIdx)
    return installReason or reason if GUI_ITEM_ECONOMY_CODE.isCurrencyError(reason) else installReason


def _getStatus(reason):
    return text_styles.error('#menu:moduleFits/' + reason.replace(' ', '_')) if reason is not None and reason not in (GUI_ITEM_ECONOMY_CODE.ITEM_IS_HIDDEN, GUI_ITEM_ECONOMY_CODE.ITEM_IS_DUPLICATED) else ''


def _formatValuesString(valuesStr):
    if valuesStr is None:
        return ''
    else:
        valuesBuilder = str_builder()
        values = valuesStr.split('/')
        length = len(values)
        for idx, value in enumerate(values):
            valuesBuilder.addStyledText(text_styles.stats, value)
            if idx < length - 1:
                valuesBuilder.addStyledText(text_styles.standard, '/')

        return valuesBuilder.render()


def _convertTarget(target, reason):
    if target == FittingItem.TARGETS.OTHER:
        return FITTING_TYPES.TARGET_OTHER
    if target == FittingItem.TARGETS.IN_INVENTORY:
        if reason in (GUI_ITEM_ECONOMY_CODE.UNDEFINED, GUI_ITEM_ECONOMY_CODE.NOT_ENOUGH_CREDITS):
            return FITTING_TYPES.TARGET_HANGAR
        if reason == GUI_ITEM_ECONOMY_CODE.ITEM_IS_DUPLICATED:
            return FITTING_TYPES.TARGET_HANGAR_DUPLICATE
        return FITTING_TYPES.TARGET_HANGAR_CANT_INSTALL
    return FITTING_TYPES.TARGET_VEHICLE if target == FittingItem.TARGETS.CURRENT else None


class CommonFittingSelectPopover(FittingSelectPopoverMeta):
    _TAB_IDX = 0
    _TABS = None

    def __init__(self, vehicle, logicProvider, ctx=None):
        super(CommonFittingSelectPopover, self).__init__(ctx)
        data = ctx.get('data')
        self._slotType = data.slotType
        self.__vehicle = vehicle
        self._logicProvider = logicProvider
        self.setCurrentTab(self._getInitialTabIndex())

    def showModuleInfo(self, itemCD):
        if self.__vehicle is not None and itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, self.__vehicle.descriptor)
        return

    def setVehicleModule(self, newId, oldId, isRemove):
        self._logicProvider.setModule(newId, oldId, isRemove)
        self.destroy()

    def setCurrentTab(self, tabIndex):
        if tabIndex not in _TAB_IDS:
            return
        self._logicProvider.setTab(tabIndex)
        if tabIndex != self._getInitialTabIndex():
            self._saveTabIndex(tabIndex)
            self.as_updateS(self._prepareInitialData())

    def _saveTabIndex(self, index):
        self.__class__._TAB_IDX = index

    def _getInitialTabIndex(self):
        return self.__class__._TAB_IDX

    def _getVehicle(self):
        return self.__vehicle

    def _populate(self):
        super(CommonFittingSelectPopover, self)._populate()
        self.as_updateS(self._prepareInitialData())

    def _dispose(self):
        self.__vehicle = None
        self._logicProvider.dispose()
        self._logicProvider = None
        super(CommonFittingSelectPopover, self)._dispose()
        return

    def _prepareInitialData(self):
        rendererName, rendererDataClass, width, title = self._getCommonData()
        result = {'title': text_styles.highTitle(title),
         'rendererName': rendererName,
         'rendererDataClass': rendererDataClass,
         'scrollToIndex': self._logicProvider.getSelectedIdx(),
         'selectedIndex': self._logicProvider.getSelectedIdx(),
         'availableDevices': self._logicProvider.getDevices(),
         'width': width}
        result.update(self._getTabsData())
        return result

    def _getTabsData(self):
        return {'tabData': self._TABS,
         'selectedTab': self._getInitialTabIndex()} if self._TABS is not None else {}

    def _getDescText(self):
        currencyName = text_styles.main(MENU.FITTINGSELECTPOPOVER_DESCTEXT_CRYSTAL)
        result = text_styles.main(i18n.makeString(MENU.FITTINGSELECTPOPOVER_DESCTEXT, currencyName=currencyName))
        return result

    def _getCommonData(self):
        title = _ms(MENU.MODULEFITS_TITLE, moduleName=getTypeInfoByName(self._slotType)['userString'], vehicleName=self.__vehicle.userName if self.__vehicle is not None else '')
        rendererDataClass = FITTING_TYPES.MODULE_FITTING_RENDERER_DATA_CLASS_NAME
        if self._slotType == FITTING_TYPES.VEHICLE_ENGINE:
            if self.__vehicle.descriptor.hasTurboshaftEngine or self.__vehicle.descriptor.hasRocketAcceleration:
                rendererName = FITTING_TYPES.ENGINE_FITTING_BIG_ITEM_RENDERER
            else:
                rendererName = FITTING_TYPES.ENGINE_FITTING_ITEM_RENDERER
            width = FITTING_TYPES.MEDUIM_POPOVER_WIDTH
        elif self._slotType == FITTING_TYPES.VEHICLE_CHASSIS:
            rendererName = FITTING_TYPES.CHASSIS_FITTING_ITEM_RENDERER
            width = FITTING_TYPES.LARGE_POPOVER_WIDTH
        elif self._slotType == FITTING_TYPES.VEHICLE_RADIO:
            rendererName = FITTING_TYPES.RADIO_FITTING_ITEM_RENDERER
            width = FITTING_TYPES.SHORT_POPOVER_WIDTH
        else:
            rendererName = FITTING_TYPES.GUN_TURRET_FITTING_ITEM_RENDERER
            width = FITTING_TYPES.LARGE_POPOVER_WIDTH
        return (rendererName,
         rendererDataClass,
         width,
         title)


class ModuleFittingSelectPopover(CommonFittingSelectPopover):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None, customProviderClass=None):
        data_ = ctx['data']
        self.__preferredLayout = data_.preferredLayout
        self.__slotIndex = data_.slotIndex
        if g_currentPreviewVehicle.isPresent():
            providerClass = _PreviewLogicProvider
            vehicle = g_currentPreviewVehicle.item
        else:
            providerClass = _HangarLogicProvider
            vehicle = g_currentVehicle.item
        providerClass = customProviderClass or providerClass
        logicProvider = providerClass(data_.slotType, data_.slotIndex)
        super(ModuleFittingSelectPopover, self).__init__(vehicle, logicProvider, ctx)
        if self._slotType is not None and self._slotType not in FITTING_MODULES:
            _logger.error('Using ModuleFittingSelectPopover for not module type: %s', self._slotType)
        return

    def _prepareInitialData(self):
        result = super(ModuleFittingSelectPopover, self)._prepareInitialData()
        result['preferredLayout'] = self.__preferredLayout
        return result

    def _getSlotIndex(self):
        return self.__slotIndex


class PopoverLogicProvider(object):
    _itemsCache = dependency.descriptor(IItemsCache)
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, slotType, slotIndex, vehicle):
        self._slotType = slotType
        self._slotIndex = slotIndex
        self._vehicle = vehicle
        self._tooltipType = ''
        self.__modulesList = None
        self._selectedIdx = -1
        self._tabIndex = 0
        self.__moduleExtenders = fittingSelectModuleExtenders()
        return

    def getSelectedIdx(self):
        if self.__modulesList is None:
            self.__modulesList = self._buildList()
        return self._selectedIdx

    def getDevices(self):
        if self.__modulesList is None:
            self.__modulesList = self._buildList()
        return self.__modulesList

    def setModule(self, newId, oldId, isRemove):
        return NotImplemented

    def setTab(self, tabIndex):
        tabSwitched = self._tabIndex != tabIndex
        self._tabIndex = tabIndex
        if self.__modulesList is not None and tabSwitched:
            self._selectedIdx = -1
            self.__modulesList = self._buildList()
        return

    def dispose(self):
        self._vehicle = None
        return

    def _buildCommonModuleData(self, module, reason):
        return {'id': module.intCD,
         'type': self._slotType,
         'target': _convertTarget(module.getTarget(self._vehicle), reason),
         'moduleLabel': module.getGUIEmblemID(),
         'tooltipType': self._tooltipType,
         'status': _getStatus(reason)}

    def _buildModuleData(self, module, isInstalled, stats):
        return NotImplemented

    def _buildList(self):
        modulesList = []
        if self._vehicle is not None:
            typeId = GUI_ITEM_TYPE_INDICES[self._slotType]
            data = self._getSuitableItems(typeId)
            currXp = self._itemsCache.items.stats.vehiclesXPs.get(self._vehicle.intCD, 0)
            stats = {'money': self._itemsCache.items.stats.money,
             'exchangeRate': self._itemsCache.items.shop.exchangeRate,
             'currXP': currXp,
             'totalXP': currXp + self._itemsCache.items.stats.freeXP}
            for idx, vehicleModule in enumerate(data):
                isInstalled = vehicleModule.isInstalled(self._vehicle, self._slotIndex)
                if isInstalled:
                    self._selectedIdx = idx
                moduleData = self._buildModuleData(vehicleModule, isInstalled, stats)
                self.__extendByTypeSpecificData(moduleData, vehicleModule)
                modulesList.append(moduleData)

        return modulesList

    def _getSuitableItems(self, typeId):
        if self._vehicle is None:
            return []
        else:
            criteria = REQ_CRITERIA.VEHICLE.SUITABLE([self._vehicle], [typeId]) | self._getSpecificCriteria(typeId)
            data = self._itemsCache.items.getItems(typeId, criteria).values()
            data.sort(reverse=True, key=self._getItemsSortingKey())
            return data

    def _getItemsSortingKey(self):
        return None

    def _getSpecificCriteria(self, typeID):
        return REQ_CRITERIA.EMPTY

    def __extendByTypeSpecificData(self, moduleData, vehicleModule):
        if vehicleModule.itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES:
            _extendByModuleData(moduleData, vehicleModule, self._vehicle.descriptor, self.__moduleExtenders)


class _HangarLogicProvider(PopoverLogicProvider):

    def __init__(self, slotType, slotIndex):
        super(_HangarLogicProvider, self).__init__(slotType, slotIndex, g_currentVehicle.item)
        self._tooltipType = TOOLTIPS_CONSTANTS.HANGAR_MODULE

    def setModule(self, newId, oldId, isRemove):
        module = self._itemsCache.items.getItemByCD(int(newId))
        if module.isUnlocked:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_AND_SELL_ITEM, newId, self._vehicle.intCD)

    def _buildModuleData(self, vehicleModule, isInstalledInSlot, stats):
        itemPrice = vehicleModule.buyPrices.itemPrice
        inInventory = vehicleModule.isInInventory
        isInstalled = vehicleModule.isInstalled(self._vehicle)
        isBought = inInventory or isInstalled
        isEnoughMoney, purchaseReason = vehicleModule.mayPurchase(stats['money'])
        if isBought:
            isFit, reason = vehicleModule.mayInstall(self._vehicle, self._slotIndex)
            if reason == 'already installed' or isFit:
                isFit, reason = True, GUI_ITEM_ECONOMY_CODE.UNDEFINED
        else:
            isFit, reason = isEnoughMoney, purchaseReason
            if not isFit:
                if GUI_ITEM_ECONOMY_CODE.isCurrencyError(reason):
                    isFit = vehicleModule.mayPurchaseWithExchange(stats['money'], stats['exchangeRate'])
        if reason != GUI_ITEM_ECONOMY_CODE.UNLOCK_ERROR:
            installReason = _getInstallReason(vehicleModule, self._vehicle, reason, self._slotIndex)
        else:
            installReason = reason
        moduleData = self._buildCommonModuleData(vehicleModule, installReason)
        moduleData.update({'targetVisible': isBought,
         'showPrice': not isBought,
         'isSelected': isInstalledInSlot,
         'disabled': not isFit or isInstalled and not isInstalledInSlot,
         'removeButtonLabel': MENU.MODULEFITS_REMOVENAME,
         'removeButtonTooltip': MENU.MODULEFITS_REMOVETOOLTIP,
         'itemPrices': getItemPricesVOWithReason(reason, itemPrice)})
        return moduleData


class _PreviewLogicProvider(PopoverLogicProvider):

    def __init__(self, slotType, slotIndex):
        super(_PreviewLogicProvider, self).__init__(slotType, slotIndex, g_currentPreviewVehicle.item)
        self._tooltipType = TOOLTIPS_CONSTANTS.PREVIEW_MODULE

    def setModule(self, newId, oldId, isRemove):
        g_currentPreviewVehicle.installComponent(int(newId))

    def _buildModuleData(self, vehicleModule, isInstalled, _):
        isFit, reason = vehicleModule.mayInstall(self._vehicle, 0)
        moduleData = self._buildCommonModuleData(vehicleModule, reason)
        moduleData.update({'targetVisible': isInstalled,
         'showPrice': False,
         'isSelected': isInstalled,
         'disabled': not isFit,
         'removeButtonLabel': MENU.MODULEFITS_REMOVENAME,
         'removeButtonTooltip': MENU.MODULEFITS_REMOVETOOLTIP})
        return moduleData
