# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/album_rewards_content.py
import logging
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.tooltips.new_year_album_rewards_content_model import NewYearAlbumRewardsContentModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items import ny19
from nations import AVAILABLE_NAMES
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class AlbumRewardsContent(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(AlbumRewardsContent, self).__init__(R.views.newYearAlbumRewardsContent, ViewFlags.VIEW, NewYearAlbumRewardsContentModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(AlbumRewardsContent, self).getViewModel()

    def _initialize(self, collectionName, subCollection):
        super(AlbumRewardsContent, self)._initialize()
        questID = ny19.g_cache.collectionRewardsByCollectionID[subCollection]
        quest = self._eventsCache.getQuestByID(questID)
        bonuses = quest.getBonuses('customizations')
        if not bonuses:
            _logger.error('Collection rewards dont have customizations bonuses')
            return
        with self.viewModel.transaction() as tx:
            for custBonus in bonuses[0].getList():
                custItem = self._itemsCache.items.getItemByCD(custBonus['intCD'])
                self.__setName(custItem, tx)

            tx.setCollectionName(collectionName)

    def __setName(self, custItem, model):
        if custItem.itemTypeID == GUI_ITEM_TYPE.STYLE:
            model.setStyleName(custItem.userName)
            if custItem.descriptor.filter is not None:
                nationArray = model.getNations()
                nationArray.clear()
                nations = custItem.descriptor.filter.include[0].nations or []
                for nationID in nations:
                    nationArray.addString(AVAILABLE_NAMES[nationID])

                nationArray.invalidate()
        elif custItem.itemTypeID == GUI_ITEM_TYPE.EMBLEM:
            model.setEmblemName(custItem.userName)
        elif custItem.itemTypeID == GUI_ITEM_TYPE.INSCRIPTION:
            model.setInscriptionName(custItem.userName)
        return
