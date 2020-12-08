# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_page21_view.py
import logging
from adisp import process
from frameworks.wulf import ViewFlags, ViewStatus
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_page21_view_model import NewYearAlbumPage21ViewModel
from gui.impl.new_year.tooltips.album_toy_content import AlbumCurrentToyContent
from gui.impl.new_year.tooltips.new_year_total_bonus_tooltip import NewYearTotalBonusTooltip
from gui.impl.new_year.tooltips.new_year_collection_bonus_tooltip import NewYearCollectionBonusTooltip
from gui.impl.new_year.tooltips.new_year_mega_toy_bonus_tooltip import NewYearMegaToyBonusTooltip
from gui.impl.new_year.views.album.album_page_view import AlbumPageView
from gui.impl.new_year.views.album.collections_builders import NY21SubCollectionBuilder
from helpers import dependency
from items import new_year
from items.components.ny_constants import ToySettings, INVALID_TOY_ID, YEARS_INFO, TOY_TYPE_IDS_BY_NAME, MAX_TOY_RANK
from new_year.ny_bonuses import CreditsBonusHelper
from new_year.ny_toy_info import NewYearCurrentToyInfo
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)

class AlbumPage21View(AlbumPageView):
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(AlbumPage21View, self).__init__(R.views.lobby.new_year.views.new_year_album_page21_view.NewYearAlbumPage21View(), ViewFlags.VIEW, NewYearAlbumPage21ViewModel, *args, **kwargs)

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.lobby.new_year.tooltips.new_year_album_toy_tooltip_content.NewYearAlbumToyTooltipContent():
            toyID = event.getArgument('toyID')
            return AlbumCurrentToyContent(toyID)
        if event.contentID == R.views.lobby.new_year.tooltips.new_year_total_bonus_tooltip.NewYearTotalBonusTooltip():
            return NewYearTotalBonusTooltip()
        return self.__getCurrentTypeBonusTooltip(self.getStateInfo()['typeName']) if event.contentID == R.views.lobby.new_year.tooltips.new_year_collection_bonus_tooltip.NewYearCollectionBonusTooltip() else super(AlbumPage21View, self).createToolTipContent(event, ctID)

    def _initialize(self, *args, **kwargs):
        super(AlbumPage21View, self)._initialize(*args, **kwargs)
        self.viewModel.onHangMegaToy += self.__onHangMegaToy

    def _finalize(self):
        self.viewModel.onHangMegaToy -= self.__onHangMegaToy
        super(AlbumPage21View, self)._finalize()

    @staticmethod
    def _getCollectionsBuilder():
        return NY21SubCollectionBuilder

    def _changeData(self, model, typeName, rank=None):
        model.setIsAnimation(False)
        super(AlbumPage21View, self)._changeData(model, typeName, rank)
        if typeName == ToySettings.MEGA_TOYS:
            model.setBonusValue(CreditsBonusHelper.getMegaToysBonus())
        else:
            model.setBonusValue(CreditsBonusHelper.getCollectionFactor(typeName))
        model.setCreditBonusValue(CreditsBonusHelper.getBonus())
        self.__prepareNewData(model, typeName)

    def _changeToyPage(self, model, toyPage):
        super(AlbumPage21View, self)._changeToyPage(model, toyPage)
        newToys = toyPage.getNewToys()
        model.setIsToysShow(bool(newToys))
        model.setNewToysCount(len(newToys))
        if newToys:
            self._nyController.sendSeenToysInCollection(newToys)

    def _onFadeOnFinish(self, _=None):
        self.viewModel.setIsAnimation(True)
        self.viewModel.setCanChange(True)

    def _onToyClick(self, args=None):
        if args is None:
            return
        else:
            toyID = args.get('toyID', None)
            if toyID is None:
                return
            toyID = int(toyID)
            toyInfo = NewYearCurrentToyInfo(toyID)
            if toyInfo.isMega():
                self._goToCraftView(isMegaOn=True)
                return
            toyTypeID = TOY_TYPE_IDS_BY_NAME[toyInfo.getToyType()]
            settingID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[toyInfo.getSetting()]
            rank = toyInfo.getRank()
            self._goToCraftView(toyTypeID=toyTypeID, settingID=settingID, rank=rank)
            return

    def __prepareNewData(self, model, typeName):
        settingID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[typeName]
        settingStrID = new_year.g_cache.collectionStrIDs[settingID]
        _, stamp, _ = self._itemsCache.items.festivity.getAlbums().get(settingStrID, (0, 0, 0))
        model.setIsGetStamp(self.getCollection(typeName).isFull())
        isStampShow = stamp != self.getCollection(typeName).isFull()
        model.setIsStampShow(isStampShow)
        if isStampShow:
            self._nyController.sendViewAlbum(settingID, MAX_TOY_RANK)

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
        if result.success and self.viewStatus == ViewStatus.LOADED:
            with self.viewModel.transaction() as tx:
                for toyRenderer in tx.toysList.getItems():
                    if toyRenderer.getToyID() == toyID:
                        toyRenderer.setBonusValue(CreditsBonusHelper.getMegaToysBonusValue())

                tx.setBonusValue(CreditsBonusHelper.getMegaToysBonus())
                tx.setCreditBonusValue(CreditsBonusHelper.getBonus())

    def __getCurrentTypeBonusTooltip(self, typeName):
        return NewYearMegaToyBonusTooltip() if typeName == ToySettings.MEGA_TOYS else NewYearCollectionBonusTooltip(self.getStateInfo()['typeName'])
