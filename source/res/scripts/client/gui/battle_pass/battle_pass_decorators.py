# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_decorators.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.tooltips.battle_pass_coin_tooltip_view import BattlePassCoinTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_gold_mission_tooltip_view import BattlePassGoldMissionTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_lock_icon_tooltip_view import BattlePassLockIconTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_points_view import BattlePassPointsTooltip
from gui.impl.lobby.battle_pass.tooltips.battle_pass_quests_chain_tooltip_view import BattlePassQuestsChainTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_taler_tooltip import BattlePassTalerTooltip
from gui.impl.lobby.battle_pass.tooltips.battle_pass_upgrade_style_tooltip_view import BattlePassUpgradeStyleTooltipView
from gui.impl.lobby.battle_pass.tooltips.random_quest_tooltip import RandomQuestTooltip
from gui.impl.lobby.lootbox_system.base.tooltips.box_tooltip import BoxTooltip
if typing.TYPE_CHECKING:
    from gui.impl.backport import TooltipData

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
            tooltipData = self.getTooltipData(event)
            if contentID == R.views.lobby.battle_pass.tooltips.BattlePassGoldMissionTooltipView():
                if tooltipData is None:
                    return
                return BattlePassGoldMissionTooltipView(*tooltipData.specialArgs)
            elif contentID == R.views.lobby.battle_pass.tooltips.BattlePassUpgradeStyleTooltipView():
                if tooltipData is None:
                    return
                return BattlePassUpgradeStyleTooltipView(*tooltipData.specialArgs)
            elif contentID == R.views.lobby.battle_pass.tooltips.BattlePassQuestsChainTooltipView():
                if tooltipData is None:
                    return
                return BattlePassQuestsChainTooltipView(*tooltipData.specialArgs)
            elif contentID == R.views.lobby.battle_pass.tooltips.RandomQuestTooltip():
                if event.hasArgument('tokenID'):
                    return RandomQuestTooltip(event.getArgument('tokenID'))
                if tooltipData is None:
                    return
                return RandomQuestTooltip(*tooltipData.specialArgs)
            elif contentID == R.views.lobby.battle_pass.tooltips.BattlePassCoinTooltipView():
                return BattlePassCoinTooltipView()
            elif contentID == R.views.lobby.battle_pass.tooltips.BattlePassPointsView():
                return BattlePassPointsTooltip()
            elif contentID == R.views.lobby.battle_pass.tooltips.BattlePassLockIconTooltipView():
                return BattlePassLockIconTooltipView()
            elif contentID == R.views.lobby.lootbox_system.tooltips.BoxTooltip():
                if tooltipData is None:
                    return
                return BoxTooltip(*tooltipData.specialArgs)
            else:
                return BattlePassTalerTooltip() if contentID == R.views.lobby.battle_pass.tooltips.BattlePassTalerTooltip() else func(self, event, contentID)

        return wrapper

    return decorator
