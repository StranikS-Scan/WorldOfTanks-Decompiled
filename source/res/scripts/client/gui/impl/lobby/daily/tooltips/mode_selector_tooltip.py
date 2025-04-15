# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/tooltips/mode_selector_tooltip.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.daily.tooltips.mode_selector_tooltip_model import ModeSelectorTooltipModel
from gui.impl.pub import ViewImpl

class ModeSelectorTooltip(ViewImpl):
    __slots__ = ('_battleTypes',)

    def __init__(self, layoutID, battleTypes):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = ModeSelectorTooltipModel()
        super(ModeSelectorTooltip, self).__init__(settings)
        self._battleTypes = battleTypes

    @property
    def viewModel(self):
        return super(ModeSelectorTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ModeSelectorTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            battleTypes = model.getBattleTypes()
            battleTypes.clear()
            for battleType in self._battleTypes:
                battleTypes.addString(str(battleType))

            battleTypes.invalidate()
