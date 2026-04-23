# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/shell.py
from constants import DAMAGE_INTERPOLATION_DIST_LAST, DAMAGE_INTERPOLATION_DIST_FIRST, SHELL_MECHANICS_TYPE
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items.gui_item_economics import isItemBuyPriceAvailable
from gui.shared.items_parameters import params_helper, formatters as params_formatters
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import makePriceBlock, CURRENCY_SETTINGS, BlocksTooltipData
from gui.shared.tooltips.module import ModuleTooltipBlockConstructor
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.utils import getVehicleDescriptorWithoutMechanics
from skeletons.gui.shared import IItemsCache
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import hasVehicleDescrMechanic
_ASTERISK = '*'
_TOOLTIP_MIN_WIDTH = 380
_TOOLTIP_MAX_WIDTH = 420
_LOW_CHARGE_SHOT_TOOLTIP_WIDTH = 500
_MECHANICS_TEXT_ROOT = R.strings.tooltips.shell.mechanics
_MECHANICS_IMAGE_ROOT = R.images.gui.maps.icons.tooltip.mechanics

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
        items.append(formatters.packBuildUpBlockData(HeaderBlockConstructor(shell, statsConfig, leftPadding, rightPadding, params).construct(), padding=formatters.packPadding(left=17, right=rightPadding, top=14)))
        extraStatus = self.__getExtraStatusBlock()
        if extraStatus is not None:
            items.append(extraStatus)
        statsBlock = self._getStatsBlockConstructor()(shell, paramsConfig, valueWidth, params).construct()
        if statsBlock:
            items.append(formatters.packBuildUpBlockData(statsBlock, padding=blockPadding, gap=textGap))
        priceBlock, invalidWidth = PriceBlockConstructor(shell, statsConfig, 80).construct()
        if priceBlock:
            self._invalidateWidth(_TOOLTIP_MAX_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
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

    def _getStatsBlockConstructor(self):
        paramsConfig = self.context.getParamsConfiguration(self.item)
        vehicle = paramsConfig.vehicle
        if vehicle is not None:
            if hasVehicleDescrMechanic(vehicle.descriptor, VehicleMechanic.LOW_CHARGE_SHOT):
                self._invalidateWidth(_LOW_CHARGE_SHOT_TOOLTIP_WIDTH)
                return TwoColumnsStatsBlockConstructor
        return CommonStatsBlockConstructor

    def __getExtraStatusBlock(self):
        paramsConfig = self.context.getParamsConfiguration(self.item)
        vehicle = paramsConfig.vehicle
        if vehicle is None:
            return
        elif hasVehicleDescrMechanic(vehicle.descriptor, VehicleMechanic.LOW_CHARGE_SHOT):
            specialModeText = text_styles.stats(backport.text(_MECHANICS_TEXT_ROOT.lowChargeShot.description.specialMode()))
            affectedParamsText = text_styles.stats(backport.text(_MECHANICS_TEXT_ROOT.lowChargeShot.description.affectedParams()))
            mechanicsDescriptionText = text_styles.main(backport.text(_MECHANICS_TEXT_ROOT.lowChargeShot.description())).format(specialMode=specialModeText, affectedParams=affectedParamsText)
            return formatters.packBuildUpBlockData([formatters.packTitleDescParameterWithIconBlockData(title=mechanicsDescriptionText, icon=backport.image(_MECHANICS_IMAGE_ROOT.lowChargeShot.ability_48x48()), padding=formatters.packPadding(), titleWidth=380, titlePadding=formatters.packPadding(top=6, left=10), iconPadding=formatters.packPadding(top=3, left=-10))], padding=formatters.packPadding(left=15), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)
        else:
            return

    def __getBasicIsUsedInCalculationsInfoBlock(self):
        paramsConfig = self.context.getParamsConfiguration(self.item)
        vehicle = paramsConfig.vehicle
        if vehicle is None:
            return
        elif paramsConfig.showBasicIsUsedinCalculations and hasVehicleDescrMechanic(vehicle.descriptor, VehicleMechanic.LOW_CHARGE_SHOT):
            basicIsUsedForCalculationsText = text_styles.main(backport.text(_MECHANICS_TEXT_ROOT.lowChargeShot.infoBlock()))
            return formatters.packBuildUpBlockData([formatters.packTitleDescParameterWithIconBlockData(title=basicIsUsedForCalculationsText, icon=backport.image(_MECHANICS_IMAGE_ROOT.lowChargeShot.info()), iconPadding=formatters.packPadding(top=2), titlePadding=formatters.packPadding(left=6))])
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
            LOG_ERROR('You are not allowed to use buyPrice and sellPrice at the same time')
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

    def __init__(self, shell, configuration, valueWidth, params):
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
                footNotes.append(backport.text(R.strings.menu.moduleInfo.params.guaranteedDamage.footnote()))
            for paramName, paramValue in formattedParameters:
                if paramName == ModuleTooltipBlockConstructor.CALIBER:
                    continue
                if paramName == 'avgDamage' and shell.isDamageMutable():
                    continue
                if paramName == 'normalizationAngle' and not self.configuration.showNormalizationAngle:
                    continue
                if paramName == 'ricochetAngle' and not self.configuration.showReboundAngle:
                    continue
                if paramName == 'penetrationLoss' and not self.configuration.showPenetrationLoss:
                    continue
                if paramName == 'screensArmorMultiplier' and not self.configuration.showScreensArmorMultiplier:
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

    def _packParamBlock(self, name, value, units):
        return formatters.packTextParameterBlockData(name=text_styles.concatStylesWithSpace(text_styles.main(name), text_styles.standard(units)), value=text_styles.stats(value), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5))

    def _getValueBlock(self, paramName, comparator, piercingPowerTable, colorScheme):
        value = None
        if comparator is not None:
            value = params_formatters.colorizedFormatParameter(comparator.getExtendedData(paramName), colorScheme)
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
        isPenetrationLoss = paramName == 'penetrationLoss'
        isScreensArmorMultiplier = paramName == 'screensArmorMultiplier'
        if isDamageMutable and vehicle is not None:
            units += _ASTERISK
            minDist = int(DAMAGE_INTERPOLATION_DIST_FIRST)
            maxDist = int(min(vehicle.descriptor.shot.maxDistance, DAMAGE_INTERPOLATION_DIST_LAST))
            if tableData:
                minDist = tableData[0][0]
                maxDist = tableData[-1][0]
            self._addFootNote(footNotes, _ASTERISK + backport.text(R.strings.menu.moduleInfo.params.piercingDistance.footnote(), minDist=minDist, maxDist=maxDist))
        if isPiercingPower:
            units += _ASTERISK
            if tableData:
                self._addFootNote(footNotes, _ASTERISK + backport.text(R.strings.menu.moduleInfo.params.piercingDistance.footnote(), minDist=tableData[0][0], maxDist=tableData[-1][0]))
            else:
                self._addFootNote(footNotes, _ASTERISK + backport.text(R.strings.menu.moduleInfo.params.noPiercingDistance.footnote()))
        if isPenetrationLoss or isScreensArmorMultiplier:
            asterisks = _ASTERISK * 2
            units += asterisks
            self._addFootNote(footNotes, asterisks + backport.text(R.strings.menu.moduleInfo.params.dyn(paramName).footnote()))
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
                fmtValue = params_formatters.formatParameter('piercingPower', value, valueState, colorScheme)
                yield fmtValue

        else:
            for value in table:
                yield params_formatters.formatParameter('piercingPower', value)

        return

    def _getValueComparator(self, vDescr):
        return params_helper.shellComparator(self.shell, vDescr)


