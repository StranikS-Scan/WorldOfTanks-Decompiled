# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/module.py
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared import g_itemsCache
from gui.shared.economics import getActionPrc
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters import params_helper, MAX_RELATIVE_VALUE, formatters as params_formatters
from gui.shared.tooltips import getComplexStatus, getUnlockPrice, TOOLTIP_TYPE
from gui.shared.utils import GUN_CLIP, SHELLS_COUNT_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, AIMING_TIME_PROP_NAME, RELOAD_TIME_PROP_NAME
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.shared.tooltips import formatters
from gui.shared.money import ZERO_MONEY
from helpers.i18n import makeString as _ms
from items import VEHICLE_COMPONENT_TYPE_NAMES, ITEM_TYPES
_TOOLTIP_MIN_WIDTH = 420
_TOOLTIP_MAX_WIDTH = 480
_AUTOCANNON_SHOT_DISTANCE = 400

class ModuleBlockTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(ModuleBlockTooltipData, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        return

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        items = super(ModuleBlockTooltipData, self)._packBlocks()
        module = self.item
        statsConfig = self.context.getStatsConfiguration(module)
        paramsConfig = self.context.getParamsConfiguration(module)
        statusConfig = self.context.getStatusConfiguration(module)
        leftPadding = 20
        rightPadding = 20
        topPadding = 20
        blockTopPadding = -4
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding)
        textGap = -2
        valueWidth = 110
        items.append(formatters.packBuildUpBlockData(HeaderBlockConstructor(module, statsConfig, leftPadding, rightPadding).construct(), padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding)))
        if module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
            effectsBlock = EffectsBlockConstructor(module, statusConfig, leftPadding, rightPadding).construct()
            if len(effectsBlock) > 0:
                items.append(formatters.packBuildUpBlockData(effectsBlock, padding=blockPadding, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        priceBlock, invalidWidth = PriceBlockConstructor(module, statsConfig, valueWidth, leftPadding, rightPadding).construct()
        if len(priceBlock) > 0:
            self._setWidth(_TOOLTIP_MAX_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
            items.append(formatters.packBuildUpBlockData(priceBlock, padding=blockPadding, gap=textGap))
        if statsConfig.vehicle is not None and not module.isInstalled(statsConfig.vehicle):
            if module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
                comparator = params_helper.artifactComparator(statsConfig.vehicle, module, statsConfig.slotIdx)
            else:
                comparator = params_helper.itemOnVehicleComparator(statsConfig.vehicle, module)
            stockParams = params_helper.getParameters(g_itemsCache.items.getStockVehicle(statsConfig.vehicle.intCD))
            simplifiedBlock = SimplifiedStatsBlockConstructor(module, paramsConfig, leftPadding, rightPadding, stockParams, comparator).construct()
            if len(simplifiedBlock) > 0:
                items.append(formatters.packBuildUpBlockData(simplifiedBlock, gap=-4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=-14, bottom=1), stretchBg=True))
        statsModules = GUI_ITEM_TYPE.VEHICLE_MODULES + (GUI_ITEM_TYPE.OPTIONALDEVICE,)
        if module.itemTypeID in statsModules:
            commonStatsBlock = CommonStatsBlockConstructor(module, paramsConfig, statsConfig.slotIdx, valueWidth, leftPadding, rightPadding).construct()
            if len(commonStatsBlock) > 0:
                items.append(formatters.packBuildUpBlockData(commonStatsBlock, padding=blockPadding, gap=textGap))
        if not module.isRemovable:
            items.append(formatters.packBuildUpBlockData(ArtefactBlockConstructor(module, statusConfig, leftPadding, rightPadding).construct(), gap=-4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_COMPLEX_BG_LINKAGE, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=2), stretchBg=False))
        statusBlock = StatusBlockConstructor(module, statusConfig, leftPadding, rightPadding).construct()
        if len(statusBlock) > 0:
            items.append(formatters.packBuildUpBlockData(statusBlock, padding=blockPadding))
        return items


class ModuleTooltipBlockConstructor(object):
    MAX_INSTALLED_LIST_LEN = 10
    CLIP_GUN_MODULE_PARAM = 'vehicleClipGun'
    MODULE_PARAMS = {GUI_ITEM_TYPE.CHASSIS: ('maxLoad', 'rotationSpeed', 'weight'),
     GUI_ITEM_TYPE.TURRET: ('armor', 'rotationSpeed', 'circularVisionRadius', 'weight'),
     GUI_ITEM_TYPE.GUN: (RELOAD_TIME_PROP_NAME,
                         'avgPiercingPower',
                         'avgDamage',
                         'dispertionRadius',
                         AIMING_TIME_PROP_NAME,
                         'maxShotDistance',
                         'weight'),
     GUI_ITEM_TYPE.ENGINE: ('enginePower', 'fireStartingChance', 'weight'),
     GUI_ITEM_TYPE.RADIO: ('radioDistance', 'weight'),
     GUI_ITEM_TYPE.OPTIONALDEVICE: ('weight',),
     CLIP_GUN_MODULE_PARAM: (SHELLS_COUNT_PROP_NAME,
                             SHELL_RELOADING_TIME_PROP_NAME,
                             RELOAD_MAGAZINE_TIME_PROP_NAME,
                             'avgPiercingPower',
                             'avgDamage',
                             'dispertionRadius',
                             'maxShotDistance',
                             AIMING_TIME_PROP_NAME,
                             'weight')}
    EXTRA_MODULE_PARAMS = {CLIP_GUN_MODULE_PARAM: (SHELLS_COUNT_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME)}

    def __init__(self, module, configuration, leftPadding=20, rightPadding=20):
        self.module = module
        self.configuration = configuration
        self.leftPadding = leftPadding
        self.rightPadding = rightPadding

    def construct(self):
        return None


class HeaderBlockConstructor(ModuleTooltipBlockConstructor):

    def __init__(self, module, configuration, leftPadding, rightPadding):
        super(HeaderBlockConstructor, self).__init__(module, configuration, leftPadding, rightPadding)

    def construct(self):
        module = self.module
        block = []
        title = module.userName
        imgPaddingLeft = 27
        desc = ''
        if module.itemTypeName in VEHICLE_COMPONENT_TYPE_NAMES:
            desc = text_styles.stats(_ms(TOOLTIPS.level(str(module.level)))) + ' ' + _ms(TOOLTIPS.VEHICLE_LEVEL)
            imgPaddingLeft = 22
        block.append(formatters.packImageTextBlockData(title=text_styles.highTitle(title), desc=text_styles.standard(desc), img=module.icon, imgPadding=formatters.packPadding(left=imgPaddingLeft), txtGap=-3, txtOffset=130 - self.leftPadding, padding=formatters.packPadding(top=-6)))
        if module.itemTypeID == GUI_ITEM_TYPE.GUN:
            vehicle = self.configuration.vehicle
            vDescr = vehicle.descriptor if vehicle is not None else None
            if module.isClipGun(vDescr):
                block.append(formatters.packImageTextBlockData(title=text_styles.standard(MENU.MODULEINFO_CLIPGUNLABEL), desc='', img=RES_ICONS.MAPS_ICONS_MODULES_MAGAZINEGUNICON, imgPadding=formatters.packPadding(top=3), padding=formatters.packPadding(left=108, top=9)))
        return block


class PriceBlockConstructor(ModuleTooltipBlockConstructor):

    def __init__(self, module, configuration, valueWidth, leftPadding, rightPadding):
        super(PriceBlockConstructor, self).__init__(module, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth

    def construct(self):
        block = []
        module = self.module
        slotIdx = self.configuration.slotIdx
        vehicle = self.configuration.vehicle
        sellPrice = self.configuration.sellPrice
        buyPrice = self.configuration.buyPrice
        unlockPrice = self.configuration.unlockPrice
        inventoryCount = self.configuration.inventoryCount
        vehiclesCount = self.configuration.vehiclesCount
        researchNode = self.configuration.node
        if buyPrice and sellPrice:
            LOG_ERROR('You are not allowed to use buyPrice and sellPrice at the same time')
            return
        else:

            def checkState(state):
                return bool(int(researchNode.state) & state) if researchNode is not None else False

            isEqOrDev = module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS
            isNextToUnlock = checkState(NODE_STATE.NEXT_2_UNLOCK)
            isInstalled = checkState(NODE_STATE.INSTALLED)
            isInInventory = checkState(NODE_STATE.IN_INVENTORY)
            isUnlocked = checkState(NODE_STATE.UNLOCKED)
            isAutoUnlock = checkState(NODE_STATE.AUTO_UNLOCKED)
            items = g_itemsCache.items
            money = items.stats.money
            itemPrice = ZERO_MONEY
            if module is not None:
                itemPrice = module.buyPrice
            isMoneyEnough = money >= itemPrice
            leftPadding = 92
            if unlockPrice and not isEqOrDev:
                parentCD = vehicle.intCD if vehicle is not None else None
                isAvailable, cost, need = getUnlockPrice(module.intCD, parentCD)
                neededValue = None
                if not isUnlocked and isNextToUnlock and need > 0:
                    neededValue = need
                if cost > 0:
                    block.append(makePriceBlock(cost, CURRENCY_SETTINGS.UNLOCK_PRICE, neededValue, leftPadding=leftPadding, valueWidth=self._valueWidth))
            creditsActionPercent, goldActionPercent = (0, 0)
            need = ZERO_MONEY
            if buyPrice and not isAutoUnlock:
                price = module.altPrice or module.buyPrice
                defPrice = module.defaultAltPrice or module.defaultPrice
                rootInInv = vehicle is not None and vehicle.isInInventory
                if researchNode:
                    showNeeded = rootInInv and not isMoneyEnough and (isNextToUnlock or isUnlocked) and not (isInstalled or isInInventory)
                else:
                    isModuleUnlocked = module.isUnlocked
                    isModuleInInventory = module.isInInventory
                    showNeeded = not isModuleInInventory and isModuleUnlocked
                if isEqOrDev or showNeeded:
                    need = price - money
                    need = need.toNonNegative()
                if price.credits > 0:
                    creditsActionPercent = getActionPrc(price.credits, defPrice.credits)
                    block.append(makePriceBlock(price.credits, CURRENCY_SETTINGS.BUY_CREDITS_PRICE, need.credits if need.credits > 0 else None, defPrice.credits if defPrice.credits > 0 else None, creditsActionPercent, self._valueWidth, leftPadding))
                if price.gold > 0:
                    goldActionPercent = getActionPrc(price.gold, defPrice.gold)
                    block.append(formatters.packTextBlockData(text=text_styles.standard(TOOLTIPS.VEHICLE_TEXTDELIMITER_OR), padding=formatters.packPadding(left=(101 if goldActionPercent > 0 else 81) + self.leftPadding)))
                    block.append(makePriceBlock(price.gold, CURRENCY_SETTINGS.BUY_GOLD_PRICE, need.gold if need.gold > 0 else None, defPrice.gold if defPrice.gold > 0 else None, goldActionPercent, self._valueWidth, leftPadding))
            if sellPrice:
                block.append(makePriceBlock(module.sellPrice.credits, CURRENCY_SETTINGS.SELL_PRICE, oldPrice=module.defaultSellPrice.credits, percent=module.sellActionPrc, valueWidth=self._valueWidth, leftPadding=leftPadding))
            if inventoryCount:
                count = module.inventoryCount
                if count > 0:
                    block.append(formatters.packTextParameterBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_INVENTORYCOUNT), value=text_styles.stats(count), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5)))
            if vehiclesCount:
                inventoryVehicles = items.getVehicles(REQ_CRITERIA.INVENTORY)
                count = len(module.getInstalledVehicles(inventoryVehicles.itervalues()))
                if count > 0:
                    block.append(formatters.packTextParameterBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_VEHICLECOUNT), value=text_styles.stats(count), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5)))
            notEnoughMoney = need > ZERO_MONEY
            hasAction = creditsActionPercent > 0 or goldActionPercent > 0 or module.sellActionPrc > 0
            return (block, notEnoughMoney or hasAction)


