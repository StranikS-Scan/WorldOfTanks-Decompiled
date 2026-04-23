# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/battle_pass_in_progress_tooltip.py
from __future__ import absolute_import
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.tooltips.battle_pass_in_progress_tooltip_view import BattlePassInProgressTooltipView
from skeletons.gui.game_control import IBattleRoyaleController
from helpers import dependency
from gui.impl import backport
ST_PATRICK_ICON = R.images.battle_royale.gui.maps.st_patrick.icons.battleTypes.c_40x40.battle_royale()

class BattleRoyaleBattlePassInProgressTooltipView(BattlePassInProgressTooltipView):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    @property
    def _customBattleTypeIcon(self):
        return backport.image(ST_PATRICK_ICON) if self.__battleRoyaleController.isStPatrick() else ''
