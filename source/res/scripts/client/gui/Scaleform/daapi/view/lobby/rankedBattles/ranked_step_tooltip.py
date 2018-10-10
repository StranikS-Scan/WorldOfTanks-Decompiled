# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_step_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from skeletons.gui.game_control import IRankedBattlesController
from helpers import dependency
from helpers.i18n import makeString as _ms
_TOOLTIP_MIN_WIDTH = 320

class RankedStepTooltip(BlocksTooltipData):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx):
        super(RankedStepTooltip, self).__init__(ctx, TOOLTIP_TYPE.RANKED_STEP)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args):
        items = super(RankedStepTooltip, self)._packBlocks()
        totalPlayers = self.rankedController.getRanksTops(isLoser=False)
        winEarnedCount = self.rankedController.getRanksTops(isLoser=False, stepDiff=RANKEDBATTLES_ALIASES.STEP_VALUE_EARN)
        winNotReceivedCount = self.rankedController.getRanksTops(isLoser=False, stepDiff=RANKEDBATTLES_ALIASES.STEP_VALUE_NO_CHANGE)
        winLostCount = self.rankedController.getRanksTops(isLoser=False, stepDiff=RANKEDBATTLES_ALIASES.STEP_VALUE_LOSE)
        loseEarnedCount = self.rankedController.getRanksTops(isLoser=True, stepDiff=RANKEDBATTLES_ALIASES.STEP_VALUE_EARN)
        loseNotReceivedCount = self.rankedController.getRanksTops(isLoser=True, stepDiff=RANKEDBATTLES_ALIASES.STEP_VALUE_NO_CHANGE)
        loseLostCount = self.rankedController.getRanksTops(isLoser=True, stepDiff=RANKEDBATTLES_ALIASES.STEP_VALUE_LOSE)
        items.append(self._packHeaderBlock())
        items.append(self._packReceivedBlock(winEarnedCount=winEarnedCount, loseEarnedCount=loseEarnedCount))
        notReceivedBlock = self._packNotReceivedBlock(winEarnedCount=winEarnedCount, winNotReceivedCount=winNotReceivedCount, loseEarnedCount=loseEarnedCount, loseNotReceivedCount=loseNotReceivedCount)
        if notReceivedBlock is not None:
            items.append(notReceivedBlock)
        items.append(self._packLostBlock(totalPlayers=totalPlayers, winLostCount=winLostCount, loseLostCount=loseLostCount))
        return items

    def _packHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(RANKED_BATTLES.TOOLTIP_STEP_HEADER), desc=text_styles.standard(RANKED_BATTLES.TOOLTIP_STEP_DESCRIPTION), img=RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKS_STAGE_STAGE_GREY_94X120, imgPadding=formatters.packPadding(left=-18, top=-28), txtGap=-4, txtOffset=70, padding=formatters.packPadding(bottom=-60))

    def _packReceivedBlock(self, winEarnedCount, loseEarnedCount):
        block = []
        block.append(self._getConditionHeaderBlock(strValue=RANKED_BATTLES.TOOLTIP_STEP_CONDITIONS_HEADER))
        if winEarnedCount > 0:
            winIcon = RES_ICONS.getRankedTooltipTopIcon(winEarnedCount)
            block.append(formatters.packImageTextBlockData(desc=text_styles.main(_ms(RANKED_BATTLES.TOOLTIP_STEP_CONDITIONS, battlesNum=winEarnedCount, team=text_styles.statInfo(RANKED_BATTLES.TOOLTIP_STEP_WINNERS))), img=winIcon, txtPadding=formatters.packPadding(left=17)))
        if winEarnedCount > 0 and loseEarnedCount > 0:
            block.append(self._getOrBlock(padding=formatters.packPadding(left=70, bottom=10)))
        if loseEarnedCount > 0:
            loseIcon = RES_ICONS.getRankedTooltipLoseIcon(loseEarnedCount)
            block.append(formatters.packImageTextBlockData(desc=text_styles.main(_ms(RANKED_BATTLES.TOOLTIP_STEP_CONDITIONS, battlesNum=loseEarnedCount, team=text_styles.critical(RANKED_BATTLES.TOOLTIP_STEP_LOSERS))), img=loseIcon, txtPadding=formatters.packPadding(left=17)))
        return formatters.packBuildUpBlockData(block, 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _packNotReceivedBlock(self, winEarnedCount, winNotReceivedCount, loseEarnedCount, loseNotReceivedCount):
        if winNotReceivedCount <= 0 and loseNotReceivedCount <= 0:
            return None
        else:
            blocks = []
            blocks.append(self._getConditionHeaderBlock(strValue=RANKED_BATTLES.TOOLTIP_STEP_NOTCHARGED_HEADER))
            if winNotReceivedCount > 0:
                blocks.append(self._getConditionBlock(topValue=winEarnedCount, placesCount=winNotReceivedCount, condition=RANKED_BATTLES.TOOLTIP_STEP_DECOMMISSIONWIN_DESCRIPTION, conditionTop=RANKED_BATTLES.TOOLTIP_STEP_NOTCHARGED_DESCRIPTION))
            if winNotReceivedCount > 0 and loseNotReceivedCount > 0:
                blocks.append(self._getOrBlock())
            if loseNotReceivedCount > 0:
                blocks.append(self._getConditionBlock(topValue=loseEarnedCount, placesCount=loseNotReceivedCount, condition=RANKED_BATTLES.TOOLTIP_STEP_DECOMMISSION_DESCRIPTION, conditionTop=RANKED_BATTLES.TOOLTIP_STEP_NOTCHARGEDLOSE_DESCRIPTION))
            return formatters.packBuildUpBlockData(blocks, 0)

    def _packLostBlock(self, totalPlayers, winLostCount, loseLostCount):
        blocks = []
        if winLostCount > 0 or loseLostCount > 0:
            winTop = totalPlayers - winLostCount + 1
            loseTop = totalPlayers - loseLostCount + 1
            blocks.append(self._getConditionHeaderBlock(strValue=RANKED_BATTLES.TOOLTIP_STEP_DECOMMISSION_HEADER))
            if winLostCount > 0:
                blocks.append(self._getConditionBlock(fromPlaceValue=winTop, placesCount=winLostCount, condition=RANKED_BATTLES.TOOLTIP_STEP_DECOMMISSIONWIN_DESCRIPTION))
            if winLostCount > 0 and loseLostCount > 0:
                blocks.append(self._getOrBlock())
            if loseLostCount > 0:
                blocks.append(self._getConditionBlock(fromPlaceValue=loseTop, placesCount=loseLostCount, condition=RANKED_BATTLES.TOOLTIP_STEP_DECOMMISSION_DESCRIPTION))
        blocks.append(formatters.packTextBlockData(text_styles.standard(RANKED_BATTLES.TOOLTIP_STEP_DECOMMISSION_BEFORERANK)))
        return formatters.packBuildUpBlockData(blocks, 0)

    def _getConditionStr(self, strValue, topValue, fromPlace, tillPlace):
        fromTill = self._getFromTillPlaceStr(formatter=text_styles.standard, fromPlace=fromPlace, tillPlace=tillPlace)
        if topValue > 0:
            resultStr = _ms(strValue, battlesNum=topValue, fromTill=fromTill)
        else:
            resultStr = _ms(strValue, fromTill=fromTill)
        return resultStr

    def _getFromTillPlaceStr(self, formatter, fromPlace, tillPlace):
        strValue = fromPlace
        if fromPlace != tillPlace:
            strValue = _ms(RANKED_BATTLES.TOOLTIP_STEP_FROMTILL, fromPlace=fromPlace, tillPlace=tillPlace)
        return formatter(strValue)

    def _getConditionBlock(self, topValue=0, fromPlaceValue=1, placesCount=0, condition='', conditionTop=''):
        if topValue > 0:
            strValue = conditionTop
            fromPlace = topValue + 1
        else:
            strValue = condition
            fromPlace = fromPlaceValue
        tillPlace = fromPlace + placesCount - 1
        return formatters.packTextBlockData(text_styles.standard(self._getConditionStr(strValue=strValue, topValue=topValue, fromPlace=fromPlace, tillPlace=tillPlace)))

    def _getConditionHeaderBlock(self, strValue):
        return formatters.packTextBlockData(text_styles.middleTitle(strValue), padding=formatters.packPadding(bottom=7))

    def _getOrBlock(self, padding=None):
        return formatters.packTextBlockData(text_styles.hightlight(RANKED_BATTLES.TOOLTIP_STEP_OR), padding=padding)
