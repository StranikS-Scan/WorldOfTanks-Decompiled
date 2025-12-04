# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/ny_menu_machine_tooltip.py
from frameworks.wulf import ViewSettings
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.menu_machine_tooltip_model import MenuMachineTooltipModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from new_year.gui.shared.ny_machine_helper import getMachineKeysCount

class NyMenuMachineTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.MenuMachineTooltip())
        settings.model = MenuMachineTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyMenuMachineTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyMenuMachineTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyMenuMachineTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setTokenCount(getMachineKeysCount())
