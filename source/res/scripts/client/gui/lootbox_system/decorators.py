# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/decorators.py
from typing import TYPE_CHECKING
from constants import IS_DEVELOPMENT
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.lobby.lootbox_system.tooltips.box_tooltip import BoxTooltip
from gui.impl.lobby.lootbox_system.tooltips.guaranteed_reward_info_tooltip import GuaranteedRewardInfoTooltip
from gui.impl.lobby.lootbox_system.tooltips.random_national_bonus_tooltip_view import RandomNationalBonusTooltipView
from gui.impl.lobby.lootbox_system.tooltips.statistics_category_tooltip import StatisticsCategoryTooltipView
if TYPE_CHECKING:
    from typing import Optional
    from gui.impl.backport import TooltipData

def onNotImplementedCall(callName, taskID):
    message = '"{}" is not implemented, will done in "{}"'.format(callName, taskID)
    if IS_DEVELOPMENT:
        SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Error)


def createTooltipContentDecorator():

    def decorator(func):

        def wrapper(self, event, contentID):
            if contentID == R.views.lobby.lootbox_system.tooltips.GuaranteedRewardInfoTooltip():
                return GuaranteedRewardInfoTooltip(event.getArgument('category'))
            elif contentID == R.views.lobby.lootbox_system.tooltips.BoxTooltip():
                return BoxTooltip(event.getArgument('boxCategory'))
            elif contentID == R.views.lobby.lootbox_system.tooltips.StatisticsCategoryTooltipView():
                return StatisticsCategoryTooltipView(event.getArgument('bonusesCategory'))
            else:
                tooltipData = getattr(self, 'getTooltipData', lambda _: None)(event)
                if tooltipData is not None:
                    if contentID == R.views.lobby.awards.tooltips.RewardCompensationTooltip():
                        compTooltipData = {'iconBefore': event.getArgument('iconBefore', ''),
                         'labelBefore': event.getArgument('labelBefore', ''),
                         'iconAfter': event.getArgument('iconAfter', ''),
                         'labelAfter': event.getArgument('labelAfter', ''),
                         'bonusName': event.getArgument('bonusName', ''),
                         'countBefore': event.getArgument('countBefore', 1),
                         'tooltipType': LootBoxCompensationTooltipTypes.VEHICLE}
                        compTooltipData.update(tooltipData.specialArgs)
                        settings = ViewSettings(R.views.lobby.awards.tooltips.RewardCompensationTooltip(), model=LootBoxVehicleCompensationTooltipModel(), kwargs=compTooltipData)
                        return VehicleCompensationTooltipContent(settings)
                    if contentID == R.views.lobby.lootbox_system.tooltips.RandomNationalBonusTooltipView():
                        return RandomNationalBonusTooltipView(*tooltipData.specialArgs)
                return func(self, event, contentID)

        return wrapper

    return decorator
