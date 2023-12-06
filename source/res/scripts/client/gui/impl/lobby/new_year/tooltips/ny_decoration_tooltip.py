# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_decoration_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_decoration_tooltip_model import NyDecorationTooltipModel
from gui.impl.pub import ViewImpl
from gui.server_events.awards_formatters import EPIC_AWARD_SIZE
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController

class NyDecorationTooltip(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)
    __slots__ = ('__toyID', '__isToyIconEnabled', '__isCountEnabled')

    def __init__(self, toyID, isToyIconEnabled=True, isCountEnabled=False, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyDecorationTooltip())
        settings.model = NyDecorationTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyDecorationTooltip, self).__init__(settings)
        self.__toyID = int(toyID)
        self.__isToyIconEnabled = isToyIconEnabled
        self.__isCountEnabled = isCountEnabled

    @property
    def viewModel(self):
        return super(NyDecorationTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        toy = self.__itemsCache.items.festivity.getToys()[self.__toyID]
        with self.viewModel.transaction() as model:
            model.setName(toy.getName())
            model.setDescription(toy.getDesc())
            model.setShardsPrice(toy.getShards())
            model.setUsedSlotAtmosphere(toy.getAtmosphere())
            model.setSetting(toy.getSetting())
            model.setCount(toy.getCount() if self.__isCountEnabled else 0)
            model.setType(toy.getToyType())
            model.setRankNumber(toy.getRank())
            model.setIcon(toy.getIcon(size=EPIC_AWARD_SIZE) if self.__isToyIconEnabled else R.invalid())
            model.setIsMaxAtmosphereLevel(self.__nyController.isMaxAtmosphereLevel())
            model.setIsPostNYEnabled(self.__nyController.isPostEvent())
            model.setIsFinished(self.__nyController.isFinished())
