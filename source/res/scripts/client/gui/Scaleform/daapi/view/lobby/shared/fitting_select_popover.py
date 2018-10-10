# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/fitting_select_popover.py
import BigWorld
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from gui import g_htmlTemplates
from constants import MAX_VEHICLE_LEVEL
from gui.Scaleform.daapi.view.meta.FittingSelectPopoverMeta import FittingSelectPopoverMeta
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters.text_styles import builder as str_builder
from gui.shared.gui_items import GUI_ITEM_TYPE_INDICES, GUI_ITEM_TYPE, GUI_ITEM_ECONOMY_CODE
from gui.shared.gui_items.processors.vehicle import VehicleAutoBattleBoosterEquipProcessor
from gui.shared.gui_items.fitting_item import FittingItem
from gui.shared.items_parameters import params_helper
from gui.shared.items_parameters.formatters import formatModuleParamName, formatParameter
from gui.shared.utils import decorators, EXTRA_MODULE_INFO
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.event_dispatcher import showBattleBoosterBuyDialog, showEpicBattleSkillView
from helpers import dependency, i18n
from helpers.i18n import makeString as _ms
from gui.shared.formatters import text_styles, getItemPricesVOWithReason
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared import event_dispatcher as shared_events
from items import getTypeInfoByName
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from account_helpers.AccountSettings import AccountSettings, SHOW_OPT_DEVICE_HINT
from skeletons.gui.game_control import IBootcampController
from bootcamp.Bootcamp import g_bootcamp
_PARAMS_LISTS = {GUI_ITEM_TYPE.RADIO: ('radioDistance',),
 GUI_ITEM_TYPE.CHASSIS: ('rotationSpeed', 'maxLoad'),
 GUI_ITEM_TYPE.ENGINE: ('enginePower', 'fireStartingChance'),
 GUI_ITEM_TYPE.TURRET: ('armor', 'rotationSpeed', 'circularVisionRadius'),
 GUI_ITEM_TYPE.GUN: ('avgDamageList', 'avgPiercingPower', 'reloadTime')}
_POPOVER_FIRST_TAB_IDX = 0
_POPOVER_SECOND_TAB_IDX = 1
_TAB_IDS = (_POPOVER_FIRST_TAB_IDX, _POPOVER_SECOND_TAB_IDX)
_POPOVER_OVERLAY_VEH_LVL_RANGE = range(4, MAX_VEHICLE_LEVEL)

def _extendByModuleData(targetData, vehicleModule, vehDescr):
    moduleType = vehicleModule.itemTypeID
    values, names = [], []
    paramsData = params_helper.getParameters(vehicleModule, vehDescr)
    paramsList = _PARAMS_LISTS[moduleType]
    if vehicleModule.itemTypeID == GUI_ITEM_TYPE.GUN and vehicleModule.isAutoReloadable(vehDescr):
        paramsList = paramsList[:-1] + ('autoReloadTime',)
        serverSettings = dependency.instance(ISettingsCore).serverSettings
        if serverSettings.checkAutoReloadHighlights():
            targetData['highlightedParameterIdx'] = 2
    for paramName in paramsList:
        value = paramsData.get(paramName)
        if value is not None:
            values.append(_formatValuesString(formatParameter(paramName, value)))
            names.append(formatModuleParamName(paramName))

    targetData['level'] = vehicleModule.level
    targetData['paramValues'] = '\n'.join(values)
    targetData['paramNames'] = '\n'.join(names)
    targetData['name'] = text_styles.middleTitle(vehicleModule.userName)
    targetData[EXTRA_MODULE_INFO] = vehicleModule.getExtraIconInfo(vehDescr)
    return


def _extendByArtefactData(targetData, module, slotIndex):
    targetData['slotIndex'] = slotIndex
    targetData['removable'] = module.isRemovable
    template = g_htmlTemplates['html_templates:lobby/popovers']['optionalDevice']
    desc = module.formattedShortDescription(template.source)
    targetData['desc'] = text_styles.main(desc)
    targetData['name'] = text_styles.stats(module.userName)


