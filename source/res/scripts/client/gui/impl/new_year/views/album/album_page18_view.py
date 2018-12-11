# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_page18_view.py
from frameworks.wulf import ViewFlags
from frameworks.wulf.gui_constants import ViewStatus
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.views.new_year_album_page18_view_model import NewYearAlbumPage18ViewModel
from gui.impl.new_year.tooltips.album_rewards_content import AlbumRewardsContent
from gui.impl.new_year.tooltips.album_toy_content import Album18ToyContent
from gui.impl.new_year.views.album.album_page_view import AlbumPageView
from gui.impl.new_year.views.album.collections_builders import NY18SubCollectionBuilder
from gui.impl.new_year.sounds import NewYearSoundEvents
from gui.shared.utils import decorators
from helpers import dependency
from new_year.ny_constants import Collections
from new_year.ny_processor import BuyToyProcessor
from new_year.ny_toy_info import NewYear18ToyInfo
from skeletons.gui.shared import IItemsCache

class AlbumPage18View(AlbumPageView):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def __init__(self, layoutID, *args, **kwargs):
        super(AlbumPage18View, self).__init__(layoutID, ViewFlags.LOBBY_SUB_VIEW, NewYearAlbumPage18ViewModel, *args, **kwargs)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.newYearAlbumToyTooltipContent:
            toyID = event.getArgument('toyID')
            return Album18ToyContent(toyID)
        return AlbumRewardsContent(Collections.NewYear18, self.viewModel.getCurrentType()) if contentID == R.views.newYearAlbumRewardsContent else super(AlbumPage18View, self).createToolTipContent(event, contentID)

    @staticmethod
    def _getCollectionsBuilder():
        return NY18SubCollectionBuilder

    def _changeData(self, model, typeName, rank=None, index=None):
        super(AlbumPage18View, self)._changeData(model, typeName, rank, index)
        subCollection = self.getCollection(typeName)
        model.setTotalToys(subCollection.totalToys())
        model.setCurrentToys(subCollection.currentToys())
        model.setIsStampShow(False)
        self.__updateShards(model)

    @decorators.process('newYear/buyToyWaiting')
    def _onToyClick(self, args=None):
        if args is None or 'toyID' not in args:
            return
        else:
            toyID = args['toyID']
            toyInfo = NewYear18ToyInfo(toyID)
            result = yield BuyToyProcessor(toyID, toyInfo.getShards()).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if result.success and self.viewStatus != ViewStatus.UNDEFINED:
                with self.viewModel.transaction() as tx:
                    for toyRenderer in tx.toysList.getItems():
                        toyRenderer.setIsCanCraft(toyRenderer.getShards() <= self._itemsCache.items.festivity.getShardsCount())
                        if toyRenderer.getToyID() == toyID:
                            toyRenderer.setIsNew(True)
                            toyRenderer.setIsInCollection(True)

                    tx.setCurrentToys(tx.getCurrentToys() + 1)
                    if tx.getCurrentToys() + 1 == tx.getTotalToys():
                        tx.setIsGetStamp(True)
                        tx.setIsStampShow(True)
                    self.__updateShards(tx)
            return

    def _onCloseBtnClick(self, arg=None):
        self._newYearSounds.playEvent(NewYearSoundEvents.ALBUM_SELECT_2018_EXIT)
        super(AlbumPage18View, self)._onCloseBtnClick(arg)

    def __updateShards(self, model):
        model.setTotalShards(self._itemsCache.items.festivity.getShardsCount())
