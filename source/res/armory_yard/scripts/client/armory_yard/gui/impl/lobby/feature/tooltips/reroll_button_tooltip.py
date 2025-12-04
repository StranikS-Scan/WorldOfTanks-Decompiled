# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/tooltips/reroll_button_tooltip.py
from frameworks.wulf import ViewSettings
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.tooltips.reroll_button_tooltip_model import RerollButtonTooltipModel
from armory_yard.skeletons.armory_yard_reroll_controller import IArmoryYardRerollController
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency

class RerollButtonTooltip(ViewImpl):
    __slots__ = ('__selectedCycleID',)
    __armoryYardRerollCtrl = dependency.descriptor(IArmoryYardRerollController)

    def __init__(self, selectedCycleID):
        settings = ViewSettings(R.views.armory_yard.lobby.feature.tooltips.RerollButtonTooltip())
        settings.model = RerollButtonTooltipModel()
        super(RerollButtonTooltip, self).__init__(settings)
        self.__selectedCycleID = selectedCycleID

    @property
    def viewModel(self):
        return super(RerollButtonTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RerollButtonTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        with self.viewModel.transaction() as tx:
            tx.setFreeRerollCount(self.__armoryYardRerollCtrl.getFreeRerollsCountByCycleID(int(self.__selectedCycleID)))
