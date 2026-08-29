# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/shell.py
from __future__ import absolute_import
import logging
from constants import DAMAGE_INTERPOLATION_DIST_LAST, DAMAGE_INTERPOLATION_DIST_FIRST, SHELL_MECHANICS_TYPE
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.backport import image
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items.gui_item_economics import isItemBuyPriceAvailable
from gui.shared.items_parameters.functions import getShellParamsSwitcherModifiedShells
from gui.shared.items_parameters.shell_params import SHELL_MECHANIC_ADDITIONAL_PARAMETERS
from gui.shared.items_parameters import params_helper, formatters as params_formatters
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import makePriceBlock, CURRENCY_SETTINGS, BlocksTooltipData
from gui.shared.tooltips.module import ModuleTooltipBlockConstructor
from gui.shared.utils import NORMALIZATION_ANGLE, RICOCHET_ANGLE, PENETRATION_LOSS
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.utils import getVehicleDescriptorWithoutMechanics
from skeletons.gui.shared import IItemsCache
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import hasVehicleDescrMechanic
from gui.impl.gen.view_models.common.vehicle_mechanic_model import MechanicsRank
_logger = logging.getLogger(__name__)
_SHELL_TOOLTIP_FORMAT_SETTINGS = dict(params_formatters.FORMAT_SETTINGS)
_SHELL_TOOLTIP_FORMAT_SETTINGS.update({'avgDamage': {'rounder': backport.getIntegralFormat},
 'avgMutableDamage': {'rounder': backport.getIntegralFormat,
                      'separator': '-'},
 'piercingPower': {'rounder': backport.getIntegralFormat}})
_ASTERISK = '*'
_TOOLTIP_MIN_WIDTH = 380
_TOOLTIP_NORMAL_WIDTH = 420
_TWO_COLUMNS_TOOLTIP_WIDTH = 500
_MECHANICS_TEXT_ROOT = R.strings.tooltips.shell.mechanics
_MECHANICS_IMAGE_ROOT = R.images.gui.maps.icons.tooltip.mechanics
_SUPPORTED_MECHANICS = (VehicleMechanic.LOW_CHARGE_SHOT,
 VehicleMechanic.SHELL_PARAMS_SWITCHER,
 VehicleMechanic.SHELL_CALIBRATION,
 VehicleMechanic.BUSTLE_FEED)
_MECHANIC_PARAMS_WIDTH = {VehicleMechanic.LOW_CHARGE_SHOT: _TWO_COLUMNS_TOOLTIP_WIDTH,
 VehicleMechanic.SHELL_PARAMS_SWITCHER: _TWO_COLUMNS_TOOLTIP_WIDTH,
 VehicleMechanic.SHELL_CALIBRATION: _TOOLTIP_NORMAL_WIDTH,
 VehicleMechanic.BUSTLE_FEED: _TWO_COLUMNS_TOOLTIP_WIDTH}
_PARAM_VISIBILITY = {ModuleTooltipBlockConstructor.CALIBER: lambda cfg, shell, value: False,
 'avgDamage': lambda cfg, shell, value: not shell.isDamageMutable(),
 NORMALIZATION_ANGLE: lambda cfg, shell, value: cfg.showNormalizationAngle and (value != 0 or _isEmptyNormalizationAngleValid(cfg, shell)),
 RICOCHET_ANGLE: lambda cfg, shell, value: cfg.showReboundAngle,
 PENETRATION_LOSS: lambda cfg, shell, value: cfg.showPenetrationLoss,
 'screensArmorMultiplier': lambda cfg, shell, value: cfg.showScreensArmorMultiplier}
_MECHANIC_ONLY_PARAMS = {paramName for mechanicParams in SHELL_MECHANIC_ADDITIONAL_PARAMETERS.values() for paramName in mechanicParams} - set(_PARAM_VISIBILITY)

def _isEmptyNormalizationAngleValid(cfg, shell):
    vehicle = cfg.vehicle
    return vehicle is not None and shell.intCD in getShellParamsSwitcherModifiedShells(vehicle.descriptor)


