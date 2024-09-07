# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/shell.py
from itertools import izip
from debug_utils import LOG_ERROR
from constants import SHELL_TYPES
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items.gui_item_economics import isItemBuyPriceAvailable
from gui.shared.items_parameters import params_helper, formatters as params_formatters, NO_DATA, MAX_RELATIVE_VALUE
from gui.shared.tooltips import formatters
from gui.shared.tooltips import getComplexStatus, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from gui.shared.tooltips.module import ModuleTooltipBlockConstructor
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache
_TOOLTIP_MIN_WIDTH = 380
_TOOLTIP_MAX_WIDTH = 420
_AUTOCANNON_SHOT_DISTANCE = 400
_ASTERISK = '*'

class ShellBlockToolTipData(BlocksTooltipData):

    def __init__(self, context, basicDataAllowed=True):
        super(ShellBlockToolTipData, self).__init__(context, TOOLTIP_TYPE.SHELL)
        self.__basicDataAllowed = basicDataAllowed
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
        statusConfig = self.context.getStatusConfiguration(shell)
        valueWidth = 107
        leftPadding = 20
        rightPadding = 20
        lrPaddings = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockTopPadding = -4
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding)
        textGap = -2
        vDescr = paramsConfig.vehicle.descriptor if paramsConfig.vehicle is not None else None
        params = params_helper.getParameters(shell, vDescr)
        showBasicData = self.__basicDataAllowed and params['isBasic']
        items.append(formatters.packBuildUpBlockData(HeaderBlockConstructor(shell, statsConfig, leftPadding, rightPadding, params).construct(), padding=formatters.packPadding(left=35, right=rightPadding, top=14)))
        priceBlock, invalidWidth = PriceBlockConstructor(shell, statsConfig, 80).construct()
        if priceBlock:
            self._setWidth(_TOOLTIP_MAX_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
            items.append(formatters.packBuildUpBlockData(priceBlock, padding=blockPadding, gap=textGap))
        statusBlock = StatusBlockConstructor(shell, statusConfig).construct()
        if self.__basicDataAllowed:
            statsBlock = CommonStatsBlockConstructor(shell, paramsConfig, valueWidth, params).construct()
        else:
            statsBlock = _AdvancedCommonStatsBlockConstructior(shell, paramsConfig, valueWidth, params).construct()
        bottomPadding = 4 if statusBlock or showBasicData else 0
        if statsBlock:
            items.append(formatters.packBuildUpBlockData(statsBlock, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=bottomPadding), gap=textGap))
        if statusBlock:
            items.append(formatters.packBuildUpBlockData(statusBlock, padding=lrPaddings))
        if statsConfig.showCompatibles:
            moduleCompatibles = params_helper.getCompatibles(shell)
            compatibleBlocks = []
            for paramType, paramValue in moduleCompatibles:
                compatibleBlocks.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(_ms(MENU.moduleinfo_compatible(paramType))), desc=text_styles.main(paramValue)))

            compatibleBlocks.append(formatters.packTextBlockData(text=text_styles.stats(_ms(MENU.MODULEINFO_ADDITIONALINFO))))
            if compatibleBlocks:
                items.append(formatters.packBuildUpBlockData(compatibleBlocks, padding=formatters.packPadding(left=leftPadding, bottom=8)))
        if showBasicData:
            shot = _ms(ITEM_TYPES.ALTSHOT_NAME if shell.type == SHELL_TYPES.FLAME else ITEM_TYPES.SHOT_NAME).lower()
            boldText = text_styles.neutral(_ms(TOOLTIPS.SHELL_BASIC_DESCRIPTION_BOLD, shot=shot))
            items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.standard(_ms(TOOLTIPS.SHELL_BASIC_DESCRIPTION, bold=boldText, shot=shot)), padding=lrPaddings)], padding=formatters.packPadding(right=rightPadding)))
        return items


class ShellBlockToolTipDataWithBasic(ShellBlockToolTipData):

    def __init__(self, context):
        super(ShellBlockToolTipDataWithBasic, self).__init__(context, basicDataAllowed=True)


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
    DEFAULT_FORMATTER = 'default'

    def construct(self):
        shell = self.shell
        formattedParameters = params_formatters.getFormattedParamsList(shell.descriptor, self._params)
        paramName = ModuleTooltipBlockConstructor.CALIBER
        paramValue = dict(formattedParameters).get(paramName)
        formatterType = shell.type if shell.type in _PARAMS_FORMATTERS_BY_KIND else self.DEFAULT_FORMATTER
        headerText = formatters.packTitleDescBlock(title=text_styles.highTitle(shell.userName), desc=text_styles.concatStylesToMultiLine(text_styles.main(backport.text(R.strings.item_types.shell.kinds.dyn(shell.type)())), _PARAMS_FORMATTERS_BY_KIND[formatterType](paramName, paramValue)), padding=formatters.packPadding(left=-15), descPadding=formatters.packPadding(top=4), gap=-4)
        headerImage = formatters.packImageBlockData(img=shell.getBonusIcon(size='big'), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(right=30, top=-5, bottom=-5))
        return [headerText, headerImage]

    @staticmethod
    def emptyFormatter(paramName, paramValue):
        pass

    @staticmethod
    def formatParam(paramName, paramValue):
        return params_formatters.formatParamNameColonValueUnits(paramName=paramName, paramValue=paramValue)


