# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/module.py
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_ECONOMY_CODE
from gui.shared.gui_items.vehicle_equipment import RegularEquipmentConsumables
from gui.shared.gui_items.gui_item_economics import isItemBuyPriceAvailable
from gui.shared.items_parameters import params_helper, formatters as params_formatters, bonus_helper
from gui.shared.items_parameters.params_helper import SimplifiedBarVO
from gui.shared.money import MONEY_UNDEFINED, Currency
from gui.shared.tooltips import formatters
from gui.shared.tooltips import getComplexStatus, getUnlockPrice, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from gui.shared.utils import GUN_CLIP, SHELLS_COUNT_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, AIMING_TIME_PROP_NAME, RELOAD_TIME_PROP_NAME
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from items import VEHICLE_COMPONENT_TYPE_NAMES, ITEM_TYPES
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared.gui_items import IGuiItemsFactory
_TOOLTIP_MIN_WIDTH = 420
_TOOLTIP_MAX_WIDTH = 480
_AUTOCANNON_SHOT_DISTANCE = 400

class ModuleBlockTooltipData(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, context):
        super(ModuleBlockTooltipData, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        return

    def _getHighLightType(self):
        return SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS if self.item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and self.item.isDeluxe() else SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT

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
        effectsItems = []
        replaceItems = []
        if module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
            if module.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
                cooldownSeconds = module.descriptor.cooldownSeconds
                if cooldownSeconds > 0:
                    items.append(formatters.packTextParameterBlockData(name=params_formatters.formatModuleParamName('cooldownSeconds'), value=text_styles.stats(int(cooldownSeconds)), valueWidth=valueWidth, padding=formatters.packPadding(left=leftPadding)))
            effectsBlock = EffectsBlockConstructor(module, statusConfig, leftPadding, rightPadding).construct()
            if effectsBlock:
                effectsItems.append(formatters.packBuildUpBlockData(effectsBlock))
        if statsConfig.vehicle is not None and not module.isInstalled(statsConfig.vehicle):
            if module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
                comparator = params_helper.artifactComparator(statsConfig.vehicle, module, statsConfig.slotIdx, True)
            else:
                comparator = params_helper.itemOnVehicleComparator(statsConfig.vehicle, module)
            stockParams = params_helper.getParameters(self.itemsCache.items.getStockVehicle(statsConfig.vehicle.intCD))
            currentOptDev = None
            if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                if statsConfig.vehicle.descriptor.optionalDevices[statsConfig.slotIdx] is not None:
                    compactDescr = statsConfig.vehicle.descriptor.optionalDevices[statsConfig.slotIdx].compactDescr
                    currentOptDev = self.itemsFactory.createOptionalDevice(compactDescr)
            if currentOptDev is not None and not module.isSimilarDevice(currentOptDev) or currentOptDev is None and module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE or module.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
                simplifiedBlock = SimplifiedStatsBlockConstructor(module, paramsConfig, leftPadding, rightPadding, stockParams, comparator).construct()
                if simplifiedBlock:
                    effectsItems.append(formatters.packBuildUpBlockData(simplifiedBlock, gap=-4, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=-3, bottom=1)))
            if statsConfig.vehicle.optDevices[statsConfig.slotIdx]:
                if module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
                    if currentOptDev is not None and module.isSimilarDevice(currentOptDev):
                        comparator = params_helper.artifactComparator(statsConfig.vehicle, module, statsConfig.slotIdx, False)
                    else:
                        comparator = params_helper.artifactRemovedComparator(statsConfig.vehicle, self.item, statsConfig.slotIdx)
                simplifiedBlock = SimplifiedStatsBlockConstructor(module, paramsConfig, leftPadding, rightPadding, stockParams, comparator).construct()
                if simplifiedBlock:
                    replaceBlock = ModuleReplaceBlockConstructor(module, statsConfig, valueWidth, leftPadding).construct()
                    if replaceBlock:
                        replaceItems.append(formatters.packBuildUpBlockData(replaceBlock))
                    replaceItems.append(formatters.packBuildUpBlockData(simplifiedBlock, gap=-4, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=2, bottom=1)))
        if effectsItems:
            items.append(formatters.packBuildUpBlockData(effectsItems, padding=blockPadding, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, stretchBg=True))
        if replaceItems:
            items.append(formatters.packBuildUpBlockData(replaceItems, gap=-4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=blockPadding, stretchBg=True))
        priceBlock, invalidWidth = PriceBlockConstructor(module, statsConfig, valueWidth, leftPadding, rightPadding).construct()
        if priceBlock:
            self._setWidth(_TOOLTIP_MAX_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
            items.append(formatters.packBuildUpBlockData(priceBlock, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=-1, bottom=-3), gap=textGap))
        statsModules = GUI_ITEM_TYPE.VEHICLE_MODULES + (GUI_ITEM_TYPE.OPTIONALDEVICE,)
        if module.itemTypeID in statsModules:
            commonStatsBlock = CommonStatsBlockConstructor(module, paramsConfig, statsConfig.slotIdx, valueWidth, leftPadding, rightPadding, params_formatters.BASE_SCHEME).construct()
            if commonStatsBlock:
                items.append(formatters.packBuildUpBlockData(commonStatsBlock, padding=blockPadding, gap=textGap))
        statusBlock = StatusBlockConstructor(module, statusConfig, leftPadding, rightPadding).construct()
        if statusBlock:
            items.append(formatters.packBuildUpBlockData(statusBlock, padding=blockPadding))
        if bonus_helper.isSituationalBonus(module.name):
            items.append(formatters.packImageTextBlockData(title='', desc=text_styles.standard(TOOLTIPS.VEHICLEPARAMS_BONUS_SITUATIONAL), img=RES_ICONS.MAPS_ICONS_TOOLTIP_ASTERISK_OPTIONAL, imgPadding=formatters.packPadding(left=4, top=3), txtGap=-4, txtOffset=20, padding=formatters.packPadding(left=59, right=20)))
        if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and statsConfig.vehicle is not None and not module.isInstalled(statsConfig.vehicle) and module.hasSimilarDevicesInstalled(statsConfig.vehicle):
            items.append(formatters.packBuildUpBlockData(SimilarOptionalDeviceBlockConstructor(module, statusConfig, leftPadding, rightPadding).construct(), gap=-4, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=2), stretchBg=False))
        return items


class VehCompareModuleBlockTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(VehCompareModuleBlockTooltipData, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self._setContentMargin(top=0, left=0, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(VehCompareModuleBlockTooltipData, self)._packBlocks()
        module = self.context.buildItem(*args, **kwargs)
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
            if effectsBlock:
                items.append(formatters.packBuildUpBlockData(effectsBlock, padding=blockPadding, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        priceBlock, invalidWidth = PriceBlockConstructor(module, statsConfig, valueWidth, leftPadding, rightPadding).construct()
        if priceBlock:
            self._setWidth(_TOOLTIP_MAX_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
            items.append(formatters.packBuildUpBlockData(priceBlock, padding=blockPadding, gap=textGap))
        statsModules = GUI_ITEM_TYPE.VEHICLE_MODULES + (GUI_ITEM_TYPE.OPTIONALDEVICE,)
        if module.itemTypeID in statsModules:
            commonStatsBlock = CommonStatsBlockConstructor(module, paramsConfig, statsConfig.slotIdx, valueWidth, leftPadding, rightPadding, False).construct()
            if commonStatsBlock:
                items.append(formatters.packBuildUpBlockData(commonStatsBlock, padding=blockPadding, gap=textGap))
        return items


class ModuleTooltipBlockConstructor(object):
    MAX_INSTALLED_LIST_LEN = 10
    CLIP_GUN_MODULE_PARAM = 'vehicleClipGun'
    WEIGHT_MODULE_PARAM = 'weight'
    MODULE_PARAMS = {GUI_ITEM_TYPE.CHASSIS: ('maxLoad', 'rotationSpeed', 'weight'),
     GUI_ITEM_TYPE.TURRET: ('armor', 'rotationSpeed', 'circularVisionRadius', 'weight'),
     GUI_ITEM_TYPE.GUN: (RELOAD_TIME_PROP_NAME,
                         'avgPiercingPower',
                         'avgDamageList',
                         'avgDamagePerMinute',
                         'stunMinDurationList',
                         'stunMaxDurationList',
                         'dispertionRadius',
                         AIMING_TIME_PROP_NAME,
                         'maxShotDistance',
                         'weight'),
     GUI_ITEM_TYPE.ENGINE: ('enginePower', 'fireStartingChance', 'weight'),
     GUI_ITEM_TYPE.RADIO: ('radioDistance', 'weight'),
     GUI_ITEM_TYPE.OPTIONALDEVICE: (),
     CLIP_GUN_MODULE_PARAM: (SHELLS_COUNT_PROP_NAME,
                             SHELL_RELOADING_TIME_PROP_NAME,
                             RELOAD_MAGAZINE_TIME_PROP_NAME,
                             'avgPiercingPower',
                             'avgDamageList',
                             'avgDamagePerMinute',
                             'dispertionRadius',
                             'maxShotDistance',
                             AIMING_TIME_PROP_NAME,
                             'weight')}
    EXTRA_MODULE_PARAMS = {CLIP_GUN_MODULE_PARAM: (SHELLS_COUNT_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME)}
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, module, configuration, leftPadding=20, rightPadding=20):
        self.module = module
        self.configuration = configuration
        self.leftPadding = leftPadding
        self.rightPadding = rightPadding

    def construct(self):
        return None


class HeaderBlockConstructor(ModuleTooltipBlockConstructor):

    def construct(self):
        module = self.module
        block = []
        title = module.userName
        imgPaddingLeft = 27
        imgPaddingTop = 0
        txtOffset = 130 - self.leftPadding
        desc = ''
        if module.itemTypeName in VEHICLE_COMPONENT_TYPE_NAMES:
            desc = text_styles.concatStylesWithSpace(text_styles.stats(_ms(TOOLTIPS.level(str(module.level)))), text_styles.standard(_ms(TOOLTIPS.VEHICLE_LEVEL)))
            imgPaddingLeft = 22
        elif module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
            imgPaddingLeft = 7
            imgPaddingTop = 5
            txtOffset = 90 - self.leftPadding
            moduleParams = params_helper.getParameters(module)
            weightUnits = text_styles.standard(TOOLTIPS.PARAMETER_WEIGHTUNITS)
            paramName = ModuleTooltipBlockConstructor.WEIGHT_MODULE_PARAM
            paramValue = params_formatters.formatParameter(paramName, moduleParams[paramName]) if paramName in moduleParams else None
            if paramValue is not None:
                desc = text_styles.main(TOOLTIPS.PARAMETER_WEIGHT) + text_styles.credits(paramValue) + weightUnits
        else:
            desc = text_styles.standard(desc)
        overlayPath, overlayPadding, blockPadding = self.__getOverlayData()
        block.append(formatters.packItemTitleDescBlockData(title=text_styles.highTitle(title), desc=desc, img=module.icon, imgPadding=formatters.packPadding(left=imgPaddingLeft, top=imgPaddingTop), txtGap=-3, txtOffset=txtOffset, padding=blockPadding, overlayPath=overlayPath, overlayPadding=overlayPadding))
        if module.itemTypeID == GUI_ITEM_TYPE.GUN:
            vehicle = self.configuration.vehicle
            vDescr = vehicle.descriptor if vehicle is not None else None
            if module.isClipGun(vDescr):
                block.append(formatters.packImageTextBlockData(title=text_styles.standard(MENU.MODULEINFO_CLIPGUNLABEL), desc='', img=RES_ICONS.MAPS_ICONS_MODULES_MAGAZINEGUNICON, imgPadding=formatters.packPadding(top=3), padding=formatters.packPadding(left=108, top=9)))
        elif module.itemTypeID == GUI_ITEM_TYPE.CHASSIS:
            if module.isHydraulicChassis():
                block.append(formatters.packImageTextBlockData(title=text_styles.standard(MENU.MODULEINFO_HYDRAULICCHASSISLABEL), desc='', img=RES_ICONS.MAPS_ICONS_MODULES_HYDRAULICCHASSISICON, imgPadding=formatters.packPadding(top=3), padding=formatters.packPadding(left=108, top=9)))
        return block

    def __getOverlayData(self):
        blockPadding = formatters.packPadding(top=-6)
        if self.module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and self.module.isDeluxe():
            overlayPath = RES_ICONS.MAPS_ICONS_ARTEFACT_EQUIPMENTPLUS_OVERLAY
            padding = formatters.packPadding(top=SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS_PADDING_TOP, left=SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS_PADDING_LEFT)
            blockPadding['bottom'] = -12
        else:
            overlayPath = padding = None
        return (overlayPath, padding, blockPadding)


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
            isNextToUnlock = checkState(NODE_STATE_FLAGS.NEXT_2_UNLOCK)
            isInstalled = checkState(NODE_STATE_FLAGS.INSTALLED)
            isInInventory = checkState(NODE_STATE_FLAGS.IN_INVENTORY)
            isUnlocked = checkState(NODE_STATE_FLAGS.UNLOCKED)
            isAutoUnlock = checkState(NODE_STATE_FLAGS.AUTO_UNLOCKED)
            items = self.itemsCache.items
            money = items.stats.money
            itemPrice = MONEY_UNDEFINED
            if module is not None:
                itemPrice = module.buyPrices.itemPrice.price
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
            notEnoughMoney = False
            hasAction = False
            if buyPrice and not isAutoUnlock:
                shop = self.itemsCache.items.shop
                money = self.itemsCache.items.stats.money
                rootInInv = vehicle is not None and vehicle.isInInventory
                if researchNode:
                    showNeeded = rootInInv and not isMoneyEnough and (isNextToUnlock or isUnlocked) and not (isInstalled or isInInventory)
                else:
                    isModuleUnlocked = module.isUnlocked
                    isModuleInInventory = module.isInInventory
                    showNeeded = not isModuleInInventory and isModuleUnlocked
                showDelimiter = False
                leftPadding = 92
                for itemPrice in module.buyPrices.iteritems(directOrder=False):
                    if not isItemBuyPriceAvailable(module, itemPrice, shop):
                        continue
                    currency = itemPrice.getCurrency()
                    value = itemPrice.price.getSignValue(currency)
                    defValue = itemPrice.defPrice.getSignValue(currency)
                    actionPercent = itemPrice.getActionPrc()
                    if isEqOrDev or showNeeded:
                        needValue = value - money.getSignValue(currency)
                        if needValue > 0:
                            notEnoughMoney = True
                        else:
                            needValue = None
                    else:
                        needValue = None
                    if currency == Currency.GOLD and actionPercent > 0:
                        leftActionPadding = 101 + self.leftPadding
                    else:
                        leftActionPadding = 81 + self.leftPadding
                    if actionPercent > 0:
                        hasAction = True
                    if showDelimiter:
                        block.append(formatters.packTextBlockData(text=text_styles.standard(TOOLTIPS.VEHICLE_TEXTDELIMITER_OR), padding=formatters.packPadding(left=leftActionPadding)))
                    block.append(makePriceBlock(value, CURRENCY_SETTINGS.getBuySetting(currency), needValue, defValue if defValue > 0 else None, actionPercent, valueWidth=self._valueWidth, leftPadding=leftPadding))
                    showDelimiter = True

            if sellPrice and module.sellPrices:
                block.append(makePriceBlock(module.sellPrices.itemPrice.price.credits, CURRENCY_SETTINGS.SELL_PRICE, oldPrice=module.sellPrices.itemPrice.defPrice.credits, percent=module.sellPrices.itemPrice.getActionPrc(), valueWidth=self._valueWidth, leftPadding=leftPadding))
            if inventoryCount:
                count = module.inventoryCount
                if count > 0:
                    block.append(self._getInventoryBlock(count))
            if vehiclesCount:
                inventoryVehicles = items.getVehicles(REQ_CRITERIA.INVENTORY)
                count = len(module.getInstalledVehicles(inventoryVehicles.itervalues()))
                if count > 0:
                    block.append(formatters.packTextParameterBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_VEHICLECOUNT), value=text_styles.stats(count), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5)))
            isOptionalDevice = module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE
            if isOptionalDevice and not module.isRemovable and not self.configuration.isAwardWindow:
                removalPrice = module.getRemovalPrice(self.itemsCache.items)
                removalPriceCurrency = removalPrice.getCurrency()
                currencyTextFormatter = getattr(text_styles, removalPriceCurrency, text_styles.gold)
                block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.MODULEFITS_NOT_REMOVABLE_DISMANTLING_PRICE), value=currencyTextFormatter(removalPrice.price.get(removalPriceCurrency)), icon=removalPriceCurrency, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5)))
            hasAction |= module.sellPrices.itemPrice.isActionPrice()
            return (block, notEnoughMoney or hasAction)

    def _getInventoryBlock(self, count):
        return formatters.packTextParameterBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_INVENTORYCOUNT), value=text_styles.stats(count), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5))


