# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/module.py
import logging
import typing
from gui.Scaleform import MENU
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import backport_r
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.common.specialization_model import SpecializationModel
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_ECONOMY_CODE, getKpiValueString
from gui.shared.gui_items.gui_item_economics import isItemBuyPriceAvailable
from gui.shared.items_parameters import params_helper, formatters as params_formatters, bonus_helper
from gui.shared.items_parameters.params_helper import SimplifiedBarVO
from gui.shared.money import MONEY_UNDEFINED, Currency
from gui.shared.tooltips import getComplexStatusWULF, getUnlockPrice, TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS, makeRemovalPriceBlock
from gui.shared.utils import GUN_CLIP, SHELLS_COUNT_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, AIMING_TIME_PROP_NAME, RELOAD_TIME_PROP_NAME, GUN_AUTO_RELOAD, AUTO_RELOAD_PROP_NAME, RELOAD_TIME_SECS_PROP_NAME, DUAL_GUN_RATE_TIME, DUAL_GUN_CHARGE_TIME, GUN_DUAL_GUN, GUN_CAN_BE_CLIP, GUN_CAN_BE_AUTO_RELOAD, GUN_CAN_BE_DUAL_GUN, TURBOSHAFT_ENGINE_POWER
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.supply_slot_categories import SlotCategories
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
_TOOLTIP_WIDTH = 468
_DEFAULT_PADDING = 20
_EMPTY_TOOLTIP_WIDTH = 350
_AUTOCANNON_SHOT_DISTANCE = 400
_OPT_DEVICE_SPEC_ALPHA = 0.5
_OPT_DEVICE_SELECTED_SPEC_ALPHA = 1
_logger = logging.getLogger(__name__)

class ModuleBlockTooltipData(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, context):
        super(ModuleBlockTooltipData, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=_DEFAULT_PADDING, right=_DEFAULT_PADDING)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_WIDTH)
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
        leftPadding = _DEFAULT_PADDING
        rightPadding = _DEFAULT_PADDING
        topPadding = _DEFAULT_PADDING
        priceValueWidth = 97
        blockTopPadding = -4
        textGap = -2
        itemTypeID = module.itemTypeID
        if itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES:
            headerBottom = -10
            headBlock = ModuleHeaderBlockConstructor
            headConfig = statusConfig if statusConfig.vehicle else paramsConfig
        else:
            headerBottom = -38
            headBlock = HeaderBlockConstructor
            headConfig = statusConfig
        items.append(formatters.packBuildUpBlockData(headBlock(module, headConfig, leftPadding, rightPadding).construct(), padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding, bottom=headerBottom)))
        if itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
            if itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                effectsBlock = OptDeviceEffectsBlockConstructor(module, statusConfig, leftPadding, 10).construct()
            else:
                effectsBlock = EffectsBlockConstructor(module, statusConfig, leftPadding, rightPadding).construct()
            if effectsBlock:
                effectsPaddings = formatters.packPadding(left=leftPadding, right=rightPadding, top=-4, bottom=-8)
                if statusConfig.useWhiteBg:
                    bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE
                else:
                    bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE
                items.append(formatters.packBuildUpBlockData(effectsBlock, padding=effectsPaddings, linkage=bgLinkage, stretchBg=True))
        if itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES:
            if paramsConfig.colorless:
                colorScheme = params_formatters.COLORLESS_SCHEME
            else:
                colorScheme = params_formatters.BASE_SCHEME
            commonStatsBlock = CommonStatsBlockConstructor(module, paramsConfig, statsConfig.slotIdx, leftPadding, rightPadding, colorScheme).construct()
            if commonStatsBlock:
                if statusConfig.useWhiteBg:
                    linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE
                else:
                    linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE
                items.append(formatters.packBuildUpBlockData(commonStatsBlock, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=-8), gap=textGap, linkage=linkage))
        priceBlock = PriceBlockConstructor(module, statsConfig, priceValueWidth, leftPadding, rightPadding).construct()
        if priceBlock:
            items.append(formatters.packBuildUpBlockData(priceBlock, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=-5, bottom=-8), gap=textGap))
        showModuleCompatibles = statsConfig.showCompatibles and itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES
        if showModuleCompatibles:
            if paramsConfig.vehicle is not None:
                paramVehDescr = paramsConfig.vehicle.descriptor
            else:
                paramVehDescr = None
            moduleCompatibles = params_helper.getCompatibles(module, paramVehDescr)
            compatibleBlocks = []
            for paramType, paramValue in moduleCompatibles:
                compatibleBlocks.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(_ms(MENU.moduleinfo_compatible(paramType))), desc=text_styles.standard(paramValue)))

            if compatibleBlocks:
                items.append(formatters.packBuildUpBlockData(compatibleBlocks, padding=formatters.packPadding(left=leftPadding)))
        if itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            canNotBuyBlock = None
            if module.isTrophy:
                canNotBuyBlock = self.__trophyDeviceBlocks(module, statusConfig)
            elif module.isDeluxe and module.isHidden:
                canNotBuyBlock = self.__hiddenDeluxeDeviceBlock(module, statusConfig)
            if canNotBuyBlock is not None:
                items.append(formatters.packBuildUpBlockData(canNotBuyBlock, padding=formatters.packPadding(top=-4, bottom=-5, left=_DEFAULT_PADDING, right=_DEFAULT_PADDING), gap=4))
        statusBlock = StatusBlockConstructor(module, statusConfig, leftPadding, rightPadding).construct()
        if statusBlock:
            statusTopPadding = -30 if showModuleCompatibles else blockTopPadding
            items.append(formatters.packBuildUpBlockData(statusBlock, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=statusTopPadding, bottom=-15)))
        if bonus_helper.isSituationalBonus(module.name):
            items.append(formatters.packImageTextBlockData(title='', desc=text_styles.standard(backport.text(R.strings.tooltips.vehicleParams.bonus.situational())), img=backport.image(R.images.gui.maps.icons.tooltip.asterisk_optional()), imgPadding=formatters.packPadding(left=4, top=3), txtGap=-4, txtOffset=20, padding=formatters.packPadding(left=59, right=_DEFAULT_PADDING)))
        if itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and statsConfig.vehicle is not None and not module.isInstalled(statsConfig.vehicle) and module.hasSimilarDevicesInstalled(statsConfig.vehicle) and not module.mayInstall(statsConfig.vehicle, statusConfig.slotIdx)[0]:
            items.append(formatters.packBuildUpBlockData(blocks=[formatters.packTitleDescBlock(title=text_styles.critical(backport.text(R.strings.tooltips.moduleFits.duplicated.header())), gap=0, desc=text_styles.standard(backport.text(R.strings.tooltips.moduleFits.duplicated.note())))], padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=-13), stretchBg=False))
        if statsConfig.isStaticInfoOnly:
            lastItem = items[-1]
            lastPadding = lastItem.get('padding', None)
            if lastPadding is None:
                lastItem['padding'] = {}
            lastItem['padding']['bottom'] = lastItem['padding'].get('bottom', 0) + 15
        return items

    def __trophyDeviceBlocks(self, module, statusConfig):
        trophyBlocks = []
        state = ''
        headerStyle = None
        if module.isUpgradable:
            headerStyle = text_styles.statusAttention
            state = 'basic'
        elif module.isUpgraded:
            headerStyle = text_styles.statInfo
            state = 'upgraded'
        trophyBlocks.append(formatters.packItemTitleDescBlockData(title=headerStyle(backport.text(R.strings.tooltips.moduleFits.trophyEquipment.dyn(state).header())), desc=text_styles.main(backport.text(R.strings.tooltips.moduleFits.trophyEquipment.dyn(state).description()))))
        trophyBlocks.append(self.__getCannotBuyBlock(module, statusConfig))
        return trophyBlocks

    def __hiddenDeluxeDeviceBlock(self, module, statusConfig):
        return [self.__getCannotBuyBlock(module, statusConfig)]

    @staticmethod
    def __getCannotBuyBlock(module, statusConfig):
        deviceType = 'trophyEquipment' if module.isTrophy else 'deluxeEquipment'
        statsVehicle = statusConfig.vehicle
        if statsVehicle is None or module in statsVehicle.optDevices.installed or module.isInInventory:
            cannotBuyHeaderStyle = text_styles.warning
        else:
            cannotBuyHeaderStyle = text_styles.critical
        return formatters.packItemTitleDescBlockData(title=cannotBuyHeaderStyle(backport.text(R.strings.tooltips.moduleFits.dyn(deviceType).cannotBuy.header())), desc=text_styles.main(backport.text(R.strings.tooltips.moduleFits.dyn(deviceType).cannotBuy.description())))


