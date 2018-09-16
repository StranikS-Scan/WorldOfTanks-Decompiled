# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/basic_item.py
from items import ITEM_TYPE_NAMES
from items.components import legacy_stuff, shared_components, component_constants

class BasicItem(legacy_stuff.LegacyStuff):
    __slots__ = ('typeID', 'id', 'name', 'compactDescr', 'tags', 'i18n')

    def __init__(self, typeID, itemID, itemName, compactDescr):
        super(BasicItem, self).__init__()
        self.typeID = typeID
        self.id = itemID
        self.name = itemName
        self.compactDescr = compactDescr
        self.tags = component_constants.EMPTY_TAGS
        self.i18n = None
        return

    def __repr__(self):
        return '{}(id={}, name={})'.format(self.__class__.__name__, self.id, self.name)

    @property
    def itemTypeName(self):
        return ITEM_TYPE_NAMES[self.typeID]

    @property
    def userString(self):
        if self.i18n is not None:
            return self.i18n.userString
        else:
            return ''
            return

    @property
    def shortUserString(self):
        if self.i18n is not None:
            return self.i18n.shortString
        else:
            return ''
            return

    @property
    def description(self):
        if self.i18n is not None:
            return self.i18n.description
        else:
            return ''
            return

    def copy(self):
        component = self.__class__(self.typeID, self.id, self.name, self.compactDescr)
        component.tags = self.tags
        component.i18n = self.i18n
        return component
