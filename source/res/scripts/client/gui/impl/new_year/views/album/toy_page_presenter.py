# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/toy_page_presenter.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_album_toy20_renderer_model import NewYearAlbumToy20RendererModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_album_toy_old_renderer_model import NewYearAlbumToyOldRendererModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_album_toy_renderer_model import NewYearAlbumToyRendererModel
from helpers import dependency
from items import new_year
from items.components.ny_constants import ToyTypes
from new_year.ny_bonuses import CreditsBonusHelper
from skeletons.gui.shared import IItemsCache
_DEFAULT_PAGE_SIZE = 15
_MAX_RANK_PAGE_SIZE = 14

class ToyPagePresenter(object):
    __slots__ = ('_toys', '__rank')

    def __init__(self, toys, rank):
        super(ToyPagePresenter, self).__init__()
        self._toys = toys
        self.__rank = rank

    def getTotalIndexes(self):
        return (len(self._toys) - 1) // self._getPageSize() + 1

    def hasStamp(self):
        return True if self.__rank == new_year.CONSTS.MAX_TOY_RANK else False

    def getToys(self, index=0):
        left, right = self._getRange(index)
        result = Array()
        result.reserve(right - left)
        for toyIndex in xrange(left, right):
            toy = self._toys[toyIndex]
            renderer = self._getToyRendererModel()
            self._setToyRendererModel(renderer, toy)
            result.addViewModel(renderer)

        return result

    def _getRange(self, index):
        left = self._getPageSize() * index
        right = min(left + self._getPageSize(), len(self._toys))
        return (left, right)

    @staticmethod
    def _getToyRendererModel():
        return NewYearAlbumToyRendererModel()

    def _setToyRendererModel(self, renderer, toy):
        renderer.setIsInCollection(toy.isInCollection())
        renderer.setToyID(toy.getID())
        renderer.setPassepartoutImage(toy.getPassepartout())
        renderer.setEmptyPassepartoutImage(toy.getEmptyPassepartout())

    def _getPageSize(self):
        return _MAX_RANK_PAGE_SIZE if self.hasStamp() else _DEFAULT_PAGE_SIZE


class ToySinglePagePresenter(ToyPagePresenter):
    __slots__ = ()

    def _getPageSize(self):
        return len(self._toys)


class ToyOldPagePresenter(ToySinglePagePresenter):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    @staticmethod
    def _getToyRendererModel():
        return NewYearAlbumToyOldRendererModel()

    def _setToyRendererModel(self, renderer, toy):
        super(ToyOldPagePresenter, self)._setToyRendererModel(renderer, toy)
        renderer.setToyImage(toy.getIcon())
        renderer.setShards(toy.getShards())
        renderer.setIsCanCraft(toy.getShards() <= self._itemsCache.items.festivity.getShardsCount())


class Toy20PagePresenter(ToySinglePagePresenter):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__newToys',)

    def __init__(self, toys, rank):
        super(Toy20PagePresenter, self).__init__(toys, rank)
        self.__newToys = set()

    def getToys(self, index=0):
        self.__newToys = set()
        return super(Toy20PagePresenter, self).getToys(index)

    def getNewToys(self):
        return self.__newToys

    @staticmethod
    def _getToyRendererModel():
        return NewYearAlbumToy20RendererModel()

    def _setToyRendererModel(self, renderer, toy):
        super(Toy20PagePresenter, self)._setToyRendererModel(renderer, toy)
        toyInfo = self._itemsCache.items.festivity.getToys().get(toy.getID())
        renderer.setIsMega(toy.isMega())
        renderer.setToyType(ToyTypes.MEGA_COMMON if toy.isMega() else toy.getToyType())
        renderer.setToyImage(toy.getIcon(toy.isMega()))
        if toyInfo is not None:
            renderer.setIsNew(toyInfo.isNewInCollection())
            if toyInfo.isNewInCollection():
                self.__newToys.add(toyInfo.getID())
                renderer.setNewNumber(len(self.__newToys))
            if toyInfo.isMega():
                megaCount = 1 if toyInfo.getID() in self._itemsCache.items.festivity.getSlots() else 0
                renderer.setBonusValue(CreditsBonusHelper.getMegaToysBonusByCount(megaCount))
                renderer.setIsInInventory(toyInfo.getCount() > 0)
        return
