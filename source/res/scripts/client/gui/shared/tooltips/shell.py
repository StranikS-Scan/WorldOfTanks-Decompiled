# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/shell.py
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import g_itemsCache
from gui.shared.items_parameters import params_helper, formatters as params_formatters, NO_DATA, MAX_RELATIVE_VALUE
from gui.shared.tooltips import formatters
from gui.shared.tooltips import getComplexStatus, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from gui.shared.formatters import text_styles
from gui.shared.money import ZERO_MONEY
from helpers.i18n import makeString as _ms
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
        leftPadding = 20
        rightPadding = 20
        topPadding = 20
        lrPaddings = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockTopPadding = -4
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding)
        textGap = -2
        vDescr = paramsConfig.vehicle.descriptor if paramsConfig.vehicle is not None else None
        params = params_helper.getParameters(shell, vDescr)
        showBasicData = self.__basicDataAllowed and params['isBasic']
        items.append(formatters.packBuildUpBlockData(HeaderBlockConstructor(shell, statsConfig, leftPadding, rightPadding, params).construct(), padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding)))
        priceBlock, invalidWidth = PriceBlockConstructor(shell, statsConfig, 80).construct()
        if len(priceBlock) > 0:
            self._setWidth(_TOOLTIP_MAX_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
            items.append(formatters.packBuildUpBlockData(priceBlock, padding=blockPadding, gap=textGap))
        if vDescr is not None and not showBasicData:
            simplifiedStatsBlock = SimplifiedStatsBlockConstructor(shell, paramsConfig, params).construct()
            if len(simplifiedStatsBlock) > 0:
                items.append(formatters.packBuildUpBlockData(simplifiedStatsBlock, padding=blockPadding, gap=textGap))
        statusBlock = StatusBlockConstructor(shell, statusConfig).construct()
        if self.__basicDataAllowed:
            statsBlock = CommonStatsBlockConstructor(shell, paramsConfig, 80, params).construct()
        else:
            statsBlock = _AdvancedCommonStatsBlockConstructior(shell, paramsConfig, 80, params).construct()
        bottomPadding = 4 if len(statusBlock) > 0 or showBasicData else 0
        if len(statsBlock) > 0:
            items.append(formatters.packBuildUpBlockData(statsBlock, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=bottomPadding), gap=textGap))
        if len(statusBlock) > 0:
            items.append(formatters.packBuildUpBlockData(statusBlock, padding=lrPaddings))
        if showBasicData:
            boldText = text_styles.neutral(TOOLTIPS.SHELL_BASIC_DESCRIPTION_BOLD)
            items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.standard(_ms(TOOLTIPS.SHELL_BASIC_DESCRIPTION, bold=boldText)), padding=lrPaddings)], padding=formatters.packPadding(right=rightPadding)))
        return items


class ShellTooltipBlockConstructor(object):

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
        block = list()
        block.append(formatters.packImageTextBlockData(title=text_styles.highTitle(shell.userName), desc=text_styles.standard('#item_types:shell/kinds/' + shell.type), img=shell.icon, imgPadding=formatters.packPadding(left=7), txtGap=-4, txtOffset=100 - self.leftPadding))
        if self._params['isBasic']:
            block.append(formatters.packAlignedTextBlockData(text=text_styles.neutral(TOOLTIPS.SHELL_BASIC), align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(right=self.rightPadding, top=-25, bottom=4)))
        return block


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
            need = ZERO_MONEY
            if buyPrice:
                money = g_itemsCache.items.stats.money
                price = shell.altPrice or shell.buyPrice
                need = price - money
                need = need.toNonNegative()
                defPrice = shell.defaultAltPrice or shell.defaultPrice
                addCreditPrice = price.credits > 0
                if price.isAllSet() and not g_itemsCache.items.shop.isEnabledBuyingGoldShellsForCredits:
                    addCreditPrice = False
                addGoldPrice = price.gold > 0
                addDelimeter = addCreditPrice and addGoldPrice
                if addCreditPrice:
                    block.append(makePriceBlock(price.credits, CURRENCY_SETTINGS.BUY_CREDITS_PRICE, need.credits if need.credits > 0 else None, defPrice.credits if defPrice.credits > 0 else None, percent=shell.actionPrc, valueWidth=self._valueWidth))
                if addDelimeter:
                    block.append(formatters.packTextBlockData(text=text_styles.standard(TOOLTIPS.VEHICLE_TEXTDELIMITER_OR), padding=formatters.packPadding(left=81 + self.leftPadding)))
                if addGoldPrice:
                    block.append(makePriceBlock(price.gold, CURRENCY_SETTINGS.BUY_GOLD_PRICE, need.gold if need.gold > 0 else None, defPrice.gold if defPrice.gold > 0 else None, percent=shell.actionPrc, valueWidth=self._valueWidth))
            if sellPrice:
                block.append(makePriceBlock(shell.sellPrice.credits, CURRENCY_SETTINGS.SELL_PRICE, oldPrice=shell.defaultSellPrice.credits, percent=shell.sellActionPrc, valueWidth=self._valueWidth))
            inventoryCount = shell.inventoryCount
            if inventoryCount:
                block.append(formatters.packTextParameterBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_INVENTORYCOUNT), value=text_styles.stats(inventoryCount), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5)))
            notEnoughMoney = need.credits > 0 or need.gold > 0
            hasAction = shell.actionPrc > 0 or shell.sellActionPrc > 0
            return (block, notEnoughMoney or hasAction)


