# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/tooltips/title_step_tooltip.py
from collections import namedtuple
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
_TOOLTIP_MIN_WIDTH = 320
_TopBorders = namedtuple('TopBorders', 'increase, idle, decrease')

class TitleStepTooltip(BlocksTooltipData):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, ctx):
        super(TitleStepTooltip, self).__init__(ctx, TOOLTIP_TYPE.BATTLE_ROYALE_STEP)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args):
        items = super(TitleStepTooltip, self)._packBlocks()
        soloStepChanges = self.__battleRoyaleController.getSoloStepsTop()
        squadStepChanges = self.__battleRoyaleController.getSquadStepsTop()
        soloBorders = self.__getTopBorders(soloStepChanges)
        squadBorders = self.__getTopBorders(squadStepChanges)
        items.append(self.__packHeaderBlock())
        increaseBlock = self.__packIncreaseBlock(soloBorders, squadBorders)
        if increaseBlock:
            items.append(increaseBlock)
        idleBlock = self.__packIdleBlock(soloBorders, squadBorders)
        if idleBlock:
            items.append(idleBlock)
        decreaseBlock = self.__packDecreaseBlock(soloBorders, squadBorders)
        if decreaseBlock:
            items.append(decreaseBlock)
        return items

    @staticmethod
    def __getConditionHeaderBlock(strValue):
        return formatters.packTextBlockData(text_styles.highTitle(strValue), padding=formatters.packPadding(bottom=7))

    @staticmethod
    def __getTopBorders(stepChanges):
        increase = TitleStepTooltip.__getRightBorder(stepChanges, lambda x: x > 0)
        idle = TitleStepTooltip.__getRightBorder(stepChanges, lambda x: x == 0)
        decrease = len(stepChanges)
        return _TopBorders(increase, idle, decrease)

    @staticmethod
    def __getRightBorder(stepChanges, condition):
        resultIdx = 0
        for idx, element in enumerate(stepChanges):
            if condition(element):
                resultIdx = idx + 1

        return resultIdx

    @staticmethod
    def __packRangeBlock(leftBorder, rightBorder, signKey, playersKey):
        if leftBorder != rightBorder:
            text = backport.text(R.strings.battle_royale.tooltips.step.dyn(signKey).dyn(playersKey).range(), maxPlace=leftBorder, minPlace=rightBorder)
        else:
            text = backport.text(R.strings.battle_royale.tooltips.step.dyn(signKey).dyn(playersKey).one(), place=leftBorder)
        return formatters.packTextBlockData(text_styles.standard(text))

    @staticmethod
    def __packHeaderBlock():
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.battle_royale.tooltips.step.header())), desc=text_styles.standard(backport.text(R.strings.battle_royale.tooltips.step.description())), img=backport.image(R.images.gui.maps.icons.battleRoyale.stageGrey()), imgPadding=formatters.packPadding(left=-18, top=-28), txtGap=-4, txtOffset=70, padding=formatters.packPadding(bottom=-60))

    def __packIncreaseBlock(self, soloStepBorders, squadStepBorders):
        soloBlock = None
        squadBlock = None
        if soloStepBorders.increase:
            soloBlock = self.__packRangeBlock(1, soloStepBorders.increase, 'increase', 'solo')
        if squadStepBorders.increase:
            squadBlock = self.__packRangeBlock(1, squadStepBorders.increase, 'increase', 'sqaud')
        if not soloBlock and not squadBlock:
            return
        else:
            blocks = list()
            blocks.append(self.__getConditionHeaderBlock(strValue=backport.text(R.strings.battle_royale.tooltips.step.increase.header())))
            blocks.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.battle_royale.tooltips.step.increase.description()))))
            if soloBlock:
                blocks.append(soloBlock)
            if squadBlock:
                blocks.append(squadBlock)
            return formatters.packBuildUpBlockData(blocks, 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def __packIdleBlock(self, soloStepBorders, squadStepBorders):
        soloBlock = None
        squadBlock = None
        if soloStepBorders.idle and soloStepBorders.idle != soloStepBorders.increase:
            leftBorder = soloStepBorders.increase + 1
            soloBlock = self.__packRangeBlock(leftBorder, soloStepBorders.idle, 'idle', 'solo')
        if squadStepBorders.idle and squadStepBorders.idle != squadStepBorders.increase:
            leftBorder = squadStepBorders.increase + 1
            squadBlock = self.__packRangeBlock(leftBorder, squadStepBorders.idle, 'idle', 'sqaud')
        if not soloBlock and not squadBlock:
            return
        else:
            blocks = list()
            blocks.append(self.__getConditionHeaderBlock(strValue=backport.text(R.strings.battle_royale.tooltips.step.idle.header())))
            if soloBlock:
                blocks.append(soloBlock)
            if squadBlock:
                blocks.append(squadBlock)
            return formatters.packBuildUpBlockData(blocks, 0)

    def __packDecreaseBlock(self, soloBorders, squadBorders):
        soloBlock = None
        squadBlock = None
        if soloBorders.decrease and soloBorders.decrease not in (soloBorders.idle, soloBorders.increase):
            leftBorder = soloBorders.idle + 1 if soloBorders.idle else soloBorders.increase + 1
            soloBlock = self.__packRangeBlock(leftBorder, soloBorders.decrease, 'decrease', 'solo')
        if squadBorders.decrease and squadBorders.decrease not in (squadBorders.idle, squadBorders.increase):
            leftBorder = squadBorders.idle + 1 if squadBorders.idle else squadBorders.increase + 1
            squadBlock = self.__packRangeBlock(leftBorder, squadBorders.decrease, 'decrease', 'sqaud')
        if not soloBlock and not squadBlock:
            return
        else:
            blocks = list()
            blocks.append(self.__getConditionHeaderBlock(strValue=backport.text(R.strings.battle_royale.tooltips.step.decrease.header())))
            if soloBlock:
                blocks.append(soloBlock)
            if squadBlock:
                blocks.append(squadBlock)
            return formatters.packBuildUpBlockData(blocks, 0)
