# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/detachment/detachment_cache.py
from collections import defaultdict
from typing import Any, Optional, TYPE_CHECKING
from constants import SkinInvData
from gui.shared.gui_items import GUI_ITEM_TYPE, ItemsCollection
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from items.components.detachment_constants import NO_DETACHMENT_ID
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if TYPE_CHECKING:
    from gui.shared.gui_items.detachment import Detachment
    from gui.shared.gui_items.instructor import Instructor
    from skeletons.gui.shared.utils.requesters import IInventoryRequester

class DetachmentCache(IDetachmentCache):
    _itemsCache = dependency.descriptor(IItemsCache)
    _itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self):
        self.clear()

    @property
    def inventory(self):
        return self._itemsCache.items.inventory

    def init(self):
        pass

    def fini(self):
        pass

    def clear(self):
        self._cache = defaultdict(dict)

    def update(self, diff):
        self._invalidateItems(diff)

    def getDetachments(self, criteria=REQ_CRITERIA.EMPTY, withExpired=False):
        if not withExpired:
            criteria |= ~REQ_CRITERIA.DETACHMENT.EXPIRED
        result = ItemsCollection()
        detachmentsData = self.inventory.getItemsData(GUI_ITEM_TYPE.DETACHMENT)
        for invID, detachmentInvData in detachmentsData.iteritems():
            item = self._makeItem(GUI_ITEM_TYPE.DETACHMENT, invID, detachmentInvData.compDescr, invID=invID, proxy=self, vehInvID=detachmentInvData.linkedInvID)
            if criteria(item):
                result[invID] = item

        return result

    def getDetachment(self, invID):
        detachmentsData = self.inventory.getItemsData(GUI_ITEM_TYPE.DETACHMENT)
        detachmentInvData = detachmentsData.get(invID)
        return self._makeItem(GUI_ITEM_TYPE.DETACHMENT, invID, detachmentInvData.compDescr, invID=invID, proxy=self, vehInvID=detachmentInvData.linkedInvID) if detachmentInvData is not None else None

    def getInstructors(self, criteria=REQ_CRITERIA.EMPTY, withHidden=False):
        if not withHidden:
            criteria |= ~REQ_CRITERIA.CUSTOM(lambda item: item.isUnremovable and item.isExcluded)
        result = ItemsCollection()
        instructorsData = self.inventory.getItemsData(GUI_ITEM_TYPE.INSTRUCTOR)
        for invID, instructorInvData in instructorsData.iteritems():
            item = self._makeItem(GUI_ITEM_TYPE.INSTRUCTOR, invID, instructorInvData.compDescr, invID=invID, proxy=self, detInvID=instructorInvData.linkedInvID)
            if criteria(item):
                result[invID] = item

        return result

    def getInstructor(self, invID):
        instructorsData = self.inventory.getItemsData(GUI_ITEM_TYPE.INSTRUCTOR)
        instructorInvData = instructorsData.get(invID)
        return self._makeItem(GUI_ITEM_TYPE.INSTRUCTOR, invID, instructorInvData.compDescr, invID=invID, proxy=self, detInvID=instructorInvData.linkedInvID) if instructorInvData is not None else None

    def _invalidateItems(self, diff):
        if diff is None:
            self.clear()
            return
        else:
            invalidate = defaultdict(set)
            inventoryDiff = diff.get('inventory')
            if inventoryDiff:
                crewSkinsDiff = inventoryDiff.get(GUI_ITEM_TYPE.CREW_SKINS)
                if crewSkinsDiff:
                    outfitsDiff = crewSkinsDiff.get(SkinInvData.OUTFITS, {})
                    invalidate[GUI_ITEM_TYPE.DETACHMENT].update(outfitsDiff.iterkeys())
                detachmentsDiff = inventoryDiff.get(GUI_ITEM_TYPE.DETACHMENT)
                if detachmentsDiff:
                    detachmentsCompDescrDiff = detachmentsDiff.get('compDescr')
                    if detachmentsCompDescrDiff:
                        invalidate[GUI_ITEM_TYPE.DETACHMENT].update(detachmentsCompDescrDiff.iterkeys())
                    for vehInvID, detInvID in detachmentsDiff.get('vehicle', {}).iteritems():
                        vehicle = self._itemsCache.items.getVehicle(vehInvID)
                        if vehicle:
                            curVehDetInvID = vehicle.getLinkedDetachmentID()
                            if curVehDetInvID != NO_DETACHMENT_ID:
                                invalidate[GUI_ITEM_TYPE.DETACHMENT].add(curVehDetInvID)
                        if detInvID:
                            invalidate[GUI_ITEM_TYPE.DETACHMENT].add(detInvID)

                    detachmentRecycleBin = detachmentsDiff.get('recycleBin')
                    if detachmentRecycleBin:
                        invalidate[GUI_ITEM_TYPE.DETACHMENT].update(detachmentRecycleBin.iterkeys())
                instructorsDiff = inventoryDiff.get(GUI_ITEM_TYPE.INSTRUCTOR)
                if instructorsDiff:
                    compDescrDiff = instructorsDiff.get('compDescr')
                    if compDescrDiff:
                        invalidate[GUI_ITEM_TYPE.INSTRUCTOR].update(compDescrDiff.iterkeys())
                    detDiff = instructorsDiff.get('detachment')
                    if detDiff:
                        invalidate[GUI_ITEM_TYPE.INSTRUCTOR].update(detDiff.iterkeys())
                    excludedDiff = instructorsDiff.get('excluded')
                    if excludedDiff:
                        invalidate[GUI_ITEM_TYPE.INSTRUCTOR].update(excludedDiff.iterkeys())
            for itemTypeID, uniqueIDs in invalidate.iteritems():
                itemTypeCache = self._cache[itemTypeID]
                for uid in uniqueIDs:
                    self.inventory.invalidateItem(itemTypeID, uid)
                    itemTypeCache.pop(uid, 0)

            return

    def _makeItem(self, itemTypeIdx, uid, *args, **kwargs):
        container = self._cache[itemTypeIdx]
        if uid in container:
            return container[uid]
        else:
            item = self._itemsFactory.createGuiItem(itemTypeIdx, *args, **kwargs)
            if item is not None:
                container[uid] = item
            return item
