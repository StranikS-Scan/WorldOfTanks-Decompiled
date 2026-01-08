# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/base/decorators.py
from typing import TYPE_CHECKING
from gui.impl import backport
from constants import IS_DEVELOPMENT
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.lobby.crew.tooltips.mentoring_license_tooltip import MentoringLicenseTooltip
from gui.impl.lobby.battle_pass.tooltips.battle_pass_coin_tooltip_view import BattlePassCoinTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_taler_tooltip import BattlePassTalerTooltip
from gui.impl.lobby.lootbox_system.base.tooltips.box_tooltip import BoxTooltip, BoxCompensationTooltip
from gui.impl.lobby.lootbox_system.base.tooltips.guaranteed_reward_info_tooltip import GuaranteedRewardInfoTooltip
from gui.impl.lobby.lootbox_system.base.tooltips.random_national_bonus_tooltip_view import RandomNationalBonusTooltipView
from gui.impl.lobby.lootbox_system.base.tooltips.statistics_category_tooltip import StatisticsCategoryTooltipView
from gui.impl.lobby.personal_reserves.quest_booster_tooltip import QuestBoosterTooltip
if TYPE_CHECKING:
    from typing import Optional
    from gui.impl.backport import TooltipData

def onNotImplementedCall(callName, taskID):
    message = '"{}" is not implemented, will done in "{}"'.format(callName, taskID)
    if IS_DEVELOPMENT:
        SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Error)


def createBackportTooltipDecorator():

    def decorator(func):

        def wrapper(self, event):
            if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                tooltipData = self.getTooltipData(event)
                if tooltipData is None:
                    return
                window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
                if window is None:
                    return
                window.load()
                return window
            else:
                return func(self, event)

        return wrapper

    return decorator


def createTooltipContentDecorator():

    def decorator(func):

        def wrapper(self, event, contentID):
            if contentID == R.views.mono.lootbox.tooltips.guaranteed_reward_info():
                return GuaranteedRewardInfoTooltip(event.getArgument('category'), event.getArgument('eventName'))
            elif contentID == R.views.mono.lootbox.tooltips.box_tooltip():
                return BoxTooltip(event.getArgument('boxCategory'), event.getArgument('eventName'))
            elif contentID == R.views.mono.lootbox.tooltips.statistics_category():
                return StatisticsCategoryTooltipView(event.getArgument('bonusesCategory'), event.getArgument('eventName'))
            elif contentID == R.views.lobby.battle_pass.tooltips.BattlePassCoinTooltipView():
                return BattlePassCoinTooltipView()
            elif contentID == R.views.lobby.battle_pass.tooltips.BattlePassTalerTooltip():
                return BattlePassTalerTooltip()
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
                if contentID == R.views.mono.lootbox.tooltips.random_national_bonus():
                    return RandomNationalBonusTooltipView(*tooltipData.specialArgs)
            if contentID == R.views.mono.lootbox.tooltips.box_compensation():
                if tooltipData is None:
                    return
                return BoxCompensationTooltip(*tooltipData.specialArgs)
            elif contentID == R.views.lobby.crew.tooltips.MentoringLicenseTooltip():
                return MentoringLicenseTooltip(*tooltipData.specialArgs)
            else:
                return QuestBoosterTooltip(*tooltipData.specialArgs) if contentID == R.views.lobby.personal_reserves.QuestBoosterTooltip() else func(self, event, contentID)

        return wrapper

    return decorator