class ModuleTooltipBlockConstructor(object):
    MAX_INSTALLED_LIST_LEN = 10
    CLIP_GUN_MODULE_PARAM = 'vehicleClipGun'
    AUTO_RELOAD_GUN_MODULE_PARAM = 'autoReloadGun'
    DUAL_GUN_MODULE_PARAM = 'dualGun'
    WEIGHT_MODULE_PARAM = 'weight'
    TURBOSHAFT_ENGINE_MODULE_PARAM = 'turboshaftEngine'
    COOLDOWN_SECONDS = 'cooldownSeconds'
    CALIBER = 'caliber'
    MODULE_PARAMS = {GUI_ITEM_TYPE.CHASSIS: ('maxLoad', 'rotationSpeed', 'maxSteeringLockAngle', 'vehicleChassisRepairSpeed', 'chassisRepairTime'),
     GUI_ITEM_TYPE.TURRET: ('armor', 'rotationSpeed', 'circularVisionRadius'),
     GUI_ITEM_TYPE.GUN: ('avgDamageList',
                         'avgPiercingPower',
                         RELOAD_TIME_SECS_PROP_NAME,
                         RELOAD_TIME_PROP_NAME,
                         'avgDamagePerMinute',
                         'stunMinDurationList',
                         'stunMaxDurationList',
                         'dispertionRadius',
                         'maxShotDistance',
                         AIMING_TIME_PROP_NAME),
     GUI_ITEM_TYPE.ENGINE: ('enginePower', 'fireStartingChance'),
     GUI_ITEM_TYPE.RADIO: ('radioDistance',),
     CLIP_GUN_MODULE_PARAM: ('avgDamageList',
                             'avgPiercingPower',
                             SHELLS_COUNT_PROP_NAME,
                             SHELL_RELOADING_TIME_PROP_NAME,
                             RELOAD_MAGAZINE_TIME_PROP_NAME,
                             'avgDamagePerMinute',
                             'stunMinDurationList',
                             'stunMaxDurationList',
                             'dispertionRadius',
                             'maxShotDistance',
                             AIMING_TIME_PROP_NAME),
     AUTO_RELOAD_GUN_MODULE_PARAM: ('avgDamageList',
                                    'avgPiercingPower',
                                    SHELLS_COUNT_PROP_NAME,
                                    SHELL_RELOADING_TIME_PROP_NAME,
                                    AUTO_RELOAD_PROP_NAME,
                                    'stunMinDurationList',
                                    'stunMaxDurationList',
                                    'dispertionRadius',
                                    'maxShotDistance',
                                    AIMING_TIME_PROP_NAME),
     DUAL_GUN_MODULE_PARAM: ('avgDamageList',
                             'avgPiercingPower',
                             RELOAD_TIME_SECS_PROP_NAME,
                             DUAL_GUN_RATE_TIME,
                             DUAL_GUN_CHARGE_TIME,
                             'dispertionRadius',
                             AIMING_TIME_PROP_NAME),
     TURBOSHAFT_ENGINE_MODULE_PARAM: ('enginePower', TURBOSHAFT_ENGINE_POWER, 'fireStartingChance')}
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, module, configuration, leftPadding=_DEFAULT_PADDING, rightPadding=_DEFAULT_PADDING):
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
        descList = []
        moduleCategories = None
        if module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS:
            moduleParams = params_helper.getParameters(module)
            if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                moduleCategories = self.module.descriptor.categories
                if moduleCategories:
                    specsDesc, specsText = _getSpecsDescAndText(moduleCategories)
                    descList.append('{}{}'.format(specsDesc, specsText))
            paramName = ModuleTooltipBlockConstructor.WEIGHT_MODULE_PARAM
            paramValue = params_formatters.formatParameter(paramName, moduleParams[paramName]) if paramName in moduleParams else None
            if paramValue is not None:
                descList.append(params_formatters.formatParamNameColonValueUnits(paramName=paramName, paramValue=paramValue))
            elif module.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
                descParts = []
                cooldownSeconds = module.descriptor.cooldownSeconds
                if cooldownSeconds:
                    paramName = ModuleTooltipBlockConstructor.COOLDOWN_SECONDS
                    paramValue = params_formatters.formatParameter(paramName, cooldownSeconds)
                    descParts.append(params_formatters.formatParamNameColonValueUnits(paramName=paramName, paramValue=paramValue))
                if module.isBuiltIn and not module.isBuiltInInfoHidden:
                    descParts.append(text_styles.main(backport.text(R.strings.tooltips.equipment.builtIn())))
                descList.append(text_styles.concatStylesToMultiLine(*descParts))
        block.append(formatters.packTitleDescBlock(title=text_styles.highTitle(title), desc='\n'.join(descList), gap=-3, padding=formatters.packPadding(top=-6)))
        if self.configuration.withSlots and module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            block.append(formatters.packBuildUpBlockData(OptDeviceSlotsHeaderBlockConstructor(module=None, configuration=self.configuration, leftPadding=_DEFAULT_PADDING, rightPadding=_DEFAULT_PADDING).construct(), padding=formatters.packPadding(top=5, bottom=5)))
        else:
            imageBlocks = []
            overlayPath, overlayPadding, bottomOffset = self.__getOverlayData()
            imageBlocks.append(formatters.packItemTitleDescBlockData(img=backport.image(self._getIcon()), imgPadding=formatters.packPadding(top=7), overlayPath=overlayPath, overlayPadding=overlayPadding, padding=formatters.packPadding(left=120, top=10, bottom=5)))
            if moduleCategories:
                imageBlocks.append(_packSpecsIconsBlockData(vehicle=self.configuration.vehicle, categories=moduleCategories, slotIdx=self.configuration.slotIdx, topOffset=-40, leftOffset=(_TOOLTIP_WIDTH - _DEFAULT_PADDING * 2) * 0.5 - 3))
                bottomOffset = 10
            block.append(formatters.packBuildUpBlockData(blocks=imageBlocks, padding=formatters.packPadding(top=-14, bottom=bottomOffset)))
        return block

    def _getIcon(self):
        moduleName = self.module.descriptor.iconName
        icon = R.images.gui.maps.shop.artefacts.c_180x135.dyn(moduleName)
        if not icon:
            _logger.warn('Artefact icon missed: R.images.gui.maps.shop.artefacts.c_180x135.%s', moduleName)
            return R.invalid()
        return icon()

    def __getOverlayData(self):
        padding = formatters.packPadding(top=SLOT_HIGHLIGHT_TYPES.TOOLTIP_BIG_OVERLAY_PADDING_TOP, left=SLOT_HIGHLIGHT_TYPES.TOOLTIP_BIG_OVERLAY_PADDING_LEFT)
        bottomOffset = -60
        if self.module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and self.module.isDeluxe:
            overlayPath = backport.image(R.images.gui.maps.shop.artefacts.c_180x135.equipmentPlus_overlay())
        elif self.module.itemTypeID is GUI_ITEM_TYPE.EQUIPMENT and self.module.isBuiltIn and not self.module.isBuiltInInfoHidden:
            padding = formatters.packPadding(top=SLOT_HIGHLIGHT_TYPES.TOOLTIP_BUILD_IN_180_X_135_OVERLAY_PADDING_TOP, left=SLOT_HIGHLIGHT_TYPES.TOOLTIP_BUILD_IN_180_X_135_OVERLAY_PADDING_LEFT)
            overlayPath = backport.image(R.images.gui.maps.icons.quests.bonuses.small.builtInEquipment_overlay())
            bottomOffset = 0
        elif self.module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and self.module.isTrophy:
            suffix = ''
            if self.module.isUpgradable:
                suffix = 'Basic'
            elif self.module.isUpgraded:
                suffix = 'Upgraded'
            overlayPath = backport.image(R.images.gui.maps.shop.artefacts.c_180x135.dyn('equipmentTrophy{}_overlay'.format(suffix))())
        else:
            overlayPath = padding = None
            bottomOffset = 10
        return (overlayPath, padding, bottomOffset)


