# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_decoration_unavailable_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_decoration_unavailable_tooltip_model import NyDecorationUnavailableTooltipModel
from gui.impl.pub import ViewImpl
from items.components.ny_constants import TOY_TYPES_BY_OBJECT, CustomizationObjects
from new_year.ny_toy_info import NewYearCurrentToyInfo

class NyDecorationUnavailableTooltip(ViewImpl):

    def __init__(self, toyID, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyDecorationUnavailableTooltip())
        settings.model = NyDecorationUnavailableTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyDecorationUnavailableTooltip, self).__init__(settings)
        self.__toyID = int(toyID)

    @property
    def viewModel(self):
        return super(NyDecorationUnavailableTooltip, self).getViewModel()

    def __getObjectTypeByToy(self):
        toy = NewYearCurrentToyInfo(self.__toyID)
        for objectType, types in TOY_TYPES_BY_OBJECT.iteritems():
            if toy.getToyType() in types:
                return objectType

        return CustomizationObjects.FIR

    def _initialize(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setType(self.__getObjectTypeByToy())
