# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_page20_view.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_page20_view_model import NewYearAlbumPage20ViewModel
from gui.impl.new_year.sounds import NewYearSoundEvents
from gui.impl.new_year.views.album.album_page_view import AlbumPageOldView
from gui.impl.new_year.views.album.collections_builders import NY20SubCollectionBuilder
from new_year.ny_toy_info import NewYear20ToyInfo

class AlbumPage20View(AlbumPageOldView):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(AlbumPage20View, self).__init__(R.views.lobby.new_year.views.new_year_album_page20_view.NewYearAlbumPage20View(), ViewFlags.VIEW, NewYearAlbumPage20ViewModel, *args, **kwargs)

    @staticmethod
    def _getCollectionsBuilder():
        return NY20SubCollectionBuilder

    def _onToyClick(self, args=None):
        if args is None or 'toyID' not in args:
            return
        else:
            toyID = args['toyID']
            self._buyToy(NewYear20ToyInfo(toyID))
            return

    def _finalize(self):
        self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_2020_EXIT)
        super(AlbumPage20View, self)._finalize()
