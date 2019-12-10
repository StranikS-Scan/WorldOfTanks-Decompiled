# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_cover_view.py
from collections import namedtuple
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_cover_view_model import NewYearAlbumCoverViewModel
from gui.impl.new_year.navigation import ViewAliases
from gui.impl.new_year.views.album.album_child_tab_view import AlbumChildTabView
from gui.impl.new_year.views.album.collections_builders import NY18SubCollectionBuilder, NY19SubCollectionBuilder, NY20SubCollectionBuilder
from helpers import dependency
from items import new_year
from new_year.ny_constants import Collections
from skeletons.gui.shared import IItemsCache
_CollectionData = namedtuple('_CollectionData', ('view', 'viewAlias', 'typesList'))
_COLLECTIONS = {Collections.NewYear18: _CollectionData(R.views.lobby.new_year.views.new_year_album18_view.NewYearAlbum18View(), ViewAliases.ALBUM_PAGE18_VIEW, NY18SubCollectionBuilder.ORDER),
 Collections.NewYear19: _CollectionData(R.views.lobby.new_year.views.new_year_album19_view.NewYearAlbum19View(), ViewAliases.ALBUM_PAGE19_VIEW, NY19SubCollectionBuilder.ORDER),
 Collections.NewYear20: _CollectionData(R.views.lobby.new_year.views.new_year_album20_view.NewYearAlbum20View(), ViewAliases.ALBUM_PAGE20_VIEW, NY20SubCollectionBuilder.ORDER)}

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
        maxLevel = self._itemsCache.items.festivity.getMaxLevel()
        with self.viewModel.transaction() as tx:
            tx.setIsMaxLvl(maxLevel == new_year.CONSTS.MAX_ATMOSPHERE_LVL)
            for typeName in _COLLECTIONS[self.__name].typesList:
                tx.getTypesList().addString(typeName)

        self.viewModel.onPictureBtnClick += self.__onPictureBtnClick

    def _finalize(self):
        super(AlbumCoverView, self)._finalize()
        self.viewModel.onPictureBtnClick -= self.__onPictureBtnClick

    def _getInfoForHistory(self):
        return self.__name

    def __onPictureBtnClick(self, args=None):
        parentView = self.getParentView()
        if parentView is not None:
            parentView.viewModel.onPictureBtnClick(args)
        return
