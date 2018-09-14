# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/fitting_select_popover.py
import BigWorld
from gui.Scaleform.daapi.view.meta.FittingSelectPopoverMeta import FittingSelectPopoverMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters.text_styles import builder as str_builder
from gui.shared.gui_items import GUI_ITEM_TYPE_INDICES, FittingItem
from gui.shared.items_parameters import params_helper
from gui.shared.items_parameters.formatters import formatModuleParamName, baseFormatParameter
from gui.shared.tooltips.formatters import packItemActionTooltipData
from gui.shared.utils import EXTRA_MODULE_INFO, CLIP_ICON_PATH, HYDRAULIC_ICON_PATH
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers.i18n import makeString as _ms
from gui.shared.formatters import text_styles
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared import event_dispatcher as shared_events
from items import getTypeInfoByName
_PARAMS_LISTS = {'vehicleRadio': ('radioDistance',),
 'vehicleChassis': ('rotationSpeed', 'maxLoad'),
 'vehicleEngine': ('enginePower', 'fireStartingChance'),
 'vehicleTurret': ('armor', 'rotationSpeed', 'circularVisionRadius'),
 'vehicleGun': ('avgDamage', 'avgPiercingPower', 'reloadTime')}

def _getInstallReason(module, vehicle, reason, slotIdx=None):
    _, installReason = module.mayInstall(vehicle, slotIdx)
    if reason == 'credits_error':
        return installReason or reason
    else:
        return installReason


def _getStatus(reason):
    return text_styles.error('#menu:moduleFits/' + reason.replace(' ', '_')) if reason is not None and reason != 'isHidden' else ''


def _formatValuesString(valuesStr):
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
        if reason in ('', 'credits_error'):
            return FITTING_TYPES.TARGET_HANGAR
        else:
            return FITTING_TYPES.TARGET_HANGAR_CANT_INSTALL
    elif target == FittingItem.TARGETS.CURRENT:
        return FITTING_TYPES.TARGET_VEHICLE


class FittingSelectPopover(FittingSelectPopoverMeta):
    """
    Class provides functionality for fitting select popover. Popover is created for particular fitting slot in
    ammunition panel in hangar or for modules slot in preview window.
    """

    def __init__(self, ctx=None):
        """
        @param ctx: dictionary with data from AS, which contains:
                    -slotType - one of ITEM_TYPE_NAMES;
                    -slotIndex - number of slot in panel. Is important for optional device, as they have many
                    slots of same type;
        """
        super(FittingSelectPopover, self).__init__(ctx)
        data = ctx.get('data')
        self._slotType = data.slotType
        if g_currentPreviewVehicle.isPresent():
            self.__logicProvider = _PreviewLogicProvider(data.slotType, data.slotIndex)
            self.__vehicle = g_currentPreviewVehicle.item
        else:
            self.__logicProvider = _HangarLogicProvider(data.slotType, data.slotIndex)
            self.__vehicle = g_currentVehicle.item

    def showModuleInfo(self, itemCD):
        if itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, self.__vehicle.descriptor)
        return

    def setVehicleModule(self, newId, oldId, isRemove):
        self.__logicProvider.setModule(newId, oldId, isRemove)
        self.destroy()

    def _populate(self):
        super(FittingSelectPopover, self)._populate()
        if self._slotType == 'optionalDevice':
            title = MENU.OPTIONALDEVICEFITS_TITLE
            rendererName = FITTING_TYPES.OPTIONAL_DEVICE_FITTING_ITEM_RENDERER
            rendererDataClass = FITTING_TYPES.OPTIONAL_DEVICE_RENDERER_DATA_CLASS_NAME
            width = FITTING_TYPES.LARGE_POPOVER_WIDTH
        else:
            title = _ms(MENU.MODULEFITS_TITLE, moduleName=getTypeInfoByName(self._slotType)['userString'], vehicleName=self.__vehicle.userName)
            rendererDataClass = FITTING_TYPES.MODULE_FITTING_RENDERER_DATA_CLASS_NAME
            if self._slotType in ('vehicleChassis', 'vehicleEngine'):
                rendererName = FITTING_TYPES.ENGINE_CHASSIS_FITTING_ITEM_RENDERER
                width = FITTING_TYPES.MEDUIM_POPOVER_WIDTH
            elif self._slotType == 'vehicleRadio':
                rendererName = FITTING_TYPES.RADIO_FITTING_ITEM_RENDERER
                width = FITTING_TYPES.SHORT_POPOVER_WIDTH
            else:
                rendererName = FITTING_TYPES.GUN_TURRET_FITTING_ITEM_RENDERER
                width = FITTING_TYPES.LARGE_POPOVER_WIDTH
        self.as_updateS({'title': text_styles.highTitle(title),
         'rendererName': rendererName,
         'rendererDataClass': rendererDataClass,
         'selectedIndex': self.__logicProvider.getSelectedIdx(),
         'availableDevices': self.__logicProvider.getDevices(),
         'width': width})


