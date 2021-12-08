# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/album_toy_content.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_album_old_toy_content_model import NewYearAlbumOldToyContentModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_album_toy_content_model import NewYearAlbumToyContentModel
from gui.impl.new_year.new_year_helper import formatRomanNumber
from gui.impl.pub import ViewImpl
from helpers import dependency
from items.components.ny_constants import ToyTypes
from new_year.ny_bonuses import CreditsBonusHelper
from new_year.ny_toy_info import NewYearCurrentToyInfo, TOYS_INFO_REGISTRY
from skeletons.gui.shared import IItemsCache

class AlbumToyContent(ViewImpl):
    __slots__ = ()

    @property
    def viewModel(self):
        return super(AlbumToyContent, self).getViewModel()

    def _createToyInfo(self, toyID):
        raise NotImplementedError

    def _initialize(self, toyID):
        toy = self._createToyInfo(toyID)
        with self.viewModel.transaction() as tx:
            self._initModel(tx, toy)

    def _initModel(self, model, toyInfo):
        model.setRankRoman(formatRomanNumber(toyInfo.getRank()))
        model.setRankNumber(str(toyInfo.getRank()))
        model.setToyDesc(toyInfo.getDesc())
        model.setToyIcon(toyInfo.getIcon())
        model.setToyName(toyInfo.getName())
        model.setIsInCollection(toyInfo.isInCollection())
        model.setSetting(toyInfo.getSetting())


class AlbumCurrentToyContent(AlbumToyContent):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.new_year_album_toy_tooltip_content.NewYearAlbumToyTooltipContent())
        settings.model = NewYearAlbumToyContentModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AlbumCurrentToyContent, self).__init__(settings)

    def _createToyInfo(self, toyID):
        return NewYearCurrentToyInfo(toyID)

    def _initModel(self, model, toyInfo):
        super(AlbumCurrentToyContent, self)._initModel(model, toyInfo)
        toy = self._itemsCache.items.festivity.getToys().get(toyInfo.getID())
        model.setIsInInventory(bool(toy and toy.getCount() > 0))
        model.setIsMount(toyInfo.getID() in self._itemsCache.items.festivity.getSlots())
        model.setIsMega(toyInfo.isMega())
        model.setTypeName(ToyTypes.MEGA_COMMON if toyInfo.isMega() else toyInfo.getToyType())
        model.setTotalBonus(CreditsBonusHelper.getMegaToysBonus())
        model.setToyBonus(CreditsBonusHelper.getMegaToysBonusValue())


class AlbumOldToyContent(AlbumToyContent):
    __slots__ = ('__yearName',)

    def __init__(self, yearName, toyID):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.new_year_toy_old_tooltip_content.NewYearAlbumToyOldTooltipContent())
        settings.model = NewYearAlbumOldToyContentModel()
        settings.args = (toyID,)
        super(AlbumOldToyContent, self).__init__(settings)
        self.__yearName = yearName

    def _createToyInfo(self, toyID):
        return TOYS_INFO_REGISTRY[self.__yearName](toyID)

    def _initModel(self, model, toyInfo):
        super(AlbumOldToyContent, self)._initModel(model, toyInfo)
        model.setShards(toyInfo.getShards())
        model.setIsMega(toyInfo.isMega())
