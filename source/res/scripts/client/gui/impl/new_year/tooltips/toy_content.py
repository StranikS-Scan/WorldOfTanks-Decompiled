# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/toy_content.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_mega_toy_tooltip_model import NyMegaToyTooltipModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_regular_toy_tooltip_model import NyRegularToyTooltipModel
from gui.impl.new_year.new_year_helper import formatRomanNumber
from gui.impl.pub import ViewImpl
from gui.server_events.awards_formatters import EPIC_AWARD_SIZE
from helpers import dependency
from new_year.ny_bonuses import CreditsBonusHelper
from skeletons.gui.shared import IItemsCache

class RegularToyContent(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__toyID', '__isToyIconEnabled')

    def __init__(self, toyID, isToyIconEnabled=True, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.ny_regular_toy_tooltip_content.NyRegularToyTooltipContent())
        settings.model = NyRegularToyTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(RegularToyContent, self).__init__(settings)
        self.__toyID = int(toyID)
        self.__isToyIconEnabled = isToyIconEnabled

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
            model.setRank(formatRomanNumber(toy.getRank()))
            model.setSetting(toy.getSetting())
            model.setCount(toy.getCount())
            model.setType(toy.getToyType())
            model.setIcon(toy.getIcon(size=EPIC_AWARD_SIZE) if self.__isToyIconEnabled else R.invalid())


class MegaToyContent(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__toyID', '__isToyIconEnabled')

    def __init__(self, toyID, isToyIconEnabled=True, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.ny_mega_toy_tooltip_content.NyMegaToyTooltipContent())
        settings.model = NyMegaToyTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(MegaToyContent, self).__init__(settings)
        self.__toyID = int(toyID)
        self.__isToyIconEnabled = isToyIconEnabled

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
            model.setIcon(toy.getIcon(size=EPIC_AWARD_SIZE) if self.__isToyIconEnabled else R.invalid())
