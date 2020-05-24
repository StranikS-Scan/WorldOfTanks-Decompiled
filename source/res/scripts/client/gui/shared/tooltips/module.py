# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/module.py
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.impl import backport
from gui.impl.backport import backport_r
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_ECONOMY_CODE
from gui.shared.gui_items.gui_item_economics import isItemBuyPriceAvailable
from gui.shared.gui_items.vehicle_equipment import RegularEquipmentConsumables
from gui.shared.items_parameters import params_helper, formatters as params_formatters, bonus_helper
from gui.shared.items_parameters.params_helper import SimplifiedBarVO
from gui.shared.money import MONEY_UNDEFINED, Currency
from gui.shared.tooltips import formatters
from gui.shared.tooltips import getComplexStatus, getUnlockPrice, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS, getFormattedPriceString, getFormattedDiscountPriceString
from gui.shared.utils import GUN_CLIP, SHELLS_COUNT_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, AIMING_TIME_PROP_NAME, RELOAD_TIME_PROP_NAME, GUN_AUTO_RELOAD, AUTO_RELOAD_PROP_NAME, RELOAD_TIME_SECS_PROP_NAME, DUAL_GUN_RATE_TIME, DUAL_GUN_CHARGE_TIME, GUN_DUAL_GUN
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from items import VEHICLE_COMPONENT_TYPE_NAMES, ITEM_TYPES
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
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
        return self.item.getHighlightType()

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
            perksController = statsConfig.vehicle.getPerksController()
            if perksController and not perksController.isInitialized():
                perksController.recalc()
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
            if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and statsConfig.vehicle.optDevices[statsConfig.slotIdx]:
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
        isComplexDevice = module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and not module.isRemovable
        if isComplexDevice and not statsConfig.isAwardWindow:
            complexDeviceBlock = ComplexDeviceBlockConstructor(module, statsConfig, leftPadding, rightPadding).construct
            if complexDeviceBlock:
                items.append(formatters.packBuildUpBlockData(complexDeviceBlock, padding=blockPadding))
        if bonus_helper.isSituationalBonus(module.name):
            items.append(formatters.packImageTextBlockData(title='', desc=text_styles.standard(backport.text(R.strings.tooltips.vehicleParams.bonus.situational())), img=backport.image(R.images.gui.maps.icons.tooltip.asterisk_optional()), imgPadding=formatters.packPadding(left=4, top=3), txtGap=-4, txtOffset=20, padding=formatters.packPadding(left=59, right=20)))
        if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and statsConfig.vehicle is not None and not module.isInstalled(statsConfig.vehicle) and module.hasSimilarDevicesInstalled(statsConfig.vehicle):
            items.append(formatters.packBuildUpBlockData(SimilarOptionalDeviceBlockConstructor(module, statusConfig, leftPadding, rightPadding).construct(), gap=-4, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=2), stretchBg=False))
        if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and module.isTrophy:
            state = ''
            headerStyle = None
            if module.isUpgradable:
                headerStyle = text_styles.statusAttention
                state = 'basic'
            elif module.isUpgraded:
                headerStyle = text_styles.statInfo
                state = 'upgraded'
            items.append(formatters.packItemTitleDescBlockData(title=headerStyle(backport.text(R.strings.tooltips.moduleFits.trophyEquipment.dyn(state).header())), desc=text_styles.main(backport.text(R.strings.tooltips.moduleFits.trophyEquipment.dyn(state).description())), padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=2)))
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
    AUTO_RELOAD_GUN_MODULE_PARAM = 'autoReloadGun'
    DUAL_GUN_MODULE_PARAM = 'dualGun'
    WEIGHT_MODULE_PARAM = 'weight'
    MODULE_PARAMS = {GUI_ITEM_TYPE.CHASSIS: ('maxLoad', 'rotationSpeed', 'maxSteeringLockAngle', 'weight'),
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
                             'weight'),
     AUTO_RELOAD_GUN_MODULE_PARAM: (AUTO_RELOAD_PROP_NAME,
                                    'avgPiercingPower',
                                    'avgDamageList',
                                    'avgDamagePerMinute',
                                    'stunMinDurationList',
                                    'stunMaxDurationList',
                                    'dispertionRadius',
                                    AIMING_TIME_PROP_NAME,
                                    'maxShotDistance',
                                    'weight'),
     DUAL_GUN_MODULE_PARAM: (RELOAD_TIME_SECS_PROP_NAME,
                             DUAL_GUN_RATE_TIME,
                             DUAL_GUN_CHARGE_TIME,
                             'avgPiercingPower',
                             'avgDamageList',
                             'dispertionRadius',
                             AIMING_TIME_PROP_NAME,
                             'weight')}
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
            desc = text_styles.concatStylesWithSpace(text_styles.stats(backport.text(R.strings.tooltips.level.num(str(module.level))())), text_styles.standard(backport.text(R.strings.tooltips.vehicle.level())))
            imgPaddingLeft = 22
        elif module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
            imgPaddingLeft = 7
            imgPaddingTop = 5
            txtOffset = 90 - self.leftPadding
            moduleParams = params_helper.getParameters(module)
            weightUnits = text_styles.standard(backport.text(R.strings.tooltips.parameter.weightUnits()))
            paramName = ModuleTooltipBlockConstructor.WEIGHT_MODULE_PARAM
            paramValue = params_formatters.formatParameter(paramName, moduleParams[paramName]) if paramName in moduleParams else None
            if paramValue is not None:
                desc = text_styles.main(backport.text(R.strings.tooltips.parameter.weight())) + text_styles.credits(paramValue) + weightUnits
            elif module.itemTypeID is GUI_ITEM_TYPE.EQUIPMENT and module.isBuiltIn:
                desc = text_styles.standard(backport.text(R.strings.tooltips.equipment.builtIn()))
        else:
            desc = text_styles.standard(desc)
        overlayPath, overlayPadding, blockPadding = self.__getOverlayData()
        block.append(formatters.packItemTitleDescBlockData(title=text_styles.highTitle(title), desc=desc, img=module.icon, imgPadding=formatters.packPadding(left=imgPaddingLeft, top=imgPaddingTop), txtGap=-3, txtOffset=txtOffset, padding=blockPadding, overlayPath=overlayPath, overlayPadding=overlayPadding))
        vehicle = self.configuration.vehicle
        vDescr = vehicle.descriptor if vehicle is not None else None
        if module.itemTypeID == GUI_ITEM_TYPE.GUN:
            extraInfo = module.getExtraIconInfo(vDescr)
            if extraInfo:
                if module.isClipGun(vDescr):
                    titleKey = backport.text(R.strings.menu.moduleInfo.clipGunLabel())
                elif module.isAutoReloadable(vDescr):
                    titleKey = backport.text(R.strings.menu.moduleInfo.autoReloadGunLabel())
                elif module.isDualGun(vDescr):
                    titleKey = backport.text(R.strings.menu.moduleInfo.dualGunLabel())
                block.append(formatters.packImageTextBlockData(title=text_styles.standard(titleKey), desc='', img=extraInfo, imgPadding=formatters.packPadding(top=3), padding=formatters.packPadding(left=108, top=9)))
        elif module.itemTypeID == GUI_ITEM_TYPE.CHASSIS:
            if module.isHydraulicChassis() and not vDescr.isDualgunVehicle:
                if module.isWheeledChassis():
                    title = text_styles.standard(backport.text(R.strings.menu.moduleInfo.hydraulicWheeledChassisLabel()))
                elif module.hasAutoSiege():
                    title = text_styles.standard(backport.text(R.strings.menu.moduleInfo.hydraulicAutoSiegeChassisLabel()))
                else:
                    title = text_styles.standard(backport.text(R.strings.menu.moduleInfo.hydraulicChassisLabel()))
                block.append(formatters.packImageTextBlockData(title=title, desc='', img=module.getExtraIconInfo(vDescr), imgPadding=formatters.packPadding(top=3), padding=formatters.packPadding(left=108, top=9)))
        return block

    def __getOverlayData(self):
        blockPadding = formatters.packPadding(top=-6)
        bottomBlockPadding = -12
        padding = formatters.packPadding(top=SLOT_HIGHLIGHT_TYPES.TOOLTIP_OVERLAY_PADDING_TOP, left=SLOT_HIGHLIGHT_TYPES.TOOLTIP_OVERLAY_PADDING_LEFT)
        blockPadding['bottom'] = bottomBlockPadding
        if self.module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and self.module.isDeluxe:
            overlayPath = backport.image(R.images.gui.maps.icons.quests.bonuses.small.equipmentPlus_overlay())
        elif self.module.itemTypeID is GUI_ITEM_TYPE.EQUIPMENT and self.module.isBuiltIn:
            overlayPath = backport.image(R.images.gui.maps.icons.quests.bonuses.small.builtInEquipment_overlay())
        elif self.module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and self.module.isTrophy:
            suffix = ''
            if self.module.isUpgradable:
                suffix = 'Basic'
            elif self.module.isUpgraded:
                suffix = 'Upgraded'
            overlayPath = backport.image(R.images.gui.maps.icons.quests.bonuses.small.dyn('equipmentTrophy{}_overlay'.format(suffix))())
        else:
            overlayPath = padding = None
            blockPadding['bottom'] = 0
        return (overlayPath, padding, blockPadding)


