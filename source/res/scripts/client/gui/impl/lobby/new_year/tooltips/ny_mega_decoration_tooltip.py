# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_mega_decoration_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_mega_decoration_tooltip_model import NyMegaDecorationTooltipModel
from gui.impl.pub import ViewImpl
from gui.server_events.awards_formatters import EPIC_AWARD_SIZE
from helpers import dependency
from new_year.ny_bonuses import CreditsBonusHelper
from skeletons.gui.shared import IItemsCache
from shared_utils import inPercents
from skeletons.new_year import INewYearController

class NyMegaDecorationTooltip(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)
    __slots__ = ('__toyID', '__isToyIconEnabled', '__isPureToy')

    def __init__(self, toyID, isToyIconEnabled=True, isPureToy=False, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyMegaDecorationTooltip())
        settings.model = NyMegaDecorationTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyMegaDecorationTooltip, self).__init__(settings)
        self.__toyID = int(toyID)
        self.__isPureToy = isPureToy
        self.__isToyIconEnabled = isToyIconEnabled

    @property
    def viewModel(self):
        return super(NyMegaDecorationTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        toy = self.__itemsCache.items.festivity.getToys()[self.__toyID]
        hasPureSlotForToy = self.__nyController.hasPureSlotForToy(toy)
        with self.viewModel.transaction() as model:
            model.setName(toy.getName())
            model.setDescription(toy.getDesc())
            model.setShardsPrice(toy.getShards())
            model.setIsPure(bool(self.__isPureToy))
            model.setPureSlotAtmosphere(toy.getAtmosphere(self.__isPureToy, hasPureSlotForToy))
            model.setBonus(inPercents(CreditsBonusHelper.getMegaToysBonusValue()))
            model.setIcon(toy.getIcon(size=EPIC_AWARD_SIZE) if self.__isToyIconEnabled else R.invalid())
            model.setIsMaxAtmosphereLevel(self.__nyController.isMaxAtmosphereLevel())
            model.setIsPostNYEnabled(self.__nyController.isPostEvent())
            model.setIsFinished(self.__nyController.isFinished())