def _extendByOptionalDeviceData(targetData, module):
    highlight = SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS if module.isDeluxe() else SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT
    _extendHighlightData(targetData, highlight)


def _extendByBattleBoosterData(targetData, module, vehicle):
    if module.isCrewBooster():
        skillLearnt = module.isAffectedSkillLearnt(vehicle)
        template = g_htmlTemplates['html_templates:lobby/popovers']['crewBattleBooster']
        desc = module.getCrewBoosterDescription(not skillLearnt, template.source)
        targetData['desc'] = text_styles.main(desc)
        highlight = SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER if skillLearnt else SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_CREW_REPLACE
        _extendHighlightData(targetData, highlight)
    else:
        if getattr(BigWorld.player(), 'isLongDisconnectedFromCenter', False):
            targetData['notAffectedTTC'] = False
        else:
            targetData['notAffectedTTC'] = not module.isAffectsOnVehicle(vehicle)
        targetData['desc'] = text_styles.main(module.getOptDeviceBoosterDescription(vehicle, text_styles.bonusAppliedText))
        _extendHighlightData(targetData, SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER)
    targetData['count'] = module.inventoryCount
    targetData['removeButtonLabel'] = MENU.BOOSTERFITTINGRENDERER_REMOVEBUTTON
    targetData['buyButtonLabel'] = MENU.BOOSTERFITTINGRENDERER_BUYBUTTON
    targetData['buyButtonTooltip'] = ''
    targetData['buyButtonVisible'] = targetData['isSelected']


def _extendByBattleAbilityData(targetData, ability, slotIndex):
    targetData['slotIndex'] = slotIndex
    targetData['desc'] = text_styles.main(ability.shortDescription)
    targetData['name'] = text_styles.stats(ability.userName)
    targetData['level'] = ability.level
    targetData['removeButtonLabel'] = EPIC_BATTLE.FITTINGSELECTPOPOVER_REMOVEBUTTON
    targetData['changeOrderButtonLabel'] = EPIC_BATTLE.FITTINGSELECTPOPOVER_CHANGEORDER


def _extendHighlightData(targetData, highlight):
    targetData['highlightType'] = highlight
    targetData['bgHighlightType'] = highlight


def _getInstallReason(module, vehicle, reason, slotIdx=None):
    _, installReason = module.mayInstall(vehicle, slotIdx)
    return installReason or reason if GUI_ITEM_ECONOMY_CODE.isMoneyError(reason) else installReason


