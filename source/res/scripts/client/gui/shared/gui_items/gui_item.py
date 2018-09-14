# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/gui_item.py
import nations
from items import ITEM_TYPE_NAMES, vehicles
from gui import nationCompareByIndex
from helpers import dependency
from skeletons.gui.shared.gui_items import IGuiItemsFactory

class GUIItem(object):
    """
    Root gui items class. Provides common interface for serialization and deserialization.
    """
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, proxy=None):
        pass

    def __repr__(self):
        return self.__class__.__name__


class HasIntCD(object):
    """
    Abstract class of items which contains int compact descriptor.
    """

    def __init__(self, intCompactDescr):
        self.intCompactDescr = intCompactDescr
        self.itemTypeID, self.nationID, self.innationID = self._parseIntCompDescr(self.intCompactDescr)

    def _parseIntCompDescr(self, intCompactDescr):
        """
        Parses int compact descriptor. Will be overridden by inherited items classes.
        :param intCompactDescr: int compact descriptor
        :return: tuple(item type id, nation id, innation id)
        """
        return vehicles.parseIntCompactDescr(intCompactDescr)

    @property
    def intCD(self):
        return self.intCompactDescr

    @property
    def itemTypeName(self):
        return ITEM_TYPE_NAMES[self.itemTypeID]

    @property
    def nationName(self):
        return nations.NAMES[self.nationID]

    def __cmp__(self, other):
        """
        Compares items by nation and types.
        """
        if self is other:
            return 1
        res = nationCompareByIndex(self.nationID, other.nationID)
        return res if res else 0


class HasStrCD(object):
    """
    Abstract class of items which contains string compact descriptor.
    """

    def __init__(self, strCompactDescr):
        self.strCompactDescr = strCompactDescr

    @property
    def strCD(self):
        return self.strCompactDescr