class CommonStatsBlockConstructor(ModuleTooltipBlockConstructor):

    def __init__(self, module, configuration, slotIdx, valueWidth, leftPadding, rightPadding, colorScheme=None):
        super(CommonStatsBlockConstructor, self).__init__(module, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        self._slotIdx = slotIdx
        self.__colorScheme = colorScheme or params_formatters.COLORLESS_SCHEME

    def construct(self):
        module = self.module
        vehicle = self.configuration.vehicle
        params = self.configuration.params
        block = []
        vDescr = vehicle.descriptor if vehicle is not None else None
        moduleParams = params_helper.getParameters(module, vDescr)
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
                    currModule = self.itemsCache.items.getItemByCD(currModuleDescr.compactDescr)
                comparator = params_helper.itemsComparator(module, currModule, vehicle.descriptor)
                for paramName in paramsList:
                    if paramName in moduleParams:
                        paramInfo = comparator.getExtendedData(paramName)
                        fmtValue = params_formatters.colorizedFormatParameter(paramInfo, self.__colorScheme)
                        if fmtValue is not None:
                            block.append(formatters.packTextParameterBlockData(name=params_formatters.formatModuleParamName(paramName), value=fmtValue, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5)))

            else:
                formattedModuleParameters = params_formatters.getFormattedParamsList(module.descriptor, moduleParams)
                for paramName, paramValue in formattedModuleParameters:
                    if paramName in paramsList and paramValue is not None:
                        block.append(formatters.packTextParameterBlockData(name=params_formatters.formatModuleParamName(paramName), value=paramValue, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5)))

        if block:
            block.insert(0, formatters.packTextBlockData(text_styles.middleTitle(_ms(TOOLTIPS.TANKCARUSEL_MAINPROPERTY)), padding=formatters.packPadding(bottom=8)))
        return block


