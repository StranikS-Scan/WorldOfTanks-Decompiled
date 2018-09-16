# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/gui_item.py
import nations
from items import ITEM_TYPE_NAMES, vehicles
from gui import nationCompareByIndex
from gui.Scaleform.locale.MENU import MENU
from helpers import dependency, i18n
from skeletons.gui.shared.gui_items import IGuiItemsFactory

class GUIItem(object):
    __slots__ = ()
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, proxy=None):
        pass

    def __repr__(self):
        return self.__class__.__name__


class HasIntCD(object):

    def __init__(self, intCompactDescr):
        self.intCompactDescr = intCompactDescr
        self.itemTypeID, self.nationID, self.innationID = self._parseIntCompDescr(self.intCompactDescr)

    def _parseIntCompDescr(self, intCompactDescr):
        return vehicles.parseIntCompactDescr(intCompactDescr)

    @property
    def intCD(self):
        return self.intCompactDescr

    @property
    def itemTypeName(self):
        return ITEM_TYPE_NAMES[self.itemTypeID]

    @property
    def nationName(self):
        return nations.NAMES[self.nationID] if self.nationID != nations.NONE_INDEX else ''

    @property
    def nationUserName(self):
        return i18n.makeString(MENU.nations(self.nationName)) if self.nationName else ''

    def __cmp__(self, other):
        if self is other:
            return 1
        res = nationCompareByIndex(self.nationID, other.nationID)
        return res if res else 0


class HasStrCD(object):

    def __init__(self, strCompactDescr):
        self.strCompactDescr = strCompactDescr

    @property
    def strCD(self):
        return self.strCompactDescr
