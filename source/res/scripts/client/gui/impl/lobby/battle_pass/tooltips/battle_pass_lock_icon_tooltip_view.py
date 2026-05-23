# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_lock_icon_tooltip_view.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_lock_icon_tooltip_view_model import BattlePassLockIconTooltipViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController

class BattlePassLockIconTooltipView(ViewImpl):
    __battlePass = dependency.descriptor(IBattlePassController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.mono.battle_pass.tooltips.lock_icon())
        settings.model = BattlePassLockIconTooltipViewModel()
        super(BattlePassLockIconTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassLockIconTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassLockIconTooltipView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setIsHoliday(self.__battlePass.isHoliday())
