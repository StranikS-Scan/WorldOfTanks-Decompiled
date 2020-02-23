# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_undefined_style_view.py
import typing
from frameworks.wulf import WindowFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_undefined_style_view_model import BattlePassUndefinedStyleViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.style_option_model import StyleOptionModel
from gui.impl.pub import ViewImpl, WindowImpl
if typing.TYPE_CHECKING:
    from gui.battle_pass.undefined_bonuses import UndefinedStyleTooltipData

class BattlePassUndefinedStyleView(ViewImpl):
    __slots__ = ('__tooltipData',)

    def __init__(self, tooltipData, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassUndefinedStyleView())
        settings.model = BattlePassUndefinedStyleViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BattlePassUndefinedStyleView, self).__init__(settings)
        self.__tooltipData = tooltipData

    @property
    def viewModel(self):
        return super(BattlePassUndefinedStyleView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassUndefinedStyleView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            self.__setStylesInfo(model)

    def __setStylesInfo(self, model):
        optionA = StyleOptionModel()
        optionB = StyleOptionModel()
        optionA.setIcon(self.__tooltipData.imageA)
        optionA.setStyle(self.__tooltipData.styleA)
        optionA.setTank(self.__tooltipData.tankA)
        optionB.setIcon(self.__tooltipData.imageB)
        optionB.setStyle(self.__tooltipData.styleB)
        optionB.setTank(self.__tooltipData.tankB)
        model.options.addViewModel(optionA)
        model.options.addViewModel(optionB)


class BattlePassUndefinedStyleTooltip(WindowImpl):
    __slots__ = ()

    def __init__(self, tooltipData, parent=None):
        super(BattlePassUndefinedStyleTooltip, self).__init__(WindowFlags.TOOLTIP, content=BattlePassUndefinedStyleView(tooltipData), parent=parent, areaID=R.areas.specific())
