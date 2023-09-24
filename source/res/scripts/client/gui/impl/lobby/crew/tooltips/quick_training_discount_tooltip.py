# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/quick_training_discount_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.quick_training_discount_tooltip_model import QuickTrainingDiscountTooltipModel
from gui.impl.pub import ViewImpl

class QuickTrainingDiscountTooltip(ViewImpl):
    __slots__ = ('_oldFreeXpBase', '_newFreeXpBase', '_oldXpExchange', '_newXpExchange')

    def __init__(self, oldFreeXpBase, newFreeXpBase, oldXpExchange, newXpExchange):
        self._oldFreeXpBase = oldFreeXpBase
        self._newFreeXpBase = newFreeXpBase
        self._oldXpExchange = oldXpExchange
        self._newXpExchange = newXpExchange
        settings = ViewSettings(R.views.lobby.crew.tooltips.QuickTrainingDiscountTooltip(), model=QuickTrainingDiscountTooltipModel())
        super(QuickTrainingDiscountTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(QuickTrainingDiscountTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            vm.setOldFreeXpBaseValue(self._oldFreeXpBase)
            vm.setNewFreeXpBaseValue(self._newFreeXpBase)
            vm.setOldXpExchangeValue(self._oldXpExchange)
            vm.setNewXpExchangeValue(self._newXpExchange)