class SimplifiedStatsBlockConstructor(ShellTooltipBlockConstructor):

    def __init__(self, shell, configuration, params):
        super(SimplifiedStatsBlockConstructor, self).__init__(shell, configuration, params=params)

    def construct(self):
        block = []
        if self.configuration.params:
            comparator = params_helper.shellOnVehicleComparator(self.shell, self.configuration.vehicle)
            stockParams = params_helper.getParameters(g_itemsCache.items.getStockVehicle(self.configuration.vehicle.intCD))
            for parameter in params_formatters.getRelativeDiffParams(comparator):
                delta = parameter.state[1]
                value = parameter.value
                if delta > 0:
                    value -= delta
                block.append(formatters.packStatusDeltaBlockData(title=text_styles.middleTitle(MENU.tank_params(parameter.name)), valueStr=params_formatters.simlifiedDeltaParameter(parameter), statusBarData={'value': value,
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
        return formatters.packTextParameterBlockData(name=text_styles.main(name) + text_styles.standard(measureUnits), value=text_styles.stats(value), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5))


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
                if comparator is not None:
                    paramValue = params_formatters.colorizedFormatParameter(comparator.getExtendedData(paramName), params_formatters.BASE_SCHEME)
                if paramValue is not None:
                    paramUnits = _ms(params_formatters.measureUnitsForParameter(paramName))
                    isPiercingPower = paramName == 'avgPiercingPower'
                    paramUnits += _ASTERISK if isPiercingPower and not isDistanceDependent else ''
                    block.append(self._packParameterBlock(_ms('#menu:moduleInfo/params/' + paramName), paramValue, paramUnits))

        return block


class CommonStatsBlockConstructor(_BaseCommonStatsBlockConstructor):

    def __init__(self, shell, configuration, valueWidth, params):
        super(CommonStatsBlockConstructor, self).__init__(shell, configuration, valueWidth, params=params)

    def construct(self):
        block = []
        if self.configuration.params:
            top = 8
            bottom = 8
            topPadding = formatters.packPadding(top=top)
            bottomPadding = formatters.packPadding(bottom=bottom)
            tbPadding = formatters.packPadding(top=top, bottom=bottom)
            shell = self.shell
            comparator = params_helper.shellComparator(shell, self.configuration.vehicle)
            piercingPowerTable = self._params.pop('piercingPowerTable')
            isDistanceDependent = piercingPowerTable is not None
            maxShotDistance = self._params.pop('maxShotDistance', None)
            formattedParameters = params_formatters.getFormattedParamsList(shell.descriptor, self._params)
            block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(_ms(TOOLTIPS.TANKCARUSEL_MAINPROPERTY)), padding=bottomPadding))
            for paramName, paramValue in formattedParameters:
                if comparator is not None:
                    paramValue = params_formatters.colorizedFormatParameter(comparator.getExtendedData(paramName), params_formatters.BASE_SCHEME)
                if paramValue is not None:
                    paramUnits = _ms(params_formatters.measureUnitsForParameter(paramName))
                    isPiercingPower = paramName == 'avgPiercingPower'
                    paramUnits += _ASTERISK if isPiercingPower and not isDistanceDependent else ''
                    if not (isPiercingPower and isDistanceDependent):
                        block.append(self._packParameterBlock(_ms('#menu:moduleInfo/params/' + paramName), paramValue, paramUnits))

            if isinstance(piercingPowerTable, list):
                piercingUnits = _ms(params_formatters.measureUnitsForParameter('piercingPower'))
                block.append(formatters.packTitleDescBlock(title=text_styles.standard(_ms(MENU.MODULEINFO_PARAMS_PIERCINGDISTANCEHEADER)), padding=tbPadding))
                for distance, value in self.__iteratePiercingPowerTable(piercingPowerTable, comparator):
                    if maxShotDistance is not None and distance == _AUTOCANNON_SHOT_DISTANCE:
                        piercingUnits += _ASTERISK
                    block.append(self._packParameterBlock(_ms(MENU.MODULEINFO_PARAMS_PIERCINGDISTANCE, dist=distance), value, piercingUnits))

                if maxShotDistance is not None:
                    block.append(formatters.packTitleDescBlock(title=text_styles.standard(_ms(MENU.MODULEINFO_PARAMS_MAXSHOTDISTANCE_FOOTNOTE)), padding=topPadding))
            elif piercingPowerTable != NO_DATA:
                title = _ms(MENU.MODULEINFO_PARAMS_NOPIERCINGDISTANCE_FOOTNOTE)
                distanceNote = ''
                if maxShotDistance is not None:
                    distanceNote = _ms(MENU.MODULEINFO_PARAMS_NOPIERCINGDISTANCE_FOOTNOTE_MAXDISTANCE)
                title = title % distanceNote
                block.append(formatters.packTitleDescBlock(title=text_styles.standard(title), padding=topPadding))
        return block

    @staticmethod
    def __iteratePiercingPowerTable(table, comparator):
        if comparator is not None:
            extendedTable = comparator.getExtendedData('piercingPowerTable')
            for (distance, value), (_, valueState) in zip(extendedTable.value, extendedTable.state):
                fmtValue = params_formatters.formatParameter('piercingPower', value, valueState, params_formatters.BASE_SCHEME)
                yield (distance, fmtValue)

        else:
            for distance, value in table:
                yield (distance, params_formatters.formatParameter('piercingPower', value))

        return


class StatusBlockConstructor(ShellTooltipBlockConstructor):

    def construct(self):
        shell = self.shell
        configuration = self.configuration
        block = []
        status = None
        checkBuying = configuration.checkBuying
        if checkBuying:
            couldBeBought, reason = shell.mayPurchase(g_itemsCache.items.stats.money)
            if not couldBeBought:
                status = '#tooltips:shellFits/%s' % reason
        statusHeader, statusText = getComplexStatus(status)
        if statusHeader is not None or statusText is not None:
            block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(statusHeader if statusHeader is not None else ''), desc=text_styles.main(statusText if statusText is not None else '')))
        return block
