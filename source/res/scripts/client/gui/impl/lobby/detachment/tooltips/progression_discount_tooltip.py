# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/progression_discount_tooltip.py
from frameworks.wulf import View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.discount_item_tooltip_model import DiscountItemTooltipModel

class ProgressionDiscountTooltip(View):
    __slots__ = ()

    def __init__(self, name, description, discountLabel, discountAmount):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.ProgressionDiscountTooltip())
        settings.model = DiscountItemTooltipModel()
        settings.args = (name,
         description,
         discountLabel,
         discountAmount)
        super(ProgressionDiscountTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ProgressionDiscountTooltip, self).getViewModel()

    def _onLoading(self, name, description, discountLabel, discountAmount):
        with self.viewModel.transaction() as tx:
            tx.setName(name)
            tx.setDescription(description)
            tx.setDiscountLabel(discountLabel)
            tx.setDiscountAmount(discountAmount)
