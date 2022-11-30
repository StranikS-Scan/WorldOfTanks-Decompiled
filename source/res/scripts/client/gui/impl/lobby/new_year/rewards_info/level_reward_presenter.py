# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/rewards_info/level_reward_presenter.py
import copy
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_rewards_renderer_model import NewYearRewardsRendererModel
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.impl.lobby.new_year.tooltips.ny_guest_dog_token_tooltip import NyGuestDogTokenTooltip
from gui.impl.lobby.new_year.tooltips.ny_marketplace_token_tooltip import NyMarketplaceTokenTooltip
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.new_year.new_year_bonus_packer import getNewYearBonusPacker, packBonusModelAndTooltipData
from gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED, formatRomanNumber, ADDITIONAL_BONUS_NAME_GETTERS, BLUEPRINT_NATION_ORDER, CREEBOOK_NATION_ORDER
from gui.server_events.bonuses import splitBonuses
from gui.server_events.recruit_helper import DEFAULT_NY_GIRL
from helpers import dependency
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items.components.ny_constants import Ny23CoinToken, NyATMReward
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from typing import Dict, List
    from new_year.ny_level_helper import LevelInfo
    from gui.server_events.bonuses import SimpleBonus
_BONUSES_ORDER_GF = (Ny23CoinToken.TYPE,
 'vehicles',
 NyATMReward.DOG,
 'tmanToken',
 'customizations_style',
 NyATMReward.MARKETPLACE,
 CREW_BOOK_RARITY.PERSONAL,
 'playerBadges',
 'singleAchievements') + CREEBOOK_NATION_ORDER + (CREW_BOOK_RARITY.CREW_RARE,
 CREW_BOOK_RARITY.UNIVERSAL,
 'crewBooks',
 'booster_credits',
 'booster_xp',
 'booster_crew_xp',
 'slots') + BLUEPRINT_NATION_ORDER + ('BlueprintNationFragmentCongrats', 'BlueprintUniversalFragmentCongrats')

def _nyLevelBonusesSortOrder(bonus):
    bonusName = bonus.getName()
    getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
    if getAdditionalName is not None:
        bonusName = getAdditionalName(bonus)
    return _BONUSES_ORDER_GF.index(bonusName) if bonusName in _BONUSES_ORDER_GF else len(_BONUSES_ORDER_GF)


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
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = int(event.getArgument('showedCount'))
            bonusPackers = getNewYearBonusPacker()
            bonuses = self.__bonuses[showCount:]
            packedBonuses = []
            for bonus in bonuses:
                if bonus.isShowInGUI():
                    bonusList = bonusPackers.pack(bonus)
                    for item in bonusList:
                        packedBonuses.append(item)

            return AdditionalRewardsTooltip(packedBonuses)
        elif event.contentID == R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip():
            return NyGiftMachineTokenTooltip()
        elif event.contentID == R.views.lobby.new_year.tooltips.NyGuestDogTokenTooltip():
            return NyGuestDogTokenTooltip()
        else:
            return NyMarketplaceTokenTooltip() if event.contentID == R.views.lobby.new_year.tooltips.NyMarketplaceTokenTooltip() else None

    def getRenderer(self):
        renderer = NewYearRewardsRendererModel()
        renderer.setIdx(self.__index)
        renderer.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
        self.updateRenderer(renderer)
        self.__makeRewardsGroup(renderer)
        return renderer

    def updateRenderer(self, renderer):
        with renderer.transaction() as tx:
            tx.setIsCurrentLevel(self.__levelInfo.isCurrent())
            tx.setIsLevelAchieved(self.__levelInfo.isAchieved())
            tx.setLevelText(formatRomanNumber(self.__levelInfo.level()))

    def clear(self):
        self.__levelInfo = None
        self.__tooltips.clear()
        return

    def __makeRewardsGroup(self, renderer):
        rewardModelsList = renderer.rewardsGroup.getItems()
        rewardModelsList.clear()
        self.__tooltips.clear()
        self.__bonuses = copy.deepcopy(self.__levelInfo.getBonuses())
        self.__bonuses = splitBonuses(self.__bonuses)
        self.__bonuses.sort(key=_nyLevelBonusesSortOrder)
        packBonusModelAndTooltipData(self.__bonuses, rewardModelsList, getNewYearBonusPacker(), self.__tooltips)
