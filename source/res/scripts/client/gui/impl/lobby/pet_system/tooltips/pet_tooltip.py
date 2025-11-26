# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pet_system/tooltips/pet_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.pet_system.tooltips.pet_tooltip_model import PetTooltipModel
from gui.impl.pub import ViewImpl

class PetTooltip(ViewImpl):

    def __init__(self, context=None, *args, **kwargs):
        settings = ViewSettings(R.views.mono.pet_system.tooltips.pet_tooltip())
        settings.model = PetTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        self.context = context
        super(PetTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PetTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PetTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setPetNameID(self.context['petNameID'])
            model.setPetType(self.context['petType'])
            model.setBreedName(self.context['breedName'])
            model.setPetID(self.context['petID'])
            model.setPromotionBonuses(self.context['promotionBonuses'])
