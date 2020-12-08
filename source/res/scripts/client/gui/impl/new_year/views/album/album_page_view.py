# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_page_view.py
import logging
from frameworks.wulf import ViewStatus, ViewSettings
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED, formatRomanNumber
from gui.impl.new_year.tooltips.album_toy_content import AlbumOldToyContent
from gui.impl.new_year.views.album.album_child_tab_view import AlbumChildTabView
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_page_old_view_model import NewYearAlbumPageOldViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_page_view_model import NewYearAlbumPageViewModel
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from helpers import dependency
from items.components.ny_constants import YEARS_INFO
from new_year.collection_presenters import getCollectionCost
from new_year.ny_constants import SyncDataKeys
from new_year.ny_processor import BuyToyProcessor, BuyCollectionProcessor
from skeletons.gui.shared import IItemsCache
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
_logger = logging.getLogger(__name__)
DEFAULT_RANK = 1
_NEED_TO_SHOW_SCROLL = 15

class AlbumPageView(AlbumChildTabView):
    __slots__ = ('__collections', '__tempType', '__tempRank')

    def __init__(self, layoutID, wsFlags, viewModelClazz, typeName=None, rank=DEFAULT_RANK, parentModel=None, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = viewModelClazz()
        settings.args = args
        settings.kwargs = kwargs
        super(AlbumPageView, self).__init__(settings)
        self.__tempType = typeName
        self.__tempRank = rank
        self.__collections = None
        return

    @property
    def viewModel(self):
        return super(AlbumPageView, self).getViewModel()

    def getCollection(self, typeName):
        return self.__collections[typeName]

    def getStateInfo(self):
        return {'typeName': self.__tempType,
         'rank': self.__tempRank}

    @staticmethod
    def _getCollectionsBuilder():
        raise NotImplementedError

    def _initialize(self, *args, **kwargs):
        soundConfig = {}
        super(AlbumPageView, self)._initialize(soundConfig)
        self.viewModel.onChangeData += self._onChangeData
        self.viewModel.onPreChangeTypeName += self._onPreChangeType
        self.viewModel.onPreChangeRank += self._onPreChangeRank
        self.viewModel.onToyClick += self._onToyClick
        self.viewModel.onFadeOnFinish += self._onFadeOnFinish
        self.viewModel.onGoToRewards += self._onGoToRewards
        self.__collections = self._getCollectionsBuilder().getCollections()
        with self.viewModel.transaction() as tx:
            for name in self._getCollectionsBuilder().ORDER:
                tx.getTypesList().addString(name)

            self._changeData(tx, self.__tempType, self.__tempRank)
            tx.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)

    def _getInfoForHistory(self):
        viewModel = self.viewModel
        return {'typeName': viewModel.getCurrentType(),
         'rank': viewModel.getCurrentRank()}

    def _changeData(self, model, typeName, rank=None):
        model.setCurrentRank(rank)
        model.setCurrentType(typeName)
        model.setCurrentRomanRank(formatRomanNumber(rank))
        subCollection = self.__collections[typeName]
        model.setIsGetStamp(subCollection.isFull())
        self._changeToyPage(model, subCollection.getToyPage(rank))
        model.setTotalToys(subCollection.totalToys())
        model.setCurrentToys(subCollection.currentToys())
        model.setFadeIn(True)
        model.setCurrentRankToys(subCollection.currentRankToys(rank))
        model.setTotalRankToys(subCollection.totalRankToys(rank))
        self._newYearSounds.setStylesSwitchBox(typeName)

    def _changeToyPage(self, model, toyPage):
        model.setHasStamp(toyPage.hasStamp())
        toysList = toyPage.getToys()
        model.toysList.setItems(toysList)
        model.setIsNeedShowScroll(len(toysList) > _NEED_TO_SHOW_SCROLL)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.ALBUM_CLICK)

    def _updateData(self):
        with self.viewModel.transaction() as tx:
            self._changeData(tx, tx.getCurrentType(), tx.getCurrentRank())

    def _finalize(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.ALBUM_ITEM_STOP)
        self.viewModel.onChangeData -= self._onChangeData
        self.viewModel.onPreChangeTypeName -= self._onPreChangeType
        self.viewModel.onPreChangeRank -= self._onPreChangeRank
        self.viewModel.onToyClick -= self._onToyClick
        self.viewModel.onFadeOnFinish -= self._onFadeOnFinish
        self.viewModel.onGoToRewards -= self._onGoToRewards
        super(AlbumPageView, self)._finalize()

    def _onToyClick(self, args=None):
        pass

    def _onPreChangeType(self, args=None):
        if not self.viewModel.getCanChange() or args is None or 'typeName' not in args:
            return
        else:
            self.__fadeOut()
            self.__tempType = args['typeName']
            self.__tempRank = DEFAULT_RANK
            return

    def _onPreChangeRank(self, args=None):
        if not self.viewModel.getCanChange() or args is None or 'rank' not in args:
            return
        else:
            self.__fadeOut()
            self.__tempRank = int(args['rank'])
            self.__tempType = self.viewModel.getCurrentType()
            return

    def _onChangeData(self, _=None):
        with self.viewModel.transaction() as tx:
            self._changeData(tx, self.__tempType, self.__tempRank)

    def _onFadeOnFinish(self, _=None):
        self.viewModel.setCanChange(True)

    def _onGoToRewards(self, *_):
        yearName = self._getCollectionsBuilder().YEAR_NAME
        self._goToRewardsView(tabName=yearName, year=yearName, collection=self.viewModel.getCurrentType())

    def __fadeOut(self):
        with self.viewModel.transaction() as tx:
            tx.setCanChange(False)
            tx.setFadeOut(True)


