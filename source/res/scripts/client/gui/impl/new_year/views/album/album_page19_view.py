# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_page19_view.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.views.new_year_album_page19_view_model import NewYearAlbumPage19ViewModel
from gui.impl.new_year.tooltips.album_rewards_content import AlbumRewardsContent
from gui.impl.new_year.tooltips.album_toy_content import Album19ToyContent
from gui.impl.new_year.tooltips.new_year_album_bonus_tooltip import NewYearAlbumBonusTooltip
from gui.impl.new_year.views.album.album_page_view import AlbumPageView
from gui.impl.new_year.views.album.collections_builders import NY19SubCollectionBuilder
from gui.impl.new_year.views.new_year_craft_view import createFilter
from gui.impl.new_year.sounds import NewYearSoundEvents
from helpers import dependency
from items.components.ny_constants import TOY_SETTING_IDS_BY_NAME, MAX_TOY_RANK
from items.ny19 import calcCollectionBonusBySum
from new_year.ny_constants import Collections
from new_year.ny_toy_info import NewYear19ToyInfo
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
_RESET_VALUE = -1

class AlbumPage19View(AlbumPageView):
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)
    __slots__ = ('__newToys', '__newBonus', '__newCount', '__newStamp')

    def __init__(self, layoutID, *args, **kwargs):
        super(AlbumPage19View, self).__init__(layoutID, ViewFlags.LOBBY_SUB_VIEW, NewYearAlbumPage19ViewModel, *args, **kwargs)
        self.__newToys = 0
        self.__newBonus = 0
        self.__newCount = 0
        self.__newStamp = 0

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.newYearAlbumToyTooltipContent:
            toyID = event.getArgument('toyID')
            return Album19ToyContent(toyID)
        if contentID == R.views.newYearAlbumRewardsContent:
            return AlbumRewardsContent(Collections.NewYear19, self.viewModel.getCurrentType())
        return NewYearAlbumBonusTooltip(self.viewModel) if contentID == R.views.newYearAlbumBonusTooltip else super(AlbumPage19View, self).createToolTipContent(event, contentID)

    @staticmethod
    def _getCollectionsBuilder():
        return NY19SubCollectionBuilder

    def _initialize(self, *args, **kwargs):
        super(AlbumPage19View, self)._initialize(*args, **kwargs)
        self.viewModel.onCountAnimFinish += self.__showBonuses
        self.viewModel.onBonusAnimFinish += self.__showNewToys
        self.viewModel.onToysAnimFinish += self.__showStamp
        self.viewModel.onStampAnimFinish += self.__endAnimation

    def _finalize(self):
        self.viewModel.onCountAnimFinish -= self.__showBonuses
        self.viewModel.onBonusAnimFinish -= self.__showNewToys
        self.viewModel.onToysAnimFinish -= self.__showStamp
        self.viewModel.onStampAnimFinish -= self.__endAnimation
        super(AlbumPage19View, self)._finalize()

    def _changeData(self, model, typeName, rank=None, index=None):
        self.__resetAnimation()
        super(AlbumPage19View, self)._changeData(model, typeName, rank, index)
        model.setTotalToys(self.getCollection(typeName).totalToys())
        self.__prepareNewData(model, typeName, rank)

    def _changeToyPage(self, model, toyPage, index):
        super(AlbumPage19View, self)._changeToyPage(model, toyPage, index)
        self.__newToys = toyPage.getNewToys()
        model.setNewToysCount(len(self.__newToys))
        if self.__newToys:
            self._nyController.sendSeenToysInCollection(self.__newToys)

    def _onToyClick(self, args=None):
        if args is None or 'toyID' not in args:
            return
        else:
            toyID = args['toyID']
            toyInfo = NewYear19ToyInfo(toyID)
            craftFilter = createFilter(toyInfo.getToyType(), toyInfo.getSetting(), toyInfo.getRank())
            self._setCraftFilter(*craftFilter)
            self._goToCraftView()
            return

    def _onFadeOnFinish(self, _=None):
        self.viewModel.setIsAnimation(True)
        self.viewModel.setCanChange(True)
        self.__showToysCount()

    def _onCloseBtnClick(self, arg=None):
        self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_2019_EXIT)
        super(AlbumPage19View, self)._onCloseBtnClick(arg)

    def __prepareNewData(self, model, typeName, rank):
        settingID = TOY_SETTING_IDS_BY_NAME[typeName]
        count, stamp, level = self._itemsCache.items.festivity.getAlbums().get(settingID, (0, 0, 0))
        bonus = calcCollectionBonusBySum(settingID, count) * level
        model.setBonusValue(bonus)
        model.setCurrentToys(count)
        model.setIsGetStamp(bool(stamp))
        self.__newBonus = self._nyController.getBattleBonus(settingID)
        self.__newCount = self.getCollection(typeName).currentToys()
        self.__newStamp = self.getCollection(typeName).isFull()
        if self.__newCount > count or self.__newStamp != stamp or self.__newBonus != bonus:
            self._nyController.sendViewAlbum(TOY_SETTING_IDS_BY_NAME[typeName], rank)

    def __showToysCount(self):
        if self.viewModel.getCurrentToys() == self.__newCount:
            self.__showBonuses()
            return
        with self.viewModel.transaction() as tx:
            tx.setNewCurrentToys(self.__newCount)

    def __showBonuses(self):
        if not self.viewModel.getIsAnimation():
            return
        if self.viewModel.getBonusValue() == self.__newBonus:
            self.__showNewToys()
            return
        with self.viewModel.transaction() as tx:
            tx.setNewBonusValue(self.__newBonus)

    def __showNewToys(self):
        if not self.viewModel.getIsAnimation():
            return
        if not self.__newToys:
            self.__showStamp()
            return
        with self.viewModel.transaction() as tx:
            tx.setIsToysShow(True)

    def __showStamp(self):
        if not self.viewModel.getIsAnimation():
            return
        if self.viewModel.getIsGetStamp() == self.__newStamp or self.viewModel.getCurrentRank() != MAX_TOY_RANK:
            self.__endAnimation()
            return
        with self.viewModel.transaction() as tx:
            tx.setIsStampShow(True)
            tx.setIsGetStamp(self.__newStamp)

    def __endAnimation(self):
        self.__resetAnimation()

    def __resetAnimation(self):
        with self.viewModel.transaction() as tx:
            tx.setBonusValue(_RESET_VALUE)
            tx.setCurrentToys(_RESET_VALUE)
            tx.setNewBonusValue(_RESET_VALUE)
            tx.setNewCurrentToys(_RESET_VALUE)
            tx.setIsToysShow(False)
            tx.setIsStampShow(False)
