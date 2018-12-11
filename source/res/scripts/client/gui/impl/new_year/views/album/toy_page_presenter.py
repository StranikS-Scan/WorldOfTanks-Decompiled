# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/toy_page_presenter.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.new_year.components.new_year_album_toy18_renderer_model import NewYearAlbumToy18RendererModel
from gui.impl.gen.view_models.new_year.components.new_year_album_toy19_renderer_model import NewYearAlbumToy19RendererModel
from gui.impl.gen.view_models.new_year.components.new_year_album_toy_renderer_model import NewYearAlbumToyRendererModel
from helpers import dependency
from items import ny19
from skeletons.gui.shared import IItemsCache
_DEFAULT_PAGE_SIZE = 15
_MAX_RANK_PAGE_SIZE = 14

class ToyPagePresenter(object):
    __slots__ = ('__toys', '__rank')

    def __init__(self, toys, rank):
        super(ToyPagePresenter, self).__init__()
        self.__rank = rank
        self.__toys = toys

    def getTotalIndexes(self):
        return (len(self.__toys) - 1) // self._getPageSize() + 1

    def hasStamp(self):
        return True if self.__rank == ny19.CONSTS.MAX_TOY_RANK else False

    def getToys(self, index):
        result = Array()
        left, right = self._getRange(index)
        for toyIndex in xrange(left, right):
            toy = self.__toys[toyIndex]
            renderer = self._getToyRendererModel()
            self._setToyRendererModel(renderer, toy)
            result.addViewModel(renderer)

        return result

    def _getRange(self, index):
        left = self._getPageSize() * index
        right = min(left + self._getPageSize(), len(self.__toys))
        return (left, right)

    @staticmethod
    def _getToyRendererModel():
        return NewYearAlbumToyRendererModel()

    def _setToyRendererModel(self, renderer, toy):
        renderer.setIsInCollection(toy.isInCollection())
        renderer.setToyID(toy.getID())
        renderer.setPassepartoutImage(toy.getPassepartout())
        renderer.setEmptyPassepartoutImage(toy.getEmptyPassepartout())
        renderer.setToyImage(toy.getIcon())

    def _getPageSize(self):
        return _MAX_RANK_PAGE_SIZE if self.hasStamp() else _DEFAULT_PAGE_SIZE


class Toy18PagePresenter(ToyPagePresenter):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    @staticmethod
    def _getToyRendererModel():
        return NewYearAlbumToy18RendererModel()

    def _setToyRendererModel(self, renderer, toy):
        super(Toy18PagePresenter, self)._setToyRendererModel(renderer, toy)
        renderer.setShards(toy.getShards())
        renderer.setIsCanCraft(toy.getShards() <= self._itemsCache.items.festivity.getShardsCount())


class Toy19PagePresenter(ToyPagePresenter):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__newToys',)

    def __init__(self, toys, rank):
        super(Toy19PagePresenter, self).__init__(toys, rank)
        self.__newToys = set()

    def getToys(self, index):
        self.__newToys = set()
        return super(Toy19PagePresenter, self).getToys(index)

    def getNewToys(self):
        return self.__newToys

    @staticmethod
    def _getToyRendererModel():
        return NewYearAlbumToy19RendererModel()

    def _setToyRendererModel(self, renderer, toy):
        super(Toy19PagePresenter, self)._setToyRendererModel(renderer, toy)
        toyInfo = self._itemsCache.items.festivity.getToys().get(toy.getID())
        if toyInfo is not None:
            renderer.setIsNew(toyInfo.isNewInCollection())
            if toyInfo.isNewInCollection():
                self.__newToys.add(toyInfo.getID())
                renderer.setNewNumber(len(self.__newToys))
        return
