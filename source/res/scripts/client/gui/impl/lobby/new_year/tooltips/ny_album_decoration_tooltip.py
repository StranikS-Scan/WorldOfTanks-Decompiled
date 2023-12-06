# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_album_decoration_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_album_decoration_tooltip_model import NyAlbumDecorationTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.new_year import INewYearController
from new_year.ny_toy_info import NewYearCurrentToyInfo

class NyAlbumDecorationTooltip(ViewImpl):
    __nyController = dependency.descriptor(INewYearController)
    __slots__ = ('__toyID', '__isToyIconEnabled', '__isCountEnabled')

    def __init__(self, toyID, isCountEnabled=False, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyAlbumDecorationTooltip())
        settings.model = NyAlbumDecorationTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyAlbumDecorationTooltip, self).__init__(settings)
        self.__toyID = int(toyID)
        self.__isCountEnabled = isCountEnabled

    @property
    def viewModel(self):
        return super(NyAlbumDecorationTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        toy = NewYearCurrentToyInfo(self.__toyID)
        with self.viewModel.transaction() as model:
            model.setName(toy.getName())
            model.setDescription(toy.getDesc())
            model.setShardsPrice(toy.getShards())
            model.setUsedSlotAtmosphere(toy.getAtmosphere())
            model.setSetting(toy.getSetting())
            model.setCount(toy.getCount() if self.__isCountEnabled else 0)
            model.setType(toy.getToyType())
            model.setRankNumber(toy.getRank())
            model.setIsMaxAtmosphereLevel(self.__nyController.isMaxAtmosphereLevel())
            model.setIsPostNYEnabled(self.__nyController.isPostEvent())
            model.setIsFinished(self.__nyController.isFinished())
            model.setIsInCollection(toy.isInCollection())
