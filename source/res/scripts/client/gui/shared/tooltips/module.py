# Embedded file name: scripts/client/gui/shared/tooltips/module.py
import gui
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.Scaleform.locale.MENU import MENU
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.tooltips import ToolTipDataField, getComplexStatus, getUnlockPrice, ToolTipParameterField, ToolTipData, ToolTipAttrField, ToolTipMethodCheckField, TOOLTIP_TYPE
from gui.shared.utils import ItemsParameters, GUN_CAN_BE_CLIP, GUN_CLIP, SHELLS_COUNT_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, AIMING_TIME_PROP_NAME, RELOAD_TIME_PROP_NAME, CLIP_ICON_PATH
from helpers.i18n import makeString
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import i18n

class ModuleStatusField(ToolTipDataField):

    def _getValue(self):
        module = self._tooltip.item
        configuration = self._tooltip.context.getStatusConfiguration(module)
        if configuration.isResearchPage:
            return self._getResearchPageStatus(module, configuration)
        else:
            return self._getStatus(module, configuration)

    def _getStatus(self, module, configuration):
        vehicle = configuration.vehicle
        slotIdx = configuration.slotIdx
        eqs = configuration.eqs
        checkBuying = configuration.checkBuying
        isEqOrDev = module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS
        isFit = True
        reason = ''
        if checkBuying:
            isFit, reason = module.mayPurchase(g_itemsCache.items.stats.money)
        if isFit and vehicle is not None and vehicle.isInInventory:
            currentVehicleEqs = list()
            if vehicle is not None and vehicle.isInInventory:
                currentVehicleEqs = list(vehicle.eqs)
                vehicle.eqs = [None, None, None]
                if eqs:
                    for i, e in enumerate(eqs):
                        if e is not None:
                            intCD = int(e)
                            eq = g_itemsCache.items.getItemByCD(intCD)
                            vehicle.eqs[i] = eq

            isFit, reason = module.mayInstall(vehicle, slotIdx)
            vehicle.eqs = list(currentVehicleEqs)
        inventoryVehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
        installedVehicles = map(lambda x: x.shortUserName, module.getInstalledVehicles(inventoryVehicles))[:self._tooltip.MAX_INSTALLED_LIST_LEN]
        messageLvl = Vehicle.VEHICLE_STATE_LEVEL.WARNING
        tooltipHeader = ''
        tooltipText = ''
        if not isFit:
            reason = reason.replace(' ', '_')
            tooltipHeader, tooltipText = getComplexStatus('#tooltips:moduleFits/%s' % reason)
            if reason == 'credit_error' or reason == 'gold_error':
                messageLvl = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
            elif reason == 'not_with_installed_equipment':
                if vehicle is not None:
                    conflictEqs = module.getConflictedEquipments(vehicle)
                    tooltipText %= {'eqs': ', '.join([ makeString(e.userName) for e in conflictEqs ])}
            elif reason == 'already_installed' and isEqOrDev and len(installedVehicles):
                tooltipHeader, _ = getComplexStatus('#tooltips:deviceFits/already_installed' if module.itemTypeName == GUI_ITEM_TYPE.OPTIONALDEVICE else '#tooltips:moduleFits/already_installed')
                tooltipText = ', '.join(installedVehicles)
        elif len(installedVehicles):
            tooltipHeader, _ = getComplexStatus('#tooltips:deviceFits/already_installed' if module.itemTypeName == GUI_ITEM_TYPE.OPTIONALDEVICE else '#tooltips:moduleFits/already_installed')
            tooltipText = ', '.join(installedVehicles)
        return {'level': messageLvl,
         'header': tooltipHeader,
         'text': tooltipText}

    def _getResearchPageStatus(self, module, configuration):
        vehicle = configuration.vehicle
        node = configuration.node

        def status(header = None, text = None, level = Vehicle.VEHICLE_STATE_LEVEL.WARNING):
            if header is not None or text is not None:
                return {'header': header,
                 'text': text,
                 'level': level}
            else:
                return
                return

        header, text = (None, None)
        level = Vehicle.VEHICLE_STATE_LEVEL.WARNING
        nodeState = int(node.state)
        statusTemplate = '#tooltips:researchPage/module/status/%s'
        parentCD = vehicle.intCD if vehicle is not None else None
        _, _, need = getUnlockPrice(module.intCD, parentCD)
        if not nodeState & NODE_STATE.UNLOCKED:
            if not vehicle.isUnlocked:
                header, text = getComplexStatus(statusTemplate % 'rootVehicleIsLocked')
            elif not nodeState & NODE_STATE.NEXT_2_UNLOCK:
                header, text = getComplexStatus(statusTemplate % 'parentModuleIsLocked')
            elif need > 0:
                header, text = getComplexStatus(statusTemplate % 'notEnoughXP')
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
            return status(header, text, level)
        elif not vehicle.isInInventory:
            header, text = getComplexStatus(statusTemplate % 'needToBuyTank')
            text %= {'vehiclename': vehicle.userName}
            return status(header, text, Vehicle.VEHICLE_STATE_LEVEL.WARNING)
        elif nodeState & NODE_STATE.INSTALLED:
            return status()
        else:
            if vehicle is not None:
                if vehicle.isInInventory:
                    vState = vehicle.getState()
                    if vState == 'battle':
                        header, text = getComplexStatus(statusTemplate % 'vehicleIsInBattle')
                    elif vState == 'locked':
                        header, text = getComplexStatus(statusTemplate % 'vehicleIsReadyToFight')
                    elif vState == 'damaged' or vState == 'exploded' or vState == 'destroyed':
                        header, text = getComplexStatus(statusTemplate % 'vehicleIsBroken')
                if header is not None or text is not None:
                    return status(header, text, level)
            return self._getStatus(module, configuration)