class PriceBlockConstructor(ModuleTooltipBlockConstructor):
    bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self, module, configuration, valueWidth, leftPadding, rightPadding):
        super(PriceBlockConstructor, self).__init__(module, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        self._inInventoryBlockData = {'icon': backport.image(R.images.gui.maps.icons.library.storage_icon()),
         'text': backport.text(R.strings.tooltips.vehicle.inventoryCount())}
        self._onVehicleBlockData = {'icon': backport.image(R.images.gui.maps.icons.customization.installed_on_tank_icon()),
         'text': backport.text(R.strings.tooltips.vehicle.vehicleCount())}

    def construct(self):
        block = []
        module = self.module
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
        elif self.module.itemTypeID is GUI_ITEM_TYPE.EQUIPMENT and self.module.isBuiltIn:
            return (None, False)
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
                _, cost, need, _, actionPercent = getUnlockPrice(module.intCD, parentCD)
                neededValue = None
                if not isUnlocked and isNextToUnlock and need > 0:
                    neededValue = need
                if cost > 0:
                    block.append(makePriceBlock(cost, CURRENCY_SETTINGS.UNLOCK_PRICE, neededValue, leftPadding=leftPadding, valueWidth=self._valueWidth))
            notEnoughMoney = False
            hasAction = False
            if buyPrice and not isAutoUnlock and not module.isHidden:
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
                for itemPrice in module.buyPrices.iteritems(directOrder=False):
                    if not isItemBuyPriceAvailable(module, itemPrice, shop):
                        continue
                    currency = itemPrice.getCurrency()
                    value = itemPrice.price.getSignValue(currency)
                    defValue = itemPrice.defPrice.getSignValue(currency)
                    actionPercent = itemPrice.getActionPrc() if not self.bootcamp.isInBootcamp() else 0
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
                        block.append(formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.tooltips.vehicle.textDelimiter.c_or())), padding=formatters.packPadding(left=leftActionPadding)))
                    block.append(makePriceBlock(value, CURRENCY_SETTINGS.getBuySetting(currency), needValue, defValue if defValue > 0 else None, actionPercent, valueWidth=self._valueWidth, leftPadding=leftPadding))
                    showDelimiter = True

            if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and module.isUpgradable:
                money = self.itemsCache.items.stats.money
                itemPrice = module.getUpgradePrice(self.itemsCache.items)
                currency = itemPrice.getCurrency()
                value = itemPrice.price.getSignValue(currency)
                defValue = itemPrice.defPrice.getSignValue(currency)
                if isEqOrDev:
                    needValue = value - money.getSignValue(currency)
                    if needValue > 0:
                        notEnoughMoney = True
                    else:
                        needValue = None
                else:
                    needValue = None
                block.append(makePriceBlock(value, CURRENCY_SETTINGS.getUpgradableSetting(currency), needValue, defValue if defValue > 0 else None, valueWidth=self._valueWidth, leftPadding=leftPadding))
            if sellPrice and module.sellPrices:
                block.append(makePriceBlock(module.sellPrices.itemPrice.price.credits, CURRENCY_SETTINGS.SELL_PRICE, oldPrice=module.sellPrices.itemPrice.defPrice.credits, percent=module.sellPrices.itemPrice.getActionPrc() if not self.bootcamp.isInBootcamp() else 0, valueWidth=self._valueWidth, leftPadding=leftPadding))
            if inventoryCount:
                count = module.inventoryCount
                if count > 0:
                    block.append(self._getInventoryBlock(count, self._inInventoryBlockData))
            if vehiclesCount:
                count = len(module.getInstalledVehicles(items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()))
                if count > 0:
                    block.append(self._getInventoryBlock(count, self._onVehicleBlockData))
            return (block, notEnoughMoney or hasAction)

    @staticmethod
    def _getInventoryBlock(count, blockData):
        return formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(blockData['text']), value=text_styles.stats(count), icon=blockData['icon'], padding=formatters.packPadding(left=105), titlePadding=formatters.packPadding(left=-2), iconPadding=formatters.packPadding(top=-2, left=-2))


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
            highlightPossible = False
            if reloadingType == GUN_CLIP:
                paramsKeyName = self.CLIP_GUN_MODULE_PARAM
            elif reloadingType == GUN_AUTO_RELOAD and vehicle is not None:
                serverSettings = dependency.instance(ISettingsCore).serverSettings
                highlightPossible = serverSettings.checkAutoReloadHighlights(increase=True)
                paramsKeyName = self.AUTO_RELOAD_GUN_MODULE_PARAM
            elif reloadingType == GUN_DUAL_GUN and vehicle is not None:
                serverSettings = dependency.instance(ISettingsCore).serverSettings
                highlightPossible = serverSettings.checkDualGunHighlights(increase=True)
                paramsKeyName = self.DUAL_GUN_MODULE_PARAM
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
                            block.append(formatters.packTextParameterBlockData(name=params_formatters.formatModuleParamName(paramName), value=fmtValue, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5), highlight=highlightPossible and paramName in (AUTO_RELOAD_PROP_NAME,
                             RELOAD_TIME_SECS_PROP_NAME,
                             DUAL_GUN_CHARGE_TIME,
                             DUAL_GUN_RATE_TIME)))

            else:
                formattedModuleParameters = params_formatters.getFormattedParamsList(module.descriptor, moduleParams)
                for paramName, paramValue in formattedModuleParameters:
                    if paramName in paramsList and paramValue is not None:
                        block.append(formatters.packTextParameterBlockData(name=params_formatters.formatModuleParamName(paramName), value=paramValue, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5)))

        if block:
            block.insert(0, formatters.packTextBlockData(text_styles.middleTitle(backport.text(R.strings.tooltips.tankCarusel.MainProperty())), padding=formatters.packPadding(bottom=8)))
        return block


