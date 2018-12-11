# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_historic_fact_view.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.views.new_year_album_historic_fact_view_model import NewYearAlbumHistoricFactViewModel
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundEvents
from helpers import dependency
from items.components.ny_constants import MAX_ATMOSPHERE_LEVEL
from skeletons.gui.shared import IItemsCache

class AlbumHistoricFactView(NewYearNavigation):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(AlbumHistoricFactView, self).__init__(R.views.newYearAlbumHistoricFactView, ViewFlags.LOBBY_SUB_VIEW, NewYearAlbumHistoricFactViewModel, *args, **kwargs)

    def _initialize(self, *args, **kwargs):
        nyRequester = dependency.instance(IItemsCache).items.festivity
        super(AlbumHistoricFactView, self)._initialize()
        self.viewModel.onBackBtnClick += self._onBackBtnClick
        self.viewModel.onCloseBtnClick += self._onCloseBtnClick
        self.viewModel.onPrevBtnClick += self._onPrevBtnClick
        self.viewModel.onNextBtnClick += self._onNextBtnClick
        currentLevel = nyRequester.getMaxLevel()
        with self.getViewModel().transaction() as tx:
            tx.setMaxProgressLevel(MAX_ATMOSPHERE_LEVEL)
            tx.setCurrentProgressLevel(currentLevel)
            tx.setCurrentFactIndex(currentLevel)

    def _finalize(self):
        self.viewModel.onBackBtnClick -= self._onBackBtnClick
        self.viewModel.onCloseBtnClick -= self._onCloseBtnClick
        self.viewModel.onPrevBtnClick -= self._onPrevBtnClick
        self.viewModel.onNextBtnClick -= self._onNextBtnClick
        super(AlbumHistoricFactView, self)._finalize()

    def _onBackBtnClick(self, _=None):
        self._goBack()

    def _onCloseBtnClick(self, _=None):
        self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_EXIT)
        self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_2019_EXIT)
        self._goToMainView()

    def _onPrevBtnClick(self, _=None):
        with self.getViewModel().transaction() as tx:
            factIndex = tx.getCurrentFactIndex()
            if factIndex != 1:
                factIndex = factIndex - 1
            tx.setCurrentFactIndex(factIndex)

    def _onNextBtnClick(self, _=None):
        with self.getViewModel().transaction() as tx:
            factIndex = tx.getCurrentFactIndex()
            currentProgressIndex = tx.getCurrentProgressLevel()
            maxProgressIndex = tx.getMaxProgressLevel()
            if factIndex >= currentProgressIndex:
                if currentProgressIndex < maxProgressIndex:
                    factIndex = currentProgressIndex + 1
                else:
                    factIndex = maxProgressIndex
            else:
                factIndex = factIndex + 1
            tx.setCurrentFactIndex(factIndex)

    @property
    def viewModel(self):
        return super(AlbumHistoricFactView, self).getViewModel()