class ModuleHeaderBlockConstructor(ModuleTooltipBlockConstructor):

    def construct(self):
        module = self.module
        block = []
        title = module.userName
        descList = []
        descList.append(params_formatters.formatNameColonValue(nameStr=backport.text(R.strings.tooltips.vehicle.level()), valueStr=backport.text(R.strings.tooltips.level.num(str(module.level))())))
        moduleParams = params_helper.getParameters(module)
        paramName = ModuleTooltipBlockConstructor.WEIGHT_MODULE_PARAM
        paramValue = params_formatters.formatParameter(paramName, moduleParams[paramName]) if paramName in moduleParams else None
        if paramValue is not None:
            descList.append(params_formatters.formatParamNameColonValueUnits(paramName=paramName, paramValue=paramValue))
        block.append(formatters.packTitleDescBlock(title=text_styles.highTitle(title), desc='\n'.join(descList), gap=-3, padding=formatters.packPadding(top=-6)))
        block.append(formatters.packImageBlockData(img=backport.image(self._getIcon()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(left=0, top=0, bottom=0, right=0)))
        return block

    def _getIcon(self):
        moduleName = self.module.itemTypeName
        if moduleName == 'vehicleChassis' and self.module.isWheeledChassis():
            moduleName = 'vehicleWheeledChassis'
        icon = R.images.gui.maps.shop.modules.c_180x135.dyn(moduleName)
        if not icon:
            _logger.warn('Artefact icon missed: R.images.gui.maps.shop.modules.c_180x135.%s', moduleName)
            return R.invalid()
        return icon()


class PriceBlockConstructor(ModuleTooltipBlockConstructor):
    bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self, module, configuration, valueWidth, leftPadding, rightPadding):
        super(PriceBlockConstructor, self).__init__(module, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        self._inventoryPadding = formatters.packPadding(left=82)
        self._priceLeftPadding = 67
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
            _logger.error('You are not allowed to use buyPrice and sellPrice at the same time')
            return
        elif self.module.itemTypeID is GUI_ITEM_TYPE.EQUIPMENT and self.module.isBuiltIn:
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
            if unlockPrice and not isEqOrDev:
                parentCD = vehicle.intCD if vehicle is not None else None
                _, cost, need, _, actionPercent = getUnlockPrice(module.intCD, parentCD)
                neededValue = None
                if not isUnlocked and isNextToUnlock and need > 0:
                    neededValue = need
                if cost > 0:
                    block.append(makePriceBlock(cost, CURRENCY_SETTINGS.UNLOCK_PRICE, neededValue, leftPadding=self._priceLeftPadding, valueWidth=self._valueWidth, iconRightOffset=14))
            if buyPrice and not isAutoUnlock and not module.isHidden:
                shop = self.itemsCache.items.shop
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
                        if needValue <= 0:
                            needValue = None
                    else:
                        needValue = None
                    if currency == Currency.GOLD and actionPercent > 0:
                        leftActionPadding = 101 + self.leftPadding
                    else:
                        leftActionPadding = 81 + self.leftPadding
                    if showDelimiter:
                        block.append(formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.tooltips.vehicle.textDelimiter.c_or())), padding=formatters.packPadding(left=leftActionPadding)))
                    block.append(makePriceBlock(value, CURRENCY_SETTINGS.getBuySetting(currency), needValue, defValue if defValue > 0 else None, actionPercent, valueWidth=self._valueWidth, leftPadding=self._priceLeftPadding, iconRightOffset=14))
                    showDelimiter = True

            if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and module.isUpgradable:
                money = self.itemsCache.items.stats.money
                itemPrice = module.getUpgradePrice(self.itemsCache.items)
                currency = itemPrice.getCurrency()
                value = itemPrice.price.getSignValue(currency)
                defValue = itemPrice.defPrice.getSignValue(currency)
                if isEqOrDev and not self.configuration.isStaticInfoOnly:
                    needValue = value - money.getSignValue(currency)
                    if needValue <= 0:
                        needValue = None
                else:
                    needValue = None
                block.append(makePriceBlock(value, CURRENCY_SETTINGS.getUpgradableSetting(currency), needValue, defValue if defValue > 0 else None, valueWidth=self._valueWidth, leftPadding=self._priceLeftPadding, iconRightOffset=14))
            isComplexDevice = module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and not module.isRemovable
            if isComplexDevice and not self.configuration.isAwardWindow:
                removalPrice = module.getRemovalPrice(self.itemsCache.items)
                removalPriceCurrency = removalPrice.getCurrency()
                value = removalPrice.price.getSignValue(removalPriceCurrency)
                removalActionPercent = removalPrice.getActionPrc() if not self.bootcamp.isInBootcamp() else 0
                defValue = removalPrice.defPrice.getSignValue(removalPriceCurrency)
                needValue = value - money.getSignValue(removalPriceCurrency)
                if needValue <= 0 or self.configuration.isStaticInfoOnly:
                    needValue = None
                block.append(makeRemovalPriceBlock(value, CURRENCY_SETTINGS.getRemovalSetting(removalPriceCurrency), needValue, defValue if defValue > 0 else None, removalActionPercent, valueWidth=117, gap=15, leftPadding=self._priceLeftPadding, isDeluxe=module.isDeluxe))
            if sellPrice and module.sellPrices:
                block.append(makePriceBlock(module.sellPrices.itemPrice.price.credits, CURRENCY_SETTINGS.SELL_PRICE, oldPrice=module.sellPrices.itemPrice.defPrice.credits, percent=module.sellPrices.itemPrice.getActionPrc() if not self.bootcamp.isInBootcamp() else 0, valueWidth=self._valueWidth, leftPadding=self._priceLeftPadding, iconRightOffset=14))
            if inventoryCount:
                count = module.inventoryCount
                if count > 0:
                    block.append(self._getInventoryBlock(count, self._inInventoryBlockData, self._inventoryPadding))
            if vehiclesCount:
                count = len(module.getInstalledVehicles(items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()))
                if count > 0:
                    block.append(self._getInventoryBlock(count, self._onVehicleBlockData, self._inventoryPadding))
            return block

    @staticmethod
    def _getInventoryBlock(count, blockData, padding):
        return formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(blockData['text']), value=text_styles.stats(count), icon=blockData['icon'], padding=padding, titlePadding=formatters.packPadding(left=17), iconPadding=formatters.packPadding(left=-2))

    def _getDemountCount(self):
        priceText, discountText = self._getDemountPriceText()
        dkCount = text_styles.demountKitText('1')
        dkIcon = icons.demountKit()
        dkText = text_styles.concatStylesWithSpace(dkCount, dkIcon)
        descr = R.strings.demount_kit.equipmentInstall
        if self.module.isDeluxe:
            dynAccId = descr.demount()
        else:
            dynAccId = descr.demountOr()
        text = backport.text(dynAccId, count=priceText, countDK=dkText)
        if discountText:
            text += '\n' + discountText
        return text


