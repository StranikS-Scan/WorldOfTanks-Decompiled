# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_undefined_tankman_view.py
import typing
from frameworks.wulf import WindowFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_undefined_tankman_view_model import BattlePassUndefinedTankmanViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.tankman_option_model import TankmanOptionModel
from gui.impl.pub import ViewImpl, WindowImpl
if typing.TYPE_CHECKING:
    from gui.battle_pass.undefined_bonuses import UndefinedTmanTooltipData

class BattlePassUndefinedTankmanView(ViewImpl):
    __slots__ = ('__tooltipData',)

    def __init__(self, tooltipData, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassUndefinedTankmanView())
        settings.model = BattlePassUndefinedTankmanViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BattlePassUndefinedTankmanView, self).__init__(settings)
        self.__tooltipData = tooltipData

    @property
    def viewModel(self):
        return super(BattlePassUndefinedTankmanView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassUndefinedTankmanView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            self.__setStylesInfo(model)

    def __setStylesInfo(self, model):
        optionA = TankmanOptionModel()
        optionB = TankmanOptionModel()
        optionA.setIcon(self.__tooltipData.imageA)
        optionA.setTankman(self.__tooltipData.tankmanA)
        optionB.setIcon(self.__tooltipData.imageB)
        optionB.setTankman(self.__tooltipData.tankmanB)
        model.options.addViewModel(optionA)
        model.options.addViewModel(optionB)


class BattlePassUndefinedTankmanTooltip(WindowImpl):
    __slots__ = ()

    def __init__(self, tooltipData, parent=None):
        super(BattlePassUndefinedTankmanTooltip, self).__init__(WindowFlags.TOOLTIP, content=BattlePassUndefinedTankmanView(tooltipData), parent=parent, areaID=R.areas.specific())