class CommonStatsBlockConstructor(ModuleTooltipBlockConstructor):

    def __init__(self, module, configuration, slotIdx, valueWidth, leftPadding, rightPadding):
        super(CommonStatsBlockConstructor, self).__init__(module, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        self._slotIdx = slotIdx

    def construct(self):
        module = self.module
        vehicle = self.configuration.vehicle
        params = self.configuration.params
        block = []
        vDescr = vehicle.descriptor if vehicle is not None else None
        moduleParams = dict(params_helper.getParameters(module, vDescr))
        paramsKeyName = module.itemTypeID
        if params:
            reloadingType = None
            if module.itemTypeID == GUI_ITEM_TYPE.GUN:
                reloadingType = module.getReloadingType(vehicle.descriptor if vehicle is not None else None)
            if reloadingType == GUN_CLIP:
                paramsKeyName = self.CLIP_GUN_MODULE_PARAM
            paramsList = self.MODULE_PARAMS.get(paramsKeyName, [])
            if vehicle is not None:
                if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                    currModule = module
                else:
                    currModuleDescr, _ = vehicle.descriptor.getComponentsByType(module.itemTypeName)
                    currModule = g_itemsCache.items.getItemByCD(currModuleDescr['compactDescr'])
                comparator = params_helper.itemsComparator(module, currModule, vehicle.descriptor)
                for paramName in paramsList:
                    if paramName in moduleParams:
                        paramInfo = comparator.getExtendedData(paramName)
                        fmtValue = params_formatters.colorizedFormatParameter(paramInfo, params_formatters.BASE_FORMATTERS)
                        if fmtValue is not None:
                            block.append(formatters.packTextParameterBlockData(name=params_formatters.formatModuleParamName(paramName), value=fmtValue, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5)))

            else:
                formattedModuleParameters = params_formatters.getFormattedParamsList(module.descriptor, moduleParams)
                for paramName, paramValue in formattedModuleParameters:
                    if paramName in paramsList and paramValue is not None:
                        block.append(formatters.packTextParameterBlockData(name=params_formatters.formatModuleParamName(paramName), value=paramValue, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5)))

        if len(block) > 0:
            block.insert(0, formatters.packTextBlockData(text_styles.middleTitle(_ms(TOOLTIPS.TANKCARUSEL_MAINPROPERTY)), padding=formatters.packPadding(bottom=8)))
        return block