class CommonStatsBlockConstructor(ModuleTooltipBlockConstructor):

    def __init__(self, module, configuration, slotIdx, leftPadding, rightPadding, colorScheme=None):
        super(CommonStatsBlockConstructor, self).__init__(module, configuration, leftPadding, rightPadding)
        self._valueWidth = 108
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
            highlightPossible = False
            serverSettings = dependency.instance(ISettingsCore).serverSettings
            if module.itemTypeID == GUI_ITEM_TYPE.GUN:
                reloadingType = module.getReloadingType(vehicle.descriptor if vehicle is not None else None)
                if reloadingType == GUN_CLIP or reloadingType == GUN_CAN_BE_CLIP:
                    paramsKeyName = self.CLIP_GUN_MODULE_PARAM
                elif reloadingType == GUN_CAN_BE_AUTO_RELOAD or reloadingType == GUN_AUTO_RELOAD:
                    highlightPossible = serverSettings.checkAutoReloadHighlights(increase=True)
                    paramsKeyName = self.AUTO_RELOAD_GUN_MODULE_PARAM
                elif reloadingType == GUN_CAN_BE_DUAL_GUN or reloadingType == GUN_DUAL_GUN:
                    highlightPossible = serverSettings.checkDualGunHighlights(increase=True)
                    paramsKeyName = self.DUAL_GUN_MODULE_PARAM
            elif paramsKeyName == GUI_ITEM_TYPE.ENGINE:
                if vehicle is not None and vehicle.descriptor.hasTurboshaftEngine:
                    highlightPossible = serverSettings.checkTurboshaftHighlights(increase=True)
                    paramsKeyName = self.TURBOSHAFT_ENGINE_MODULE_PARAM
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
                            block.append(formatters.packTextParameterBlockData(name=params_formatters.formatModuleParamName(paramName, vDescr), value=fmtValue, valueWidth=self._valueWidth, gap=19, highlight=highlightPossible and paramName in (AUTO_RELOAD_PROP_NAME,
                             RELOAD_TIME_SECS_PROP_NAME,
                             DUAL_GUN_CHARGE_TIME,
                             DUAL_GUN_RATE_TIME,
                             TURBOSHAFT_ENGINE_POWER)))

            else:
                formattedModuleParameters = params_formatters.getFormattedParamsList(module.descriptor, moduleParams)
                for paramName, paramValue in formattedModuleParameters:
                    if paramName in paramsList and paramValue is not None:
                        block.append(formatters.packTextParameterBlockData(name=params_formatters.formatModuleParamName(paramName), value=paramValue, valueWidth=self._valueWidth, gap=19))

        if block:
            block.insert(0, formatters.packTextBlockData(text_styles.middleTitle(backport.text(R.strings.tooltips.tankCarusel.MainProperty())), padding=formatters.packPadding(bottom=7)))
            if module.itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES:
                extraInfo = module.getExtraIconInfo(vDescr)
                title = None
                if module.itemTypeID == GUI_ITEM_TYPE.GUN:
                    if extraInfo:
                        if module.isClipGun(vDescr):
                            title = R.strings.menu.moduleInfo.clipGunLabel()
                        elif module.isAutoReloadable(vDescr):
                            hasBoost = False
                            for gun in vDescr.type.getGuns():
                                if gun.compactDescr == module.intCD:
                                    hasBoost = gun.autoreloadHasBoost

                            resource = R.strings.menu.moduleInfo.autoReloadGunLabel
                            title = resource.dyn('boost')() if hasBoost and resource.dyn('boost') else resource()
                        elif module.isDualGun(vDescr):
                            title = R.strings.menu.moduleInfo.dualGunLabel()
                elif module.itemTypeID == GUI_ITEM_TYPE.CHASSIS:
                    if module.isHydraulicChassis():
                        if module.isWheeledChassis():
                            title = R.strings.menu.moduleInfo.hydraulicWheeledChassisLabel()
                        elif module.hasAutoSiege():
                            title = R.strings.menu.moduleInfo.hydraulicAutoSiegeChassisLabel()
                        else:
                            title = R.strings.menu.moduleInfo.hydraulicChassisLabel()
                    elif module.isTrackWithinTrack():
                        title = R.strings.menu.moduleInfo.trackWithinTrackChassisLabel()
                elif module.itemTypeID == GUI_ITEM_TYPE.ENGINE:
                    if module.hasTurboshaftEngine():
                        title = R.strings.menu.moduleInfo.turboshaftEngine()
                if title:
                    block.insert(0, formatters.packImageTextBlockData(title=text_styles.neutral(backport.text(title)), desc='', img=extraInfo, imgPadding=formatters.packPadding(top=3, right=20), padding=formatters.packPadding(left=90, bottom=11), ignoreImageSize=True))
        return block


