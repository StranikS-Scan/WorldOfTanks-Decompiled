# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/basic_item.py
from items import ITEM_TYPE_NAMES
from items.components import legacy_stuff, shared_components, component_constants
_LONG_DESCR_PROPERTY = 'longDescriptionSpecial'
_SHORT_DESCR_PROPERTY = 'shortDescriptionSpecial'

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
        return '{}(id={}, name="{}")'.format(self.__class__.__name__, self.id, self.name)

    @property
    def itemTypeName(self):
        return ITEM_TYPE_NAMES[self.typeID]

    @property
    def userString(self):
        return self.i18n.userString if self.i18n is not None else ''

    @property
    def shortUserString(self):
        return self.i18n.shortString if self.i18n is not None else ''

    @property
    def description(self):
        return self.i18n.description if self.i18n is not None else ''

    @property
    def shortDescriptionSpecial(self):
        return self._getDescription(_SHORT_DESCR_PROPERTY)

    @property
    def longDescriptionSpecial(self):
        return self._getDescription(_LONG_DESCR_PROPERTY)

    def _getDescription(self, descr):
        return self.i18n.__getattribute__(descr) if self.i18n is not None else ''

    def copy(self):
        component = self.__class__(self.typeID, self.id, self.name, self.compactDescr)
        component.tags = self.tags
        component.i18n = self.i18n
        return component