class AlbumPageOldView(AlbumPageView):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    @property
    def viewModel(self):
        return super(AlbumPageOldView, self).getViewModel()

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.lobby.new_year.tooltips.new_year_toy_old_tooltip_content.NewYearAlbumToyOldTooltipContent():
            toyID = event.getArgument('toyID')
            return AlbumOldToyContent(self._getCollectionsBuilder().YEAR_NAME, toyID)
        return super(AlbumPageOldView, self).createToolTipContent(event, ctID)

    def _changeData(self, model, typeName, rank=None):
        super(AlbumPageOldView, self)._changeData(model, typeName, rank)
        model.setIsStampShow(False)
        self.__updateShards(model, typeName)

    def _initialize(self, *args, **kwargs):
        super(AlbumPageOldView, self)._initialize(*args, **kwargs)
        self.viewModel.onBuyFullCollection += self.__onBuyFullCollection
        self._nyController.onDataUpdated += self.__onDataUpdated

    def _finalize(self):
        self.viewModel.onBuyFullCollection -= self.__onBuyFullCollection
        self._nyController.onDataUpdated -= self.__onDataUpdated
        super(AlbumPageOldView, self)._finalize()

    @decorators.process('newYear/buyToyWaiting')
    def _buyToy(self, toyInfo):
        result = yield BuyToyProcessor(toyInfo, self.getParentWindow()).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        if result.success and self.viewStatus == ViewStatus.LOADED:
            with self.viewModel.transaction() as tx:
                for toyRenderer in tx.toysList.getItems():
                    toyRenderer.setIsCanCraft(toyRenderer.getShards() <= self._itemsCache.items.festivity.getShardsCount())
                    if toyRenderer.getToyID() == toyInfo.getID():
                        toyRenderer.setIsNew(True)
                        toyRenderer.setIsInCollection(True)

                tx.setCurrentToys(tx.getCurrentToys() + 1)
                tx.setCurrentRankToys(tx.getCurrentRankToys() + 1)
                if tx.getCurrentToys() + 1 == tx.getTotalToys():
                    tx.setIsStampShow(True)
                    tx.setIsGetStamp(True)
                self.__updateShards(tx, self.viewModel.getCurrentType())

    def __onDataUpdated(self, keys):
        if SyncDataKeys.TOY_FRAGMENTS in keys:
            with self.viewModel.transaction() as tx:
                self.__updateShards(tx, tx.getCurrentType())

    def __updateShards(self, model, typeName):
        model.setCostFullCollection(getCollectionCost(self._getCollectionsBuilder().YEAR_NAME, typeName))
        model.setTotalShards(self._itemsCache.items.festivity.getShardsCount())

    @decorators.process('newYear/buyCollectionWaiting')
    def __onBuyFullCollection(self, *_):
        collectionStrID = YEARS_INFO.getCollectionSettingID(self.viewModel.getCurrentType(), self._getCollectionsBuilder().YEAR_NAME)
        collectionID = YEARS_INFO.getCollectionIntID(collectionStrID)
        result = yield BuyCollectionProcessor(collectionID, self.getParentWindow()).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        if result.success and self.viewStatus == ViewStatus.LOADED:
            with self.viewModel.transaction() as tx:
                for toyRenderer in tx.toysList.getItems():
                    if not toyRenderer.getIsInCollection():
                        toyRenderer.setIsNew(True)
                        toyRenderer.setIsInCollection(True)

                tx.setCurrentToys(tx.getTotalToys())
                tx.setCurrentRankToys(tx.getTotalRankToys())
                tx.setIsGetStamp(True)
                tx.setIsStampShow(True)
                self.__updateShards(tx, self.viewModel.getCurrentType())