def _getStatus(reason):
    return text_styles.error('#menu:moduleFits/' + reason.replace(' ', '_')) if reason is not None and reason not in (GUI_ITEM_ECONOMY_CODE.ITEM_IS_HIDDEN, GUI_ITEM_ECONOMY_CODE.ITEM_IS_DUPLICATED) else ''


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
        self.__logicProvider = logicProvider
        self.setCurrentTab(self._getInitialTabIndex())

    def showModuleInfo(self, itemCD):
        if self.__vehicle is not None and itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, self.__vehicle.descriptor)
        return

    def setVehicleModule(self, newId, oldId, isRemove):
        self.__logicProvider.setModule(newId, oldId, isRemove)
        self.destroy()

    def setCurrentTab(self, tabIndex):
        if tabIndex not in _TAB_IDS:
            return
        self.__logicProvider.setTab(tabIndex)
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
        self.__logicProvider.resetCounters()

    def _dispose(self):
        self.__vehicle = None
        self.__logicProvider.dispose()
        self.__logicProvider = None
        super(CommonFittingSelectPopover, self)._dispose()
        return

    def _prepareInitialData(self):
        rendererName, rendererDataClass, width, title = self._getCommonData()
        result = {'title': text_styles.highTitle(title),
         'rendererName': rendererName,
         'rendererDataClass': rendererDataClass,
         'selectedIndex': self.__logicProvider.getSelectedIdx(),
         'availableDevices': self.__logicProvider.getDevices(),
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
        if self._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
            title = MENU.OPTIONALDEVICEFITS_TITLE
            rendererName = FITTING_TYPES.OPTIONAL_DEVICE_FITTING_ITEM_RENDERER
            rendererDataClass = FITTING_TYPES.OPTIONAL_DEVICE_RENDERER_DATA_CLASS_NAME
            width = FITTING_TYPES.LARGE_POPOVER_WIDTH
        elif self._slotType == FITTING_TYPES.BATTLE_ABILITY:
            title = MENU.BATTLEABILITY_TITLE
            rendererName = FITTING_TYPES.BATTLE_ABILITY_ITEM_RENDERER
            rendererDataClass = FITTING_TYPES.BATTLE_ABILITY_RENDERER_DATA_CLASS_NAME
            width = FITTING_TYPES.SHORT_POPOVER_WIDTH
        else:
            title = _ms(MENU.MODULEFITS_TITLE, moduleName=getTypeInfoByName(self._slotType)['userString'], vehicleName=self.__vehicle.userName if self.__vehicle is not None else '')
            rendererDataClass = FITTING_TYPES.MODULE_FITTING_RENDERER_DATA_CLASS_NAME
            if self._slotType in [FITTING_TYPES.VEHICLE_CHASSIS, FITTING_TYPES.VEHICLE_ENGINE]:
                rendererName = FITTING_TYPES.ENGINE_CHASSIS_FITTING_ITEM_RENDERER
                width = FITTING_TYPES.MEDUIM_POPOVER_WIDTH
            elif self._slotType == FITTING_TYPES.VEHICLE_RADIO:
                rendererName = FITTING_TYPES.RADIO_FITTING_ITEM_RENDERER
                width = FITTING_TYPES.SHORT_POPOVER_WIDTH
            elif self._slotType == FITTING_TYPES.BATTLE_ABILITY:
                title = MENU.BATTLEABILITY_TITLE
                rendererName = FITTING_TYPES.BATTLE_ABILITY_ITEM_RENDERER
                rendererDataClass = FITTING_TYPES.BATTLE_ABILITY_RENDERER_DATA_CLASS_NAME
                width = FITTING_TYPES.SHORT_POPOVER_WIDTH
            else:
                rendererName = FITTING_TYPES.GUN_TURRET_FITTING_ITEM_RENDERER
                width = FITTING_TYPES.LARGE_POPOVER_WIDTH
        return (rendererName,
         rendererDataClass,
         width,
         title)


class HangarFittingSelectPopover(CommonFittingSelectPopover):
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self, ctx=None, logicProvider=None):
        data_ = ctx['data']
        slotType = data_.slotType
        self.__preferredLayout = data_.preferredLayout
        self.__slotIndex = data_.slotIndex
        if g_currentPreviewVehicle.isPresent():
            _logicProvider = _PreviewLogicProvider(slotType, self.__slotIndex)
            vehicle = g_currentPreviewVehicle.item
        else:
            if self.bootcampController.isInBootcamp():
                _logicProvider = _BootCampLogicProvider(slotType, self.__slotIndex)
            else:
                _logicProvider = _HangarLogicProvider(slotType, self.__slotIndex)
            vehicle = g_currentVehicle.item
        if logicProvider is None:
            logicProvider = _logicProvider
        super(HangarFittingSelectPopover, self).__init__(vehicle, logicProvider, ctx)
        return

    def _prepareInitialData(self):
        result = super(HangarFittingSelectPopover, self)._prepareInitialData()
        result['preferredLayout'] = self.__preferredLayout
        return result

    def _getSlotIndex(self):
        return self.__slotIndex


