# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/tooltips/entry_point_before_progression_tooltip_view.py
from frameworks.wulf import ViewSettings
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.tooltips.entry_point_before_progression_tooltip_view_model import EntryPointBeforeProgressionTooltipViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController

class EntryPointBeforeProgressionTooltipView(ViewImpl):
    __slots__ = ()
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self):
        settings = ViewSettings(R.views.armory_yard.lobby.feature.tooltips.EntryPointBeforeProgressionTooltipView())
        settings.model = EntryPointBeforeProgressionTooltipViewModel()
        super(EntryPointBeforeProgressionTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointBeforeProgressionTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EntryPointBeforeProgressionTooltipView, self)._onLoading()
        if not self.__armoryYardCtrl.isEnabled():
            return
        with self.viewModel.transaction() as tx:
            startProgressionTime, _ = self.__armoryYardCtrl.getProgressionTimes()
            tx.setStartTimestamp(startProgressionTime)
