# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_decoration_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_decoration_tooltip_model import NyDecorationTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from new_year.ny_toy_info import NewYearCurrentToyInfo
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController

class NyDecorationTooltip(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, toyID, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyDecorationTooltip())
        settings.model = NyDecorationTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyDecorationTooltip, self).__init__(settings)
        self.__toyID = int(toyID)

    @property
    def viewModel(self):
        return super(NyDecorationTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        toy = NewYearCurrentToyInfo(self.__toyID)
        with self.viewModel.transaction() as model:
            model.setName(toy.getName())
            model.setType(toy.getToyType())
            model.setIcon(toy.getIcon(size='large'))
            model.setDescription(toy.getDesc())