class ModuleReplaceBlockConstructor(ModuleTooltipBlockConstructor):

    def construct(self):
        block = []
        vehicle = self.configuration.vehicle
        optionalDevice = vehicle.optDevices[self.configuration.slotIdx]
        if optionalDevice is not None:
            replaceModuleText = text_styles.main(TOOLTIPS.MODULEFITS_REPLACE)
            block.append(formatters.packImageTextBlockData(title=replaceModuleText.format(moduleName=optionalDevice.userName)))
        return block


class SimplifiedStatsBlockConstructor(ModuleTooltipBlockConstructor):

    def __init__(self, module, configuration, leftPadding, rightPadding, stockParams, comparator):
        self.__stockParams = stockParams
        self.__comparator = comparator
        self.__isSituational = bonus_helper.isSituationalBonus(module.name)
        super(SimplifiedStatsBlockConstructor, self).__init__(module, configuration, leftPadding, rightPadding)

    def construct(self):
        block = []
        if self.configuration.params:
            for parameter in params_formatters.getRelativeDiffParams(self.__comparator):
                delta = parameter.state[1]
                value = parameter.value
                if delta > 0:
                    value -= delta
                block.append(formatters.packStatusDeltaBlockData(title=text_styles.middleTitle(MENU.tank_params(parameter.name)), valueStr=params_formatters.simlifiedDeltaParameter(parameter, self.__isSituational), statusBarData=SimplifiedBarVO(value=value, delta=delta, markerValue=self.__stockParams[parameter.name], isOptional=self.__isSituational), padding=formatters.packPadding(left=105, top=8)))

        return block