class ModuleReplaceBlockConstructor(ModuleTooltipBlockConstructor):

    def construct(self):
        block = []
        vehicle = self.configuration.vehicle
        optionalDevice = vehicle.optDevices.installed[self.configuration.slotIdx]
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


class EffectsBlockConstructor(ModuleTooltipBlockConstructor):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def construct(self):
        module = self.module
        name = module.descriptor.name
        block = []
        emptyStr = backport.text(R.strings.artefacts.empty())

        def hasString(stringToCheck):
            return stringToCheck and stringToCheck != emptyStr

        if self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
            isRemovingStun = module.isRemovingStun
        else:
            isRemovingStun = False
        attribs = R.strings.artefacts.dyn(name)
        if not attribs:
            return block
        kpiArgs = {kpi.name:text_styles.bonusAppliedText(getKpiValueString(kpi, kpi.value)) for kpi in module.getKpi(self.configuration.vehicle)}
        onUseStr = backport.text((attribs.removingStun.onUse() if isRemovingStun else attribs.onUse()), **kpiArgs)
        restrictionStr = backport.text(attribs.restriction())
        alwaysStr = backport.text(attribs.always(), **kpiArgs)
        if hasString(alwaysStr):
            block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.equipment.always())), desc=text_styles.main(alwaysStr), padding=formatters.packPadding(top=5)))
        if hasString(onUseStr):
            block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.equipment.onUse())), desc=text_styles.main(onUseStr), padding=formatters.packPadding(top=5)))
        if hasString(restrictionStr):
            block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.equipment.restriction())), desc=text_styles.main(restrictionStr), padding=formatters.packPadding(top=5)))
        if block:
            block[0]['padding']['top'] = -1
            block[-1]['padding']['bottom'] = -5
        return block


