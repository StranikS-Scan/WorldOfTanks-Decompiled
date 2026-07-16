# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/gui_item.py
from __future__ import absolute_import
import typing
from functools import total_ordering
from past.builtins import cmp
import nations
from gui.impl import backport
from gui.impl.gen import R
from items import ITEM_TYPE_NAMES, vehicles
from gui import nationSortKeyByIndex
from helpers import dependency
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from soft_exception import SoftException

@total_ordering
class HasIntCD(object):
    __slots__ = ('intCompactDescr', 'itemTypeID', 'nationID', 'innationID')
    __hash__ = None

    def __init__(self, intCompactDescr):
        super(HasIntCD, self).__init__()
        self.intCompactDescr = intCompactDescr
        self.itemTypeID, self.nationID, self.innationID = self._parseIntCompDescr(self.intCompactDescr)

    def __eq__(self, other):
        return self.__compare(other) == 0

    def __lt__(self, other):
        return self.__compare(other) < 0

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
        return backport.text(R.strings.menu.nations.dyn(self.nationName)()) if self.nationName else ''

    def _parseIntCompDescr(self, intCompactDescr):
        return vehicles.parseIntCompactDescr(intCompactDescr)

    def __compare(self, other):
        return 0 if self is other else cmp(nationSortKeyByIndex(self.nationID), nationSortKeyByIndex(other.nationID))


class HasStrCD(object):
    __slots__ = ('strCompactDescr',)

    def __init__(self, strCompactDescr):
        super(HasStrCD, self).__init__()
        self.strCompactDescr = strCompactDescr

    @property
    def strCD(self):
        return self.strCompactDescr


@total_ordering
class GUIItem(object):
    __slots__ = ('_intCD', '_strCD')
    __hash__ = None
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, intCD=None, strCD=None):
        super(GUIItem, self).__init__()
        self._intCD = intCD
        self._strCD = strCD

    def __repr__(self):
        return '{}(intCD={}, strCD={})'.format(self.__class__.__name__, self._intCD, self._strCD)

    def __eq__(self, other):
        return self._compare(other) == 0

    def __lt__(self, other):
        return self._compare(other) < 0

    @property
    def intCDO(self):
        return self._intCD

    @property
    def intCD(self):
        return self._intCD.intCompactDescr if self._intCD is not None else 0

    @property
    def strCD(self):
        return self._strCD.strCD if self._strCD is not None else ''

    @property
    def itemTypeID(self):
        return self._intCD.itemTypeID if self._intCD is not None else 0

    @itemTypeID.setter
    def itemTypeID(self, typeID):
        if self._intCD is not None:
            self._intCD.itemTypeID = typeID
        else:
            raise SoftException('Object does not have HasIntCD')
        return

    @property
    def itemTypeName(self):
        return self._intCD.itemTypeName if self._intCD is not None else ''

    @property
    def nationID(self):
        return self._intCD.nationID if self._intCD is not None else -1

    @property
    def innationID(self):
        return self._intCD.innationID if self._intCD is not None else -1

    @property
    def nationName(self):
        return self._intCD.nationName if self._intCD is not None else ''

    @property
    def nationUserName(self):
        return self._intCD.nationUserName if self._intCD is not None else ''

    def _compare(self, other):
        return cmp(self._intCD, other.intCDO) if self._intCD is not None else cmp(super(GUIItem, self), other)