class BattleAbilitySelectPopover(HangarFittingSelectPopover):
    itemsCache = dependency.descriptor(IItemsCache)

    def onManageBattleAbilitiesClicked(self):
        showEpicBattleSkillView()
        self.destroy()

    def _prepareInitialData(self):
        result = super(BattleAbilitySelectPopover, self)._prepareInitialData()
        result['battleAbilitiesButtonVisible'] = True
        if self.__isHintVisible():
            result['listOverlay'] = self.__getAbilityOverlayData()
        return result

    def _getDescText(self):
        result = text_styles.main(i18n.makeString(EPIC_BATTLE.FITTINGSELECTPOPOVERBATTKEABILITY_DESCTEXT))
        return result

    def __getAbilityOverlayData(self):
        icon = RES_ICONS.MAPS_ICONS_MODULES_BATTLEABILITYLISTOVERLAY
        data = {'icon': icon,
         'titleText': text_styles.highTitle(EPIC_BATTLE.FITTINGSELECTPOPOVERBATTKEABILITY_TITLETEXT),
         'descText': self._getDescText(),
         'okBtnLabel': '',
         'displayOkBtn': False,
         'isClickEnabled': False}
        return data

    def __isHintVisible(self):
        return not self.itemsCache.items.getItems(GUI_ITEM_TYPE.BATTLE_ABILITY, REQ_CRITERIA.UNLOCKED)


class OptionalDeviceSelectPopover(HangarFittingSelectPopover):
    itemsCache = dependency.descriptor(IItemsCache)
    _TABS = [{'label': MENU.OPTIONALDEVICESELECTPOPOVER_TABS_SIMPLE,
      'id': 'simpleOptDevices'}, {'label': MENU.OPTIONALDEVICESELECTPOPOVER_TABS_DELUXE,
      'id': 'deluxeOptDevices'}]

    def __init__(self, ctx=None):
        self.__initialLoad = True
        super(OptionalDeviceSelectPopover, self).__init__(ctx, None)
        return

    def listOverlayClosed(self):
        self.__setHintVisited()

    def setCurrentTab(self, tabIndex):
        if tabIndex == _POPOVER_FIRST_TAB_IDX and self.__isHintVisible():
            self.__setHintVisited()
        super(OptionalDeviceSelectPopover, self).setCurrentTab(tabIndex)

    def _dispose(self):
        if self.__isHintVisible():
            self.__setHintVisited()
        super(OptionalDeviceSelectPopover, self)._dispose()

    def _getInitialTabIndex(self):
        if self.__isHintVisible():
            self._saveTabIndex(_POPOVER_SECOND_TAB_IDX)
        if self.__initialLoad:
            self.__initialLoad = False
            vehicle = self._getVehicle()
            if vehicle is not None:
                installedDevice = self._getVehicle().optDevices[self._getSlotIndex()]
                if installedDevice:
                    if installedDevice.isDeluxe():
                        return _POPOVER_SECOND_TAB_IDX
                    return _POPOVER_FIRST_TAB_IDX
        return self.__class__._TAB_IDX

    def _prepareInitialData(self):
        result = super(OptionalDeviceSelectPopover, self)._prepareInitialData()
        if 'availableDevices' in result and self.__isHintVisible():
            result['listOverlay'] = self.__getListOverlayData(len(result['availableDevices']))
        return result

    def __getListOverlayData(self, count):
        icon = RES_ICONS.MAPS_ICONS_MODULES_LISTOVERLAY if count > 5 else RES_ICONS.MAPS_ICONS_MODULES_LISTOVERLAYSMALL
        data = {'icon': icon,
         'titleText': text_styles.highTitle(MENU.FITTINGSELECTPOPOVER_TITLETEXT),
         'descText': self._getDescText(),
         'okBtnLabel': i18n.makeString(MENU.FITTINGSELECTPOPOVER_OKBTNLABEL),
         'displayOkBtn': True,
         'isClickEnabled': True}
        return data

    def __isHintVisible(self):
        prefSetting = AccountSettings.getSettings(SHOW_OPT_DEVICE_HINT)
        return prefSetting and self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY_OR_UNLOCKED | REQ_CRITERIA.VEHICLE.LEVELS(_POPOVER_OVERLAY_VEH_LVL_RANGE))

    @staticmethod
    def __setHintVisited():
        return AccountSettings.setSettings(SHOW_OPT_DEVICE_HINT, False)


