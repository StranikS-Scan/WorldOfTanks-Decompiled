# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/album_toy_content.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.tooltips.new_year_album18_toy_content_model import NewYearAlbum18ToyContentModel
from gui.impl.gen.view_models.new_year.tooltips.new_year_album_toy_content_model import NewYearAlbumToyContentModel
from gui.impl.pub import ViewImpl
from helpers import int2roman
from new_year.ny_toy_info import NewYear19ToyInfo, NewYear18ToyInfo

class AlbumToyContent(ViewImpl):
    __slots__ = ()

    @property
    def viewModel(self):
        return super(AlbumToyContent, self).getViewModel()

    def _createToyInfo(self, toyID):
        raise NotImplementedError

    def _initialize(self, toyID):
        toy = self._createToyInfo(toyID)
        with self.viewModel.transaction() as tx:
            self._initModel(tx, toy)

    def _initModel(self, model, toyInfo):
        model.setRankRoman(int2roman(toyInfo.getRank()))
        model.setRankNumber(str(toyInfo.getRank()))
        model.setToyDesc(toyInfo.getDesc())
        model.setToyIcon(toyInfo.getIcon())
        model.setToyName(toyInfo.getName())
        model.setIsInCollection(toyInfo.isInCollection())
        model.setSetting(toyInfo.getSetting())


class Album19ToyContent(AlbumToyContent):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(Album19ToyContent, self).__init__(R.views.newYearAlbumToyTooltipContent, ViewFlags.VIEW, NewYearAlbumToyContentModel, *args, **kwargs)

    def _createToyInfo(self, toyID):
        return NewYear19ToyInfo(toyID)


class Album18ToyContent(AlbumToyContent):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(Album18ToyContent, self).__init__(R.views.newYearAlbumToy18TooltipContent, ViewFlags.VIEW, NewYearAlbum18ToyContentModel, *args, **kwargs)

    def _createToyInfo(self, toyID):
        return NewYear18ToyInfo(toyID)

    def _initModel(self, model, toyInfo):
        super(Album18ToyContent, self)._initModel(model, toyInfo)
        model.setShards(toyInfo.getShards())