class SimplifiedStatsBlockConstructor(ModuleTooltipBlockConstructor):

    def __init__(self, module, configuration, leftPadding, rightPadding, stockParams, comparator):
        self.__stockParams = stockParams
        self.__comparator = comparator
        super(SimplifiedStatsBlockConstructor, self).__init__(module, configuration, leftPadding, rightPadding)

    def construct(self):
        block = []
        for parameter in params_formatters.getRelativeDiffParams(self.__comparator):
            delta = parameter.state[1]
            value = parameter.value
            if delta > 0:
                value -= delta
            block.append(formatters.packStatusDeltaBlockData(title=text_styles.middleTitle(MENU.tank_params(parameter.name)), valueStr=params_formatters.simlifiedDeltaParameter(parameter), statusBarData={'value': value,
             'delta': delta,
             'minValue': 0,
             'markerValue': self.__stockParams[parameter.name],
             'maxValue': MAX_RELATIVE_VALUE,
             'useAnim': False}, padding=formatters.packPadding(left=105, top=8)))

        return block


class ArtefactBlockConstructor(ModuleTooltipBlockConstructor):

    def __init__(self, module, configuration, leftPadding, rightPadding):
        super(ArtefactBlockConstructor, self).__init__(module, configuration, leftPadding, rightPadding)

    def construct(self):
        block = []
        paddingTop = 8
        block.append(formatters.packImageTextBlockData(title=text_styles.alert(TOOLTIPS.MODULEFITS_NOT_REMOVABLE_BODY), img=RES_ICONS.MAPS_ICONS_TOOLTIP_COMPLEX_EQUIPMENT, imgPadding=formatters.packPadding(left=2, top=3), txtOffset=20))
        block.append(formatters.packTextBlockData(text=text_styles.main(TOOLTIPS.MODULEFITS_NOT_REMOVABLE_NOTE), padding=formatters.packPadding(top=paddingTop)))
        block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.MODULEFITS_NOT_REMOVABLE_DISMANTLING_PRICE), value=text_styles.gold(g_itemsCache.items.shop.paidRemovalCost), icon=ICON_TEXT_FRAMES.GOLD, valueWidth=60, padding=formatters.packPadding(left=43, top=paddingTop)))
        return block


