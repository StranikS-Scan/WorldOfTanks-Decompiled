# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_page19_view.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_page19_view_model import NewYearAlbumPage19ViewModel
from gui.impl.new_year.sounds import NewYearSoundEvents
from gui.impl.new_year.views.album.album_page_view import AlbumPageOldView
from gui.impl.new_year.views.album.collections_builders import NY19SubCollectionBuilder
from new_year.ny_toy_info import NewYear19ToyInfo

class AlbumPage19View(AlbumPageOldView):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(AlbumPage19View, self).__init__(R.views.lobby.new_year.views.new_year_album_page19_view.NewYearAlbumPage19View(), ViewFlags.VIEW, NewYearAlbumPage19ViewModel, *args, **kwargs)

    @staticmethod
    def _getCollectionsBuilder():
        return NY19SubCollectionBuilder

    def _onToyClick(self, args=None):
        if args is None or 'toyID' not in args:
            return
        else:
            toyID = args['toyID']
            self._buyToy(NewYear19ToyInfo(toyID))
            return

    def _onCloseBtnClick(self, arg=None):
        self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_2019_EXIT)
        super(AlbumPage19View, self)._onCloseBtnClick(arg)
