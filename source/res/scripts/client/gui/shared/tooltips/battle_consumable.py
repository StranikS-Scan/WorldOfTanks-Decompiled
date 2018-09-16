# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/battle_consumable.py
from gui.shared.formatters import text_styles
from gui.shared.items_parameters import params_helper, formatters as params_formatters
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from helpers import int2roman
from helpers.i18n import makeString as _ms

class BattleConsumableTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(BattleConsumableTooltipData, self).__init__(context, TOOLTIP_TYPE.EQUIPMENT)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(400)
        return

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        items = super(BattleConsumableTooltipData, self)._packBlocks()
        statsConfig = self.context.getStatsConfiguration(self.item)
        paramsConfig = self.context.getParamsConfiguration(self.item)
        leftPadding = 20
        rightPadding = 20
        topPadding = 20
        textGap = -2
        items.append(formatters.packBuildUpBlockData(HeaderBlockConstructor(self.item, statsConfig, leftPadding, rightPadding).construct(), padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding)))
        items.append(formatters.packBuildUpBlockData(CommonStatsBlockConstructor(self.item, paramsConfig, 80, leftPadding, rightPadding).construct(), padding=formatters.packPadding(left=leftPadding, right=rightPadding), gap=textGap))
        return items


class BattleConsumableTooltipBlockConstructor(object):

    def __init__(self, item, configuration, leftPadding=20, rightPadding=20):
        self.item = item
        self.configuration = configuration
        self.leftPadding = leftPadding
        self.rightPadding = rightPadding

    def construct(self):
        return None


class HeaderBlockConstructor(BattleConsumableTooltipBlockConstructor):

    def construct(self):
        tier = self.item.name.split('tier')
        if len(tier) > 1:
            _, level = tier
            desc = _ms('#fortifications:orderType/battleConsumable', level=int2roman(int(level)))
        else:
            desc = _ms('#fortifications:orderType/battleConsumable_no_level')
        block = []
        title = self.item.userName
        block.append(formatters.packImageTextBlockData(title=text_styles.highTitle(title), desc=text_styles.main(desc), img=self.item.icon, imgPadding=formatters.packPadding(left=12), txtGap=-4, txtOffset=100 - self.leftPadding))
        return block


class CommonStatsBlockConstructor(BattleConsumableTooltipBlockConstructor):

    def __init__(self, item, configuration, valueWidth, leftPadding, rightPadding):
        super(CommonStatsBlockConstructor, self).__init__(item, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth

    def construct(self):
        block = []
        block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(_ms(TOOLTIPS.TANKCARUSEL_MAINPROPERTY)), padding=formatters.packPadding(bottom=8)))
        params = params_helper.getParameters(self.item)
        paramsResult = params_formatters.getFormattedParamsList(self.item.descriptor, params)
        for paramName, paramValue in paramsResult:
            block.append(self.__packParameterBloc(_ms('#menu:moduleInfo/params/' + paramName), paramValue, params_formatters.measureUnitsForParameter(paramName)))

        return block

    def __packParameterBloc(self, name, value, measureUnits):
        return formatters.packTextParameterBlockData(name=text_styles.main(name) + text_styles.standard(measureUnits), value=text_styles.stats(value), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5))