class _PopoverLogicProvider(object):

    def __init__(self, slotType, slotIndex):
        self._slotType = slotType
        self._slotIndex = slotIndex
        self._vehicle = None
        self._tooltipType = ''
        self.__modulesList = None
        self._selectedIdx = -1
        return

    def getSelectedIdx(self):
        if self.__modulesList is None:
            self.__modulesList = self.__buildList()
        return self._selectedIdx

    def getDevices(self):
        if self.__modulesList is None:
            self.__modulesList = self.__buildList()
        return self.__modulesList

    def setModule(self, newId, oldId, isRemove):
        return NotImplemented

    def _buildCommonModuleData(self, module, reason):
        return {'id': module.intCD,
         'type': self._slotType,
         'target': _convertTarget(module.getTarget(self._vehicle), reason),
         'moduleLabel': module.getGUIEmblemID(),
         'tooltipType': self._tooltipType,
         'status': _getStatus(reason)}

    def _buildModuleData(self, module, isInstalled, stats):
        return NotImplemented

    def __buildList(self):
        modulesList = []
        typeId = GUI_ITEM_TYPE_INDICES[self._slotType]
        data = g_itemsCache.items.getItems(typeId, REQ_CRITERIA.VEHICLE.SUITABLE([self._vehicle], [typeId])).values()
        data.sort(reverse=True)
        currXp = g_itemsCache.items.stats.vehiclesXPs.get(self._vehicle.intCD, 0)
        stats = {'money': g_itemsCache.items.stats.money,
         'exchangeRate': g_itemsCache.items.shop.exchangeRate,
         'currXP': currXp,
         'totalXP': currXp + g_itemsCache.items.stats.freeXP}
        for idx, module in enumerate(data):
            isInstalled = module.isInstalled(self._vehicle, self._slotIndex)
            if isInstalled:
                self._selectedIdx = idx
            moduleData = self._buildModuleData(module, isInstalled, stats)
            if self._slotType == 'optionalDevice':
                moduleData['slotIndex'] = self._slotIndex
                moduleData['removable'] = module.isRemovable
                moduleData['desc'] = text_styles.main(module.getShortInfo())
                moduleData['name'] = text_styles.stats(module.userName)
            else:
                values, names = self.__buildParams(module)
                moduleData['level'] = module.level
                moduleData['paramValues'] = values
                moduleData['paramNames'] = names
                moduleData['name'] = text_styles.middleTitle(module.userName)
            if self._slotType == 'vehicleGun':
                if module.isClipGun(self._vehicle.descriptor):
                    moduleData[EXTRA_MODULE_INFO] = CLIP_ICON_PATH
            elif self._slotType == 'vehicleChassis':
                if module.isHydraulicChassis():
                    moduleData[EXTRA_MODULE_INFO] = HYDRAULIC_ICON_PATH
            modulesList.append(moduleData)

        return modulesList

    def __buildParams(self, module):
        values, names = [], []
        paramsData = params_helper.getParameters(module)
        for paramName in _PARAMS_LISTS[self._slotType]:
            value = paramsData.get(paramName)
            if value is not None:
                values.append(_formatValuesString(baseFormatParameter(paramName, value)))
                names.append(formatModuleParamName(paramName))

        return ('\n'.join(values), '\n'.join(names))


class _HangarLogicProvider(_PopoverLogicProvider):

    def __init__(self, slotType, slotIndex):
        super(_HangarLogicProvider, self).__init__(slotType, slotIndex)
        self._vehicle = g_currentVehicle.item
        self._tooltipType = TOOLTIPS_CONSTANTS.HANGAR_MODULE

    def setModule(self, newId, oldId, isRemove):
        module = g_itemsCache.items.getItemByCD(int(newId))
        if module.isUnlocked or self._slotType == 'optionalDevice':
            if oldId < 0:
                oldId = None
            ItemsActionsFactory.doAction(ItemsActionsFactory.SET_VEHICLE_MODULE, self._vehicle.invID, newId, self._slotIndex, oldId, isRemove)
        return

    def _buildModuleData(self, module, isInstalledInSlot, stats):
        isEnoughCurrency = True
        price = module.buyPrice
        currency = price.getCurrency()
        inInventory = module.isInInventory
        isInstalled = module.isInstalled(self._vehicle)
        isBought = inInventory or isInstalled
        priceValue = price.get(currency)
        if isBought:
            isFit, reason = True, ''
        else:
            isFit, reason = module.mayPurchase(stats['money'])
            if not isFit:
                if reason == 'credits_error':
                    isEnoughCurrency = False
                    isFit = module.mayPurchaseWithExchange(stats['money'], stats['exchangeRate'])
        if isFit and reason != 'unlock_error':
            reason = _getInstallReason(module, self._vehicle, reason, self._slotIndex)
        moduleData = self._buildCommonModuleData(module, reason)
        moduleData.update({'targetVisible': isBought,
         'price': BigWorld.wg_getIntegralFormat(priceValue),
         'showPrice': not isBought,
         'isEnoughCurrency': isEnoughCurrency,
         'currency': currency,
         'actionPriceData': packItemActionTooltipData(module) if price != module.defaultPrice else None,
         'isSelected': isInstalledInSlot,
         'disabled': not isFit or isInstalled and not isInstalledInSlot})
        return moduleData


class _PreviewLogicProvider(_PopoverLogicProvider):

    def __init__(self, slotType, slotIndex):
        super(_PreviewLogicProvider, self).__init__(slotType, slotIndex)
        self._tooltipType = TOOLTIPS_CONSTANTS.PREVIEW_MODULE
        self._vehicle = g_currentPreviewVehicle.item

    def setModule(self, newId, oldId, isRemove):
        g_currentPreviewVehicle.installComponent(int(newId))

    def _buildModuleData(self, module, isInstalled, _):
        reason = _getInstallReason(module, self._vehicle, '', 0)
        moduleData = self._buildCommonModuleData(module, reason)
        moduleData.update({'targetVisible': isInstalled,
         'price': BigWorld.wg_getIntegralFormat(0),
         'showPrice': False,
         'isEnoughCurrency': True,
         'currency': 'credits',
         'actionPriceData': None,
         'isSelected': isInstalled,
         'disabled': reason == ''})
        return moduleData