class EffectsBlockConstructor(ModuleTooltipBlockConstructor):

    def __init__(self, module, configuration, leftPadding, rightPadding):
        super(EffectsBlockConstructor, self).__init__(module, configuration, leftPadding, rightPadding)

    def construct(self):
        module = self.module
        block = []

        def checkLocalization(key):
            localization = _ms('#artefacts:%s' % key)
            return (key != localization, localization)

        onUse = checkLocalization('%s/onUse' % module.descriptor['name'])
        always = checkLocalization('%s/always' % module.descriptor['name'])
        restriction = checkLocalization('%s/restriction' % module.descriptor['name'])
        if module.itemTypeID == ITEM_TYPES.optionalDevice:
            block.append(formatters.packTitleDescBlock(title='', desc=text_styles.bonusAppliedText(module.shortDescription), padding=formatters.packPadding(top=-8)))
        else:
            topPadding = 0
            if always[0] and len(always[1]) > 0:
                block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(TOOLTIPS.EQUIPMENT_ALWAYS), desc=text_styles.bonusAppliedText(always[1])))
                topPadding = 5
            if onUse[0] and len(onUse[1]) > 0:
                block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(TOOLTIPS.EQUIPMENT_ONUSE), desc=text_styles.main(onUse[1]), padding=formatters.packPadding(top=topPadding)))
                topPadding = 5
            if restriction[0] and len(restriction[1]) > 0:
                block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(TOOLTIPS.EQUIPMENT_RESTRICTION), desc=text_styles.main(restriction[1]), padding=formatters.packPadding(top=topPadding)))
        return block