class ModuleReplaceBlockConstructor(ModuleTooltipBlockConstructor):

    def construct(self):
        block = []
        vehicle = self.configuration.vehicle
        optionalDevice = vehicle.optDevices[self.configuration.slotIdx]
        if optionalDevice is not None:
            if self.module.isDeluxe != optionalDevice.isDeluxe or self.module.isTrophy != optionalDevice.isTrophy:
                msgKey = R.strings.tooltips.moduleFits.replace()
            else:
                msgKey = R.strings.tooltips.moduleFits.dismantling()
            replaceModuleText = text_styles.main(backport_r.text(msgKey, moduleName=optionalDevice.userName))
            block.append(formatters.packImageTextBlockData(title=replaceModuleText))
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
                block.append(formatters.packStatusDeltaBlockData(title=text_styles.middleTitle(backport.text(R.strings.menu.tank_params.dyn(parameter.name)())), valueStr=params_formatters.simplifiedDeltaParameter(parameter, self.__isSituational), statusBarData=SimplifiedBarVO(value=value, delta=delta, markerValue=self.__stockParams[parameter.name], isOptional=self.__isSituational), padding=formatters.packPadding(left=105, top=8)))

        return block


class SimilarOptionalDeviceBlockConstructor(ModuleTooltipBlockConstructor):

    def construct(self):
        block = list()
        paddingTop = 8
        block.append(formatters.packImageTextBlockData(title=text_styles.error(backport.text(R.strings.tooltips.moduleFits.duplicated.header())), img=backport.image(R.images.gui.maps.icons.tooltip.duplicated_optional()), imgPadding=formatters.packPadding(left=2, top=3), txtOffset=20))
        block.append(formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.moduleFits.duplicated.note())), padding=formatters.packPadding(top=paddingTop)))
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
            icon = icons.makeImageTag(backport.image(R.images.gui.maps.icons.tooltip.asterisk_optional()), 16, 16, 0, 4)
            desc = params_formatters.packSituationalIcon(effectDesc, icon)
        else:
            desc = text_styles.bonusAppliedText(_ms(module.shortDescription))
        if module.itemTypeID == ITEM_TYPES.optionalDevice:
            block.append(formatters.packTitleDescBlock(title='', desc=desc, padding=formatters.packPadding(top=-8)))
        else:
            topPadding = 0
            if always[0] and always[1]:
                block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.equipment.always())), desc=text_styles.bonusAppliedText(always[1])))
                topPadding = 5
            if onUse[0] and onUse[1]:
                block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.equipment.onUse())), desc=text_styles.main(onUse[1]), padding=formatters.packPadding(top=topPadding)))
                topPadding = 5
            if restriction[0] and restriction[1]:
                block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.equipment.restriction())), desc=text_styles.main(restriction[1]), padding=formatters.packPadding(top=topPadding)))
        return block


