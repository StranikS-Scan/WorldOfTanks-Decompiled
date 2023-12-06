# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/albums/album_sub_model_presenter.py
import logging
from collections import namedtuple
from gui.impl.gen.view_models.views.lobby.new_year.views.albums.ny_open_album_model import NyOpenAlbumModel
from gui.impl.gen.view_models.views.lobby.new_year.views.albums.ny_album_collection_tab_model import NyAlbumCollectionTabModel
from gui.impl.lobby.new_year.albums.collections_builders import NY18SubCollectionBuilder, NY19SubCollectionBuilder, NY20SubCollectionBuilder, NY21SubCollectionBuilder, NY22SubCollectionBuilder, NY24SubCollectionBuilder
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.new_year.navigation import ViewAliases
from gui.impl.new_year.new_year_helper import formatRomanNumber, collectionRewardQuestsFilterFunc
from gui.impl.new_year.sounds import NewYearSoundsManager
from new_year.ny_toy_info import NewYear18ToyInfo, NewYear19ToyInfo, NewYear20ToyInfo, NewYear21ToyInfo, NewYear22ToyInfo, NewYear24ToyInfo
from soft_exception import SoftException
from new_year.ny_constants import Collections
from skeletons.gui.server_events import IEventsCache
from helpers import dependency
from gui.impl.new_year.new_year_bonus_packer import getNewYearBonusPacker, packBonusModelAndTooltipData
from gui.shop import showIngameShop
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import newYearOldCollectionRewardUrl
_logger = logging.getLogger(__name__)
_CollectionMeta = namedtuple('_CollectionMeta', ('builder', 'toyInfo'))
COLLECTIONS_DATA = {Collections.NewYear18: _CollectionMeta(NY18SubCollectionBuilder, NewYear18ToyInfo),
 Collections.NewYear19: _CollectionMeta(NY19SubCollectionBuilder, NewYear19ToyInfo),
 Collections.NewYear20: _CollectionMeta(NY20SubCollectionBuilder, NewYear20ToyInfo),
 Collections.NewYear21: _CollectionMeta(NY21SubCollectionBuilder, NewYear21ToyInfo),
 Collections.NewYear22: _CollectionMeta(NY22SubCollectionBuilder, NewYear22ToyInfo),
 Collections.NewYear24: _CollectionMeta(NY24SubCollectionBuilder, NewYear24ToyInfo)}

class AlbumSubModelPresenter(HistorySubModelPresenter):
    DEFAULT_RANK = 1
    DEFAULT_COLLECTION = COLLECTIONS_DATA[Collections.NewYear24].builder().ORDER[0]
    _isScopeWatcher = False
    _navigationAlias = ViewAliases.ALBUM_VIEW
    __eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ('_collectionBuilder', '_collectionType', '_collectionTypeToQuest', '__year', '__rankToCollection', '__tooltips')

    def __init__(self, viewModel, parentView):
        super(AlbumSubModelPresenter, self).__init__(viewModel, parentView)
        self._collectionBuilder = None
        self._collectionType = None
        self._collectionTypeToQuest = {}
        self.__year = None
        self.__rankToCollection = dict()
        self.__tooltips = {}
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

    @property
    def toolTips(self):
        return self.__tooltips

    def initialize(self, year, collectionType, rank, *args, **kwargs):
        selectedRank = self.viewModel.getCurrentRank()
        self._collectionType = collectionType
        self.__rankToCollection[self._collectionType] = selectedRank if selectedRank else self.DEFAULT_RANK
        self._updateCollectionBuilder(year)
        with self.viewModel.transaction():
            self._updateCollectionData()
            self._updateCollectionTabs()
        self.viewModel.onToyClick += self._onToyClick
        self.viewModel.onCollectionChange += self.__onCollectionChange
        self.viewModel.onRankChange += self.__onRankChange
        self.viewModel.onCollectionShopClick += self.__onCollectionShopClick
        self.__fillRewardsModel(self.DEFAULT_COLLECTION)
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
        self.viewModel.onCollectionShopClick -= self.__onCollectionShopClick
        self._collectionBuilder = None
        self._collectionType = None
        self.__rankToCollection.clear()
        super(AlbumSubModelPresenter, self).finalize()
        return

    def _updateCollectionBuilder(self, year):
        self.__year = year
        self._collectionBuilder = COLLECTIONS_DATA[self.__year].builder()

    def _updateCollectionTabs(self):
        collectionTabsList = self.viewModel.getCollectionTabs()
        collectionTabsList.clear()
        for collectionName in self._collectionBuilder.ORDER:
            collectionTabModel = NyAlbumCollectionTabModel()
            collectionTabModel.setTitle(collectionName)
            if collectionName == self._collectionType:
                collectionTabModel.setSelectedRank(self.currentRank)
            collectionTabsList.addViewModel(collectionTabModel)

        collectionTabsList.invalidate()

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

    def __fillRewardsModel(self, collectionType):
        currentQuest = self._nyController.getCollectionAwardQuest(self._collectionTypeToQuest, collectionType, collectionRewardQuestsFilterFunc)
        if currentQuest is None:
            _logger.error("Quest for collection: %s doesn't found", collectionType)
        self.__createRewardsModel(currentQuest)
        return

    def __createRewardsModel(self, quest):
        bonusPacker = getNewYearBonusPacker()
        rewardsModel = self.viewModel.getRewards()
        rewardsModel.clear()
        self.__tooltips.clear()
        bonuses = quest.getBonuses()
        packBonusModelAndTooltipData(bonuses, rewardsModel, bonusPacker, self.__tooltips)
        isCollectionFull = self.currentCollectionPresenter.isFull()
        self.viewModel.setIsCollectionFull(isCollectionFull)

    def __onCollectionChange(self, args):
        self.__fillRewardsModel(args['collection'])
        self.update(args['collection'], self.__rankToCollection.get(args['collection'], self.DEFAULT_RANK))

    def __onRankChange(self, args):
        self.update(args['collection'], int(args['rank']))

    def __onCollectionShopClick(self):
        showIngameShop(newYearOldCollectionRewardUrl())

    def _getInfoForHistory(self):
        return {}
