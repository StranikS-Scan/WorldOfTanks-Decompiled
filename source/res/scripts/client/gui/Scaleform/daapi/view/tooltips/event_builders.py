# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/event_builders.py
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.secret_event.hangar_3dobject_tooltip import Hangar3DObjectTooltipData
from gui.shared.tooltips import advanced
from gui.shared.tooltips import common
from gui.shared.tooltips import contexts
from gui.shared.tooltips import event
from gui.shared.tooltips.builders import DataBuilder, TooltipWindowBuilder, AdvancedDataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EVENT_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventSelectorWarningTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_VEHICLE_PREVIEW_MESSAGE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventGeneralIInfoData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_SQUAD_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventSquadTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_SUBDIVISION_PUMPING_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventSubdivisionPumpingTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SECRET_EVENT_QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretQuestsPreviewTooltipData(contexts.QuestsBoosterContext())),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.SECRET_EVENT_HANGAR_OBJECT, None, Hangar3DObjectTooltipData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_RESULT_GENERAL, None, event.EventResultGeneralContentWindowData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BANNER_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventBannerInfoTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.COMMANDER_ABILITY_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventCommanderSkillTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.COMMANDER_RESPAWN_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventCommanderReviveSkillTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_PROGRESSION_POINTS_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventPointsInfoTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_SQUAD_GENERAL_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventSquadGeneralInfo(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_RESULT_KILL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.BattleResultKillTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_RESULT_DAMAGE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.BattleResultDamageTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_RESULT_ARMOR, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.BattleResultArmorTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_RESULT_ASSIST, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.BattleResultAssistTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.SECRET_EVENT_PROGRESSION_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventProgressionTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_RESULT_MISSION, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.BattleResultMissionTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_ENERGY_DISCOUNT, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventEnergyDiscount(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BONUSES_BASIC_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventBonusBasicTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BONUSES_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventBonusHangarData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BONUSES_POST_BATTLE_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.SecretEventBonusPostBattleTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, event.EventVehicleInfoTooltipData(contexts.AwardContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.COMMANDER_CHARACTERISTICS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventCommanderCharacteristicsTooltipData(contexts.ToolTipContext(None))),
     EventAdvancedDataBuilder(CURRENCIES_CONSTANTS.GOLD, TOOLTIPS_CONSTANTS.EVENT_GOLD_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     EventAdvancedDataBuilder(CURRENCIES_CONSTANTS.CREDITS, TOOLTIPS_CONSTANTS.EVENT_CREDIT_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     EventAdvancedDataBuilder(CURRENCIES_CONSTANTS.CRYSTAL, TOOLTIPS_CONSTANTS.EVENT_CRYSTAL_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     EventAdvancedDataBuilder(CURRENCIES_CONSTANTS.FREE_XP, TOOLTIPS_CONSTANTS.EVENT_FREE_XP_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI))


class EventAdvancedDataBuilder(AdvancedDataBuilder):
    __slots__ = ('__btnType',)

    def __init__(self, btnType, tooltipType, linkage):
        super(EventAdvancedDataBuilder, self).__init__(tooltipType, linkage, common.EventHeaderMoneyAndXpTooltipData(contexts.ToolTipContext(None)), advanced.MoneyAndXpAdvanced(contexts.ToolTipContext(None)))
        self.__btnType = btnType
        return

    def _buildData(self, _advanced, *args, **kwargs):
        return super(EventAdvancedDataBuilder, self)._buildData(_advanced, self.__btnType)