class ModuleStatsField(ToolTipDataField):

    def _getValue(self):
        result = []
        module = self._tooltip.item
        configuration = self._tooltip.context.getStatsConfiguration(module)
        vehicle = configuration.vehicle
        sellPrice = configuration.sellPrice
        buyPrice = configuration.buyPrice
        unlockPrice = configuration.unlockPrice
        inventoryCount = configuration.inventoryCount
        vehiclesCount = configuration.vehiclesCount
        researchNode = configuration.node
        if buyPrice and sellPrice:
            LOG_ERROR('You are not allowed to use buyPrice and sellPrice at the same time')
            return
        else:

            def checkState(state):
                if researchNode is not None:
                    return bool(int(researchNode.state) & state)
                else:
                    return False

            isEqOrDev = module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS
            isNextToUnlock = checkState(NODE_STATE.NEXT_2_UNLOCK)
            isInstalled = checkState(NODE_STATE.INSTALLED)
            isInInventory = checkState(NODE_STATE.IN_INVENTORY)
            isUnlocked = checkState(NODE_STATE.UNLOCKED)
            isAutoUnlock = checkState(NODE_STATE.AUTO_UNLOCKED)
            items = g_itemsCache.items
            credits, gold = items.stats.money
            itemPrice = (0, 0)
            if module is not None:
                itemPrice = module.buyPrice
            isMoneyEnough = credits >= itemPrice[0] and gold >= itemPrice[1]
            if unlockPrice and not isEqOrDev:
                parentCD = vehicle.intCD if vehicle is not None else None
                isAvailable, cost, need = getUnlockPrice(module.intCD, parentCD)
                unlockPriceStat = [cost]
                if not isUnlocked and isNextToUnlock and need > 0:
                    unlockPriceStat.append(need)
                if cost > 0:
                    result.append(('unlock_price', unlockPriceStat))
            if buyPrice and not isAutoUnlock:
                price = module.altPrice or module.buyPrice
                rootInInv = vehicle is not None and vehicle.isInInventory
                if researchNode:
                    showNeeded = rootInInv and not isMoneyEnough and (isNextToUnlock or isUnlocked) and not (isInstalled or isInInventory)
                else:
                    isModuleUnlocked = module.isUnlocked
                    isModuleInInventory = module.isInInventory
                    showNeeded = not isModuleInInventory and isModuleUnlocked
                need = (0, 0)
                if isEqOrDev or showNeeded:
                    creditsNeeded = price[0] - credits if price[0] else 0
                    goldNeeded = price[1] - gold if price[1] else 0
                    need = (max(0, creditsNeeded), max(0, goldNeeded))
                result.append(('buy_price', (price, need)))
                result.append(('def_buy_price', module.defaultAltPrice or module.defaultPrice))
                result.append(('action_prc', module.actionPrc))
            if sellPrice:
                result.append(('sell_price', module.sellPrice))
                result.append(('def_sell_price', module.defaultSellPrice))
                result.append(('action_prc', module.sellActionPrc))
            if inventoryCount:
                count = module.inventoryCount
                if count:
                    result.append(('inventoryCount', count))
            if vehiclesCount:
                inventoryVehicles = items.getVehicles(REQ_CRITERIA.INVENTORY)
                count = len(module.getInstalledVehicles(inventoryVehicles.itervalues()))
                if count:
                    result.append(('vehicleCount', count))
                    if count > self._tooltip.MAX_INSTALLED_LIST_LEN:
                        hiddenVehicleCount = count - self._tooltip.MAX_INSTALLED_LIST_LEN
                        result.append(('hiddenVehicleCount', hiddenVehicleCount))
            return result