class StatusBlockConstructor(ModuleTooltipBlockConstructor):

    def construct(self):
        if self.configuration.isResearchPage:
            return self._getResearchPageStatus()
        if self.configuration.isAwardWindow:
            return []
        return [] if self.module.itemTypeID is GUI_ITEM_TYPE.EQUIPMENT and self.module.isBuiltIn else self._getStatus()

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
        showAllInstalled = True
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
        totalInstalledVehicles = [ x.shortUserName for x in module.getInstalledVehicles(inventoryVehicles) ]
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
            elif reason == 'too_heavy':
                titleFormatter = text_styles.error
                showAllInstalled = False
        elif installedVehicles:
            tooltipHeader, _ = getComplexStatus('#tooltips:deviceFits/already_installed' if module.itemTypeName == GUI_ITEM_TYPE.OPTIONALDEVICE else '#tooltips:moduleFits/already_installed')
            tooltipText = ', '.join(installedVehicles)
        if tooltipHeader is not None or tooltipText is not None:
            if showAllInstalled and len(totalInstalledVehicles) > self.MAX_INSTALLED_LIST_LEN:
                hiddenVehicleCount = len(totalInstalledVehicles) - self.MAX_INSTALLED_LIST_LEN
                hiddenTxt = '%s %s' % (text_styles.main(backport.text(R.strings.tooltips.suitableVehicle.hiddenVehicleCount())), text_styles.stats(hiddenVehicleCount))
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
        _, _, need, _, _ = getUnlockPrice(module.intCD, parentCD, vehicle.level)
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


