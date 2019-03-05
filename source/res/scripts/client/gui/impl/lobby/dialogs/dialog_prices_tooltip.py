# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/dialog_prices_tooltip.py
import BigWorld
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.dialog_prices_tooltip_model import DialogPricesTooltipModel
from gui.impl.pub import ViewImpl

class DialogPricesTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(DialogPricesTooltip, self).__init__(R.views.dialogPricesTooltip(), ViewFlags.VIEW, DialogPricesTooltipModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(DialogPricesTooltip, self).getViewModel()

    def setData(self, valueMainCost, iconMainCost, labelMainCost, valueAdditionalCost, iconAdditionalCost, labelAdditionalCost, totalCost, labelTotalCost):
        with self.viewModel.transaction() as model:
            model.setValueMainCost(valueMainCost)
            model.setIconMainCost(iconMainCost)
            model.setLabelMainCost(labelMainCost)
            model.setValueAdditionalCost(valueAdditionalCost)
            model.setIconAdditionalCost(iconAdditionalCost)
            model.setLabelAdditionalCost(labelAdditionalCost)
            model.setTotalCost(BigWorld.wg_getIntegralFormat(totalCost))
            model.setLabelTotalCost(labelTotalCost)