class ShellBlockToolTipData(BlocksTooltipData):

    def __init__(self, context):
        super(ShellBlockToolTipData, self).__init__(context, TOOLTIP_TYPE.SHELL)
        self.item = None
        return

    def _invalidateWidth(self, width):
        self._setWidth(max(width, self._getWidth()))

    def _packBlocks(self, *args, **kwargs):
        self._setContentMargin(top=0, left=17, bottom=20, right=0)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        self.item = self.context.buildItem(*args, **kwargs)
        items = super(ShellBlockToolTipData, self)._packBlocks()
        shell = self.item
        statsConfig = self.context.getStatsConfiguration(shell)
        paramsConfig = self.context.getParamsConfiguration(shell)
        valueWidth = 107
        leftPadding = 0
        rightPadding = 20
        lrPaddings = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockTopPadding = -4
        bottomPadding = -5
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=bottomPadding)
        textGap = -2
        vDescr = paramsConfig.vehicle.descriptor if paramsConfig.vehicle is not None else None
        params = params_helper.getParameters(shell, vDescr)
        shellMechanic = self.__getActiveShellMechanic()
        items.append(formatters.packBuildUpBlockData(HeaderBlockConstructor(shell, statsConfig, leftPadding, rightPadding, params).construct(), padding=formatters.packPadding(left=17, right=rightPadding, top=14)))
        if shellMechanic is not None:
            newWidth = _MECHANIC_PARAMS_WIDTH.get(shellMechanic.mechanic, self._getWidth())
            self._invalidateWidth(newWidth)
            items.append(self.__getExtraStatusBlock(shellMechanic))
        statsBlockConstructor = self.__getStatsBlockConstructor(shellMechanic)
        statsBlock = statsBlockConstructor(shell, paramsConfig, valueWidth, shellMechanic, params).construct()
        if statsBlock:
            items.append(formatters.packBuildUpBlockData(statsBlock, padding=blockPadding, gap=textGap))
        priceBlock, invalidWidth = PriceBlockConstructor(shell, statsConfig, 80).construct()
        if priceBlock:
            self._invalidateWidth(_TOOLTIP_NORMAL_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
            items.append(formatters.packBuildUpBlockData(priceBlock, padding=blockPadding, gap=textGap))
        if statsConfig.showCompatibles:
            moduleCompatibles = params_helper.getCompatibles(shell)
            compatibleBlocks = []
            for paramType, paramValue in moduleCompatibles:
                compatibleBlocks.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.menu.moduleInfo.compatible.dyn(paramType)())), desc=text_styles.main(paramValue)))

            compatibleBlocks.append(formatters.packTextBlockData(text=text_styles.stats(backport.text(R.strings.menu.moduleInfo.additionalInfo()))))
            if compatibleBlocks:
                items.append(formatters.packBuildUpBlockData(compatibleBlocks, padding=formatters.packPadding(right=rightPadding, left=leftPadding, bottom=8)))
        basicIsUsedInCalculationsInfoBlock = self.__getBasicIsUsedInCalculationsInfoBlock()
        if basicIsUsedInCalculationsInfoBlock is not None:
            items.append(basicIsUsedInCalculationsInfoBlock)
        if params.get('isBasic') and paramsConfig.showBasic:
            boldText = text_styles.stats(backport.text(R.strings.tooltips.shell.basic.description.bold()))
            items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.standard(backport.text(R.strings.tooltips.shell.basic.description(), bold=boldText)), padding=lrPaddings)], padding=formatters.packPadding(right=rightPadding)))
        return items

    def __getStatsBlockConstructor(self, shellMechanic):
        defaultConstructor = CommonStatsBlockConstructor
        if shellMechanic is None:
            return defaultConstructor
        else:
            paramsConfig = self.context.getParamsConfiguration(self.item)
            vehicle = paramsConfig.vehicle
            return defaultConstructor if vehicle is None else _MECHANIC_PARAMS_CONSTRUCTOR.get(shellMechanic.mechanic, CommonStatsBlockConstructor)

    def __getActiveShellMechanic(self):
        paramsConfig = self.context.getParamsConfiguration(self.item)
        vehicle = paramsConfig.vehicle
        if vehicle is None:
            return
        else:
            mechanics = [ m for m in self.item.getShellMechanicItems(vehicle) if m.mechanic in _SUPPORTED_MECHANICS ]
            if len(mechanics) == 1:
                return mechanics[0]
            if len(mechanics) > 1:
                _logger.error('Multiple supported mechanics found for shell, expected 0 or 1: %s', [ m.mechanic for m in mechanics ])
            return

    def __getExtraStatusBlock(self, mechanicItem):
        mechanicName = mechanicItem.guiName.value
        textPath = _MECHANICS_TEXT_ROOT.dyn(mechanicName)
        text = textPath.description() if textPath.isValid() else ''
        iconPath = R.images.gui.maps.icons.vehicle_hub.mechanics
        iconPath = iconPath.special if mechanicItem.rank == MechanicsRank.GOLD else iconPath
        mechanicIcon = iconPath.x48x48.dyn(mechanicName)
        return formatters.packBuildUpBlockData([formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(backport.text(text)), icon=backport.image(mechanicIcon()), padding=formatters.packPadding(), titleWidth=380, titlePadding=formatters.packPadding(top=6, left=10), iconPadding=formatters.packPadding(top=3, left=-10), verticalAlignment='center')], padding=formatters.packPadding(left=15), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def __getBasicIsUsedInCalculationsInfoBlock(self):
        paramsConfig = self.context.getParamsConfiguration(self.item)
        vehicle = paramsConfig.vehicle
        if vehicle is None:
            return
        elif paramsConfig.showBasicIsUsedinCalculations and hasVehicleDescrMechanic(vehicle.descriptor, VehicleMechanic.LOW_CHARGE_SHOT):
            basicIsUsedForCalculationsText = text_styles.main(backport.text(_MECHANICS_TEXT_ROOT.lowChargeShot.infoBlock()))
            return formatters.packBuildUpBlockData([formatters.packTitleDescParameterWithIconBlockData(title=basicIsUsedForCalculationsText, icon=backport.image(_MECHANICS_IMAGE_ROOT.info()), iconPadding=formatters.packPadding(top=2), titlePadding=formatters.packPadding(left=6))])
        else:
            return