class OptDeviceEffectsBlockConstructor(ModuleTooltipBlockConstructor):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def construct(self):
        module = self.module
        vehicle = self.configuration.vehicle
        categories = self.module.descriptor.categories
        slotIdx = self.configuration.slotIdx
        isPanelTooltip = self.configuration.withSlots
        block = []
        isSpecMatch = False
        slotCategories = set()
        if vehicle is not None:
            slotCategories = vehicle.optDevices.getSlot(slotIdx).item.categories
            isSpec = bool(slotCategories & categories)
            if categories and isSpec:
                isSpecMatch = True
        additionalDescr = R.strings.artefacts.dyn(module.descriptor.groupName).dyn('additional_descr')
        if additionalDescr:
            descr = backport.text(R.strings.tank_setup.effects.template(), icon=icons.makeImageTag(source=backport.image(R.images.gui.maps.icons.tanksetup.cards.effect()), width=10, height=16), title=text_styles.neutral(backport.text(R.strings.tank_setup.effects.name())), descr=backport.text(additionalDescr()))
            block.append(formatters.packTextBlockData(text_styles.standard(descr)))
        if categories and isPanelTooltip and slotCategories:
            kpiTitle = backport.text(R.strings.tank_setup.tooltips.optDevice.bonusDesc(), match=self.__neutralFatTextStyle(backport.text(R.strings.tank_setup.tooltips.optDevice.bonusDesc.num(str(isSpecMatch))())))
        else:
            kpiTitle = backport.text(R.strings.tank_setup.tooltips.optDevice.bonusDesc.applied())
        block.append(formatters.packTextBlockData(text_styles.middleTitle(kpiTitle), padding=formatters.packPadding(top=8 if additionalDescr else -1, bottom=5)))
        moduleKpi = module.getKpi(vehicle)
        for kpi in moduleKpi:
            descKpi = backport.text(kpi.getLongDescriptionR())
            kpiList = []
            if not isPanelTooltip and module.isRegular and kpi.specValue is not None:
                kpiList.append(formatters.packAlignedTextBlockData(text_styles.bonusAppliedText(getKpiValueString(kpi, kpi.value)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, blockWidth=60))
            if (isSpecMatch or not isPanelTooltip) and kpi.specValue is not None:
                specValue = kpi.specValue
            else:
                specValue = kpi.value
            kpiList.append(formatters.packTextParameterBlockData(text_styles.main(descKpi), text_styles.bonusAppliedText(getKpiValueString(kpi, specValue)), valueWidth=63, padding=formatters.packPadding(left=51), gap=14))
            block.append(formatters.packBuildUpBlockData(kpiList, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, gap=-51, padding=formatters.packPadding(bottom=-9)) if len(kpiList) > 1 else kpiList[0])

        if categories and any((kpi.specValue is not None for kpi in moduleKpi)):
            if not isSpecMatch:
                howToIncrease = R.strings.tank_setup.tooltips.howToIncrease
                if len(categories) > 1:
                    howToIncrease = howToIncrease.multiple
                    cats = backport.text(R.strings.tank_setup.tooltips.separator.other()).join((text_styles.main(backport.text(R.strings.tank_setup.categories.dyn(category)())) for category in categories))
                else:
                    howToIncrease = howToIncrease.single
                    cats = text_styles.main(backport.text(R.strings.tank_setup.categories.dyn(next(iter(categories)))()))
                additionalText = backport.text(howToIncrease(), category=cats)
            else:
                additionalText = backport.text(R.strings.tank_setup.tooltips.howToIncrease.increased())
            block.append(formatters.packTextBlockData(text_styles.standard(additionalText), padding=formatters.packPadding(top=9)))
        if module.isRegular and all((kpi.specValue is None for kpi in moduleKpi)):
            additionalText = backport.text(R.strings.tank_setup.tooltips.howToIncrease.impossible())
            block.append(formatters.packTextBlockData(text_styles.standard(additionalText), padding=formatters.packPadding(top=9)))
        return block

    def _bonusStyleTextStyle(self, text, useStyle=False):

        def _matchSpecTextStyle(message):
            return "<font face='$FieldFont' size='14' color='#b4ff48'>%s</font>" % message

        return _matchSpecTextStyle(text) if useStyle else text_styles.bonusAppliedText(text)

    def __neutralFatTextStyle(self, text):
        return "<font face='$TitleFont' size='15' color='#FFDD99'>%s</font>" % text


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
        checkBuying = configuration.checkBuying
        isEqOrDev = module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS
        isFit = True
        reason = ''
        showAllInstalled = True
        titleFormatter = text_styles.middleTitle
        if vehicle is not None and (vehicle.isInInventory or configuration.isCompare):
            isFit, reason = module.mayInstall(vehicle, slotIdx)
        inventoryVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
        totalInstalledVehicles = [ x.shortUserName for x in module.getInstalledVehicles(inventoryVehicles) ]
        installedVehicles = totalInstalledVehicles[:self.MAX_INSTALLED_LIST_LEN]
        tooltipHeader = None
        tooltipText = None
        if not isFit:
            reason = reason.replace(' ', '_')
            tooltipHeader, tooltipText = getComplexStatusWULF(R.strings.tooltips.moduleFits.dyn(reason))
            if reason == 'not_with_installed_equipment':
                if vehicle is not None:
                    titleFormatter = text_styles.critical
                    conflictEqs = module.getConflictedEquipments(vehicle)
                    tooltipText %= {'eqs': ', '.join([ _ms(e.userName) for e in conflictEqs ])}
            elif reason in ('already_installed', 'similar_device_already_installed'):
                if isEqOrDev and installedVehicles:
                    tooltipHeader, tooltipText = self.__getInstalledVehiclesBlock(installedVehicles, module)
                else:
                    tooltipHeader = None
            elif reason == 'too_heavy':
                titleFormatter = text_styles.critical
                showAllInstalled = False
        elif installedVehicles:
            tooltipHeader, tooltipText = self.__getInstalledVehiclesBlock(installedVehicles, module)
        if tooltipHeader is not None or tooltipText is not None:
            if showAllInstalled and len(totalInstalledVehicles) > self.MAX_INSTALLED_LIST_LEN:
                hiddenVehicleCount = len(totalInstalledVehicles) - self.MAX_INSTALLED_LIST_LEN
                hiddenTxt = '%s %s' % (text_styles.standard(backport.text(R.strings.tooltips.suitableVehicle.hiddenVehicleCount())), text_styles.stats(hiddenVehicleCount))
                tooltipText = '%s %s' % (tooltipText, hiddenTxt)
            block.append(self._packStatusBlock(tooltipHeader, tooltipText, titleFormatter))
        if checkBuying:
            isFit, reason = module.mayPurchase(self.itemsCache.items.stats.money)
            if not isFit:
                reason = reason.replace(' ', '_')
                tooltipHeader, tooltipText = getComplexStatusWULF(R.strings.tooltips.moduleFits.dyn(reason))
                if GUI_ITEM_ECONOMY_CODE.isCurrencyError(reason):
                    titleFormatter = text_styles.critical
                if tooltipHeader is not None or tooltipText is not None:
                    block.append(self._packStatusBlock(tooltipHeader, tooltipText, titleFormatter, padding=formatters.packPadding(top=-3)))
        if vehicle is not None and slotIdx is not None and module.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT and module not in vehicle.consumables.installed:
            currentEquipment = vehicle.consumables.installed[slotIdx]
            if currentEquipment is not None and currentEquipment.isBuiltIn:
                tooltipHeader, tooltipText = getComplexStatusWULF(R.strings.tooltips.moduleFits.can_not_remove_builtin_equipment)
                if tooltipHeader is not None or tooltipText is not None:
                    block.append(self._packStatusBlock(tooltipHeader, tooltipText, text_styles.critical))
        return block

    def _packStatusBlock(self, tooltipHeader, tooltipText, titleFormatter, padding=None, gap=1):
        return formatters.packTitleDescBlock(title=titleFormatter(tooltipHeader), desc=text_styles.standard(tooltipText), padding=padding, gap=gap)

    def _getResearchPageStatus(self):
        module = self.module
        configuration = self.configuration
        vehicle = configuration.vehicle
        node = configuration.node
        block = []
        header, text = (None, None)
        nodeState = int(node.state)
        statusTemplate = R.strings.tooltips.researchPage.module.status
        parentCD = vehicle.intCD if vehicle is not None else None
        _, _, need, _, _ = getUnlockPrice(module.intCD, parentCD, vehicle.level)

        def status(title=None, desc=None):
            if title is not None or desc is not None:
                block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(title) if title is not None else '', desc=text_styles.main(desc) if desc is not None else '', gap=-1))
            return block

        if not nodeState & NODE_STATE_FLAGS.UNLOCKED:
            if not vehicle.isUnlocked:
                header, text = getComplexStatusWULF(statusTemplate.rootVehicleIsLocked)
            elif not nodeState & NODE_STATE_FLAGS.NEXT_2_UNLOCK:
                header, text = getComplexStatusWULF(statusTemplate.parentModuleIsLocked)
            elif need > 0:
                header, text = getComplexStatusWULF(statusTemplate.notEnoughXP)
                header = text_styles.critical(header)
            return status(header, text)
        elif not vehicle.isInInventory:
            header, text = getComplexStatusWULF(statusTemplate.needToBuyTank, vehiclename=vehicle.userName)
            return status(header, text)
        elif nodeState & NODE_STATE_FLAGS.INSTALLED:
            return status()
        else:
            if vehicle is not None:
                if vehicle.isInInventory:
                    vState = vehicle.getState()
                    states = vehicle.VEHICLE_STATE
                    if vState == states.BATTLE:
                        header, text = getComplexStatusWULF(statusTemplate.vehicleIsInBattle)
                    elif vState == states.LOCKED:
                        header, text = getComplexStatusWULF(statusTemplate.vehicleIsReadyToFight)
                    elif vState in (states.DAMAGED, states.EXPLODED, states.DESTROYED):
                        header, text = getComplexStatusWULF(statusTemplate.vehicleIsBroken)
                if header is not None or text is not None:
                    return status(header, text)
            return self._getStatus()

    def __getInstalledVehiclesBlock(self, installedVehicles, module):
        tooltipHeader, _ = getComplexStatusWULF(R.strings.tooltips.deviceFits.already_installed if module.itemTypeName == GUI_ITEM_TYPE.OPTIONALDEVICE else R.strings.tooltips.moduleFits.already_installed)
        tooltipText = ', '.join(installedVehicles)
        return (tooltipHeader, tooltipText)


