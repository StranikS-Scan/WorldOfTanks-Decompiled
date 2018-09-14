# Embedded file name: scripts/client/gui/shared/utils/requesters/parsers/ShopParser.py
from Parser import Parser
from ShopDataParser import ShopDataParser
from items import vehicles, ITEM_TYPE_NAMES
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.gui_items import ShopItem

class ShopParser(Parser):

    @staticmethod
    def parseVehicles(data, nationId):
        if data is None or not len(data):
            return []
        else:
            result = []
            parser = ShopDataParser(data)
            for intCD, price, isHidden, sellForGold in parser.getItemsIterator(nationId, GUI_ITEM_TYPE.VEHICLE):
                _, _, innationID = vehicles.parseIntCompactDescr(intCD)
                result.append(ShopItem(itemTypeName=ITEM_TYPE_NAMES[GUI_ITEM_TYPE.VEHICLE], compactDescr=innationID, priceOrder=price, nation=nationId, hidden=isHidden))

            return result

    @staticmethod
    def parseModules(data, itemTypeID, nationId):
        if data is None or not len(data):
            return []
        else:
            modules = []
            parser = ShopDataParser(data)
            for intCD, price, isHidden, sellForGold in parser.getItemsIterator(nationId, itemTypeID):
                modules.append(ShopItem(itemTypeName=ITEM_TYPE_NAMES[itemTypeID], compactDescr=intCD, priceOrder=price, nation=nationId, hidden=isHidden))

            return modules

    @staticmethod
    def getParser(itemTypeID):
        if itemTypeID == 1:
            return ShopParser.parseVehicles
        return lambda data, nationId: ShopParser.parseModules(data, itemTypeID, nationId)