class ShellTooltipBlockConstructor(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, shell, configuration, leftPadding=20, rightPadding=20, params=None):
        self.shell = shell
        self.configuration = configuration
        self.leftPadding = leftPadding
        self.rightPadding = rightPadding
        self._params = params

    def construct(self):
        return NotImplemented


class HeaderBlockConstructor(ShellTooltipBlockConstructor):

    def construct(self):
        shell = self.shell
        formattedParameters = params_formatters.getFormattedParamsList(shell.descriptor, self._params)
        paramName = ModuleTooltipBlockConstructor.CALIBER
        paramValue = dict(formattedParameters).get(paramName)
        shellKind = backport.text(R.strings.item_types.shell.kinds.dyn(shell.type)())
        headerText = formatters.packTitleDescBlock(title=text_styles.highTitle(shell.userName), desc=text_styles.concatStylesToMultiLine(text_styles.main(shellKind), params_formatters.formatParamNameColonValueUnits(paramName=paramName, paramValue=paramValue)), padding=formatters.packPadding(left=-15), descPadding=formatters.packPadding(top=4), gap=-4)
        headerImage = formatters.packImageBlockData(img=shell.getBonusIcon(size='big'), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(right=30, top=-5, bottom=-5))
        return [headerText, headerImage]


class PriceBlockConstructor(ShellTooltipBlockConstructor):

    def __init__(self, shell, configuration, valueWidth):
        super(PriceBlockConstructor, self).__init__(shell, configuration)
        self._valueWidth = valueWidth

    def construct(self):
        block = []
        shell = self.shell
        configuration = self.configuration
        buyPrice = configuration.buyPrice
        sellPrice = configuration.sellPrice
        if buyPrice and sellPrice:
            _logger.error('You are not allowed to use buyPrice and sellPrice at the same time')
            return
        else:
            notEnoughMoney = False
            showDelimiter = False
            shop = self.itemsCache.items.shop
            money = self.itemsCache.items.stats.money
            if buyPrice and shell.buyPrices:
                for itemPrice in shell.buyPrices.iteritems(directOrder=False):
                    if not isItemBuyPriceAvailable(shell, itemPrice, shop) or not itemPrice.price:
                        continue
                    currency = itemPrice.getCurrency()
                    value = itemPrice.price.getSignValue(currency)
                    defValue = itemPrice.defPrice.getSignValue(currency)
                    actionPercent = itemPrice.getActionPrc()
                    needValue = value - money.getSignValue(currency)
                    if needValue > 0:
                        notEnoughMoney = True
                    else:
                        needValue = None
                    if showDelimiter:
                        block.append(formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.tooltips.vehicle.textDelimiter.c_or())), padding=formatters.packPadding(left=81 + self.leftPadding)))
                    block.append(makePriceBlock(value, CURRENCY_SETTINGS.getBuySetting(currency), needValue, defValue if defValue > 0 else None, actionPercent, valueWidth=self._valueWidth, leftPadding=50))
                    showDelimiter = True

            if sellPrice and shell.sellPrices:
                block.append(makePriceBlock(shell.sellPrices.itemPrice.price.credits, CURRENCY_SETTINGS.SELL_PRICE, oldPrice=shell.sellPrices.itemPrice.defPrice.credits, percent=shell.sellPrices.itemPrice.getActionPrc(), valueWidth=self._valueWidth))
            inventoryCount = shell.inventoryCount
            if inventoryCount and configuration.inventoryCount:
                block.append(formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(backport.text(R.strings.tooltips.vehicle.inventoryCount())), value=text_styles.stats(inventoryCount), icon=backport.image(R.images.gui.maps.icons.library.storage_icon()), padding=formatters.packPadding(left=66), titlePadding=formatters.packPadding(left=16), iconPadding=formatters.packPadding(top=-2, left=-2)))
            hasAction = shell.buyPrices.itemPrice.isActionPrice() or shell.sellPrices.itemPrice.isActionPrice()
            return (block, notEnoughMoney or hasAction)


