# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_page_view.py
import logging
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.views.album.collections_builders import NY19SubCollectionBuilder
from gui.impl.new_year.sounds import NewYearSoundEvents
from helpers import int2roman
_logger = logging.getLogger(__name__)
DEFAULT_RANK = 1
DEFAULT_INDEX = 0

class AlbumPageView(NewYearNavigation):
    __slots__ = ('__collections', '__tempIndex', '__tempType', '__tempRank')

    def __init__(self, layoutID, wsFlags, viewModelClazz, typeName=None, *args, **kwargs):
        super(AlbumPageView, self).__init__(layoutID, wsFlags, viewModelClazz, *args, **kwargs)
        self.__tempIndex = DEFAULT_INDEX
        self.__tempType = typeName
        self.__tempRank = DEFAULT_RANK
        self.__collections = None
        return

    @property
    def viewModel(self):
        return super(AlbumPageView, self).getViewModel()

    def getCollection(self, typeName):
        return self.__collections[typeName]

    @staticmethod
    def _getCollectionsBuilder():
        return NY19SubCollectionBuilder

    def _initialize(self, *args, **kwargs):
        soundConfig = {}
        super(AlbumPageView, self)._initialize(soundConfig)
        self.viewModel.onBackBtnClick += self._onBackBtnClick
        self.viewModel.onChangeData += self._onChangeData
        self.viewModel.onCloseBtnClick += self._onCloseBtnClick
        self.viewModel.onPreChangeTypeName += self._onPreChangeType
        self.viewModel.onPreChangeIndex += self._onPreChangeIndex
        self.viewModel.onPreChangeRank += self._onPreChangeRank
        self.viewModel.onToyClick += self._onToyClick
        self.viewModel.onFadeOnFinish += self._onFadeOnFinish
        self.__collections = self._getCollectionsBuilder().getCollections()
        with self.viewModel.transaction() as tx:
            for name in self._getCollectionsBuilder().ORDER:
                tx.getTypesList().addString(name)

            self._changeData(tx, self.__tempType, self.__tempRank, self.__tempIndex)

    def _getInfoForHistory(self):
        viewModel = self.viewModel
        return {'type': viewModel.getCurrentType(),
         'rank': viewModel.getCurrentRank(),
         'index': viewModel.getCurrentIndex()}

    def _restoreState(self, stateInfo):
        self.__tempType = stateInfo['type']
        self.__tempRank = stateInfo['rank']
        self.__tempIndex = stateInfo['index']

    def _changeData(self, model, typeName, rank=None, index=None):
        model.setCurrentIndex(index)
        model.setCurrentRank(rank)
        model.setCurrentType(typeName)
        model.setCurrentRomanRank(int2roman(rank))
        subCollection = self.__collections[typeName]
        model.setIsGetStamp(subCollection.isFull())
        self._changeToyPage(model, subCollection.getToyPage(rank), index)
        model.setFadeIn(True)
        self._newYearSounds.setStylesSwitchBox(typeName)

    def _changeToyPage(self, model, toyPage, index):
        model.setHasStamp(toyPage.hasStamp())
        model.setTotalIndexes(toyPage.getTotalIndexes())
        model.toysList.clear()
        model.toysList.setItems(toyPage.getToys(index))
        model.toysList.getItems().invalidate()

    def _updateData(self):
        with self.viewModel.transaction() as tx:
            self._changeData(tx, tx.getCurrentType(), tx.getCurrentRank(), tx.getCurrentIndex())

    def _finalize(self):
        self.viewModel.onBackBtnClick -= self._onBackBtnClick
        self.viewModel.onCloseBtnClick -= self._onCloseBtnClick
        self.viewModel.onChangeData -= self._onChangeData
        self.viewModel.onPreChangeTypeName -= self._onPreChangeType
        self.viewModel.onPreChangeIndex -= self._onPreChangeIndex
        self.viewModel.onPreChangeRank -= self._onPreChangeRank
        self.viewModel.onToyClick -= self._onToyClick
        self.viewModel.onFadeOnFinish -= self._onFadeOnFinish
        super(AlbumPageView, self)._finalize()

    def _onCloseBtnClick(self, _=None):
        self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_EXIT)
        self._goToMainView()

    def _onBackBtnClick(self, _=None):
        self._goBack()

    def _onToyClick(self, args=None):
        pass

    def _onPreChangeType(self, args=None):
        if not self.viewModel.getCanChange() or args is None or 'typeName' not in args:
            return
        else:
            self.__fadeOut()
            self.__tempType = args['typeName']
            self.__tempRank = DEFAULT_RANK
            self.__tempIndex = DEFAULT_INDEX
            return

    def _onPreChangeRank(self, args=None):
        if not self.viewModel.getCanChange() or args is None or 'rank' not in args:
            return
        else:
            self.__fadeOut()
            self.__tempRank = int(args['rank'])
            self.__tempIndex = DEFAULT_INDEX
            self.__tempType = self.viewModel.getCurrentType()
            return

    def _onPreChangeIndex(self, args=None):
        if not self.viewModel.getCanChange() or args is None or 'index' not in args:
            return
        else:
            with self.viewModel.transaction() as tx:
                tx.setCanChange(False)
                tx.setFadeOutList(True)
            self.__tempIndex = int(args['index'])
            self.__tempRank = self.viewModel.getCurrentRank()
            self.__tempType = self.viewModel.getCurrentType()
            return

    def _onChangeData(self, _=None):
        with self.viewModel.transaction() as tx:
            self._changeData(tx, self.__tempType, self.__tempRank, self.__tempIndex)

    def _onFadeOnFinish(self, _=None):
        self.viewModel.setCanChange(True)

    def __fadeOut(self):
        with self.viewModel.transaction() as tx:
            tx.setCanChange(False)
            tx.setFadeOut(True)
