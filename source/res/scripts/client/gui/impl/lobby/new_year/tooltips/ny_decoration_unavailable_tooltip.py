# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_decoration_unavailable_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_decoration_unavailable_tooltip_model import NyDecorationUnavailableTooltipModel
from gui.impl.pub import ViewImpl
from items.components.ny_constants import TOY_TYPES_BY_OBJECT, ToyTypes
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

    def __getObjectTypeByToy(self, toy):
        for objectType, types in TOY_TYPES_BY_OBJECT.iteritems():
            toyType = toy.getToyType()
            if toyType in types:
                if toyType == ToyTypes.COLOR_FIR:
                    return ToyTypes.COLOR_FIR
                return objectType

        return toy.getDropSource()

    def _onLoading(self, *args, **kwargs):
        super(NyDecorationUnavailableTooltip, self)._onLoading(*args, **kwargs)
        toy = NewYearCurrentToyInfo(self.__toyID)
        with self.viewModel.transaction() as model:
            objectType = self.__getObjectTypeByToy(toy)
            model.setType(objectType)
            model.setDropSource(toy.getDropSource())
            if objectType == ToyTypes.COLOR_FIR:
                model.setToyName(toy.getName())
