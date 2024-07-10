# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/shell.py
from constants import DAMAGE_INTERPOLATION_DIST_LAST, DAMAGE_INTERPOLATION_DIST_FIRST
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items.gui_item_economics import isItemBuyPriceAvailable
from gui.shared.items_parameters import params_helper, formatters as params_formatters, NO_DATA
from gui.shared.tooltips import formatters
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from gui.shared.tooltips.module import ModuleTooltipBlockConstructor
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache
_TOOLTIP_MIN_WIDTH = 380
_TOOLTIP_MAX_WIDTH = 420
_ASTERISK = '*'

class ShellBlockToolTipData(BlocksTooltipData):

    def __init__(self, context):
        super(ShellBlockToolTipData, self).__init__(context, TOOLTIP_TYPE.SHELL)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=20, right=0)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        return

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        items = super(ShellBlockToolTipData, self)._packBlocks()
        shell = self.item
        statsConfig = self.context.getStatsConfiguration(shell)
        paramsConfig = self.context.getParamsConfiguration(shell)
        valueWidth = 107
        leftPadding = 20
        rightPadding = 20
        lrPaddings = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockTopPadding = -4
        bottomPadding = -5
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=bottomPadding)
        textGap = -2
        vDescr = paramsConfig.vehicle.descriptor if paramsConfig.vehicle is not None else None
        params = params_helper.getParameters(shell, vDescr)
        items.append(formatters.packBuildUpBlockData(HeaderBlockConstructor(shell, statsConfig, leftPadding, rightPadding, params).construct(), padding=formatters.packPadding(left=35, right=rightPadding, top=14)))
        statsBlock = CommonStatsBlockConstructor(shell, paramsConfig, valueWidth, params).construct()
        if statsBlock:
            items.append(formatters.packBuildUpBlockData(statsBlock, padding=blockPadding, gap=textGap))
        priceBlock, invalidWidth = PriceBlockConstructor(shell, statsConfig, 80).construct()
        if priceBlock:
            self._setWidth(_TOOLTIP_MAX_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
            items.append(formatters.packBuildUpBlockData(priceBlock, padding=blockPadding, gap=textGap))
        if statsConfig.showCompatibles:
            moduleCompatibles = params_helper.getCompatibles(shell)
            compatibleBlocks = []
            for paramType, paramValue in moduleCompatibles:
                compatibleBlocks.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.menu.moduleInfo.compatible.dyn(paramType)())), desc=text_styles.main(paramValue)))

            compatibleBlocks.append(formatters.packTextBlockData(text=text_styles.stats(backport.text(R.strings.menu.moduleInfo.additionalInfo()))))
            if compatibleBlocks:
                items.append(formatters.packBuildUpBlockData(compatibleBlocks, padding=formatters.packPadding(left=leftPadding, bottom=8)))
        if params.get('isBasic'):
            boldText = text_styles.stats(backport.text(R.strings.tooltips.shell.basic.description.bold()))
            items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.standard(backport.text(R.strings.tooltips.shell.basic.description(), bold=boldText)), padding=lrPaddings)], padding=formatters.packPadding(right=rightPadding)))
        return items


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
                    block.append(makePriceBlock(value, CURRENCY_SETTINGS.getBuySetting(currency), needValue, defValue if defValue > 0 else None, actionPercent, valueWidth=self._valueWidth))
                    showDelimiter = True

            if sellPrice and shell.sellPrices:
                block.append(makePriceBlock(shell.sellPrices.itemPrice.price.credits, CURRENCY_SETTINGS.SELL_PRICE, oldPrice=shell.sellPrices.itemPrice.defPrice.credits, percent=shell.sellPrices.itemPrice.getActionPrc(), valueWidth=self._valueWidth))
            inventoryCount = shell.inventoryCount
            if inventoryCount:
                block.append(formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(backport.text(R.strings.tooltips.vehicle.inventoryCount())), value=text_styles.stats(inventoryCount), icon=backport.image(R.images.gui.maps.icons.library.storage_icon()), padding=formatters.packPadding(left=76), titlePadding=formatters.packPadding(left=-2), iconPadding=formatters.packPadding(top=-2, left=-2)))
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
        if self.configuration.params:
            bottom = 8
            bottomPadding = formatters.packPadding(bottom=bottom)
            comparator = params_helper.shellComparator(shell, self.configuration.vehicle)
            piercingPowerTable = self._params.pop('piercingPowerTable')
            colorScheme = params_formatters.COLORLESS_SCHEME if self.configuration.colorless else params_formatters.BASE_SCHEME
            tableData = []
            if isinstance(piercingPowerTable, list):
                for distance, value in self.__iteratePiercingPowerTable(piercingPowerTable, comparator, colorScheme):
                    tableData.append((value, distance))

            block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.tankCarusel.MainProperty())), padding=bottomPadding))
            formattedParameters = params_formatters.getFormattedParamsList(shell.descriptor, self._params)
            showDistanceAsterisk = False
            footNotes = []
            for paramName, paramValue in formattedParameters:
                if paramName == ModuleTooltipBlockConstructor.CALIBER:
                    continue
                if paramName == 'avgDamage' and shell.isDamageMutable():
                    continue
                if comparator is not None:
                    paramValue = params_formatters.colorizedFormatParameter(comparator.getExtendedData(paramName), colorScheme)
                if paramValue is not None:
                    paramUnits = _ms(params_formatters.measureUnitsForParameter(paramName))
                    isPiercingPower = paramName == 'avgPiercingPower'
                    isDamageMutable = paramName == 'avgMutableDamage'
                    vehicle = self.configuration.vehicle
                    if isDamageMutable and vehicle is not None:
                        showDistanceAsterisk = True
                        paramUnits += _ASTERISK
                        minDist = int(DAMAGE_INTERPOLATION_DIST_FIRST)
                        maxDist = int(min(vehicle.descriptor.shot.maxDistance, DAMAGE_INTERPOLATION_DIST_LAST))
                        if tableData:
                            minDist = tableData[0][1]
                            maxDist = tableData[-1][1]
                        footNotes.append(_ASTERISK + backport.text(R.strings.menu.moduleInfo.params.piercingDistance.footnote(), minDist=minDist, maxDist=maxDist))
                    if isPiercingPower and piercingPowerTable != NO_DATA:
                        if tableData:
                            paramValue = '%s-%s' % (tableData[0][0], tableData[-1][0])
                            paramUnits += _ASTERISK
                            if not showDistanceAsterisk:
                                footNotes.append(_ASTERISK + backport.text(R.strings.menu.moduleInfo.params.piercingDistance.footnote(), minDist=tableData[0][1], maxDist=tableData[-1][1]))
                        else:
                            asterisks = _ASTERISK if not showDistanceAsterisk else _ASTERISK * 2
                            paramUnits += asterisks
                            footNotes.append(asterisks + backport.text(R.strings.menu.moduleInfo.params.noPiercingDistance.footnote()))
                    block.append(self._packParameterBlock(backport.text(R.strings.menu.moduleInfo.params.dyn(paramName)()), paramValue, paramUnits))

            notePadding = formatters.packPadding(top=8)
            for title in footNotes:
                block.append(formatters.packTitleDescBlock(title=text_styles.standard(title), padding=notePadding))
                notePadding = formatters.packPadding(top=0)

        return block

    def _packParameterBlock(self, name, value, measureUnits):
        return formatters.packTextParameterBlockData(name=text_styles.concatStylesWithSpace(text_styles.main(name), text_styles.standard(measureUnits)), value=text_styles.stats(value), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5))

    @staticmethod
    def __iteratePiercingPowerTable(table, comparator, colorScheme):
        if comparator is not None:
            extendedTable = comparator.getExtendedData('piercingPowerTable')
            for (distance, value), (_, valueState) in zip(extendedTable.value, extendedTable.state):
                fmtValue = params_formatters.formatParameter('piercingPower', value, valueState, colorScheme)
                yield (distance, fmtValue)

        else:
            for distance, value in table:
                yield (distance, params_formatters.formatParameter('piercingPower', value))

        return
