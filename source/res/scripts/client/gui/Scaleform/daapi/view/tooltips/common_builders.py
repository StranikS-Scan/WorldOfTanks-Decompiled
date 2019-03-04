# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/common_builders.py
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import advanced
from gui.shared.tooltips import common
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder, DefaultFormatBuilder, SimpleBuilder, AdvancedDataBuilder
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
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.ACTION_XP, TOOLTIPS_CONSTANTS.COMPLEX_UI, common.ActionXPTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.QUESTS_VEHICLE_BONUSES, TOOLTIPS_CONSTANTS.COLUMN_FIELDS_UI, common.QuestVehiclesBonusTooltipData(contexts.QuestContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.ENVIRONMENT, TOOLTIPS_CONSTANTS.ENVIRONMENT_UI, common.EnvironmentTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SQUAD_RESTRICTIONS_INFO, TOOLTIPS_CONSTANTS.SQUAD_RESTRICTIONS_INFO_UI, common.SquadRestrictionsInfo(contexts.SquadRestrictionContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.MISSIONS_TOKEN, TOOLTIPS_CONSTANTS.MISSIONS_TOKEN_UI, common.MissionsToken(contexts.QuestContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.RESERVE_MODULE, TOOLTIPS_CONSTANTS.REF_SYS_RESERVES_UI, common.ReserveTooltipData(contexts.ReserveContext())),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.CRYSTAL, TOOLTIPS_CONSTANTS.CRYSTAL_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.CREDITS, TOOLTIPS_CONSTANTS.CREDITS_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.GOLD, TOOLTIPS_CONSTANTS.GOLD_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedHeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.FREE_XP, TOOLTIPS_CONSTANTS.FREEXP_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     DataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_FILTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, VehicleFilterTooltip(contexts.TechCustomizationContext())),
     SimpleBuilder(TOOLTIPS_CONSTANTS.RSS_NEWS, TOOLTIPS_CONSTANTS.RSS_NEWS_UI),
     DataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_ELITE_BONUS, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, common.VehicleEliteBonusTooltipData(contexts.VehicleEliteBonusContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.VEHICLE_HISTORICAL_REFERENCE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, common.VehicleHistoricalReferenceTooltipData(contexts.VehicleHistoricalReferenceContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.BATTLE_TRAINING, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, common.BattleTraining(contexts.ToolTipContext(None)), advanced.BattleTraining(contexts.ToolTipContext(None))))


class HeaderMoneyAndXpBuilder(DataBuilder):
    __slots__ = ('__btnType',)

    def __init__(self, btnType, tooltipType, linkage):
        super(HeaderMoneyAndXpBuilder, self).__init__(tooltipType, linkage, common.HeaderMoneyAndXpTooltipData(contexts.ToolTipContext(None)))
        self.__btnType = btnType
        return

    def _buildData(self, _advanced, *args, **kwargs):
        return super(HeaderMoneyAndXpBuilder, self)._buildData(_advanced, self.__btnType)


class AdvancedHeaderMoneyAndXpBuilder(AdvancedDataBuilder):
    __slots__ = ('__btnType',)

    def __init__(self, btnType, tooltipType, linkage):
        super(AdvancedHeaderMoneyAndXpBuilder, self).__init__(tooltipType, linkage, common.HeaderMoneyAndXpTooltipData(contexts.ToolTipContext(None)), advanced.MoneyAndXpAdvanced(contexts.ToolTipContext(None)))
        self.__btnType = btnType
        return

    def _buildData(self, _advanced, *args, **kwargs):
        return super(AdvancedHeaderMoneyAndXpBuilder, self)._buildData(_advanced, self.__btnType)
