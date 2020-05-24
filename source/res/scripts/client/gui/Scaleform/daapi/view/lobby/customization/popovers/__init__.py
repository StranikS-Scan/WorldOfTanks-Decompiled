# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/popovers/__init__.py
from collections import namedtuple
from gui.Scaleform.daapi.view.lobby.customization.shared import TYPES_ORDER
ItemsGroupVO = namedtuple('ItemsGroupVO', ('userName', 'titleLabel', 'isTitle'))

class C11nPopoverItemData(object):
    __slots__ = ('item', 'season', 'slotsIds', 'isBase', 'isRemovable', 'isRemoved', 'isFromInventory')

    def __init__(self, item, season=None, isBase=False, isRemovable=False, isRemoved=False, isFromInventory=False):
        self.item = item
        self.season = season
        self.slotsIds = []
        self.isBase = isBase
        self.isRemovable = isRemovable
        self.isRemoved = isRemoved
        self.isFromInventory = isFromInventory


def orderKey(itemData):
    item = itemData.item
    typeOrder = TYPES_ORDER.index(item.itemTypeID)
    return (not itemData.isBase,
     itemData.isRemovable,
     typeOrder,
     item.intCD,
     not itemData.isFromInventory)
