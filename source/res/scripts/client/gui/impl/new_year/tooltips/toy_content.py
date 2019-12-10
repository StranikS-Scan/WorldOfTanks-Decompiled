# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/toy_content.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_mega_toy_tooltip_model import NyMegaToyTooltipModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_regular_toy_tooltip_model import NyRegularToyTooltipModel
from gui.impl.pub import ViewImpl
from helpers import int2roman, dependency
from new_year.ny_bonuses import CreditsBonusHelper
from skeletons.gui.shared import IItemsCache

class RegularToyContent(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__toyID',)

    def __init__(self, toyID, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.ny_regular_toy_tooltip_content.NyRegularToyTooltipContent())
        settings.model = NyRegularToyTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(RegularToyContent, self).__init__(settings)
        self.__toyID = int(toyID)

    @property
    def viewModel(self):
        return super(RegularToyContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        toy = self._itemsCache.items.festivity.getToys()[self.__toyID]
        with self.viewModel.transaction() as model:
            model.setName(toy.getName())
            model.setDescription(toy.getDesc())
            model.setShardsPrice(toy.getShards())
            model.setRankNumber(toy.getRank())
            model.setAtmospherePoint(toy.getAtmosphere())
            model.setRank(int2roman(toy.getRank()))
            model.setSetting(toy.getSetting())
            model.setCount(toy.getCount())
            model.setType(toy.getToyType())


class MegaToyContent(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__toyID',)

    def __init__(self, toyID, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.ny_mega_toy_tooltip_content.NyMegaToyTooltipContent())
        settings.model = NyMegaToyTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(MegaToyContent, self).__init__(settings)
        self.__toyID = int(toyID)

    @property
    def viewModel(self):
        return super(MegaToyContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        toy = self._itemsCache.items.festivity.getToys()[self.__toyID]
        with self.viewModel.transaction() as model:
            model.setName(toy.getName())
            model.setDescription(toy.getDesc())
            model.setShardsPrice(toy.getShards())
            model.setBonus(CreditsBonusHelper.getMegaToysBonusValue())
