# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/challenges/challenges_decorators.py
from __future__ import absolute_import
import functools
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.tooltips.battle_pass_coin_tooltip_view import BattlePassCoinTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_taler_tooltip import BattlePassTalerTooltip
from gui.impl.lobby.battle_pass.tooltips.reward_compensation_tooltip import RewardCompensationTooltip
from gui.impl.lobby.lootbox_system.base.tooltips.box_tooltip import BoxTooltip
from gui.impl.lobby.user_missions.tooltips.challenges_shields_tooltip import ChallengesShieldsTooltip

def checkIsEnabled(default=None):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            return default if not getattr(self, 'isEnabled', False) else func(self, *args, **kwargs)

        return wrapper

    return decorator


def createTooltipContentDecorator():

    def decorator(func):

        def wrapper(self, event, contentID):
            tooltipData = self.getTooltipData(event)
            if contentID == R.views.mono.user_missions.tooltips.challenges_shields_tooltip():
                return ChallengesShieldsTooltip()
            elif contentID == R.views.mono.battle_pass.tooltips.reward_compensation():
                return RewardCompensationTooltip(*tooltipData.specialArgs)
            elif contentID == R.views.mono.lootbox.tooltips.box_tooltip():
                if tooltipData is None:
                    return
                return BoxTooltip(*tooltipData.specialArgs)
            elif contentID == R.views.mono.battle_pass.tooltips.bpcoin():
                return BattlePassCoinTooltipView()
            else:
                return BattlePassTalerTooltip() if contentID == R.views.mono.battle_pass.tooltips.bptaler() else func(self, event, contentID)

        return wrapper

    return decorator
