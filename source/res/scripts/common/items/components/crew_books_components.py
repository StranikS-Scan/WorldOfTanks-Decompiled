# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/crew_books_components.py
import items
import nations
from items.components.crew_books_constants import CrewBookCacheType, CREW_BOOK_RARITY

class CrewBook(object):
    itemType = CrewBookCacheType.CREW_BOOK
    __slots__ = ('id', 'tags', 'priceGroup', 'iconID', 'name', 'description', 'nation', 'type', 'priceGroupTags')

    def __init__(self, ID, priceGroup, name, description, iconID, type, tags):
        self.id = ID
        self.priceGroup = priceGroup
        self.tags = tags
        self.name = name
        self.description = description
        self.iconID = iconID
        self.nation = None
        self.type = type
        self.priceGroupTags = frozenset()
        return

    @property
    def itemTypeName(self):
        pass

    @property
    def compactDescr(self):
        return items.makeIntCompactDescrByID('crewBook', self.itemType, self.id)

    @property
    def level(self):
        return None

    def getExtensionLessIcon(self):
        return self.iconID.split('.png')[0]

    def getUserName(self):
        name = self.type
        if name not in CREW_BOOK_RARITY.NO_NATION_TYPES:
            name += ':' + self.nation
        return name


class PriceGroup(object):
    itemType = CrewBookCacheType.ITEM_GROUP
    __slots__ = ('price', 'notInShop', 'id', 'name', 'tags')

    def __init__(self):
        self.price = (0, 0, 0)
        self.name = None
        self.id = 0
        self.notInShop = False
        self.tags = []
        return

    @property
    def compactDescr(self):
        return items.makeIntCompactDescrByID('crewBook', self.itemType, self.id)


class CrewBooksCache(object):
    __slots__ = ('priceGroups', 'priceGroupNames', 'books', 'rarityGroups', 'priceGroupTags', 'itemToPriceGroup')

    def __init__(self):
        self.priceGroupTags = {}
        self.books = {}
        self.rarityGroups = {}
        self.priceGroups = {}
        self.priceGroupNames = {}
        self.itemToPriceGroup = {}

    def getCrewBookExp(self, id):
        crewBookItem = self.books[id]
        rarityGroup = crewBookItem.type
        return self.rarityGroups[rarityGroup]

    def validateCrewBookNation(self, itemId, nationID):
        item = self.books.get(itemId, None)
        if item is None:
            return False
        else:
            nation = nations.NAMES[nationID]
            return False if item.nation and item.nation != nation else True
