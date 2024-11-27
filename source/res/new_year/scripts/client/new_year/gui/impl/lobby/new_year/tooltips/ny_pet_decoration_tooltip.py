# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/ny_pet_decoration_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.server_events.awards_formatters import EPIC_AWARD_SIZE
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.impl import INewYearNavigation
from new_year.skeletons.new_year import INewYearController
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_pet_decoration_tooltip_model import NyPetDecorationTooltipModel

class NyPetDecorationTooltip(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)
    __newYearNavigation = dependency.descriptor(INewYearNavigation)
    __slots__ = ('__toyID', '__isToyIconEnabled')

    def __init__(self, toyID, isToyIconEnabled=True, *args, **kwargs):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.NyPetDecorationTooltip())
        settings.model = NyPetDecorationTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyPetDecorationTooltip, self).__init__(settings)
        self.__toyID = int(toyID)
        self.__isToyIconEnabled = isToyIconEnabled

    @property
    def viewModel(self):
        return super(NyPetDecorationTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        toy = self.__nyController.getToyByID(self.__toyID)
        decorationTypeIcon = R.images.new_year.gui.maps.icons.newYear.decoration_types.craft.dyn(toy.getToyType())()
        with self.viewModel.transaction() as model:
            model.setName(toy.getName())
            model.setDescription(toy.getDesc())
            model.setDecorationType(toy.getToyType())
            model.setDecorationTypeIcon(decorationTypeIcon)
            model.setIsLocked(toy.getCount() == 0)
            model.setIcon(toy.getIcon(size=EPIC_AWARD_SIZE) if self.__isToyIconEnabled else R.invalid())
            model.setPrice(toy.getPrice().gold)
