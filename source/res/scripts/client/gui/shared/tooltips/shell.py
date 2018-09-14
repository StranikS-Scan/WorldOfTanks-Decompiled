# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/shell.py
from debug_utils import LOG_ERROR
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import g_itemsCache
from gui.shared.items_parameters import params_helper, formatters as params_formatters, NO_DATA
from gui.shared.tooltips import formatters
from gui.shared.tooltips import getComplexStatus, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from gui.shared.formatters import text_styles
from gui.shared.money import ZERO_MONEY
from helpers.i18n import makeString as _ms
_TOOLTIP_MIN_WIDTH = 380
_TOOLTIP_MAX_WIDTH = 420
_AUTOCANNON_SHOT_DISTANCE = 400

class ShellBlockToolTipData(BlocksTooltipData):

    def __init__(self, context):
        super(ShellBlockToolTipData, self).__init__(context, TOOLTIP_TYPE.SHELL)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=20, right=20)
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
        items.append(formatters.packBuildUpBlockData(HeaderBlockConstructor(shell, statsConfig, leftPadding, rightPadding).construct(), padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding)))
        priceBlock, invalidWidth = PriceBlockConstructor(shell, statsConfig, 80, leftPadding, rightPadding).construct()
        if len(priceBlock) > 0:
            self._setWidth(_TOOLTIP_MAX_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
            items.append(formatters.packBuildUpBlockData(priceBlock, padding=blockPadding, gap=textGap))
        items.append(formatters.packBuildUpBlockData(CommonStatsBlockConstructor(shell, paramsConfig, 80, leftPadding, rightPadding).construct(), padding=blockPadding, gap=textGap))
        statusBlock = StatusBlockConstructor(shell, statusConfig, leftPadding, rightPadding).construct()
        if len(statusBlock) > 0:
            items.append(formatters.packBuildUpBlockData(statusBlock, padding=lrPaddings))
        return items


class ShellTooltipBlockConstructor(object):

    def __init__(self, shell, configuration, leftPadding=20, rightPadding=20):
        self.shell = shell
        self.configuration = configuration
        self.leftPadding = leftPadding
        self.rightPadding = rightPadding

    def construct(self):
        return None


class HeaderBlockConstructor(ShellTooltipBlockConstructor):

    def __init__(self, shell, configuration, leftPadding, rightPadding):
        super(HeaderBlockConstructor, self).__init__(shell, configuration, leftPadding, rightPadding)

    def construct(self):
        shell = self.shell
        block = []
        title = shell.userName
        desc = '#item_types:shell/kinds/' + shell.type
        block.append(formatters.packImageTextBlockData(title=text_styles.highTitle(title), desc=text_styles.standard(desc), img=shell.icon, imgPadding=formatters.packPadding(left=7), txtGap=-4, txtOffset=100 - self.leftPadding))
        return block


class PriceBlockConstructor(ShellTooltipBlockConstructor):

    def __init__(self, shell, configuration, valueWidth, leftPadding, rightPadding):
        super(PriceBlockConstructor, self).__init__(shell, configuration, leftPadding, rightPadding)
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
                price = shell.altPrice
                need = price - money
                need = need.toNonNegative()
                defPrice = shell.defaultAltPrice or shell.defaultPrice
                block.append(makePriceBlock(price.credits, CURRENCY_SETTINGS.BUY_CREDITS_PRICE, need.credits if need.credits > 0 else None, defPrice.credits if defPrice.credits > 0 else None, percent=shell.actionPrc, valueWidth=self._valueWidth))
                if price.gold > 0:
                    block.append(formatters.packTextBlockData(text=text_styles.standard(TOOLTIPS.VEHICLE_TEXTDELIMITER_OR), padding=formatters.packPadding(left=81 + self.leftPadding)))
                    block.append(makePriceBlock(price.gold, CURRENCY_SETTINGS.BUY_GOLD_PRICE, need.gold if need.gold > 0 else None, defPrice.gold if defPrice.gold > 0 else None, percent=shell.actionPrc, valueWidth=self._valueWidth))
            if sellPrice:
                block.append(makePriceBlock(shell.sellPrice.credits, CURRENCY_SETTINGS.SELL_PRICE, oldPrice=shell.defaultSellPrice.credits, percent=shell.sellActionPrc, valueWidth=self._valueWidth))
            inventoryCount = shell.inventoryCount
            if inventoryCount:
                block.append(formatters.packTextParameterBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_INVENTORYCOUNT), value=text_styles.stats(inventoryCount), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5)))
            notEnoughMoney = need > ZERO_MONEY
            hasAction = shell.actionPrc > 0 or shell.sellActionPrc > 0
            return (block, notEnoughMoney or hasAction)