class OptDeviceSlotsHeaderBlockConstructor(ModuleTooltipBlockConstructor):

    def construct(self):
        block = []
        vehicle = self.configuration.vehicle
        slotIdx = self.configuration.slotIdx
        slotsBlocks = []
        hasSlotSpecs = False
        for idx in range(len(vehicle.optDevices.slots)):
            categories = vehicle.optDevices.getSlot(idx).item.categories
            selectedSlot = idx == slotIdx
            moduleInSlot = vehicle.optDevices.installed[idx]
            hasModuleInSlot = moduleInSlot is not None
            if moduleInSlot:
                moduleCategories = moduleInSlot.descriptor.categories
                overlayPath, overlayPadding = self.__getOverlayData(moduleInSlot)
            else:
                moduleCategories = []
                overlayPath = None
                overlayPadding = None
            if moduleCategories and categories:
                isSpecMatch = bool(categories & moduleCategories)
            else:
                isSpecMatch = False
            deviceSpecs = None
            if not isSpecMatch and moduleCategories and categories:
                deviceSpecs = []
                for spec in SlotCategories.ORDER:
                    if spec in moduleCategories:
                        deviceSpecs.append(formatters.packImageListIconData(imgSrc=backport.image(R.images.gui.maps.icons.specialization.dyn('{}_off'.format(spec))()), imgAlpha=_OPT_DEVICE_SELECTED_SPEC_ALPHA))

            slotSpecs = None
            if categories:
                slotSpecs = []
                for spec in SlotCategories.ORDER:
                    if spec not in categories:
                        continue
                    if spec in moduleCategories:
                        status = 'on'
                    else:
                        status = 'off'
                    slotSpecs.append(formatters.packImageListIconData(imgSrc=backport.image(R.images.gui.maps.icons.specialization.dyn('medium_{}_{}'.format(spec, status))()), imgAlpha=_OPT_DEVICE_SELECTED_SPEC_ALPHA))

            icon = self._getIcon(moduleInSlot) if hasModuleInSlot else None
            if selectedSlot and hasModuleInSlot and isSpecMatch:
                slotState = TOOLTIPS_CONSTANTS.OPTDEV_SLOT_STATE_ACTIVE_SELECTED
            elif selectedSlot:
                slotState = TOOLTIPS_CONSTANTS.OPTDEV_SLOT_STATE_EMPTY_SELECTED
            else:
                slotState = TOOLTIPS_CONSTANTS.OPTDEV_SLOT_STATE_EMPTY
            if categories:
                hasSlotSpecs = True
            slotsBlocks.append(formatters.packOptDeviceSlotBlockData(imagePath=backport.image(icon) if hasModuleInSlot else '', slotState=slotState, slotAlpha=1 if selectedSlot else 0.4, showUpArrow=False, showSlotHighlight=isSpecMatch, overlayPath=overlayPath, overlayPadding=overlayPadding, slotSpecs=slotSpecs, deviceSpecs=deviceSpecs))

        block.append(formatters.packBuildUpBlockData(blocks=slotsBlocks, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, gap=5, padding=formatters.packPadding(bottom=0 if hasSlotSpecs else 20)))
        return block

    def _getIcon(self, module):
        moduleName = module.descriptor.iconName
        icon = R.images.gui.maps.icons.quests.bonuses.big.dyn(moduleName)
        if not icon:
            _logger.warn('Artefact icon missed: R.images.gui.maps.icons.quests.bonuses.big.%s', moduleName)
            return R.invalid()
        return icon()

    def __getOverlayData(self, module):
        if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and module.isDeluxe:
            overlayPath = backport.image(R.images.gui.maps.icons.quests.bonuses.big.equipmentPlus_overlay())
        elif module.isTrophy:
            suffix = ''
            if module.isUpgradable:
                suffix = 'Basic'
            elif module.isUpgraded:
                suffix = 'Upgraded'
            overlayPath = backport.image(R.images.gui.maps.icons.quests.bonuses.big.dyn('equipmentTrophy{}_overlay'.format(suffix))())
        else:
            overlayPath = None
        if overlayPath is not None:
            padding = formatters.packPadding(top=SLOT_HIGHLIGHT_TYPES.TOOLTIP_OVERLAY_PADDING_TOP, left=SLOT_HIGHLIGHT_TYPES.TOOLTIP_OVERLAY_PADDING_LEFT)
        else:
            padding = None
        return (overlayPath, padding)


class OptDeviceEmptyBlockTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(OptDeviceEmptyBlockTooltipData, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self._setMargins(10, 15)
        self._setContentMargin(top=0, left=0, bottom=_DEFAULT_PADDING, right=_DEFAULT_PADDING)
        self._setWidth(_TOOLTIP_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(OptDeviceEmptyBlockTooltipData, self)._packBlocks()
        _, slotIdx, vehicle = args
        self.context.buildItem(slotIdx=slotIdx, vehicle=vehicle)
        status = self.context.getStatusConfiguration(None)
        leftPadding = _DEFAULT_PADDING
        rightPadding = _DEFAULT_PADDING
        topPadding = _DEFAULT_PADDING
        slotItem, isDyn = vehicle.optDevices.getSlot(slotIdx)
        title = backport.text(R.strings.tooltips.hangar.ammo_panel.device.empty.header())
        descList = []
        if slotItem.categories:
            specDesc, specText = _getSpecsDescAndText(slotItem.categories)
            descList.append('{}{}'.format(specDesc, specText))
            descBlock = formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tank_setup.tooltips.specializationDesc(), spec=specText)))
        else:
            descBlock = formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.hangar.ammo_panel.device.empty.body())))
        if descList:
            titleBlock = formatters.packTitleDescBlock(title=text_styles.highTitle(title), desc='\n'.join(descList))
        else:
            titleBlock = formatters.packTextBlockData(text=text_styles.highTitle(title))
        headerBlocks = OptDeviceSlotsHeaderBlockConstructor(None, status, leftPadding, rightPadding).construct()
        headerBlocks.insert(0, titleBlock)
        items.append(formatters.packBuildUpBlockData(blocks=headerBlocks, gap=10, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding, bottom=-_DEFAULT_PADDING)))
        items.append(formatters.packBuildUpBlockData(blocks=[descBlock], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, stretchLast=True, padding=formatters.packPadding(left=leftPadding, right=rightPadding)))
        if isDyn:
            dynCatsTitle = backport.text(R.strings.tank_setup.tooltips.dynamicCategory.title())
            dynCatsDesc = backport.text(R.strings.tank_setup.tooltips.dynamicCategory.desc())
            items.append(formatters.packTitleDescBlock(title=text_styles.warning(dynCatsTitle), desc=text_styles.main(dynCatsDesc), padding=formatters.packPadding(left=leftPadding, right=rightPadding)))
        return items


class AmmunitionEmptyBlockTooltipData(BlocksTooltipData):
    _HEADER = 'header'
    _BODY = 'body'

    def __init__(self, context):
        super(AmmunitionEmptyBlockTooltipData, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self._setWidth(_EMPTY_TOOLTIP_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        items = super(AmmunitionEmptyBlockTooltipData, self)._packBlocks()
        linkage = args
        title = _ms('{}/{}'.format(linkage, self._HEADER))
        desc = _ms('{}/{}'.format(linkage, self._BODY))
        items.append(formatters.packTextBlockData(text=text_styles.highTitle(title)))
        items.append(formatters.packBuildUpBlockData(blocks=[formatters.packTextBlockData(text=text_styles.main(desc))], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, stretchLast=True))
        return items


class AmmunitionSlotSpecTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(AmmunitionSlotSpecTooltipData, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self._setWidth(_EMPTY_TOOLTIP_WIDTH)
        self._setContentMargin(bottom=7)

    def _packBlocks(self, spec, isDyn, isClickable):
        items = super(AmmunitionSlotSpecTooltipData, self)._packBlocks()
        title = backport.text(R.strings.tank_setup.categories.dyn(spec)())
        desc = backport.text(R.strings.tank_setup.categories.slotEffect.dyn(spec)())
        blocks = [formatters.packTitleDescBlock(title=text_styles.middleTitle(title), desc=text_styles.main(desc))]
        if isDyn and spec != SpecializationModel.EMPTY:
            titleDyn = backport.text(R.strings.tank_setup.tooltips.dynamicCategory.title())
            if isClickable:
                descDyn = backport.text(R.strings.tank_setup.tooltips.dynamicCategoryClickable.desc())
            else:
                descDyn = backport.text(R.strings.tank_setup.tooltips.dynamicCategory.desc())
            blocks.append(formatters.packTitleDescBlock(title=text_styles.warning(titleDyn), desc=text_styles.main(descDyn)))
        items.append(formatters.packBuildUpBlockData(blocks))
        return items


def _getSpecsDescAndText(categories):
    specText = text_styles.standard(' / ').join((text_styles.expText(backport.text(R.strings.tank_setup.categories.dyn(spec)())) for spec in SlotCategories.ORDER if spec in categories))
    specDesc = text_styles.main(backport.text(R.strings.tooltips.parameter.categories()))
    return (specDesc, specText)


def _packSpecsIconsBlockData(vehicle, categories, slotIdx, topOffset=0, leftOffset=0):
    specIcons = []
    for spec in SlotCategories.ORDER:
        if spec not in categories:
            continue
        if vehicle is not None and spec in vehicle.optDevices.slots[slotIdx].categories:
            status = 'on'
            alpha = _OPT_DEVICE_SELECTED_SPEC_ALPHA
        else:
            status = 'off'
            alpha = _OPT_DEVICE_SPEC_ALPHA
        specIcons.append(formatters.packImageListIconData(imgSrc=backport.image(R.images.gui.maps.icons.specialization.dyn('medium_{}_{}'.format(spec, status))()), imgAlpha=alpha))

    iconSize = 64
    hGap = -32
    catsLen = len(categories)
    paddingLeft = leftOffset - (catsLen * iconSize + (catsLen - 1) * hGap) * 0.5
    return formatters.packImageListParameterBlockData(listIconSrc=specIcons, columnWidth=iconSize, rowHeight=iconSize, horizontalGap=hGap, padding=formatters.packPadding(left=paddingLeft, top=topOffset))
