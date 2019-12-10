# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_page18_view.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_page18_view_model import NewYearAlbumPage18ViewModel
from gui.impl.new_year.views.album.album_page_view import AlbumPageOldView
from gui.impl.new_year.views.album.collections_builders import NY18SubCollectionBuilder
from gui.impl.new_year.sounds import NewYearSoundEvents
from new_year.ny_toy_info import NewYear18ToyInfo

class AlbumPage18View(AlbumPageOldView):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(AlbumPage18View, self).__init__(R.views.lobby.new_year.views.new_year_album_page18_view.NewYearAlbumPage18View(), ViewFlags.VIEW, NewYearAlbumPage18ViewModel, *args, **kwargs)

    @staticmethod
    def _getCollectionsBuilder():
        return NY18SubCollectionBuilder

    def _onToyClick(self, args=None):
        if args is None or 'toyID' not in args:
            return
        else:
            toyID = args['toyID']
            self._buyToy(NewYear18ToyInfo(toyID))
            return

    def _onCloseBtnClick(self, arg=None):
        self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_2018_EXIT)
        super(AlbumPage18View, self)._onCloseBtnClick(arg)