class BattleBoosterSelectPopover(HangarFittingSelectPopover):
    _TABS = [{'label': MENU.BOOSTERSELECTPOPOVER_TABS_FOREQUIPMENT,
      'id': 'boostersForAmmunition'}, {'label': MENU.BOOSTERSELECTPOPOVER_TABS_FORCREW,
      'id': 'boostersForCrew'}]

    def __init__(self, ctx=None, logicProvider=None):
        self.__initialLoad = True
        super(BattleBoosterSelectPopover, self).__init__(ctx, logicProvider)

    @decorators.process('loadStats')
    def setAutoRearm(self, autoRearm):
        vehicle = self._getVehicle()
        if vehicle is not None:
            yield VehicleAutoBattleBoosterEquipProcessor(vehicle, autoRearm).request()
        return

    def buyVehicleModule(self, moduleId):
        showBattleBoosterBuyDialog(int(moduleId), install=False)
        self.destroy()

    def _prepareInitialData(self):
        result = super(BattleBoosterSelectPopover, self)._prepareInitialData()
        result['rearmCheckboxVisible'] = True
        vehicle = g_currentVehicle.item
        result['rearmCheckboxValue'] = vehicle.isAutoBattleBoosterEquip() if vehicle is not None else False
        return result

    def _getCommonData(self):
        return (FITTING_TYPES.BOOSTER_FITTING_ITEM_RENDERER,
         FITTING_TYPES.BOOSTER_FITTING_RENDERER_DATA_CLASS_NAME,
         FITTING_TYPES.LARGE_POPOVER_WIDTH,
         MENU.BOOSTERSELECTPOPOVER_TITLE)

    def _getInitialTabIndex(self):
        if self.__initialLoad:
            self.__initialLoad = False
            vehicle = g_currentVehicle.item
            battleBooster = vehicle.equipment.battleBoosterConsumables[self._getSlotIndex()] if vehicle is not None else None
            if battleBooster:
                if battleBooster.isCrewBooster():
                    return _POPOVER_SECOND_TAB_IDX
                return _POPOVER_FIRST_TAB_IDX
        return self.__class__._TAB_IDX


