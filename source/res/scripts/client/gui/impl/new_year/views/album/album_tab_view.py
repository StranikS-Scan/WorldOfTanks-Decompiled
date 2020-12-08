# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_tab_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_model import NewYearAlbumModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.navigation import NewYearTabCache
from gui.impl.new_year.views.album.album_cover_view import AlbumCoverView
from gui.impl.new_year.views.album.album_page18_view import AlbumPage18View
from gui.impl.new_year.views.album.album_page19_view import AlbumPage19View
from gui.impl.new_year.views.album.album_page20_view import AlbumPage20View
from gui.impl.new_year.views.album.album_page21_view import AlbumPage21View
from new_year.ny_constants import Collections
_ALBUM_PAGE_VIEWS = {Collections.NewYear18: AlbumPage18View,
 Collections.NewYear19: AlbumPage19View,
 Collections.NewYear20: AlbumPage20View,
 Collections.NewYear21: AlbumPage21View}
_STATE_NAVIGATION = {NewYearTabCache.COVER_STATE: lambda yearName, *args, **kwargs: AlbumCoverView(yearName, *args, **kwargs),
 NewYearTabCache.PAGE_STATE: lambda yearName, *args, **kwargs: _ALBUM_PAGE_VIEWS[yearName](*args, **kwargs)}

class AlbumTabView(NewYearHistoryNavigation):
    __slots__ = ('__yearName', '__currentState')

    def __init__(self, yearName, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_album_tab_view.NewYearAlbumTabView())
        settings.model = NewYearAlbumModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AlbumTabView, self).__init__(settings)
        self.__yearName = yearName

    @property
    def viewModel(self):
        return super(AlbumTabView, self).getViewModel()

    def switchYear(self, yearName):
        self.__saveState()
        self.__yearName = yearName
        self.__invalidate()

    def _initialize(self, stateInfo=None):
        super(AlbumTabView, self)._initialize()
        self.viewModel.onPictureBtnClick += self.__onPictureBtnClick
        self.viewModel.onBackBtnClick += self.__onBackBtnClick
        self.__invalidate(stateInfo)

    def _finalize(self):
        self.viewModel.onPictureBtnClick -= self.__onPictureBtnClick
        self.viewModel.onBackBtnClick -= self.__onBackBtnClick
        self.__saveState()
        super(AlbumTabView, self)._finalize()

    def __saveState(self):
        currentStateInfo = self.getChildView(R.dynamic_ids.newYearAlbumView()).getStateInfo()
        self._tabCache.saveState(self.__yearName, (self.__currentState, currentStateInfo))

    def __invalidate(self, stateInfo=None):
        stateName, stateInfo = stateInfo or self._tabCache.getState(self.__yearName)
        self.__nextState(stateName, **stateInfo)

    def __onCloseBtnClick(self, _=None):
        self._goToMainView()

    def __onBackBtnClick(self, _=None):
        if self._navigationHistory.getLast():
            self._goBack()
        else:
            self.__nextState(NewYearTabCache.COVER_STATE)

    def __updateBackBtn(self):
        if self.__currentState == NewYearTabCache.COVER_STATE:
            self.viewModel.setBackViewName(R.invalid())
        else:
            self.viewModel.setBackViewName(self._getBackPageName() or R.strings.ny.backButton.AlbumMainView())

    def __onPictureBtnClick(self, args=None):
        if args is None or 'typeName' not in args:
            return
        else:
            self.__nextState(NewYearTabCache.PAGE_STATE, args['typeName'])
            return

    def __nextState(self, stateName, *args, **kwargs):
        self.__currentState = stateName
        viewHolder = _STATE_NAVIGATION[stateName](self.__yearName, parentModel=self.viewModel, *args, **kwargs)
        self.setChildView(R.dynamic_ids.newYearAlbumView(), viewHolder)
        self.__updateBackBtn()
