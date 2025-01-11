# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_resource_converter_info_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_resource_converter_info_tooltip_model import NyResourceConverterInfoTooltipModel, ConverterInfoTooltipType
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.new_year import INewYearController

class NyResourceConverterInfoTooltip(ViewImpl):
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyResourceConverterInfoTooltip())
        settings.model = NyResourceConverterInfoTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyResourceConverterInfoTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyResourceConverterInfoTooltip, self).getViewModel()

    def _onLoading(self, tooltipType, *args, **kwargs):
        super(NyResourceConverterInfoTooltip, self)._onLoading()
        initialValueCoeff, receivedValueCoeff = self.__nyController.currencies.getResourceConverterCoefficients()
        multiple = initialValueCoeff if tooltipType == ConverterInfoTooltipType.FROM else receivedValueCoeff
        with self.viewModel.transaction() as model:
            model.setTooltipType(tooltipType)
            model.setMultiple(multiple)