_PARAMS_FORMATTERS_BY_KIND = {SHELL_TYPES.FLAME: HeaderBlockConstructor.emptyFormatter,
 HeaderBlockConstructor.DEFAULT_FORMATTER: HeaderBlockConstructor.formatParam}

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
                        block.append(formatters.packTextBlockData(text=text_styles.standard(TOOLTIPS.VEHICLE_TEXTDELIMITER_OR), padding=formatters.packPadding(left=81 + self.leftPadding)))
                    block.append(makePriceBlock(value, CURRENCY_SETTINGS.getBuySetting(currency), needValue, defValue if defValue > 0 else None, actionPercent, valueWidth=self._valueWidth))
                    showDelimiter = True

            if sellPrice and shell.sellPrices:
                block.append(makePriceBlock(shell.sellPrices.itemPrice.price.credits, CURRENCY_SETTINGS.SELL_PRICE, oldPrice=shell.sellPrices.itemPrice.defPrice.credits, percent=shell.sellPrices.itemPrice.getActionPrc(), valueWidth=self._valueWidth))
            inventoryCount = shell.inventoryCount
            if inventoryCount:
                block.append(formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(TOOLTIPS.VEHICLE_INVENTORYCOUNT), value=text_styles.stats(inventoryCount), icon=RES_ICONS.MAPS_ICONS_LIBRARY_STORAGE_ICON, padding=formatters.packPadding(left=76), titlePadding=formatters.packPadding(left=-2), iconPadding=formatters.packPadding(top=-2, left=-2)))
            hasAction = shell.buyPrices.itemPrice.isActionPrice() or shell.sellPrices.itemPrice.isActionPrice()
            return (block, notEnoughMoney or hasAction)


class SimplifiedStatsBlockConstructor(ShellTooltipBlockConstructor):

    def __init__(self, shell, configuration, params):
        super(SimplifiedStatsBlockConstructor, self).__init__(shell, configuration, params=params)

    def construct(self):
        block = []
        if self.configuration.params:
            comparator = params_helper.shellOnVehicleComparator(self.shell, self.configuration.vehicle)
            stockParams = params_helper.getParameters(self.itemsCache.items.getStockVehicle(self.configuration.vehicle.intCD))
            for parameter in params_formatters.getRelativeDiffParams(comparator):
                delta = parameter.state[1]
                value = parameter.value
                if delta > 0:
                    value -= delta
                block.append(formatters.packStatusDeltaBlockData(title=text_styles.middleTitle(MENU.tank_params(parameter.name)), valueStr=params_formatters.simplifiedDeltaParameter(parameter), statusBarData={'value': value,
                 'delta': delta,
                 'minValue': 0,
                 'markerValue': stockParams.get(parameter.name, value),
                 'maxValue': max(MAX_RELATIVE_VALUE, value + delta),
                 'useAnim': False}, padding=formatters.packPadding(left=75)))

        return block


class _BaseCommonStatsBlockConstructor(ShellTooltipBlockConstructor):

    def __init__(self, shell, configuration, valueWidth, params):
        super(_BaseCommonStatsBlockConstructor, self).__init__(shell, configuration, params=params)
        self._valueWidth = valueWidth

    def _packParameterBlock(self, name, value, measureUnits):
        return formatters.packTextParameterBlockData(name=text_styles.concatStylesWithSpace(text_styles.main(name), text_styles.standard(measureUnits)), value=text_styles.stats(value), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5))


class _AdvancedCommonStatsBlockConstructior(_BaseCommonStatsBlockConstructor):

    def construct(self):
        block = []
        if self.configuration.params:
            bottom = 8
            bottomPadding = formatters.packPadding(bottom=bottom)
            shell = self.shell
            comparator = params_helper.shellOnVehicleComparator(shell, self.configuration.vehicle)
            isDistanceDependent = self._params.pop('piercingPowerTable') is not None
            formattedParameters = params_formatters.getFormattedParamsList(shell.descriptor, self._params)
            block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(_ms(TOOLTIPS.TANKCARUSEL_MAINPROPERTY)), padding=bottomPadding))
            for paramName, paramValue in formattedParameters:
                if paramName == ModuleTooltipBlockConstructor.CALIBER:
                    continue
                if comparator is not None:
                    paramValue = params_formatters.colorizedFormatParameter(comparator.getExtendedData(paramName), params_formatters.BASE_SCHEME)
                if paramValue is not None:
                    paramUnits = _ms(params_formatters.measureUnitsForParameter(paramName))
                    isPiercingPower = paramName == 'avgPiercingPower'
                    paramUnits += _ASTERISK if isPiercingPower and not isDistanceDependent else ''
                    block.append(self._packParameterBlock(backport.text(R.strings.menu.moduleInfo.params.dyn(paramName)()), paramValue, paramUnits))

        return block