class CommonStatsBlockConstructor(ShellTooltipBlockConstructor):

    def __init__(self, shell, configuration, valueWidth, leftPadding, rightPadding):
        super(CommonStatsBlockConstructor, self).__init__(shell, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth

    def construct(self):
        block = []
        shell = self.shell
        vehicle = self.configuration.vehicle
        vDescr = vehicle.descriptor if vehicle is not None else None
        params = params_helper.getParameters(shell, vDescr)
        piercingPower = params.pop('piercingPower')
        piercingPowerTable = params.pop('piercingPowerTable')
        maxShotDistance = params.pop('maxShotDistance') if 'maxShotDistance' in params else None
        formattedParameters = params_formatters.getFormattedParamsList(shell.descriptor, params)
        block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(_ms(TOOLTIPS.TANKCARUSEL_MAINPROPERTY)), padding=formatters.packPadding(bottom=8)))
        for paramName, paramValue in formattedParameters:
            block.append(self.__packParameterBlock(_ms('#menu:moduleInfo/params/' + paramName), paramValue, params_formatters.measureUnitsForParameter(paramName)))

        piercingUnits = _ms(params_formatters.measureUnitsForParameter('piercingPower'))
        if isinstance(piercingPowerTable, list):
            block.append(formatters.packTitleDescBlock(title=text_styles.standard(_ms(MENU.MODULEINFO_PARAMS_PIERCINGDISTANCEHEADER)), padding=formatters.packPadding(bottom=8, top=8)))
            for distance, value in piercingPowerTable:
                if maxShotDistance is not None and distance == _AUTOCANNON_SHOT_DISTANCE:
                    piercingUnits += '*'
                block.append(self.__packParameterBlock(_ms(MENU.MODULEINFO_PARAMS_PIERCINGDISTANCE, dist=distance), params_formatters.baseFormatParameter('piercingPower', value), piercingUnits))

            if maxShotDistance is not None:
                block.append(formatters.packTitleDescBlock(title=text_styles.standard(_ms(MENU.MODULEINFO_PARAMS_MAXSHOTDISTANCE_FOOTNOTE)), padding=formatters.packPadding(top=8)))
        else:
            if piercingPowerTable != NO_DATA:
                piercingUnits += '*'
            block.append(self.__packParameterBlock(_ms(MENU.MODULEINFO_PARAMS_PIERCINGPOWER), params_formatters.baseFormatParameter('piercingPower', piercingPower), piercingUnits))
            if piercingPowerTable != NO_DATA:
                title = _ms(MENU.MODULEINFO_PARAMS_NOPIERCINGDISTANCE_FOOTNOTE)
                distanceNote = ''
                if maxShotDistance is not None:
                    distanceNote = _ms(MENU.MODULEINFO_PARAMS_NOPIERCINGDISTANCE_FOOTNOTE_MAXDISTANCE)
                title = title % distanceNote
                block.append(formatters.packTitleDescBlock(title=text_styles.standard(title), padding=formatters.packPadding(top=8)))
        return block

    def __packParameterBlock(self, name, value, measureUnits):
        return formatters.packTextParameterBlockData(name=text_styles.main(name) + text_styles.standard(measureUnits), value=text_styles.stats(value), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5))


class StatusBlockConstructor(ShellTooltipBlockConstructor):

    def __init__(self, shell, configuration, leftPadding, rightPadding):
        super(StatusBlockConstructor, self).__init__(shell, configuration, leftPadding, rightPadding)

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
