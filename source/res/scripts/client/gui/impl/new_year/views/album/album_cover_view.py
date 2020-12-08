# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_cover_view.py
from collections import namedtuple
import constants
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_OLD_COLLECTIONS_VISITED, NY_OLD_COLLECTIONS_BY_YEAR_VISITED
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_cover_view_model import NewYearAlbumCoverViewModel
from gui.impl.new_year.navigation import ViewAliases
from gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED
from gui.impl.new_year.views.album.album_child_tab_view import AlbumChildTabView
from gui.impl.new_year.views.album.collections_builders import NY18SubCollectionBuilder, NY19SubCollectionBuilder, NY20SubCollectionBuilder, NY21SubCollectionBuilder
from helpers import dependency
from new_year.ny_constants import Collections
from skeletons.gui.shared import IItemsCache
from gui.impl.new_year.navigation import NewYearNavigation
from items.components.ny_constants import YEARS_INFO
_CollectionData = namedtuple('_CollectionData', ('view', 'viewAlias', 'typesList'))
_COLLECTIONS = {Collections.NewYear18: _CollectionData(R.views.lobby.new_year.views.new_year_album18_view.NewYearAlbum18View(), ViewAliases.ALBUM_PAGE18_VIEW, NY18SubCollectionBuilder.ORDER),
 Collections.NewYear19: _CollectionData(R.views.lobby.new_year.views.new_year_album19_view.NewYearAlbum19View(), ViewAliases.ALBUM_PAGE19_VIEW, NY19SubCollectionBuilder.ORDER),
 Collections.NewYear20: _CollectionData(R.views.lobby.new_year.views.new_year_album20_view.NewYearAlbum20View(), ViewAliases.ALBUM_PAGE20_VIEW, NY20SubCollectionBuilder.ORDER),
 Collections.NewYear21: _CollectionData(R.views.lobby.new_year.views.new_year_album21_view.NewYearAlbum21View(), ViewAliases.ALBUM_PAGE21_VIEW, NY21SubCollectionBuilder.ORDER)}

class AlbumCoverView(AlbumChildTabView):
    _itemsCache = dependency.descriptor(IItemsCache)
    _isScopeWatcher = False
    _navigationAlias = ViewAliases.ALBUM_VIEW
    __slots__ = ('__name',)

    def __init__(self, collectionName, parentModel=None, *args, **kwargs):
        settings = ViewSettings(_COLLECTIONS[collectionName].view)
        settings.flags = ViewFlags.COMPONENT
        settings.model = NewYearAlbumCoverViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AlbumCoverView, self).__init__(settings)
        self.__name = collectionName

    @property
    def viewModel(self):
        return super(AlbumCoverView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(AlbumCoverView, self)._initialize()
        isMaxLevel = self._nyController.isMaxAtmosphereLevel()
        with self.viewModel.transaction() as tx:
            tx.setIsMaxLvl(isMaxLevel)
            if constants.IS_CHINA:
                tx.setIsNeedToShowCover(not AccountSettings.getUIFlag(NY_OLD_COLLECTIONS_VISITED))
            else:
                tx.setIsNeedToShowCover(not isMaxLevel)
            for typeName in _COLLECTIONS[self.__name].typesList:
                tx.getTypesList().addString(typeName)

            tx.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
        self.viewModel.onGotoBtnClick += self.__onCollectionBtnClick
        self.viewModel.onPictureBtnClick += self.__onPictureBtnClick
        if not self.viewModel.getIsNeedToShowCover():
            year = YEARS_INFO.convertYearToNum(self.__name)
            if year != YEARS_INFO.CURRENT_YEAR:
                oldCollectionsByYearVisited = AccountSettings.getUIFlag(NY_OLD_COLLECTIONS_BY_YEAR_VISITED)
                oldCollectionsByYearVisited[year] = True
                AccountSettings.setUIFlag(NY_OLD_COLLECTIONS_BY_YEAR_VISITED, oldCollectionsByYearVisited)

    def _finalize(self):
        super(AlbumCoverView, self)._finalize()
        self.viewModel.onGotoBtnClick -= self.__onCollectionBtnClick
        self.viewModel.onPictureBtnClick -= self.__onPictureBtnClick

    def _getInfoForHistory(self):
        return self.__name

    def __onPictureBtnClick(self, args=None):
        parentView = self.getParentView()
        if parentView is not None:
            parentView.viewModel.onPictureBtnClick(args)
        return

    def __onCollectionBtnClick(self):
        if self._nyController.isMaxAtmosphereLevel():
            with self.viewModel.transaction() as tx:
                tx.setIsNeedToShowCover(False)
                AccountSettings.setUIFlag(NY_OLD_COLLECTIONS_VISITED, True)
        else:
            NewYearNavigation.closeMainView()
