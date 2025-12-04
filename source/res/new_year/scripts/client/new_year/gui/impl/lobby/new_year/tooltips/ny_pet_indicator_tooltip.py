# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/ny_pet_indicator_tooltip.py
from frameworks.wulf import ViewSettings
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_pet_indicator_tooltip_model import NyPetIndicatorTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class NyPetIndicatorTooltip(ViewImpl):

    def __init__(self, indicator):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.NyPetIndicatorTooltip())
        settings.model = NyPetIndicatorTooltipModel()
        array = settings.model.getIndicator()
        array.clear()
        array.addViewModel(indicator)
        array.invalidate()
        super(NyPetIndicatorTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyPetIndicatorTooltip, self).getViewModel()
