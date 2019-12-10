# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/collections_builders.py
import typing
from collections import defaultdict
from gui.impl.new_year.views.album.toy_page_presenter import Toy20PagePresenter, ToyOldPagePresenter
from helpers import dependency
from items.collectibles import g_cache
from items.components.ny_constants import ToySettings
from new_year.ny_constants import Collections
from new_year.ny_toy_info import TOYS_INFO_REGISTRY
from skeletons.gui.shared import IItemsCache

class _SubCollectionPresenter(object):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__objectName', '__totalToys', '__toyPageClazz', '__toys')

    def __init__(self, objectName, toys, toyPage):
        super(_SubCollectionPresenter, self).__init__()
        self.__objectName = objectName
        self.__totalToys = len(toys)
        self.__toyPageClazz = toyPage
        self.__toys = defaultdict(list)
        for toy in toys:
            self.__toys[toy.getRank()].append(toy)

    def totalToys(self):
        return self.__totalToys

    def isFull(self):
        return self.totalToys() == self.currentToys()

    def currentToys(self):
        result = 0
        for rank in self.__toys:
            for toy in self.__toys[rank]:
                if toy.isInCollection():
                    result += 1

        return result

    def getToyPage(self, rank):
        return self.__toyPageClazz(self.__toys[rank], rank)


class _SubCollectionBuilder(object):
    YEAR_NAME = None

    @classmethod
    def getCollections(cls):
        collection = {}
        subCollections = defaultdict(list)
        for toy in cls._getToysIterator():
            toyInfo = cls._getToyInfo(toy)
            subCollections[toyInfo.getCollectionName()].append(toyInfo)

        for collectionName, toys in subCollections.iteritems():
            collection[collectionName] = _SubCollectionPresenter(collectionName, toys, cls._getToyPageClazz())

        return collection

    @classmethod
    def _getToysIterator(cls):
        return g_cache[cls.YEAR_NAME].toys.itervalues()

    @staticmethod
    def _getToyPageClazz():
        return ToyOldPagePresenter

    @classmethod
    def _getToyInfo(cls, toyDesc):
        return TOYS_INFO_REGISTRY[cls.YEAR_NAME](toyDesc.id)


class NY18SubCollectionBuilder(_SubCollectionBuilder):
    YEAR_NAME = Collections.NewYear18
    ORDER = ('soviet', 'asian', 'traditionalWestern', 'modernWestern')

    @staticmethod
    def _getToyPageClazz():
        return ToyOldPagePresenter


class NY19SubCollectionBuilder(_SubCollectionBuilder):
    YEAR_NAME = Collections.NewYear19
    ORDER = (ToySettings.NEW_YEAR,
     ToySettings.ORIENTAL,
     ToySettings.FAIRYTALE,
     ToySettings.CHRISTMAS)

    @staticmethod
    def _getToyPageClazz():
        return ToyOldPagePresenter


class NY20SubCollectionBuilder(_SubCollectionBuilder):
    YEAR_NAME = Collections.NewYear20
    ORDER = (ToySettings.NEW_YEAR,
     ToySettings.ORIENTAL,
     ToySettings.FAIRYTALE,
     ToySettings.CHRISTMAS,
     ToySettings.MEGA_TOYS)

    @staticmethod
    def _getToyPageClazz():
        return Toy20PagePresenter