class PopoverLogicProvider(object):
    itemsCache = dependency.descriptor(IItemsCache)
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, slotType, slotIndex, vehicle):
        self._slotType = slotType
        self._slotIndex = slotIndex
        self._vehicle = vehicle
        self._tooltipType = ''
        self.__modulesList = None
        self._selectedIdx = -1
        self._tabIndex = 0
        self._needToResetCounters = False
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

    def resetCounters(self):
        if self._needToResetCounters:
            self._settingsCore.serverSettings.saveInUIStorage({UI_STORAGE_KEYS.AUTO_RELOAD_MARK_IS_SHOWN: True})

    def _checkCounters(self, vehicleModule):
        if vehicleModule.itemTypeID == GUI_ITEM_TYPE.GUN and not self._needToResetCounters and vehicleModule.isAutoReloadable(self._vehicle.descriptor):
            self._needToResetCounters = True

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
            currXp = self.itemsCache.items.stats.vehiclesXPs.get(self._vehicle.intCD, 0)
            stats = {'money': self.itemsCache.items.stats.money,
             'exchangeRate': self.itemsCache.items.shop.exchangeRate,
             'currXP': currXp,
             'totalXP': currXp + self.itemsCache.items.stats.freeXP}
            hasAutoLoaderHighlights = False
            for idx, vehicleModule in enumerate(data):
                isInstalled = vehicleModule.isInstalled(self._vehicle, self._slotIndex)
                if isInstalled:
                    self._selectedIdx = idx
                moduleData = self._buildModuleData(vehicleModule, isInstalled, stats)
                self.__extendByTypeSpecificData(moduleData, vehicleModule)
                modulesList.append(moduleData)
                if 'highlightedParameterIdx' in moduleData:
                    hasAutoLoaderHighlights = True

            if hasAutoLoaderHighlights:
                self._settingsCore.serverSettings.updateUIStorageCounter(UI_STORAGE_KEYS.AUTO_RELOAD_HIGHLIGHTS_COUNTER)
        return modulesList

    def _getSuitableItems(self, typeId):
        if self._vehicle is None:
            return []
        else:
            criteria = REQ_CRITERIA.VEHICLE.SUITABLE([self._vehicle], [typeId]) | self._getSpecificCriteria(typeId)
            data = self.itemsCache.items.getItems(typeId, criteria).values()
            data.sort(reverse=True)
            return data

    def _getSpecificCriteria(self, typeID):
        if typeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            criteria = REQ_CRITERIA.BATTLE_BOOSTER.OPTIONAL_DEVICE_EFFECT if self._tabIndex == _POPOVER_FIRST_TAB_IDX else REQ_CRITERIA.BATTLE_BOOSTER.CREW_EFFECT
        elif typeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            criteria = REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE if self._tabIndex == _POPOVER_FIRST_TAB_IDX else REQ_CRITERIA.OPTIONAL_DEVICE.DELUXE
        elif typeID == GUI_ITEM_TYPE.BATTLE_ABILITY:
            criteria = REQ_CRITERIA.UNLOCKED
        else:
            criteria = REQ_CRITERIA.EMPTY
        return criteria

    def __extendByTypeSpecificData(self, moduleData, vehicleModule):
        if vehicleModule.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
            _extendByArtefactData(moduleData, vehicleModule, self._slotIndex)
        elif vehicleModule.itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES:
            _extendByModuleData(moduleData, vehicleModule, self._vehicle.descriptor)
        if self._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
            _extendByOptionalDeviceData(moduleData, vehicleModule)
        elif self._slotType == FITTING_TYPES.BOOSTER:
            _extendByBattleBoosterData(moduleData, vehicleModule, self._vehicle)
        elif self._slotType == FITTING_TYPES.BATTLE_ABILITY:
            _extendByBattleAbilityData(moduleData, vehicleModule, self._slotIndex)


