# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_cover_view.py
from collections import namedtuple
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.views.new_year_album_cover_view_model import NewYearAlbumCoverViewModel
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundStates
from gui.impl.new_year.views.album.collections_builders import NY18SubCollectionBuilder, NY19SubCollectionBuilder
from helpers import dependency
from items import ny19
from new_year.ny_constants import Collections
from skeletons.gui.shared import IItemsCache
_CollectionData = namedtuple('_CollectionData', ('view', 'viewAlias', 'typesList'))
_COLLECTIONS = {Collections.NewYear18: _CollectionData(R.views.newYearAlbum18View, ViewAliases.ALBUM_PAGE18_VIEW, NY18SubCollectionBuilder.ORDER),
 Collections.NewYear19: _CollectionData(R.views.newYearAlbum19View, ViewAliases.ALBUM_PAGE19_VIEW, NY19SubCollectionBuilder.ORDER)}
_SOUNDS_MAP = {Collections.NewYear18: {NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.ALBUM_SELECT_2018},
 Collections.NewYear19: {NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.ALBUM_SELECT_2019}}

class AlbumCoverView(NewYearNavigation):
    _itemsCache = dependency.descriptor(IItemsCache)
    _isScopeWatcher = False
    _navigationAlias = ViewAliases.ALBUM_VIEW
    __slots__ = ('__name',)

    def __init__(self, collectionName, *args, **kwargs):
        super(AlbumCoverView, self).__init__(_COLLECTIONS[collectionName].view, ViewFlags.COMPONENT, NewYearAlbumCoverViewModel, *args, **kwargs)
        self.__name = collectionName

    @property
    def viewModel(self):
        return super(AlbumCoverView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        soundConfig = _SOUNDS_MAP.get(self.__name, {})
        super(AlbumCoverView, self)._initialize(soundConfig)
        maxLevel = self._itemsCache.items.festivity.getMaxLevel()
        with self.viewModel.transaction() as tx:
            tx.setIsMaxLvl(maxLevel == ny19.CONSTS.MAX_ATMOSPHERE_LEVEL)
            for typeName in _COLLECTIONS[self.__name].typesList:
                tx.getTypesList().addString(typeName)

        self.viewModel.onPictureBtnClick += self.__onPictureBtnClick
        self.viewModel.onOpenFactsBtnClick += self.__onOpenFactsBtnClick

    def _finalize(self):
        super(AlbumCoverView, self)._finalize()
        self.viewModel.onPictureBtnClick -= self.__onPictureBtnClick
        self.viewModel.onOpenFactsBtnClick -= self.__onOpenFactsBtnClick

    def _getInfoForHistory(self):
        return self.__name

    def __onPictureBtnClick(self, args=None):
        if args is None or 'typeName' not in args:
            return
        else:
            self._goToByViewAlias(_COLLECTIONS[self.__name].viewAlias, args['typeName'])
            return

    def __onOpenFactsBtnClick(self, args=None):
        self._goToHistoricFacts()
