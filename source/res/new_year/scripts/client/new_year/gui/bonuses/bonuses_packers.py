# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/bonuses/bonuses_packers.py
import copy
import typing
from gui.impl.backport import createTooltipData
from gui.server_events.awards_formatters import AWARDS_SIZES, EPIC_AWARD_SIZE
from gui.server_events.bonuses import SimpleBonus
from gui.shared.missions.packers.bonus import BaseBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID
from helpers import dependency, int2roman
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.bonus_items_names import BonusItemsNames
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.new_year_toy_icon_bonus_model import NewYearToyIconBonusModel
from new_year.gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.utils.functions import makeTooltip
from shared_utils import first
from gui.impl import backport
from gui.impl.gen import R
from new_year.gui.shared.ny_toy_info import NewYearCurrentToyInfo
from new_year.skeletons.new_year import INewYearController
from new_year_common.items.components.ny_constants import CurrentNYConstants, MIN_TOY_RANK, YEARS_INFO, TOKEN_NY25_MANDARIN
from skeletons.gui.shared import IItemsCache
from NewYearBonusesClient import MandarinsTokenBonus
VEH_COMP_R_ID = R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent()
if typing.TYPE_CHECKING:
    from NewYearBonusesClient import ToyBonus

class NYToyBonusUIPacker(BaseBonusUIPacker):
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _pack(cls, bonus):
        toyId, count = first(bonus.getValue().items())
        return [cls._packSingleBonus(bonus, toyId, count)]

    @classmethod
    def _packSingleBonus(cls, bonus, toyId, count):
        toys = cls.__itemsCache.items.festivity.getToys()
        toyInfo = toys[toyId]
        model = NewYearToyIconBonusModel()
        model.setName(bonus.getName())
        model.setLabel(backport.text(toyInfo.getName()))
        model.setValue(str(count))
        model.setIcon(backport.image(toyInfo.getIcon(cls._getImageSize())))
        model.setRankValue(toyInfo.getRank())
        model.setToyID(toyId)
        model.setIsNew(toyId in bonus.getNewToys())
        model.setAtmosphereBonus(toyInfo.getAtmosphere())
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        toyId = first(bonus.getValue().keys())
        tooltipData = backport.createTooltipData(tooltip={R.views.new_year.lobby.new_year.tooltips.NyDecorationTooltip(): NyDecorationTooltip}, specialArgs=(toyId,))
        return [tooltipData]

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.new_year.lobby.new_year.tooltips.NyDecorationTooltip()]

    @classmethod
    def _getImageSize(cls):
        return AWARDS_SIZES.BIG


class NYToyBonusUIPackerLarge(NYToyBonusUIPacker):

    @classmethod
    def _getImageSize(cls):
        return EPIC_AWARD_SIZE


class NYBoxWithToysBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        hasNewToy = any((toy.getValue().keys()[0] in toy.getNewToys() for toy in cls._getSplitToys(bonus)))
        values = bonus.getToyBonusValues()
        compensationModifier = 1 if CurrentNYConstants.MANDARINS in values else 0
        model = NewYearToyIconBonusModel()
        model.setName(BonusItemsNames.BOX_WITH_TOYS)
        model.setRankValue(cls._getToysRank(bonus))
        model.setValue(str(len(values[CurrentNYConstants.TOYS]) + compensationModifier))
        model.setIsNew(hasNewToy)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        from new_year.gui.impl.lobby.new_year.tooltips.ny_box_with_toys_tooltip import NyBoxWithToysTooltip
        toys = cls._getSplitToys(bonus, withMandarins=True)
        tooltipData = backport.createTooltipData(tooltip={R.views.new_year.lobby.new_year.tooltips.NyBoxWithToysTooltip(): NyBoxWithToysTooltip}, specialArgs=(toys,))
        return [tooltipData]

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.new_year.lobby.new_year.tooltips.NyBoxWithToysTooltip()]

    @classmethod
    def _getImageSize(cls):
        return AWARDS_SIZES.BIG

    @classmethod
    def _getSplitToys(cls, bonus, withMandarins=False):
        toys = []
        values = bonus.getToyBonusValues()
        for value in values[CurrentNYConstants.TOYS]:
            toy = copy.deepcopy(bonus)
            toy.setValue(value)
            toys.append(toy)

        if CurrentNYConstants.MANDARINS in values and withMandarins:
            toys.append(MandarinsTokenBonus(CurrentNYConstants.MANDARINS, {TOKEN_NY25_MANDARIN: {'count': values[CurrentNYConstants.MANDARINS]}}, isCompensation=True))
        return toys

    @classmethod
    def _getToysRank(cls, bonus):
        anyOfToys = bonus.getToyBonusValues()[CurrentNYConstants.ANY_OF]
        specificToys = bonus.getToyBonusValues()[CurrentNYConstants.TOYS]
        anyOfRanks = set((rank for _, _, rank in anyOfToys))
        specificToyRanks = set((NewYearCurrentToyInfo(toy.keys()[0]).getRank() for toy in specificToys))
        allRanks = anyOfRanks.union(specificToyRanks)
        return first(allRanks) if len(allRanks) == 1 else -1


class NYMysteryBoxWithToysBonusUIPacker(NYBoxWithToysBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = NewYearToyIconBonusModel()
        model.setName(BonusItemsNames.BOX_WITH_TOYS)
        model.setLabel(backport.text(R.strings.ny.boxWithToys.tooltip.rewards()))
        model.setRankValue(cls._getToysRank(bonus))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        allToysRank = cls._getToysRank(bonus)
        ranks = toRomanRangeString(range(MIN_TOY_RANK, YEARS_INFO.currYearMaxToyRank() + 1)) if allToysRank == -1 else int2roman(allToysRank)
        return [createTooltipData(makeTooltip(header=backport.text(R.strings.ny.boxWithToys.tooltip.title(), rank=ranks), body=backport.text(R.strings.ny.boxWithToys.tooltip.description())))]

    @classmethod
    def _getContentId(cls, bonus):
        return [BACKPORT_TOOLTIP_CONTENT_ID]