class _HangarLogicProvider(PopoverLogicProvider):

    def __init__(self, slotType, slotIndex):
        super(_HangarLogicProvider, self).__init__(slotType, slotIndex, g_currentVehicle.item)
        if slotType == FITTING_TYPES.BOOSTER:
            self._tooltipType = TOOLTIPS_CONSTANTS.BATTLE_BOOSTER
        elif slotType == FITTING_TYPES.BATTLE_ABILITY:
            self._tooltipType = TOOLTIPS_CONSTANTS.EPIC_SKILL_SLOT_INFO
        else:
            self._tooltipType = TOOLTIPS_CONSTANTS.HANGAR_MODULE

    def setModule(self, newId, oldId, isRemove):
        module = self.itemsCache.items.getItemByCD(int(newId))
        if module.isUnlocked or self._slotType == FITTING_TYPES.OPTIONAL_DEVICE:
            if oldId < 0:
                if not isRemove and self._slotType == FITTING_TYPES.OPTIONAL_DEVICE and g_currentVehicle.isPresent():
                    installedOptDevice = g_currentVehicle.item.optDevices[self._slotIndex]
                    oldId = installedOptDevice.intCD if installedOptDevice else None
                else:
                    oldId = None
            ItemsActionsFactory.doAction(ItemsActionsFactory.SET_VEHICLE_MODULE, self._vehicle.invID, newId, self._slotIndex, oldId, isRemove)
        elif self._slotType == FITTING_TYPES.BOOSTER:
            battleBooster = 0 if isRemove else module
            if battleBooster and not battleBooster.isInInventory:
                showBattleBoosterBuyDialog(int(newId), install=True)
            else:
                ItemsActionsFactory.doAction(ItemsActionsFactory.SET_VEHICLE_LAYOUT, self._vehicle, None, None, battleBooster)
        return

    def _buildModuleData(self, vehicleModule, isInstalledInSlot, stats):
        itemPrice = vehicleModule.buyPrices.itemPrice
        inInventory = vehicleModule.isInInventory
        isInstalled = vehicleModule.isInstalled(self._vehicle)
        isBought = inInventory or isInstalled
        isEnoughMoney, purchaseReason = vehicleModule.mayPurchase(stats['money'])
        if vehicleModule.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and not isInstalled and vehicleModule.hasSimilarDevicesInstalled(self._vehicle) and isEnoughMoney:
            isFit, reason = False, GUI_ITEM_ECONOMY_CODE.ITEM_IS_DUPLICATED
        elif isBought:
            isFit, reason = vehicleModule.mayInstall(self._vehicle, self._slotIndex)
            if reason == 'already installed' or isFit:
                isFit, reason = True, GUI_ITEM_ECONOMY_CODE.UNDEFINED
        else:
            isFit, reason = isEnoughMoney, purchaseReason
            if not isFit:
                if GUI_ITEM_ECONOMY_CODE.isMoneyError(reason):
                    isFit = vehicleModule.mayPurchaseWithExchange(stats['money'], stats['exchangeRate'])
        if reason != GUI_ITEM_ECONOMY_CODE.UNLOCK_ERROR:
            installReason = _getInstallReason(vehicleModule, self._vehicle, reason, self._slotIndex)
        else:
            installReason = reason
        self._checkCounters(vehicleModule)
        moduleData = self._buildCommonModuleData(vehicleModule, installReason)
        moduleData.update({'targetVisible': isBought,
         'showPrice': not isBought,
         'isSelected': isInstalledInSlot,
         'disabled': not isFit or isInstalled and not isInstalledInSlot,
         'removeButtonLabel': MENU.MODULEFITS_REMOVENAME,
         'removeButtonTooltip': MENU.MODULEFITS_REMOVETOOLTIP,
         'itemPrices': getItemPricesVOWithReason(reason, itemPrice)})
        if vehicleModule.itemTypeID == GUI_ITEM_TYPE.BATTLE_ABILITY:
            moduleData['disabled'] = isInstalled and not isInstalledInSlot
            moduleData['showPrice'] = False
        return moduleData


class _BootCampLogicProvider(_HangarLogicProvider):

    def _buildModuleData(self, module, isInstalledInSlot, stats):
        data = super(_BootCampLogicProvider, self)._buildModuleData(module, isInstalledInSlot, stats)
        if self._slotType == FITTING_TYPES.OPTIONAL_DEVICE and isInstalledInSlot:
            data.update({'disabled': True})
        return data

    def _buildList(self):
        defaultModules = super(_BootCampLogicProvider, self)._buildList()
        if self._slotType != FITTING_TYPES.OPTIONAL_DEVICE:
            return defaultModules
        else:
            nationData = g_bootcamp.getNationData()
            optionalDeviceId = nationData['equipment']
            optionalDeviceValue = None
            for device in defaultModules:
                if device['id'] == optionalDeviceId:
                    optionalDeviceValue = device

            if optionalDeviceValue is not None:
                defaultModules.remove(optionalDeviceValue)
                defaultModules.insert(0, optionalDeviceValue)
            scrollCountOptionalDevices = g_bootcamp.getContextIntParameter('scrollCountOptionalDevices')
            del defaultModules[scrollCountOptionalDevices:]
            return defaultModules


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
        self._checkCounters(vehicleModule)
        return moduleData