class ModuleParamsField(ToolTipParameterField):

    def _getValue(self):
        result = list()
        module = self._tooltip.item
        configuration = self._tooltip.context.getParamsConfiguration(module)
        vehicle = configuration.vehicle
        params = configuration.params
        vDescr = vehicle.descriptor if vehicle is not None else None
        moduleParams = dict(ItemsParameters.g_instance.getParameters(module.descriptor, vDescr))
        paramsKeyName = module.itemTypeName
        if params:
            if module.itemTypeID == GUI_ITEM_TYPE.GUN:
                reloadingType = module.getReloadingType(vehicle.descriptor if vehicle is not None else None)
                if reloadingType == GUN_CLIP:
                    paramsKeyName = self._tooltip.CLIP_GUN_MODULE_PARAM
            p = self._tooltip.MODULE_PARAMS.get(paramsKeyName)
            if p is not None:
                result.append([])
                for paramName in p:
                    if paramName in moduleParams:
                        result[-1].append([paramName, moduleParams.get(paramName)])

        return result


class ModuleInfoExtraField(ToolTipDataField):

    def _getValue(self):
        module = self._tooltip.item
        configuration = self._tooltip.context.getParamsConfiguration(module)
        vehicle = configuration.vehicle
        vDescr = vehicle.descriptor if vehicle is not None else None
        self._isAvailable = module.itemTypeID == GUI_ITEM_TYPE.GUN and module.isClipGun(vDescr)
        return {'source': CLIP_ICON_PATH,
         'text': '<h>' + makeString(MENU.MODULEINFO_CLIPGUNLABEL) + '</h>'}


class ModuleParamsExtraField(ToolTipDataField):

    def _getValue(self):
        result = list()
        module = self._tooltip.item
        configuration = self._tooltip.context.getParamsConfiguration(module)
        vehicle = configuration.vehicle
        vDescr = vehicle.descriptor if vehicle is not None else None
        imgPathArr = CLIP_ICON_PATH.split('..')
        imgPath = 'img://gui' + imgPathArr[1]
        if module.itemTypeID == GUI_ITEM_TYPE.GUN and module.getReloadingType(vDescr) == GUN_CAN_BE_CLIP:
            moduleParams = dict(ItemsParameters.g_instance.getParameters(module.descriptor, vDescr))
            extraParamsKeyName = self._tooltip.CLIP_GUN_MODULE_PARAM
            extra = self._tooltip.EXTRA_MODULE_PARAMS.get(extraParamsKeyName)
            if extra is not None:
                for paramName in extra:
                    if paramName in moduleParams:
                        result.append([paramName, moduleParams.get(paramName)])

            if result:
                self._isAvailable = True
                return {'headerText': i18n.makeString(MENU.MODULEINFO_PARAMETERSCLIPGUNLABEL, imgPath),
                 'params': result}
        self._isAvailable = False
        return super(ModuleParamsExtraField, self)._getValue()


