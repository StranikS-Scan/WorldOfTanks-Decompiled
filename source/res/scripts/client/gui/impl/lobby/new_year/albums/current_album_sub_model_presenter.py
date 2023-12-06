# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/albums/current_album_sub_model_presenter.py
import logging
from gui.impl.gen.view_models.views.lobby.new_year.views.albums.ny_current_album_model import NyCurrentAlbumModel
from gui.impl.lobby.new_year.albums.album_sub_model_presenter import AlbumSubModelPresenter
from gui.impl.lobby.new_year.tooltips.ny_album_decoration_tooltip import NyAlbumDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_collection_bonus_tooltip import NyCollectionBonusTooltip
from items import new_year
from items.components.ny_constants import TOY_TYPE_IDS_BY_NAME, YEARS_INFO
from new_year.ny_bonuses import BonusHelper
from new_year.ny_constants import SyncDataKeys
from new_year.ny_toy_info import NewYearCurrentToyInfo
from shared_utils import inPercents
from gui.impl.backport import BackportTooltipWindow
_logger = logging.getLogger(__name__)

class CurrentAlbumSubModelPresenter(AlbumSubModelPresenter):
    __slots__ = ()
    DEFAULT_RANK = 1

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, year, collectionType, rank=0, *args, **kwargs):
        super(CurrentAlbumSubModelPresenter, self).initialize(year, collectionType, rank, *args, **kwargs)
        self._nyController.onDataUpdated += self.__onDataUpdated

    def finalize(self):
        self._nyController.onDataUpdated -= self.__onDataUpdated
        super(CurrentAlbumSubModelPresenter, self).finalize()

    @staticmethod
    def createToyTooltip(event):
        toyID = event.getArgument('toyID')
        return NyAlbumDecorationTooltip(toyID)

    def createAwardTooltip(self, event):
        tooltipId = event.getArgument('tooltipId')
        window = None
        if self.toolTips.get(tooltipId, None) is not None:
            window = BackportTooltipWindow(self.toolTips[tooltipId], self.getParentWindow())
            window.load()
        return window

    def createCollectionBonusTooltip(self):
        return NyCollectionBonusTooltip(self._collectionType)

    def _updateCollectionData(self):
        super(CurrentAlbumSubModelPresenter, self)._updateCollectionData()
        self.viewModel.setBonusValue(inPercents(BonusHelper.getCommonCollectionFactor(self._collectionType)))
        self.viewModel.setCreditBonusValue(BonusHelper.getCommonBonusInPercents())
        self.__prepareNewData()

    def _updateToys(self, toysPage):
        super(CurrentAlbumSubModelPresenter, self)._updateToys(toysPage)
        newToys = toysPage.getNewToys()
        self.viewModel.setIsToysHidden(not newToys)
        self.viewModel.setNewToysCount(len(newToys))
        if newToys:
            self._nyController.sendSeenToysInCollection(newToys)

    def _onToyClick(self, args=None):
        if args is None:
            return
        else:
            toyID = args.get('toyID', None)
            if toyID is None:
                return
            toyInfo = NewYearCurrentToyInfo(int(toyID))
            toyTypeID = TOY_TYPE_IDS_BY_NAME[toyInfo.getToyType()]
            settingID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[toyInfo.getSetting()]
            self._goToCraftView(toyTypeID=toyTypeID, settingID=settingID, rank=toyInfo.getRank())
            return

    def __prepareNewData(self):
        isCollectionFull = self.currentCollectionPresenter.isFull()
        self.viewModel.setIsCollectionFull(isCollectionFull)
        settingID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[self._collectionType]
        settingStrID = new_year.g_cache.collectionStrIDs[settingID]
        _, stamp, _ = self._itemsCache.items.festivity.getAlbums().get(settingStrID, (0, 0, 0))
        isStampShow = stamp != isCollectionFull
        if isStampShow:
            self._nyController.sendViewAlbum(settingID, YEARS_INFO.getMaxToyRankByYear(YEARS_INFO.CURRENT_YEAR))

    def __onDataUpdated(self, keys):
        if SyncDataKeys.TOY_COLLECTION in keys:
            self._updateCollectionData()