class TwoColumnsStatsBlockConstructor(CommonStatsBlockConstructor):

    def __init__(self, shell, configuration, valueWidth, params=None):
        super(TwoColumnsStatsBlockConstructor, self).__init__(shell, configuration, valueWidth, params)
        self.__modifiedComparator = self._getValueComparator(self.configuration.vehicle.descriptor, dropMechanic=False)

    def _getValueBlock(self, paramName, comparator, piercingPowerTable, colorScheme):
        modifiedComparator = self.__modifiedComparator
        if modifiedComparator is None:
            return
        else:
            leftValue = super(TwoColumnsStatsBlockConstructor, self)._getValueBlock(paramName, comparator, piercingPowerTable, colorScheme)
            if leftValue is None:
                return
            rightValue = super(TwoColumnsStatsBlockConstructor, self)._getValueBlock(paramName, modifiedComparator, piercingPowerTable, colorScheme)
            return None if rightValue is None else (leftValue, rightValue)

    def _getHeaderBlock(self, bottomPadding):
        return formatters.packTextParameterTwoColWithIconBlockData(leftText=text_styles.middleTitle(backport.text(_MECHANICS_TEXT_ROOT.lowChargeShot.paramsHeader.basic())), rightText=text_styles.middleTitle(backport.text(_MECHANICS_TEXT_ROOT.lowChargeShot.paramsHeader.specific())), icon=backport.image(_MECHANICS_IMAGE_ROOT.lowChargeShot.ability_20x20()), valueWidth=self._valueWidth, padding=formatters.packPadding(bottom=8), value2Gap=15, iconPadding=formatters.packPadding(top=2, right=7))

    def _packParamBlock(self, name, value, units):
        return formatters.packTextParameterTwoColBlockData(name=text_styles.concatStylesWithSpace(text_styles.main(name), text_styles.standard(units)), value=text_styles.stats(value[0]), value2=text_styles.stats(value[1]), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-3), gap=20, value2Gap=17)

    def _getValueComparator(self, vDescr, dropMechanic=True):
        return super(TwoColumnsStatsBlockConstructor, self)._getValueComparator(getVehicleDescriptorWithoutMechanics(vDescr, VehicleMechanic.LOW_CHARGE_SHOT.value) if dropMechanic else vDescr)