class CommonStatsBlockConstructor(ShellTooltipBlockConstructor):

    def __init__(self, shell, configuration, valueWidth, mechanic, params):
        super(CommonStatsBlockConstructor, self).__init__(shell, configuration, valueWidth, params=params)
        self._valueWidth = valueWidth

    def construct(self):
        block = []
        shell = self.shell
        if shell.isNonPiercingDamageMechanics:
            block.append(formatters.packTitleDescBlock(title=text_styles.neutral(backport.text(R.strings.menu.moduleInfo.nonPiercingDamageLabel()))))
        if not self.configuration.params:
            return block
        else:
            colorScheme = params_formatters.COLORLESS_SCHEME if self.configuration.colorless else params_formatters.BASE_SCHEME
            bottomPadding = formatters.packPadding(bottom=8)
            piercingPowerTable = self._params.pop('piercingPowerTable')
            vehicle = self.configuration.vehicle
            comparator = self._getValueComparator(vehicle and vehicle.descriptor)
            block.append(self._getHeaderBlock(bottomPadding))
            formattedParameters = params_formatters.getFormattedParamsList(shell.descriptor, self._params)
            footNotes = []
            isModernHE = shell.descriptor.type.mechanics == SHELL_MECHANICS_TYPE.MODERN
            if self.configuration.showScreensArmorMultiplier and isModernHE:
                footNotes.append(backport.text(R.strings.menu.moduleInfo.params.footnote.guaranteedDamage()))
            for paramName, paramValue in formattedParameters:
                if self._isSkippedParam(paramName, shell):
                    continue
                value = self._getValueBlock(paramName, comparator, piercingPowerTable, colorScheme) or paramValue
                if value is None:
                    continue
                units = self._applyParamMeta(paramName, piercingPowerTable, footNotes)
                block.append(self._packParamBlock(backport.text(R.strings.menu.moduleInfo.params.dyn(paramName)()), value, units))

            block.extend(self._packFootNotes(footNotes))
            return block

    def _getHeaderBlock(self, bottomPadding):
        return formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.tankCarusel.MainProperty())), padding=bottomPadding)

    def _isSkippedParam(self, paramName, shell):
        if paramName in _MECHANIC_ONLY_PARAMS:
            return True
        else:
            visibilityCheck = _PARAM_VISIBILITY.get(paramName)
            if visibilityCheck is not None:
                paramValue = self._params.get(paramName) if self._params else None
                return not visibilityCheck(self.configuration, shell, paramValue)
            return False

    def _packParamBlock(self, name, value, units):
        return formatters.packTextParameterBlockData(name=text_styles.concatStylesWithSpace(text_styles.main(name), text_styles.standard(units)), value=text_styles.stats(value), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5))

    def _getValueBlock(self, paramName, comparator, piercingPowerTable, colorScheme):
        value = None
        if comparator is not None:
            param = comparator.getExtendedData(paramName)
            value = params_formatters.formatParameter(param.name, param.value, param.state, colorScheme, formatSettings=_SHELL_TOOLTIP_FORMAT_SETTINGS)
        if paramName == 'avgPiercingPower':
            tableData = []
            if isinstance(piercingPowerTable, list):
                for value in self._iteratePiercingPowerTable(piercingPowerTable, comparator, colorScheme):
                    tableData.append(value)

            if tableData:
                value = '%s-%s' % (tableData[0], tableData[-1])
        if paramName == 'screensArmorMultiplier':
            value = backport.text(R.strings.menu.moduleInfo.params.screensArmorMultiplier.value(), multiplier=value)
        return value

    def _applyParamMeta(self, paramName, tableData, footNotes):
        vehicle = self.configuration.vehicle
        units = _ms(params_formatters.measureUnitsForParameter(paramName))
        isPiercingPower = paramName == 'avgPiercingPower'
        isDamageMutable = paramName == 'avgMutableDamage'
        isPenetrationLoss = paramName == PENETRATION_LOSS
        isScreensArmorMultiplier = paramName == 'screensArmorMultiplier'
        if isDamageMutable and vehicle is not None:
            units += _ASTERISK
            minDist = int(DAMAGE_INTERPOLATION_DIST_FIRST)
            maxDist = int(min(vehicle.descriptor.shot.maxDistance, DAMAGE_INTERPOLATION_DIST_LAST))
            if tableData:
                minDist = tableData[0][0]
                maxDist = tableData[-1][0]
            self._addFootNote(footNotes, _ASTERISK + backport.text(R.strings.menu.moduleInfo.params.footnote.piercingDistance(), minDist=minDist, maxDist=maxDist))
        if isPiercingPower:
            units += _ASTERISK
            if tableData:
                self._addFootNote(footNotes, _ASTERISK + backport.text(R.strings.menu.moduleInfo.params.footnote.piercingDistance(), minDist=tableData[0][0], maxDist=tableData[-1][0]))
            else:
                self._addFootNote(footNotes, _ASTERISK + backport.text(R.strings.menu.moduleInfo.params.footnote.noPiercingDistance()))
        if isPenetrationLoss or isScreensArmorMultiplier:
            asterisks = _ASTERISK * 2
            units += asterisks
            self._addFootNote(footNotes, asterisks + backport.text(R.strings.menu.moduleInfo.params.footnote.dyn(paramName)()))
        return units

    @staticmethod
    def _addFootNote(container, note):
        if note not in container:
            container.append(note)

    @staticmethod
    def _packFootNotes(footNotes):
        blocks = []
        padding = formatters.packPadding(top=8, right=12)
        for note in footNotes:
            blocks.append(formatters.packTitleDescBlock(title=text_styles.standard(note), padding=padding))
            padding = formatters.packPadding(top=-4, right=12)

        return blocks

    @staticmethod
    def _iteratePiercingPowerTable(table, comparator, colorScheme):
        if comparator is not None:
            extendedTable = comparator.getExtendedData('piercingPowerTable')
            for (_, value), (_, valueState) in zip(extendedTable.value, extendedTable.state):
                fmtValue = params_formatters.formatParameter('piercingPower', value, valueState, colorScheme, formatSettings=_SHELL_TOOLTIP_FORMAT_SETTINGS)
                yield fmtValue

        else:
            for _, value in table:
                yield params_formatters.formatParameter('piercingPower', value, formatSettings=_SHELL_TOOLTIP_FORMAT_SETTINGS)

        return

    def _getValueComparator(self, vDescr):
        return params_helper.shellComparator(self.shell, vDescr)


