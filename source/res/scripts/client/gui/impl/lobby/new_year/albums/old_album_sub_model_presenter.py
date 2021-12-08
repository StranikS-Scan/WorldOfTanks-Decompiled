# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/albums/old_album_sub_model_presenter.py
import typing
from gui import SystemMessages
from gui.impl.lobby.new_year.dialogs.album.album_buy_collection_dialog_builder import AlbumCollectionDialogBuilder
from gui.impl.lobby.new_year.dialogs.album.album_buy_collection_item_dialog_builder import AlbumCollectionItemDialogBuilder
from gui.impl.new_year.tooltips.album_toy_content import AlbumOldToyContent
from gui.impl.lobby.new_year.albums.album_sub_model_presenter import AlbumSubModelPresenter
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from items.components.ny_constants import YEARS_INFO
from new_year.collection_presenters import getCollectionCost
from new_year.ny_constants import SyncDataKeys
from new_year.ny_processor import BuyToyProcessor, BuyCollectionProcessor
from new_year.ny_toy_info import TOYS_INFO_REGISTRY
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.views.albums.ny_old_album_model import NyOldAlbumModel
    from gui.impl.gen.view_models.views.lobby.new_year.components.ny_old_album_decoration_model import NyOldAlbumDecorationModel

class OldAlbumSubModelPresenter(AlbumSubModelPresenter):
    __slots__ = ('__confirmationWindow',)

    def __init__(self, viewModel, parentView):
        super(OldAlbumSubModelPresenter, self).__init__(viewModel, parentView)
        self.__confirmationWindow = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(OldAlbumSubModelPresenter, self).initialize(*args, **kwargs)
        self.viewModel.onBuyFullCollection += self.__onBuyFullCollection
        self._nyController.onDataUpdated += self.__onDataUpdated

    def finalize(self):
        self.viewModel.onBuyFullCollection -= self.__onBuyFullCollection
        self._nyController.onDataUpdated -= self.__onDataUpdated
        if self.__confirmationWindow is not None:
            self.__confirmationWindow.stopWaiting(DialogButtons.CANCEL)
            self.__confirmationWindow = None
        super(OldAlbumSubModelPresenter, self).finalize()
        return

    def _updateCollectionData(self):
        super(OldAlbumSubModelPresenter, self)._updateCollectionData()
        self.__updateShards()

    def createToyTooltip(self, event):
        toyID = event.getArgument('toyID')
        return AlbumOldToyContent(self._collectionBuilder.YEAR_NAME, toyID)

    def updateBuilder(self, year):
        self._updateCollectionBuilder(year)
        self._updateCollectionTabs()

    def _onToyClick(self, args=None):
        if args is None or 'toyID' not in args:
            return
        else:
            toyID = args['toyID']
            toyInfo = TOYS_INFO_REGISTRY[self._collectionBuilder.YEAR_NAME](toyID)
            self.__buyToy(toyInfo)
            return

    def __updateShards(self):
        self.viewModel.setFullCollectionCost(getCollectionCost(self._collectionBuilder.YEAR_NAME, self._collectionType))
        self.viewModel.setTotalShardsPrice(self._itemsCache.items.festivity.getShardsCount())

    @decorators.process('newYear/buyToyWaiting')
    def __buyToy(self, toyInfo):
        builder = AlbumCollectionItemDialogBuilder(toyInfo)
        self.__confirmationWindow = builder.build(withBlur=True)
        result = yield BuyToyProcessor(toyInfo, self.__confirmationWindow).request()
        self.__confirmationWindow = None
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        if not self.isLoaded or not result.success:
            return
        else:
            with self.viewModel.transaction() as model:
                for toyRenderer in model.getToys():
                    canCraft = toyRenderer.getShards() <= self._itemsCache.items.festivity.getShardsCount()
                    toyRenderer.setIsCanCraft(canCraft)
                    if toyRenderer.getToyID() == toyInfo.getID():
                        toyRenderer.setIsNew(True)
                        toyRenderer.setIsInCollection(True)

                newCollectedToysCount = model.getCollectedToysCount() + 1
                model.setCollectedToysCount(newCollectedToysCount)
                model.setCurrentRankToysCount(model.getCurrentRankToysCount() + 1)
                if newCollectedToysCount == model.getTotalToysCount():
                    model.setIsCollectionFull(True)
                self.__updateShards()
            return

    @decorators.process('newYear/buyCollectionWaiting')
    def __onBuyFullCollection(self, *_):
        collectionStrID = YEARS_INFO.getCollectionSettingID(self._collectionType, self._collectionBuilder.YEAR_NAME)
        collectionID = YEARS_INFO.getCollectionIntID(collectionStrID)
        builder = AlbumCollectionDialogBuilder(collectionID)
        self.__confirmationWindow = builder.build(withBlur=True)
        result = yield BuyCollectionProcessor(collectionID, self.__confirmationWindow).request()
        self.__confirmationWindow = None
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        if not self.isLoaded or not result.success:
            return
        else:
            with self.viewModel.transaction() as model:
                for toyRenderer in model.getToys():
                    if not toyRenderer.getIsInCollection():
                        toyRenderer.setIsNew(True)
                        toyRenderer.setIsInCollection(True)

                model.setCollectedToysCount(model.getTotalToysCount())
                model.setCurrentRankToysCount(model.getTotalRankToysCount())
                model.setIsCollectionFull(True)
                self.__updateShards()
            return

    def __onDataUpdated(self, keys):
        if SyncDataKeys.TOY_FRAGMENTS in keys:
            self.__updateShards()
