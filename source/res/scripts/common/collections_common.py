# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/collections_common.py
from collections import namedtuple
from copy import deepcopy
import typing
if typing.TYPE_CHECKING:
    from typing import Optional
USABLE_COLLECTION_ENTITIES = {'customizationItem', 'dossier', 'tankman'}
UNUSABLE_COLLECTION_ENTITIES = {'photo', 'video', 'note'}
COLLECTION_ITEM_TYPE_NAMES = USABLE_COLLECTION_ENTITIES.union(UNUSABLE_COLLECTION_ENTITIES)
COLLECTIONS_PREFIX = 'cllc'

class CollectionItem(namedtuple('CollectionItem', ('itemId', 'type', 'isSpecial', 'url', 'cdn', 'relatedId'))):

    def __new__(cls, **kwargs):
        defaults = dict(relatedId=0, itemId=0, type='', isSpecial=False, url='', cdn={})
        defaults.update(kwargs)
        return super(CollectionItem, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls()


class Collection(namedtuple('Collection', ('collectionId', 'name', 'items', 'tags', 'rewards', 'isRelatedEventActive'))):

    def __new__(cls, **kwargs):
        defaults = dict(collectionId=0, items={}, tags=set(), rewards={}, name='', isRelatedEventActive=False)
        defaults.update(kwargs)
        cls.__packItemConfigs(defaults)
        return super(Collection, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        self.__packItemConfigs(dataToUpdate)
        return self._replace(**dataToUpdate)

    @classmethod
    def __packItemConfigs(cls, dataToUpdate):
        items = {}
        for itemId, item in dataToUpdate['items'].iteritems():
            items[itemId] = CollectionItem(itemId=itemId, **item)

        dataToUpdate['items'] = items


class CollectionsConfig(namedtuple('CollectionsConfig', ('isEnabled', 'collections'))):

    def __new__(cls, **kwargs):
        cls.__rawData = kwargs
        defaults = dict(isEnabled=False, collections={})
        defaults.update(kwargs)
        cls.__packCollectionConfigs(defaults)
        return super(CollectionsConfig, cls).__new__(cls, **defaults)

    def getCollection(self, collectionId):
        return self.collections.get(collectionId)

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        self.__packCollectionConfigs(dataToUpdate)
        return self._replace(**dataToUpdate)

    def getRawData(self):
        return deepcopy(self.__rawData)

    @classmethod
    def __packCollectionConfigs(cls, dataToUpdate):
        collections = {}
        for collectionId, collection in dataToUpdate['collections'].iteritems():
            collections[collectionId] = Collection(collectionId=collectionId, **collection)

        dataToUpdate['collections'] = collections


def isCollectionsPrefix(itemName):
    return itemName.startswith(COLLECTIONS_PREFIX)


def makeCollectionItemEntitlementName(collectionId, itemId):
    return '_'.join((COLLECTIONS_PREFIX,
     'item',
     str(collectionId),
     str(itemId)))


def makeCollectionRewardEntitlementName(collectionId, requiredCount):
    return '_'.join((COLLECTIONS_PREFIX,
     'reward',
     str(collectionId),
     str(requiredCount)))


class CollectionRelatedItems:

    def __init__(self):
        self.__items = {}

    def setData(self, data):
        relatedItemsCfg = {}
        for collectionId, collectionCfg in data['collections'].iteritems():
            for itemId, itemCfg in collectionCfg['items'].iteritems():
                if 'relatedId' in itemCfg:
                    relatedItemsCfg[itemCfg['relatedId']] = (collectionId, itemId)

        self.__items = relatedItemsCfg

    @property
    def items(self):
        return self.__items


g_collectionsRelatedItems = CollectionRelatedItems()
