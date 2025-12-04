# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/ny_pet_token_stepper_tooltip.py
from frameworks.wulf import ViewSettings
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_pet_token_stepper_tooltip_model import NyPetTokenStepperTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class NyPetTokenStepperTooltip(ViewImpl):

    def __init__(self, itemType):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.NyPetTokenStepperTooltip())
        settings.model = NyPetTokenStepperTooltipModel()
        super(NyPetTokenStepperTooltip, self).__init__(settings)
        self.viewModel.setType(itemType)

    @property
    def viewModel(self):
        return super(NyPetTokenStepperTooltip, self).getViewModel()