class SimilarOptionalDeviceBlockConstructor(ModuleTooltipBlockConstructor):
    """
    Notification if the vehicle has an optional device with the same effect
    """

    def construct(self):
        block = list()
        paddingTop = 8
        block.append(formatters.packImageTextBlockData(title=text_styles.error(TOOLTIPS.MODULEFITS_DUPLICATED_HEADER), img=RES_ICONS.MAPS_ICONS_TOOLTIP_DUPLICATED_OPTIONAL, imgPadding=formatters.packPadding(left=2, top=3), txtOffset=20))
        block.append(formatters.packTextBlockData(text=text_styles.main(TOOLTIPS.MODULEFITS_DUPLICATED_NOTE), padding=formatters.packPadding(top=paddingTop)))
        return block


class EffectsBlockConstructor(ModuleTooltipBlockConstructor):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def construct(self):
        module = self.module
        block = []

        def checkLocalization(key):
            localization = _ms('#artefacts:%s' % key)
            return (key != localization, localization)

        if self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
            isRemovingStun = module.isRemovingStun
        else:
            isRemovingStun = False
        onUseStr = '%s/removingStun/onUse' if isRemovingStun else '%s/onUse'
        onUse = checkLocalization(onUseStr % module.descriptor.name)
        always = checkLocalization('%s/always' % module.descriptor.name)
        restriction = checkLocalization('%s/restriction' % module.descriptor.name)
        if bonus_helper.isSituationalBonus(module.name):
            effectDesc = text_styles.bonusPreviewText(_ms(module.shortDescription))
            icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_TOOLTIP_ASTERISK_OPTIONAL, 16, 16, 0, 4)
            desc = params_formatters.packSituationalIcon(effectDesc, icon)
        else:
            desc = text_styles.bonusAppliedText(_ms(module.shortDescription))
        if module.itemTypeID == ITEM_TYPES.optionalDevice:
            block.append(formatters.packTitleDescBlock(title='', desc=desc, padding=formatters.packPadding(top=-8)))
        else:
            topPadding = 0
            if always[0] and always[1]:
                block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(TOOLTIPS.EQUIPMENT_ALWAYS), desc=text_styles.bonusAppliedText(always[1])))
                topPadding = 5
            if onUse[0] and onUse[1]:
                block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(TOOLTIPS.EQUIPMENT_ONUSE), desc=text_styles.main(onUse[1]), padding=formatters.packPadding(top=topPadding)))
                topPadding = 5
            if restriction[0] and restriction[1]:
                block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(TOOLTIPS.EQUIPMENT_RESTRICTION), desc=text_styles.main(restriction[1]), padding=formatters.packPadding(top=topPadding)))
        return block


