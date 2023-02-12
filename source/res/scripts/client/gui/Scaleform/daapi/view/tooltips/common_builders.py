# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/common_builders.py
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import advanced, common, contexts, stronghold
from gui.shared.tooltips.builders import AdvancedDataBuilder, DataBuilder, DefaultFormatBuilder, TooltipWindowBuilder
from gui.shared.tooltips.dog_tags import DogTagInfoTooltip
from gui.shared.tooltips.filter import VehicleFilterTooltip
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EFFICIENCY_PARAM, TOOLTIPS_CONSTANTS.FINAL_STSTS_UI, common.EfficiencyTooltipData(contexts.FinalStatisticContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.IGR_INFO, TOOLTIPS_CONSTANTS.IGR_INFO_UI, common.IgrTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.CONTACT, TOOLTIPS_CONSTANTS.CONTACT_UI, common.ContactTooltipData(contexts.ContactContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SORTIE_DIVISION, TOOLTIPS_CONSTANTS.SORTIE_DIVISION_UI, common.SortieDivisionTooltipData(contexts.FortificationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.MAP, TOOLTIPS_CONSTANTS.MAP_UI, common.MapTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.MAP_SMALL, TOOLTIPS_CONSTANTS.MAP_SMALL_UI, common.MapSmallTooltipData(contexts.FortificationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.CLAN_COMMON_INFO, TOOLTIPS_CONSTANTS.CLAN_COMMON_INFO_UI, common.ClanCommonInfoTooltipData(contexts.HangarContext())),
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.ACTION_PRICE, TOOLTIPS_CONSTANTS.COMPLEX_UI, common.ActionTooltipData(contexts.HangarContext())),
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.ACTION_SLOT_PRICE, TOOLTIPS_CONSTANTS.COMPLEX_UI, common.ActionSlotTooltipData(contexts.HangarContext())),
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.PRICE_DISCOUNT, TOOLTIPS_CONSTANTS.COMPLEX_UI, common.PriceDiscountTooltipData(contexts.HangarContext())),
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.FRONTLINE_PRICE_DISCOUNT, TOOLTIPS_CONSTANTS.COMPLEX_UI, common.FrontlineDiscountTooltipData(contexts.HangarContext())),
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.ACTION_XP, TOOLTIPS_CONSTANTS.COMPLEX_UI, common.ActionXPTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.QUESTS_VEHICLE_BONUSES, TOOLTIPS_CONSTANTS.COLUMN_FIELDS_UI, common.QuestVehiclesBonusTooltipData(contexts.QuestContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.ENVIRONMENT, TOOLTIPS_CONSTANTS.ENVIRONMENT_UI, common.EnvironmentTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.MISSIONS_TOKEN, TOOLTIPS_CONSTANTS.MISSIONS_TOKEN_UI, common.MissionsToken(contexts.QuestContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.OLD_RESERVE_MODULE, TOOLTIPS_CONSTANTS.REF_SYS_RESERVES_UI, common.ReserveTooltipData(contexts.ReserveContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.RESERVE_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, stronghold.ReserveTooltipData(contexts.ReserveContext())),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.CRYSTAL, TOOLTIPS_CONSTANTS.CRYSTAL_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.EVENT_COIN, TOOLTIPS_CONSTANTS.EVENT_COIN_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.CREDITS, TOOLTIPS_CONSTANTS.CREDITS_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.GOLD, TOOLTIPS_CONSTANTS.GOLD_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.BPCOIN, TOOLTIPS_CONSTANTS.BPCOIN_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.FREE_XP, TOOLTIPS_CONSTANTS.FREEXP_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.GOLD, TOOLTIPS_CONSTANTS.GOLD_INFO_FULL_SCREEN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, True),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.CREDITS, TOOLTIPS_CONSTANTS.CREDITS_INFO_FULL_SCREEN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, True),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.CRYSTAL, TOOLTIPS_CONSTANTS.CRYSTAL_INFO_FULL_SCREEN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, True),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.FREE_XP, TOOLTIPS_CONSTANTS.FREEXP_INFO_FULL_SCREEN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, True),
     HeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.BRCOIN, TOOLTIPS_CONSTANTS.BRCOIN_INFO_FULL_SCREEN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, True),
     HeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.EQUIP_COIN, TOOLTIPS_CONSTANTS.EQUIP_COIN_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, True),
     HeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.EQUIP_COIN, TOOLTIPS_CONSTANTS.EQUIP_COIN_INFO_FULL_SCREEN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, True),
     DataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_FILTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, VehicleFilterTooltip(contexts.TechCustomizationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_ELITE_BONUS, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, common.VehicleEliteBonusTooltipData(contexts.VehicleEliteBonusContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_HISTORICAL_REFERENCE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, common.VehicleHistoricalReferenceTooltipData(contexts.VehicleHistoricalReferenceContext())),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.SQUAD_BONUS, None, common.SquadBonusTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.BATTLE_PASS_VEHICLE_POINTS, None, common.VehiclePointsTooltipContentWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.BATTLE_PASS_NOT_STARTED, None, common.BattlePassNotStartedTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.BATTLE_PASS_IN_PROGRESS, None, common.BattlePassInProgressTooltipContentWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.BATTLE_PASS_COMPLETED, None, common.BattlePassCompletedTooltipContentWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.BATTLE_PASS_NO_CHAPTER, None, common.BattlePassNoChapterTooltipWindowData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.TECHTREE_DISCOUNT_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, common.TechTreeDiscountInfoTooltip(contexts.QuestContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TECHTREE_NATION_DISCOUNT, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, common.TechTreeNationDiscountTooltip(contexts.TechTreeContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.DOG_TAGS_INFO, TOOLTIPS_CONSTANTS.DOG_TAGS_INFO_UI, DogTagInfoTooltip(contexts.DogTagInfoContext())),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.VEH_POST_PROGRESSION_ENTRY_POINT, None, common.VehPostProgressionEntryPointTooltipContentWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.WOT_PLUS, None, common.WotPlusTooltipContentWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.ADDITIONAL_REWARDS, None, common.AdditionalRewardsTooltipContentWindowData(contexts.ToolTipContext(None))))


class HeaderMoneyAndXpBuilder(DataBuilder):
    __slots__ = ('__btnType', '__hideActionBlock')

    def __init__(self, btnType, tooltipType, linkage, hideActionBlock=False):
        super(HeaderMoneyAndXpBuilder, self).__init__(tooltipType, linkage, common.HeaderMoneyAndXpTooltipData(contexts.ToolTipContext(None)))
        self.__btnType = btnType
        self.__hideActionBlock = hideActionBlock
        return

    def _buildData(self, _advanced, *args, **kwargs):
        return super(HeaderMoneyAndXpBuilder, self)._buildData(_advanced, self.__btnType, self.__hideActionBlock)


class AdvancedHeaderMoneyAndXpBuilder(AdvancedDataBuilder):
    __slots__ = ('__btnType', '__hideActionBlock')

    def __init__(self, btnType, tooltipType, linkage, hideActionBlock=False):
        super(AdvancedHeaderMoneyAndXpBuilder, self).__init__(tooltipType, linkage, common.HeaderMoneyAndXpTooltipData(contexts.ToolTipContext(None)), advanced.MoneyAndXpAdvanced(contexts.ToolTipContext(None)))
        self.__btnType = btnType
        self.__hideActionBlock = hideActionBlock
        return

    def _buildData(self, _advanced, *args, **kwargs):
        return super(AdvancedHeaderMoneyAndXpBuilder, self)._buildData(_advanced, self.__btnType, self.__hideActionBlock)
