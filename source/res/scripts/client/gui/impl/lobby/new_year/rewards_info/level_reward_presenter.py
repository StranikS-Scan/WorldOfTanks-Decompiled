# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/rewards_info/level_reward_presenter.py
import copy
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_rewards_renderer_model import NewYearRewardsRendererModel
from gui.impl.lobby.new_year.tooltips.ny_additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.lobby.new_year.tooltips.ny_marketplace_token_tooltip import NyMarketplaceTokenTooltip
from gui.impl.lobby.new_year.tooltips.ny_menu_collections_tooltip import NyMenuCollectionsTooltip
from gui.impl.lobby.new_year.tooltips.ny_shards_tooltip import NyShardsTooltip
from gui.impl.new_year.new_year_bonus_packer import getNewYearBonusPacker, packBonusModelAndTooltipData
from gui.impl.new_year.new_year_helper import formatRomanNumber, IS_ROMAN_NUMBERS_ALLOWED, nyBonusGFSortOrder
from gui.server_events.bonuses import splitBonuses
from gui.server_events.recruit_helper import DEFAULT_NY_GIRL
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from new_year.ny_level_helper import LevelInfo
    from gui.server_events.bonuses import SimpleBonus

class LevelRewardPresenter(object):
    __slots__ = ('__index', '__levelInfo', '__tooltips', '__bonuses')
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, index, level):
        self.__index = index
        self.__levelInfo = self.__nyController.getLevel(level)
        self.__tooltips = {}
        self.__bonuses = []

    def createToolTipData(self, tooltipId):
        if tooltipId is None:
            return
        else:
            tooltipData = self.__tooltips.get(tooltipId)
            if self.__levelInfo.hasTankman() and tooltipData is not None and tooltipData.specialAlias == TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED and not self.__levelInfo.isAchieved():
                tooltipData = TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[DEFAULT_NY_GIRL, True])
            return tooltipData

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyMenuCollectionsTooltip():
            return NyMenuCollectionsTooltip()
        elif contentID == R.views.lobby.new_year.tooltips.NyShardsTooltip():
            return NyShardsTooltip()
        elif contentID == R.views.lobby.new_year.tooltips.NyMarketplaceTokenTooltip():
            return NyMarketplaceTokenTooltip()
        elif contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = int(event.getArgument('showedCount'))
            return AdditionalRewardsTooltip(self.__bonuses[showCount:])
        elif R.views.dyn('gui_lootboxes').isValid() and contentID == R.views.dyn('gui_lootboxes').lobby.gui_lootboxes.tooltips.LootboxTooltip():
            tooltipData = self.__tooltips[event.getArgument('tooltipId')]
            return tooltipData.tooltip(*tooltipData.specialArgs)
        else:
            return None

    def getRenderer(self):
        renderer = NewYearRewardsRendererModel()
        renderer.setIdx(self.__index)
        renderer.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
        self.updateRenderer(renderer)
        self.__makeRewardsGroup(renderer)
        return renderer

    def updateRenderer(self, renderer):
        with renderer.transaction() as tx:
            tx.setIsCurrentLevel(self.__levelInfo.isMaxReachedLevel())
            tx.setIsLevelAchieved(self.__levelInfo.isAchieved())
            tx.setLevelText(formatRomanNumber(self.__levelInfo.level()))
        self.__makeRewardsGroup(renderer)

    def clear(self):
        self.__levelInfo = None
        self.__tooltips.clear()
        return

    def __makeRewardsGroup(self, renderer):
        rewardModelsList = renderer.rewardsGroup.getItems()
        rewardModelsList.clear()
        self.__tooltips.clear()
        self.__bonuses = copy.deepcopy(self.__levelInfo.getBonuses())
        self.__bonuses = [ bonus for bonus in splitBonuses(self.__bonuses) if bonus.isShowInGUI() ]
        self.__bonuses.sort(key=nyBonusGFSortOrder)
        packBonusModelAndTooltipData(self.__bonuses, rewardModelsList, getNewYearBonusPacker(), self.__tooltips)
        rewardModelsList.invalidate()