class CommonStatsBlockConstructor(_BaseCommonStatsBlockConstructor):

    @property
    def colorScheme(self):
        return params_formatters.COLORLESS_SCHEME if self.configuration.colorless else params_formatters.BASE_SCHEME

    def __iterPiercingPowerTable(self, table, comparator):
        if comparator is not None:
            extendedTable = comparator.getExtendedData('piercingPowerTable')
            for (distance, value), (_, valueState) in izip(extendedTable.value, extendedTable.state):
                yield (distance, params_formatters.formatParameter('piercingPower', value, valueState, self.colorScheme))

        else:
            for distance, value in table:
                yield (distance, params_formatters.formatParameter('piercingPower', value))

        return

    def _getDamagePackInfo(self):
        distanceDmg = self.shell.descriptor.distanceDmg
        if distanceDmg is None:
            return
        else:
            distance = distanceDmg.distance
            return backport.text(R.strings.menu.moduleInfo.params.distanceDamage(), minDmg=backport.getNiceNumberFormat(distance.min), maxDmg=backport.getNiceNumberFormat(distance.max))

    def _getAvgPiercingPowerPackInfo(self, pTable, tableData):
        asteriksTitle = None
        value = None
        if pTable != NO_DATA:
            asteriksTitle = self._getAvgPiercingPowerTitle(pTable, tableData)
        if tableData and pTable is not None:
            value = '%s-%s' % (tableData[0][0], tableData[-1][0])
        return (value, asteriksTitle)

    def _getAvgPiercingPowerTitle(self, pTable, tableData):
        if pTable is not None and tableData:
            return backport.text(R.strings.menu.moduleInfo.params.piercingDistance.footnote(), minDist=tableData[0][1], maxDist=tableData[-1][1])
        else:
            return backport.text(R.strings.menu.moduleInfo.params.noPiercingDistance.footnoteFlame()) if self.shell.type == SHELL_TYPES.FLAME else backport.text(R.strings.menu.moduleInfo.params.noPiercingDistance.footnote())

    def _getFormattedParameter(self, value, comparator):
        return params_formatters.colorizedFormatParameter(comparator.getExtendedData(value), self.colorScheme)

    def _getTableData(self, piercingPowerTable, comparator):
        if not isinstance(piercingPowerTable, list):
            return []
        return [ (value, distance) for distance, value in self.__iterPiercingPowerTable(piercingPowerTable, comparator) ]

    def construct(self):
        if not self.configuration.params:
            return []
        else:
            comparator = params_helper.shellComparator(self.shell, self.configuration.vehicle)
            piercingPowerTable = self._params.pop('piercingPowerTable')
            tableData = self._getTableData(piercingPowerTable, comparator)
            block = [formatters.packTitleDescBlock(title=text_styles.middleTitle(_ms(TOOLTIPS.TANKCARUSEL_MAINPROPERTY)), padding=formatters.packPadding(bottom=8))]
            asteriks = _ASTERISK
            asteriksTitles = []
            for paramName, paramValue in params_formatters.getFormattedParamsList(self.shell.descriptor, self._params):
                if paramName == ModuleTooltipBlockConstructor.CALIBER:
                    continue
                if comparator is not None:
                    paramValue = self._getFormattedParameter(paramName, comparator)
                if paramValue is None:
                    continue
                paramUnits = _ms(params_formatters.measureUnitsForParameter(paramName))
                asteriksTitle = None
                if paramName == 'avgPiercingPower':
                    value, asteriksTitle = self._getAvgPiercingPowerPackInfo(piercingPowerTable, tableData)
                    paramValue = value or paramValue
                if paramName == 'damage':
                    asteriksTitle = self._getDamagePackInfo()
                if asteriksTitle is not None:
                    asteriksTitles.append(asteriksTitle)
                    paramUnits += asteriks
                    asteriks += _ASTERISK
                block.append(self._packParameterBlock(backport.text(R.strings.menu.moduleInfo.params.dyn(paramName)()), paramValue, paramUnits))

            asteriks = ''
            padding = formatters.packPadding(top=16)
            for title in asteriksTitles:
                block.append(formatters.packTitleDescBlock(title=text_styles.standard(asteriks + title), padding=padding))
                asteriks += _ASTERISK
                padding = None

            return block


class StatusBlockConstructor(ShellTooltipBlockConstructor):

    def construct(self):
        shell = self.shell
        configuration = self.configuration
        block = []
        status = None
        checkBuying = configuration.checkBuying
        if checkBuying:
            couldBeBought, reason = shell.mayPurchase(self.itemsCache.items.stats.money)
            if not couldBeBought:
                status = '#tooltips:shellFits/%s' % reason
        statusHeader, statusText = getComplexStatus(status)
        if statusHeader is not None or statusText is not None:
            block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(statusHeader if statusHeader is not None else ''), desc=text_styles.main(statusText if statusText is not None else '')))
        return block