class StatusBlockConstructor(ModuleTooltipBlockConstructor):

    def __init__(self, module, configuration, leftPadding, rightPadding):
        super(StatusBlockConstructor, self).__init__(module, configuration, leftPadding, rightPadding)

    def construct(self):
        if self.configuration.isResearchPage:
            return self._getResearchPageStatus()
        else:
            return self._getStatus()

    def _getStatus(self):
        block = []
        module = self.module
        configuration = self.configuration
        vehicle = configuration.vehicle
        slotIdx = configuration.slotIdx
        eqs = configuration.eqs
        checkBuying = configuration.checkBuying
        isEqOrDev = module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS
        isFit = True
        reason = ''
        titleFormatter = text_styles.middleTitle
        cachedEqs = [None, None, None]
        currentVehicleEqs = [None, None, None]
        if vehicle is not None and vehicle.isInInventory:
            if vehicle is not None and vehicle.isInInventory:
                currentVehicleEqs = list(vehicle.eqs)
                vehicle.eqs = [None, None, None]
                if eqs:
                    for i, e in enumerate(eqs):
                        if e is not None:
                            intCD = int(e)
                            eq = g_itemsCache.items.getItemByCD(intCD)
                            cachedEqs[i] = eq

                    vehicle.eqs = cachedEqs
            isFit, reason = module.mayInstall(vehicle, slotIdx)
            vehicle.eqs = currentVehicleEqs
        inventoryVehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
        totalInstalledVehicles = map(lambda x: x.shortUserName, module.getInstalledVehicles(inventoryVehicles))
        installedVehicles = totalInstalledVehicles[:self.MAX_INSTALLED_LIST_LEN]
        tooltipHeader = None
        tooltipText = None
        if not isFit:
            reason = reason.replace(' ', '_')
            tooltipHeader, tooltipText = getComplexStatus('#tooltips:moduleFits/%s' % reason)
            if reason == 'not_with_installed_equipment':
                if vehicle is not None:
                    vehicle.eqs = cachedEqs
                    conflictEqs = module.getConflictedEquipments(vehicle)
                    tooltipText %= {'eqs': ', '.join([ _ms(e.userName) for e in conflictEqs ])}
                    vehicle.eqs = currentVehicleEqs
            elif reason == 'already_installed' and isEqOrDev and len(installedVehicles):
                tooltipHeader, _ = getComplexStatus('#tooltips:deviceFits/already_installed' if module.itemTypeName == GUI_ITEM_TYPE.OPTIONALDEVICE else '#tooltips:moduleFits/already_installed')
                tooltipText = ', '.join(installedVehicles)
        elif len(installedVehicles):
            tooltipHeader, _ = getComplexStatus('#tooltips:deviceFits/already_installed' if module.itemTypeName == GUI_ITEM_TYPE.OPTIONALDEVICE else '#tooltips:moduleFits/already_installed')
            tooltipText = ', '.join(installedVehicles)
        if tooltipHeader is not None or tooltipText is not None:
            if len(totalInstalledVehicles) > self.MAX_INSTALLED_LIST_LEN:
                hiddenVehicleCount = len(totalInstalledVehicles) - self.MAX_INSTALLED_LIST_LEN
                hiddenTxt = '%s %s' % (text_styles.main(TOOLTIPS.SUITABLEVEHICLE_HIDDENVEHICLECOUNT), text_styles.stats(hiddenVehicleCount))
                tooltipText = '%s\n%s' % (tooltipText, hiddenTxt)
            block.append(self._packStatusBlock(tooltipHeader, tooltipText, titleFormatter))
        if checkBuying:
            isFit, reason = module.mayPurchase(g_itemsCache.items.stats.money)
            if not isFit:
                reason = reason.replace(' ', '_')
                if reason in ('gold_error', 'credits_error'):
                    titleFormatter = text_styles.critical
                tooltipHeader, tooltipText = getComplexStatus('#tooltips:moduleFits/%s' % reason)
                if tooltipHeader is not None or tooltipText is not None:
                    if len(block):
                        padding = formatters.packPadding(bottom=15)
                        block.insert(0, self._packStatusBlock(tooltipHeader, tooltipText, titleFormatter, padding))
                    else:
                        block.append(self._packStatusBlock(tooltipHeader, tooltipText, titleFormatter))
        return block

    def _packStatusBlock(self, tooltipHeader, tooltipText, titleFormatter, padding=None):
        return formatters.packTitleDescBlock(title=titleFormatter(tooltipHeader), desc=text_styles.standard(tooltipText), padding=padding)

    def _getResearchPageStatus(self):
        module = self.module
        configuration = self.configuration
        vehicle = configuration.vehicle
        node = configuration.node
        block = []

        def status(title=None, desc=None):
            if title is not None or desc is not None:
                block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(title) if title is not None else '', desc=text_styles.main(desc) if desc is not None else ''))
            return block

        header, text = (None, None)
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
            return status(header, text)
        elif not vehicle.isInInventory:
            header, text = getComplexStatus(statusTemplate % 'needToBuyTank')
            text %= {'vehiclename': vehicle.userName}
            return status(header, text)
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
                    return status(header, text)
            return self._getStatus()
