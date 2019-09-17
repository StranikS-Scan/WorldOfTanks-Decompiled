# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/festival/racing.py
from binary_collection import BinarySetCollection
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from web_client_api import w2c, W2CSchema

class RacingEventWebApiMixin(object):

    @w2c(W2CSchema, 'get_collections')
    def getRaceCollections(self, _):
        itemsCache = dependency.instance(IItemsCache)
        raceCollections = itemsCache.items.festivity.getRaceCollections()
        binaryCollections = (BinarySetCollection(collection) for collection in raceCollections)
        raceCollections = {}
        for idx, collection in enumerate(binaryCollections):
            elements = [ elementID for elementID, isReceived in collection if isReceived ]
            raceCollections[idx] = elements

        return {'race_collections': raceCollections}