class ICompareStrategy(object):

    @staticmethod
    def resolveDescriptors(vDescr):
        raise NotImplementedError

    @staticmethod
    def buildComparators(shell, vDescr):
        raise NotImplementedError


class _LowChargeShotCompareStrategy(ICompareStrategy):

    @staticmethod
    def resolveDescriptors(vDescr):
        return (vDescr.defaultVehicleDescr, vDescr.siegeVehicleDescr)

    @staticmethod
    def buildComparators(shell, vDescr):
        basicDescr, modifiedDescr = _LowChargeShotCompareStrategy.resolveDescriptors(vDescr)
        leftComparator = params_helper.shellComparator(shell, basicDescr)
        rightComparator = params_helper.shellComparator(shell, modifiedDescr)
        return (leftComparator, rightComparator)


class _ShellParamsSwitcherCompareStrategy(ICompareStrategy):

    @staticmethod
    def resolveDescriptors(vDescr):
        return (vDescr.defaultVehicleDescr, vDescr.siegeVehicleDescr)

    @staticmethod
    def buildComparators(shell, vDescr):
        descrs = (vDescr, vDescr.defaultVehicleDescr, vDescr.siegeVehicleDescr)
        leftComparator = params_helper.shellModesComparator(shell, descrs, isBase=True)
        rightComparator = None
        modifiedShot = params_helper.getSiegeDescrShot(vDescr, shell)
        if modifiedShot is not None:
            rightComparator = params_helper.shellModesComparator(shell, descrs, itemDescr=modifiedShot.shell)
        return (leftComparator, rightComparator)