class ModuleFitReasonCheckField(ToolTipDataField):

    def __init__(self, context, name, reason):
        super(ModuleFitReasonCheckField, self).__init__(context, name)
        self.__reason = reason

    def _getValue(self):
        module = self._tooltip.item
        configuration = self._tooltip.context.getStatusConfiguration(module)
        vehicle = configuration.vehicle
        slotIdx = configuration.slotIdx
        if vehicle is not None:
            isFit, reason = module.mayInstall(vehicle, slotIdx)
            if not isFit:
                reason = reason.replace(' ', '_')
                return reason == self.__reason
        return False


class ModuleNoteField(ToolTipDataField):

    def _getValue(self):
        module = self._tooltip.item
        if module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
            if not module.isRemovable:
                return {'title': gui.makeHtmlString('html_templates:lobby/tooltips', 'permanent_module_title'),
                 'text': gui.makeHtmlString('html_templates:lobby/tooltips', 'permanent_module_note', {'gold': g_itemsCache.items.shop.paidRemovalCost})}
        return None


class ModuleEffectField(ToolTipDataField):

    def _getValue(self):
        module = self._tooltip.item
        if module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:

            def checkLocalization(key):
                localization = makeString('#artefacts:%s' % key)
                return (key != localization, localization)

            onUse = checkLocalization('%s/onUse' % module.descriptor['name'])
            always = checkLocalization('%s/always' % module.descriptor['name'])
            restriction = checkLocalization('%s/restriction' % module.descriptor['name'])
            return {'onUse': onUse[1] if onUse[0] else '',
             'always': always[1] if always[0] else '',
             'restriction': restriction[1] if restriction[0] else ''}
        else:
            return None


class ModuleTooltipData(ToolTipData):
    CLIP_GUN_MODULE_PARAM = 'vehicleClipGun'
    MAX_INSTALLED_LIST_LEN = 10
    MODULE_PARAMS = {GUI_ITEM_TYPE_NAMES[2]: ('maxLoad', 'rotationSpeed', 'weight'),
     GUI_ITEM_TYPE_NAMES[3]: ('armor', 'rotationSpeed', 'circularVisionRadius', 'weight'),
     GUI_ITEM_TYPE_NAMES[4]: (RELOAD_TIME_PROP_NAME,
                              'avgPiercingPower',
                              'avgDamage',
                              'dispertionRadius',
                              AIMING_TIME_PROP_NAME,
                              'weight'),
     GUI_ITEM_TYPE_NAMES[5]: ('enginePower', 'fireStartingChance', 'weight'),
     GUI_ITEM_TYPE_NAMES[7]: ('radioDistance', 'weight'),
     GUI_ITEM_TYPE_NAMES[9]: ('weight',),
     CLIP_GUN_MODULE_PARAM: (SHELLS_COUNT_PROP_NAME,
                             SHELL_RELOADING_TIME_PROP_NAME,
                             RELOAD_MAGAZINE_TIME_PROP_NAME,
                             'avgPiercingPower',
                             'avgDamage',
                             'dispertionRadius',
                             AIMING_TIME_PROP_NAME,
                             'weight')}
    EXTRA_MODULE_PARAMS = {CLIP_GUN_MODULE_PARAM: (SHELLS_COUNT_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME)}

    def __init__(self, context):
        super(ModuleTooltipData, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self.fields = (ToolTipAttrField(self, 'level'),
         ToolTipAttrField(self, 'name', 'userName'),
         ToolTipAttrField(self, 'type', 'itemTypeName'),
         ToolTipAttrField(self, 'removeable', 'isRemovable'),
         ToolTipAttrField(self, 'descr', 'shortDescription'),
         ToolTipMethodCheckField(self, 'gold', 'gold', 'getSellPriceCurrency'),
         ModuleFitReasonCheckField(self, 'tooHeavy', 'too_heavy'),
         ModuleStatsField(self, 'stats'),
         ModuleParamsField(self, 'params'),
         ModuleNoteField(self, 'note'),
         ModuleEffectField(self, 'effect'),
         ModuleParamsExtraField(self, 'paramsEx'),
         ModuleInfoExtraField(self, 'extraModuleInfo'),
         ModuleStatusField(self, 'status'))
