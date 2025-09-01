# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/shared/tooltips/comp7_tooltips.py
import logging
from comp7.gui.shared.tooltips import TOOLTIP_TYPE
from comp7_common_const import offerRewardGiftToken
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.game_control import IComp7Controller
from comp7_core.gui.shared.tooltips.comp7_core_tooltips import RoleSkillLobbyTooltipData, RoleSkillBattleTooltipData
_logger = logging.getLogger(__name__)

class BattleResultsRatingPointsTooltip(BlocksTooltipData):

    def __init__(self, ctx):
        super(BattleResultsRatingPointsTooltip, self).__init__(ctx, None)
        self._setContentMargin(top=14, left=20, bottom=10, right=20)
        self._setMargins(afterBlock=10)
        self._setWidth(350)
        return

    def _packBlocks(self, *args):
        items = super(BattleResultsRatingPointsTooltip, self)._packBlocks()
        items.append(self.__packHeaderBlock())
        items.append(self.__packDescriptionBlock())
        return items

    def __packHeaderBlock(self):
        blocks = [formatters.packTextBlockData(text_styles.highTitle(backport.text(R.strings.comp7_ext.battleResult.personal.tooltip.title()))), formatters.packTextBlockData(text_styles.main(backport.text(R.strings.comp7_ext.battleResult.personal.tooltip.descr())))]
        return formatters.packBuildUpBlockData(blocks=blocks)

    def __packDescriptionBlock(self):
        blocks = [formatters.packTextBlockData(text_styles.alert(backport.text(R.strings.comp7_ext.battleResult.personal.tooltip.loseTitle())), padding=formatters.packPadding(top=-6, bottom=4)), formatters.packTextBlockData(text_styles.main(backport.text(R.strings.comp7_ext.battleResult.personal.tooltip.loseDescr())))]
        return formatters.packBuildUpBlockData(blocks=blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)


class BattleResultsTournamentRatingPointsTooltip(BlocksTooltipData):

    def __init__(self, ctx):
        super(BattleResultsTournamentRatingPointsTooltip, self).__init__(ctx, None)
        self._setContentMargin(top=14, left=20, bottom=10, right=20)
        self._setMargins(afterBlock=10)
        self._setWidth(350)
        return

    def _packBlocks(self, *args):
        items = super(BattleResultsTournamentRatingPointsTooltip, self)._packBlocks()
        items.append(self.__packHeaderBlock())
        return items

    def __packHeaderBlock(self):
        blocks = [formatters.packTextBlockData(text_styles.highTitle(backport.text(R.strings.comp7_ext.battleResult.personal.tooltip.title()))), formatters.packTextBlockData(text_styles.main(backport.text(R.strings.comp7_ext.tournament.battleResult.personal.tooltip.descr())))]
        return formatters.packBuildUpBlockData(blocks=blocks)


class BattleResultsTrainingRatingPointsTooltip(BlocksTooltipData):

    def __init__(self, ctx):
        super(BattleResultsTrainingRatingPointsTooltip, self).__init__(ctx, None)
        self._setContentMargin(top=14, left=20, bottom=10, right=20)
        self._setMargins(afterBlock=10)
        self._setWidth(350)
        return

    def _packBlocks(self, *args):
        items = super(BattleResultsTrainingRatingPointsTooltip, self)._packBlocks()
        items.append(self.__packHeaderBlock())
        return items

    def __packHeaderBlock(self):
        blocks = [formatters.packTextBlockData(text_styles.highTitle(backport.text(R.strings.comp7_ext.battleResult.personal.tooltip.title()))), formatters.packTextBlockData(text_styles.main(backport.text(R.strings.comp7_ext.training.battleResult.personal.tooltip.descr())))]
        return formatters.packBuildUpBlockData(blocks=blocks)


class Comp7SelectableRewardTooltip(BlocksTooltipData):
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self, context):
        super(Comp7SelectableRewardTooltip, self).__init__(context, TOOLTIP_TYPE.COMP7_SELECTABLE_REWARD)
        self._setContentMargin(top=20, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(370)

    def _packBlocks(self, token, **kwargs):
        self._items = super(Comp7SelectableRewardTooltip, self)._packBlocks(token, **kwargs)
        _, _, tokenCategory = token.split(':')
        giftTokenCategory = offerRewardGiftToken(tokenCategory)
        self._items.append(self.__packImageBlock(giftTokenCategory))
        self._items.append(self.__packRewardsBlock(tokenCategory))
        return self._items

    @staticmethod
    def __packImageBlock(giftTokenCategory):
        return formatters.packImageBlockData(img=backport.image(R.images.comp7.gui.maps.icons.icons.dyn(giftTokenCategory)()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    @staticmethod
    def __packRewardsBlock(tokenCategory):
        blocks = [formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.selectable_reward.tabs.items.dyn(tokenCategory)())), padding={'bottom': 10})]
        selectableRewardList = R.strings.comp7_ext.rewardSelection.tooltip.selectableRewardList.dyn(tokenCategory)()
        if selectableRewardList:
            blocks.append(formatters.packTextBlockData(text=text_styles.main(backport.text(selectableRewardList))))
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)


class Comp7RoleSkillLobbyTooltipData(RoleSkillLobbyTooltipData):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @property
    def _modeController(self):
        return self.__comp7Controller


class Comp7RoleSkillBattleTooltipData(RoleSkillBattleTooltipData):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @property
    def _modeController(self):
        return self.__comp7Controller