class _ShellCalibrationCompareStrategy(ICompareStrategy):

    @staticmethod
    def resolveDescriptors(vDescr):
        return (getVehicleDescriptorWithoutMechanics(vDescr, VehicleMechanic.SHELL_CALIBRATION.value), vDescr)

    @staticmethod
    def buildComparators(shell, vDescr):
        basicDescr, modifiedDescr = _ShellCalibrationCompareStrategy.resolveDescriptors(vDescr)
        leftComparator = params_helper.shellComparator(shell, basicDescr)
        rightComparator = params_helper.shellComparator(shell, modifiedDescr)
        return (leftComparator, rightComparator)


class _ShellParamsBustleFeedCompareStrategy(ICompareStrategy):

    @staticmethod
    def resolveDescriptors(vDescr):
        defaultVehicleDescr = vDescr.defaultVehicleDescr
        basicDescr = getVehicleDescriptorWithoutMechanics(defaultVehicleDescr, VehicleMechanic.BUSTLE_FEED.value)
        return (basicDescr, defaultVehicleDescr)

    @staticmethod
    def buildComparators(shell, vDescr):
        basicDescr, modifiedDescr = _ShellParamsBustleFeedCompareStrategy.resolveDescriptors(vDescr)
        descrs = (vDescr, basicDescr, modifiedDescr)
        leftComparator = params_helper.shellModesComparator(shell, descrs, isBase=True)
        rightComparator = params_helper.shellModesComparator(shell, descrs)
        return (leftComparator, rightComparator)


