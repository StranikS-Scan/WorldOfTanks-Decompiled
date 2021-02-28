# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_decorators.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.tooltips.battle_pass_upgrade_style_tooltip_view import BattlePassUpgradeStyleTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_coin_tooltip_view import BattlePassCoinTooltipView
if typing.TYPE_CHECKING:
    from gui.impl.backport import TooltipData

def createBackportTooltipDecorator():

    def decorator(func):

        def wrapper(self, event):
            if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                tooltipData = self.getTooltipData(event)
                if tooltipData is None:
                    return
                window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
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
            if contentID == R.views.lobby.battle_pass.tooltips.BattlePassUpgradeStyleTooltipView():
                tooltipData = self.getTooltipData(event)
                if tooltipData is None:
                    return
                return BattlePassUpgradeStyleTooltipView(*tooltipData.specialArgs)
            else:
                return BattlePassCoinTooltipView() if contentID == R.views.lobby.battle_pass.tooltips.BattlePassCoinTooltipView() else func(self, event, contentID)

        return wrapper

    return decorator