class StatusBlockConstructor(ModuleTooltipBlockConstructor):

    def construct(self):
        if self.configuration.isResearchPage:
            return self._getResearchPageStatus()
        return [] if self.configuration.isAwardWindow else self._getStatus()

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
        cachedEqs = RegularEquipmentConsumables()
        currentVehicleEqs = RegularEquipmentConsumables()
        if vehicle is not None and vehicle.isInInventory:
            if vehicle is not None and vehicle.isInInventory:
                currentVehicleEqs = vehicle.equipment.regularConsumables
                vehicle.equipment.setRegularConsumables(RegularEquipmentConsumables())
                if eqs:
                    for i, e in enumerate(eqs):
                        if e is not None:
                            intCD = int(e)
                            eq = self.itemsCache.items.getItemByCD(intCD)
                            cachedEqs[i] = eq

                    vehicle.equipment.setRegularConsumables(cachedEqs)
            isFit, reason = module.mayInstall(vehicle, slotIdx)
            vehicle.equipment.setRegularConsumables(currentVehicleEqs)
        inventoryVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
        totalInstalledVehicles = map(lambda x: x.shortUserName, module.getInstalledVehicles(inventoryVehicles))
        installedVehicles = totalInstalledVehicles[:self.MAX_INSTALLED_LIST_LEN]
        tooltipHeader = None
        tooltipText = None
        if not isFit:
            reason = reason.replace(' ', '_')
            tooltipHeader, tooltipText = getComplexStatus('#tooltips:moduleFits/%s' % reason)
            if reason == 'not_with_installed_equipment':
                if vehicle is not None:
                    vehicle.equipment.setRegularConsumables(cachedEqs)
                    conflictEqs = module.getConflictedEquipments(vehicle)
                    tooltipText %= {'eqs': ', '.join([ _ms(e.userName) for e in conflictEqs ])}
                    vehicle.equipment.setRegularConsumables(currentVehicleEqs)
            elif reason == 'already_installed' and isEqOrDev and installedVehicles:
                tooltipHeader, _ = getComplexStatus('#tooltips:deviceFits/already_installed' if module.itemTypeName == GUI_ITEM_TYPE.OPTIONALDEVICE else '#tooltips:moduleFits/already_installed')
                tooltipText = ', '.join(installedVehicles)
        elif installedVehicles:
            tooltipHeader, _ = getComplexStatus('#tooltips:deviceFits/already_installed' if module.itemTypeName == GUI_ITEM_TYPE.OPTIONALDEVICE else '#tooltips:moduleFits/already_installed')
            tooltipText = ', '.join(installedVehicles)
        if tooltipHeader is not None or tooltipText is not None:
            if len(totalInstalledVehicles) > self.MAX_INSTALLED_LIST_LEN:
                hiddenVehicleCount = len(totalInstalledVehicles) - self.MAX_INSTALLED_LIST_LEN
                hiddenTxt = '%s %s' % (text_styles.main(TOOLTIPS.SUITABLEVEHICLE_HIDDENVEHICLECOUNT), text_styles.stats(hiddenVehicleCount))
                tooltipText = '%s\n%s' % (tooltipText, hiddenTxt)
            block.append(self._packStatusBlock(tooltipHeader, tooltipText, titleFormatter))
        if checkBuying:
            isFit, reason = module.mayPurchase(self.itemsCache.items.stats.money)
            if not isFit:
                reason = reason.replace(' ', '_')
                if GUI_ITEM_ECONOMY_CODE.isMoneyError(reason):
                    titleFormatter = text_styles.critical
                tooltipHeader, tooltipText = getComplexStatus('#tooltips:moduleFits/%s' % reason)
                if tooltipHeader is not None or tooltipText is not None:
                    if block:
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
        if not nodeState & NODE_STATE_FLAGS.UNLOCKED:
            if not vehicle.isUnlocked:
                header, text = getComplexStatus(statusTemplate % 'rootVehicleIsLocked')
            elif not nodeState & NODE_STATE_FLAGS.NEXT_2_UNLOCK:
                header, text = getComplexStatus(statusTemplate % 'parentModuleIsLocked')
            elif need > 0:
                header, text = getComplexStatus(statusTemplate % 'notEnoughXP')
                header = text_styles.critical(header)
            return status(header, text)
        elif not vehicle.isInInventory:
            header, text = getComplexStatus(statusTemplate % 'needToBuyTank')
            text %= {'vehiclename': vehicle.userName}
            return status(header, text)
        elif nodeState & NODE_STATE_FLAGS.INSTALLED:
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
