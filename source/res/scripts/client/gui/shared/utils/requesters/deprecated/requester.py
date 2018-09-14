# Embedded file name: scripts/client/gui/shared/utils/requesters/deprecated/Requester.py
import BigWorld
import nations
from adisp import async
from items import ITEM_TYPE_INDICES
from debug_utils import LOG_ERROR
from gui.shared.utils.requesters.parsers import InventoryParser
from gui.shared.utils.requesters.parsers import ShopParser
_ARTEFACTS_ITEMS = (ITEM_TYPE_INDICES['optionalDevice'], ITEM_TYPE_INDICES['equipment'])

class Requester(object):
    """
    Async requester of items @see: helpers.Scaleform.utils.items
    @param itemTypeName: item type to request @see: items.ITEM_TYPE_NAMES
    
    Example of usage:
    #Dont forget annotate function @process
    @process
    def updateGuns():
            #make request to inventory
            inventoryGuns = yield Requester('vehicleGun').getFromInventory()
            #continue after request complete
            #do somthing with guns list [InventoryItem, InventoryItem, ...]
    
            #make request to shop
            guns = yield Requester('vehicleGun').getFromShop()
            #continue after request complete
            #do somthing with guns list [ShopItem, ShopItem, ...]
    """
    PARSERS = {'inventory': InventoryParser,
     'shop': ShopParser}

    def __init__(self, itemTypeName):
        self._itemTypeId = ITEM_TYPE_INDICES[itemTypeName]
        self._callback = None
        self._requestsCount = 0
        self._responsesCount = 0
        self._response = []
        return

    @async
    def getAllPossible(self, callback):
        """
        Make request to inventory and shop
        return InventoryItems and ShopItems
        
        Example of usage:
        @process
        def updateGuns():
                guns = yield Requester('vehicleGun').getAllPossible()
                #continue after request complete
                #do somthing with guns list [InventoryItem, InventoryItem, ShopItem, ...]
        """
        self._callback = callback
        self._requestsCount = count(nations.INDICES) + 1
        self._requestInventory()
        for nationId in nations.INDICES.values():
            self._requestShop(nationId)

    @async
    def getFromInventory(self, callback):
        """
        Make request to inventory
        
        Example of usage:
        @process
        def updateGuns():
                guns = yield Requester('vehicleGun').getFromInventory()
                #continue after request complete
                #do somthing with guns list [InventoryItem, InventoryItem, ...]
        """
        self._callback = callback
        self._requestsCount = 1
        self._requestInventory()

    @async
    def getFromShop(self, callback, nation = None):
        """
        Make request to shop
        
        Example of usage:
        @process
        def updateGuns():
                guns = yield Requester('vehicleGun').getFromShop()
                #continue after request complete
                #do somthing with guns list [ShopItem, ShopItem, ...]
        """
        self._callback = callback
        if self._itemTypeId in _ARTEFACTS_ITEMS:
            self._requestsCount = 1
            self._requestShop(nation)
        elif nation is not None:
            self._requestsCount = 1
            self._requestShop(nation)
        else:
            self._requestsCount = len(nations.INDICES)
            for nationId in nations.INDICES.values():
                self._requestShop(nationId)

        return

    def _requestInventory(self):
        raise hasattr(BigWorld.player(), 'inventory') or AssertionError('Request from inventory is not possible')
        BigWorld.player().inventory.getItems(self._itemTypeId, self.__parseInventoryResponse)

    def __parseInventoryResponse(self, responseCode, data):
        listData = []
        if responseCode >= 0:
            listData = Requester.PARSERS['inventory'].getParser(self._itemTypeId)(data)
        else:
            LOG_ERROR('Server return error for inventory getItems request: responseCode=%s, itemTypeId=%s.' % (responseCode, self._itemTypeId))
        self._collectResponse(listData, 'inventory')

    def _requestShop(self, nationId):
        raise hasattr(BigWorld.player(), 'shop') or AssertionError('Request from shop is not possible')
        BigWorld.player().shop.getAllItems(lambda res, data, rev: self.__parseShopResponse(res, data, nationId))

    def __parseShopResponse(self, responseCode, data, nationId):
        listData = []
        if responseCode >= 0:
            listData = Requester.PARSERS['shop'].getParser(self._itemTypeId)(data, nationId)
        else:
            LOG_ERROR('Server return error for shop getItems request: responseCode=%s, itemTypeId=%s, nationId=%s, data=%s.' % (responseCode,
             self._itemTypeId,
             nationId,
             data))
        self._collectResponse(listData, 'shop')

    def _collectResponse(self, response, requestType):
        self._responsesCount += 1
        self._response.extend(response)
        if self._responsesCount == self._requestsCount:
            if self._callback is not None:
                self._callback(self._response)
        return
