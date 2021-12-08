# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/albums/toy_page_presenter.py
import typing
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_album_decoration_model import NyAlbumDecorationModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_current_album_decoration_model import NyCurrentAlbumDecorationModel, MegaToyState
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_old_album_decoration_model import NyOldAlbumDecorationModel
from helpers import dependency
from items.components.ny_constants import ToyTypes, YEARS_INFO
from new_year.ny_bonuses import CreditsBonusHelper
from skeletons.gui.shared import IItemsCache
from shared_utils import inPercents
if typing.TYPE_CHECKING:
    from new_year.ny_toy_info import _NewYearCommonToyInfo
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
        return True if self.__rank == YEARS_INFO.getMaxToyRankByYear(YEARS_INFO.CURRENT_YEAR) else False

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
        return NyAlbumDecorationModel()

    def _setToyRendererModel(self, renderer, toy):
        renderer.setIsInCollection(toy.isInCollection())
        renderer.setToyID(toy.getID())
        isMega = toy.isMega()
        renderer.setIsMega(isMega)
        renderer.setToyType(ToyTypes.MEGA_COMMON if isMega else toy.getToyType())
        renderer.setToyImageName(toy.getIconName())

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
        return NyOldAlbumDecorationModel()

    def _setToyRendererModel(self, renderer, toy):
        super(ToyOldPagePresenter, self)._setToyRendererModel(renderer, toy)
        renderer.setShards(toy.getShards())
        renderer.setIsCanCraft(toy.getShards() <= self._itemsCache.items.festivity.getShardsCount())


class NYToyPagePresenter(ToySinglePagePresenter):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__newToys',)

    def __init__(self, toys, rank):
        super(NYToyPagePresenter, self).__init__(toys, rank)
        self.__newToys = set()

    def getToys(self, index=0):
        self.__newToys = set()
        return super(NYToyPagePresenter, self).getToys(index)

    def getNewToys(self):
        return self.__newToys

    @staticmethod
    def _getToyRendererModel():
        return NyCurrentAlbumDecorationModel()

    def _setToyRendererModel(self, renderer, toy):
        super(NYToyPagePresenter, self)._setToyRendererModel(renderer, toy)
        toyInfo = self._itemsCache.items.festivity.getToys().get(toy.getID())
        if toyInfo is not None:
            renderer.setIsNew(toyInfo.isNewInCollection())
            if toyInfo.isNewInCollection():
                self.__newToys.add(toyInfo.getID())
                renderer.setNewNumber(len(self.__newToys))
            if toyInfo.isMega():
                if toyInfo.getID() in self._itemsCache.items.festivity.getSlots():
                    renderer.setBonusValue(inPercents(CreditsBonusHelper.getMegaToysBonusByCount(1)))
                    renderer.setState(MegaToyState.INSTALLED)
                elif toyInfo.getCount() > 0:
                    renderer.setState(MegaToyState.RECEIVED)
                elif toyInfo.isInCollection():
                    renderer.setState(MegaToyState.CRASHED)
                else:
                    renderer.setState(MegaToyState.NOTRECEIVED)
        return
