# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/albums/album_sub_model_presenter.py
import logging
from collections import namedtuple
from gui.impl.gen.view_models.views.lobby.new_year.views.albums.ny_open_album_model import NyOpenAlbumModel
from gui.impl.lobby.new_year.albums.collections_builders import NY18SubCollectionBuilder, NY19SubCollectionBuilder, NY20SubCollectionBuilder, NY21SubCollectionBuilder, NY22SubCollectionBuilder
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.new_year.navigation import ViewAliases
from gui.impl.new_year.new_year_helper import formatRomanNumber
from gui.impl.new_year.sounds import NewYearSoundsManager
from new_year.ny_constants import Collections
from new_year.ny_toy_info import NewYear18ToyInfo, NewYear19ToyInfo, NewYear20ToyInfo, NewYear21ToyInfo, NewYear22ToyInfo
from soft_exception import SoftException
from uilogging.ny.loggers import NyAlbumsFlowLogger
_logger = logging.getLogger(__name__)
_CollectionMeta = namedtuple('_CollectionMeta', ('builder', 'toyInfo'))
COLLECTIONS_DATA = {Collections.NewYear18: _CollectionMeta(NY18SubCollectionBuilder, NewYear18ToyInfo),
 Collections.NewYear19: _CollectionMeta(NY19SubCollectionBuilder, NewYear19ToyInfo),
 Collections.NewYear20: _CollectionMeta(NY20SubCollectionBuilder, NewYear20ToyInfo),
 Collections.NewYear21: _CollectionMeta(NY21SubCollectionBuilder, NewYear21ToyInfo),
 Collections.NewYear22: _CollectionMeta(NY22SubCollectionBuilder, NewYear22ToyInfo)}

class AlbumSubModelPresenter(HistorySubModelPresenter):
    DEFAULT_RANK = 1
    _isScopeWatcher = False
    _navigationAlias = ViewAliases.ALBUM_VIEW
    __slots__ = ('_collectionBuilder', '_collectionType', '__year', '__rankToCollection')
    _flowLogger = NyAlbumsFlowLogger()

    def __init__(self, viewModel, parentView):
        super(AlbumSubModelPresenter, self).__init__(viewModel, parentView)
        self._collectionBuilder = None
        self._collectionType = None
        self.__year = None
        self.__rankToCollection = dict()
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def currentCollectionPresenter(self):
        if self._collectionBuilder is None:
            raise SoftException('Collection builder is not initialized properly.')
        return self._collectionBuilder.getCollections()[self._collectionType]

    @property
    def currentRank(self):
        return self.__rankToCollection.get(self._collectionType, self.DEFAULT_RANK)

    @property
    def currentTab(self):
        return self.__year

    @property
    def stateInfo(self):
        return {'collectionType': self._collectionType,
         'rankToCollection': self.__rankToCollection}

    def initialize(self, year, collectionType, rank=1, *args, **kwargs):
        self._collectionType = collectionType
        self.__rankToCollection[self._collectionType] = rank
        self._updateCollectionBuilder(year)
        with self.viewModel.transaction():
            self._updateCollectionData()
            self._updateCollectionTabs()
        self.viewModel.onToyClick += self._onToyClick
        self.viewModel.onGoToRewards += self.__onGoToRewards
        self.viewModel.onCollectionChange += self.__onCollectionChange
        self.viewModel.onRankChange += self.__onRankChange
        super(AlbumSubModelPresenter, self).initialize(*args, **kwargs)

    def update(self, collectionType, rank):
        self._collectionType = collectionType
        if self._collectionType is None:
            return
        else:
            self.__rankToCollection[self._collectionType] = rank
            with self.viewModel.transaction():
                self._updateCollectionData()
            return

    def finalize(self):
        self.viewModel.onCollectionChange -= self.__onCollectionChange
        self.viewModel.onRankChange -= self.__onRankChange
        self.viewModel.onToyClick -= self._onToyClick
        self.viewModel.onGoToRewards -= self.__onGoToRewards
        self._collectionBuilder = None
        self._collectionType = None
        self.__rankToCollection.clear()
        super(AlbumSubModelPresenter, self).finalize()
        return

    def _updateCollectionBuilder(self, year):
        self.__year = year
        self._collectionBuilder = COLLECTIONS_DATA[self.__year].builder()

    def _updateCollectionTabs(self):
        self.viewModel.getCollectionTabs().clear()
        for collectionName in self._collectionBuilder.ORDER:
            self.viewModel.getCollectionTabs().addString(collectionName)

    def _updateCollectionData(self):
        subCollection = self.currentCollectionPresenter
        self.viewModel.setCurrentRank(self.currentRank)
        self.viewModel.setCurrentCollection(self._collectionType)
        self.viewModel.setCurrentRomanRank(formatRomanNumber(self.currentRank))
        self.viewModel.setIsCollectionFull(subCollection.isFull())
        self.viewModel.setTotalToysCount(subCollection.totalToys())
        self.viewModel.setCollectedToysCount(subCollection.currentToys())
        self.viewModel.setTotalRankToysCount(subCollection.totalRankToys(self.currentRank))
        self.viewModel.setCurrentRankToysCount(subCollection.currentRankToys(self.currentRank))
        self._updateToys(subCollection.getToyPage(self.currentRank))
        NewYearSoundsManager.setStylesSwitchBox(self._collectionType)

    def _updateToys(self, toysPage):
        toysList = toysPage.getToys()
        self.viewModel.setToys(toysList)

    def _onToyClick(self):
        pass

    def __onGoToRewards(self):
        self._flowLogger.logRewardsClick(albumTab=self.__year)
        self._goToRewardsView(saveHistory=True, tabName=self.__year, collection=self._collectionType, year=self.__year)

    def __onCollectionChange(self, args):
        self.update(args['collection'], self.__rankToCollection.get(args['collection'], self.DEFAULT_RANK))

    def __onRankChange(self, args):
        self.update(args['collection'], int(args['rank']))

    def _getInfoForHistory(self):
        return {}