class ComplexDeviceBlockConstructor(ModuleTooltipBlockConstructor):
    bootcamp = dependency.descriptor(IBootcampController)

    @property
    def construct(self):
        image = formatters.packImageBlockData(backport.image(R.images.gui.maps.icons.tooltip.complex_equipment()), BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(left=3, top=3))
        message = formatters.packTextBlockData(self._getMessage(), useHtml=True, padding=formatters.packPadding(left=5, right=5))
        block = formatters.packBuildUpBlockData(blocks=[image, message], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, stretchLast=True)
        return [block]

    def _getMessage(self):
        priceText, discountText = self._getPriceText()
        dkCount = text_styles.demountKitText('1')
        dkIcon = icons.demountKit()
        dkText = text_styles.concatStylesWithSpace(dkCount, dkIcon)
        descr = R.strings.demount_kit.equipmentInstall.demountDescription
        if self.module.isDeluxe:
            dynAccId = descr.bonds()
        elif self.module.isTrophy:
            dynAccId = descr.trophy()
        else:
            dynAccId = descr.common()
        text = backport.text(dynAccId, count=priceText, countDK=dkText)
        if discountText:
            text += '\n' + discountText
        return text_styles.standard(text)

    def _getPriceText(self):
        module = self.module
        money = self.itemsCache.items.stats.money
        removalPrice = module.getRemovalPrice(self.itemsCache.items)
        removalPriceCurrency = removalPrice.getCurrency()
        value = removalPrice.price.getSignValue(removalPriceCurrency)
        needValue = value - money.getSignValue(removalPriceCurrency)
        if needValue <= 0:
            needValue = None
        currencySettings = CURRENCY_SETTINGS.getRemovalSetting(removalPriceCurrency)
        text = getFormattedPriceString(value, currencySettings, needValue)
        defValue = removalPrice.defPrice.getSignValue(removalPriceCurrency)
        removalActionPercent = removalPrice.getActionPrc() if not self.bootcamp.isInBootcamp() else 0
        discountText = None
        if removalActionPercent != 0:
            discountText = getFormattedDiscountPriceString(currencySettings, removalActionPercent, defValue)
        return (text, discountText)
