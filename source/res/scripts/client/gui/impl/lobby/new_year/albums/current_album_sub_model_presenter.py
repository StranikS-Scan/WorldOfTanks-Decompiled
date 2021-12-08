# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/albums/current_album_sub_model_presenter.py
import logging
import typing
from adisp import process
from gui.impl.gen.view_models.views.lobby.new_year.views.albums.ny_current_album_model import NyCurrentAlbumModel
from gui.impl.lobby.new_year.albums.album_sub_model_presenter import AlbumSubModelPresenter
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_current_album_decoration_model import MegaToyState
from gui.impl.new_year.tooltips.album_toy_content import AlbumCurrentToyContent
from gui.impl.lobby.new_year.tooltips.ny_collection_bonus_tooltip import NyCollectionBonusTooltip
from gui.impl.lobby.new_year.tooltips.ny_mega_collection_bonus_tooltip import NyMegaCollectionBonusTooltip
from items import new_year
from items.components.ny_constants import ToySettings, INVALID_TOY_ID, TOY_TYPE_IDS_BY_NAME, YEARS_INFO, MIN_TOY_RANK
from new_year.ny_bonuses import CreditsBonusHelper
from new_year.ny_constants import SyncDataKeys
from new_year.ny_toy_info import NewYearCurrentToyInfo
from shared_utils import findFirst, inPercents
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.components.ny_current_album_decoration_model import NyCurrentAlbumDecorationModel
_logger = logging.getLogger(__name__)

class CurrentAlbumSubModelPresenter(AlbumSubModelPresenter):
    __slots__ = ()
    DEFAULT_RANK = 0

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, year, collectionType, rank=0, *args, **kwargs):
        super(CurrentAlbumSubModelPresenter, self).initialize(year, collectionType, rank, *args, **kwargs)
        self.viewModel.onHangMegaToy += self.__onHangMegaToy
        self._nyController.onDataUpdated += self.__onDataUpdated

    def finalize(self):
        self.viewModel.onHangMegaToy -= self.__onHangMegaToy
        self._nyController.onDataUpdated -= self.__onDataUpdated
        super(CurrentAlbumSubModelPresenter, self).finalize()

    @staticmethod
    def createToyTooltip(event):
        toyID = event.getArgument('toyID')
        return AlbumCurrentToyContent(toyID)

    def createCollectionBonusTooltip(self):
        return NyMegaCollectionBonusTooltip() if self._collectionType == ToySettings.MEGA_TOYS else NyCollectionBonusTooltip(self._collectionType)

    def _updateCollectionData(self):
        super(CurrentAlbumSubModelPresenter, self)._updateCollectionData()
        if self._collectionType == ToySettings.MEGA_TOYS:
            self.viewModel.setBonusValue(inPercents(CreditsBonusHelper.getMegaToysBonus()))
        else:
            self.viewModel.setBonusValue(inPercents(CreditsBonusHelper.getCollectionFactor(self._collectionType)))
        self.viewModel.setCreditBonusValue(CreditsBonusHelper.getBonusInPercents())
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
            self._flowLogger.logToySlotClick(self.currentTab)
            if toyInfo.isMega():
                self._goToCraftView(isMegaOn=True)
            else:
                toyTypeID = TOY_TYPE_IDS_BY_NAME[toyInfo.getToyType()]
                settingID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[toyInfo.getSetting()]
                self._goToCraftView(toyTypeID=toyTypeID, settingID=settingID, rank=MIN_TOY_RANK)
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

    def __onHangMegaToy(self, args):
        toyID = int(args.get('toyID'))
        toyInfo = self._itemsCache.items.festivity.getToys().get(toyID, None)
        if toyInfo is None:
            _logger.error('Mega toy(toyID = %s) not in inventory', toyID)
            return
        else:
            slotDescr = findFirst(lambda slot: slot.type == toyInfo.getToyType(), self._nyController.getSlotDescrs())
            if slotDescr is not None and self._itemsCache.items.festivity.getSlots()[slotDescr.id] == INVALID_TOY_ID:
                self.__hangToy(toyID, slotDescr.id)
            return

    @process
    def __hangToy(self, toyID, slotID):
        result = yield self._nyController.hangToy(toyID, slotID)
        if result.success and self.isLoaded:
            with self.viewModel.transaction() as tx:
                for toyRenderer in tx.getToys():
                    if toyRenderer.getToyID() == toyID:
                        toyRenderer.setBonusValue(inPercents(CreditsBonusHelper.getMegaToysBonusValue()))
                        toyRenderer.setState(MegaToyState.INSTALLED)

                tx.getToys().invalidate()
                tx.setBonusValue(inPercents(CreditsBonusHelper.getMegaToysBonus()))
                tx.setCreditBonusValue(CreditsBonusHelper.getBonusInPercents())

    def __onDataUpdated(self, keys):
        if SyncDataKeys.TOY_COLLECTION in keys:
            self._updateCollectionData()
