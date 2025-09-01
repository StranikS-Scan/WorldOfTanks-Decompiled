# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/tooltips/otg_equipment_set_tooltip_view.py
from gui.impl.gen import R
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip

class OTGEquipmentSetTooltipView(AdditionalRewardsTooltip):

    @classmethod
    def _getHeader(cls):
        return R.strings.one_time_gift.equipmentSet.tooltip.header()
