# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/hb_efficiency_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.tooltips.common import EfficiencyTooltipData
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.shared.tooltips.efficiency import LinerItemPacker, KillItemPacker
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS

class HBDamageItemPacker(LinerItemPacker):

    def __init__(self):
        super(HBDamageItemPacker, self).__init__(BATTLE_RESULTS.COMMON_TOOLTIP_DAMAGE_HEADER, backport.image(R.images.historical_battles.gui.maps.icons.common.stats.c_48x48.damage()), BATTLE_RESULTS.COMMON_TOOLTIP_DAMAGE_DESCRIPTION)


class HBKillItemPacker(KillItemPacker):

    def __init__(self):
        super(KillItemPacker, self).__init__(BATTLE_RESULTS.COMMON_TOOLTIP_KILL_HEADER, backport.image(R.images.historical_battles.gui.maps.icons.common.stats.c_48x48.kills()), BATTLE_RESULTS.COMMON_TOOLTIP_KILL_1_DESCRIPTION)


class HBAssistItemPacker(LinerItemPacker):

    def __init__(self):
        super(HBAssistItemPacker, self).__init__(BATTLE_RESULTS.COMMON_TOOLTIP_ASSIST_HEADER, backport.image(R.images.historical_battles.gui.maps.icons.common.stats.c_48x48.assist()), BATTLE_RESULTS.COMMON_TOOLTIP_ASSIST_DESCRIPTION)


class HBArmorItemPacker(LinerItemPacker):

    def __init__(self):
        super(HBArmorItemPacker, self).__init__(BATTLE_RESULTS.COMMON_TOOLTIP_ARMOR_HEADER, backport.image(R.images.historical_battles.gui.maps.icons.common.stats.c_48x48.blocked()), BATTLE_RESULTS.COMMON_TOOLTIP_ARMOR_DESCRIPTION)


class HBEfficiencyTooltipData(EfficiencyTooltipData):
    _packers = {BATTLE_EFFICIENCY_TYPES.DAMAGE: HBDamageItemPacker,
     BATTLE_EFFICIENCY_TYPES.DESTRUCTION: HBKillItemPacker,
     BATTLE_EFFICIENCY_TYPES.ASSIST: HBAssistItemPacker,
     BATTLE_EFFICIENCY_TYPES.ARMOR: HBArmorItemPacker}