class TwoColumnsStatsBlockConstructor(CommonStatsBlockConstructor):
    _MECHANIC_DESCRIPTOR_RESOLVERS = {VehicleMechanic.LOW_CHARGE_SHOT: _LowChargeShotCompareStrategy,
     VehicleMechanic.SHELL_PARAMS_SWITCHER: _ShellParamsSwitcherCompareStrategy,
     VehicleMechanic.SHELL_CALIBRATION: _ShellCalibrationCompareStrategy,
     VehicleMechanic.BUSTLE_FEED: _ShellParamsBustleFeedCompareStrategy}

    def __init__(self, shell, configuration, valueWidth, mechanic, params=None):
        super(TwoColumnsStatsBlockConstructor, self).__init__(shell, configuration, valueWidth, mechanic, params)
        self._mechanic = mechanic
        strategy = self._MECHANIC_DESCRIPTOR_RESOLVERS.get(mechanic.mechanic)
        if strategy is not None:
            vehDescr = self.configuration.vehicle.descriptor
            self._leftComparator, self._rightComparator = strategy.buildComparators(shell, vehDescr)
            leftDescr, rightDescr = strategy.resolveDescriptors(vehDescr)
            self._mechanicParameters = [(None, params_helper.getParameters(shell, leftDescr)), (None, params_helper.getParameters(shell, rightDescr))]
        else:
            self._leftComparator, self._rightComparator = (None, None)
            self._mechanicParameters = []
        return

    def _isSkippedParam(self, paramName, shell):
        mechanicParams = SHELL_MECHANIC_ADDITIONAL_PARAMETERS.get(self._mechanic.mechanic, {})
        validator = mechanicParams.get(paramName)
        return not validator(paramName, self._mechanicParameters) if validator is not None else super(TwoColumnsStatsBlockConstructor, self)._isSkippedParam(paramName, shell)

    def _getValueComparator(self, vDescr, dropMechanic=True):
        return self._leftComparator if self._leftComparator is not None else super(TwoColumnsStatsBlockConstructor, self)._getValueComparator(vDescr)

    def _getValueBlock(self, paramName, comparator, piercingPowerTable, colorScheme):
        rightComparator = self._rightComparator
        if rightComparator is None:
            return
        else:
            leftValue = super(TwoColumnsStatsBlockConstructor, self)._getValueBlock(paramName, comparator, piercingPowerTable, colorScheme)
            if leftValue is None:
                return
            rightValue = super(TwoColumnsStatsBlockConstructor, self)._getValueBlock(paramName, rightComparator, piercingPowerTable, colorScheme)
            return None if rightValue is None else (leftValue, rightValue)

    def _getHeaderBlock(self, bottomPadding):
        mechanicName = self._mechanic.guiName.value
        headerRoot = _MECHANICS_TEXT_ROOT.dyn(mechanicName).paramsHeader
        iconRoot = _MECHANICS_IMAGE_ROOT.dyn(mechanicName)
        mechanicSubtype = self._mechanic.mechanicSubtype
        leftIconPath = iconRoot.dyn(mechanicSubtype['basic'] if mechanicSubtype else 'basic')
        rightIconPath = iconRoot.dyn(mechanicSubtype['modified'] if mechanicSubtype else 'modified')
        return formatters.packTextParameterTwoColWithIconsBlockData(name='', leftValue=text_styles.middleTitle(backport.text(headerRoot.basic())), leftIcon=backport.image(leftIconPath()) if leftIconPath.isValid() else '', rightValue=text_styles.middleTitle(backport.text(headerRoot.specific())), rightIcon=backport.image(rightIconPath()) if rightIconPath.isValid() else '', valueWidth=self._valueWidth, valueGap=15, iconPadding=formatters.packPadding(top=2, right=7), padding=formatters.packPadding(bottom=8))

    def _packParamBlock(self, name, value, units):
        return formatters.packTextParameterTwoColBlockData(name=text_styles.concatStylesWithSpace(text_styles.main(name), text_styles.standard(units)), leftValue=text_styles.stats(value[0]), rightValue=text_styles.stats(value[1]), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-3), gap=20, valueGap=17)


class ShellCalibrationStatsBlockConstructor(TwoColumnsStatsBlockConstructor):

    def _getHeaderBlock(self, bottomPadding):
        headerRoot = _MECHANICS_TEXT_ROOT.dyn(self._mechanic.guiName.value).paramsHeader
        return formatters.packTextParameterBlockData(name='', value=text_styles.middleTitle(backport.text(headerRoot())), valueWidth=self._valueWidth, padding=formatters.packPadding(bottom=8, left=-34))

    def _packParamBlock(self, name, value, units):
        iconRoot = _MECHANICS_IMAGE_ROOT.dyn(self._mechanic.guiName.value)
        iconPath = iconRoot.calibrated
        if isinstance(value, (list, tuple)) and value[0] != value[1]:
            value = text_styles.stats('%s / %s' % (value[0], value[1]))
            img = formatters.getImage(image(iconPath()), width=16, height=16, vspace=-2)
            return formatters.packTextParameterBlockData(name=text_styles.concatStylesWithSpace(text_styles.main(name), text_styles.standard(units)), value=text_styles.concatStylesWithSpace(value, img), valueWidth=self._valueWidth + 50, padding=formatters.packPadding(left=0))
        value = text_styles.stats(value[0])
        return formatters.packTextParameterBlockData(name=text_styles.concatStylesWithSpace(text_styles.main(name), text_styles.standard(units)), value=value, valueWidth=self._valueWidth, padding=formatters.packPadding(left=50))


_MECHANIC_PARAMS_CONSTRUCTOR = {VehicleMechanic.LOW_CHARGE_SHOT: TwoColumnsStatsBlockConstructor,
 VehicleMechanic.SHELL_PARAMS_SWITCHER: TwoColumnsStatsBlockConstructor,
 VehicleMechanic.SHELL_CALIBRATION: ShellCalibrationStatsBlockConstructor,
 VehicleMechanic.BUSTLE_FEED: TwoColumnsStatsBlockConstructor}
