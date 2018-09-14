# Embedded file name: scripts/client/gui/shared/utils/requesters/parsers/InventoryParser.py
from Parser import Parser
from items import ITEM_TYPE_NAMES
from gui.shared.utils.gui_items import InventoryItem, InventoryVehicle, InventoryTankman

class InventoryParser(Parser):

    @staticmethod
    def parseVehicles(data):
        if data is None:
            return []
        else:
            vehicles = []
            for id, vehCompDescr in data.get('compDescr', {}).items():
                descriptor = vehCompDescr
                ammoLayout = dict(data['shellsLayout'].get(id, {}))
                shells = list(data['shells'].get(id, []))
                crew = list(data['crew'].get(id, []))
                repairCost, health = data['repair'].get(id, (0, 0))
                equipmentsLayout = data['eqsLayout'].get(id, [0, 0, 0])
                equipments = data['eqs'].get(id, [0, 0, 0])
                if not equipments:
                    equipments = [0, 0, 0]
                settings = data['settings'].get(id, 0)
                lock = data['lock'].get(id, 0)
                vehicles.append(InventoryVehicle(compactDescr=descriptor, id=id, crew=crew, shells=shells, ammoLayout=ammoLayout, repairCost=repairCost, health=health, lock=lock, equipments=equipments, equipmentsLayout=equipmentsLayout, settings=settings))

            return vehicles

    @staticmethod
    def parseTankmen(data):
        if data is None:
            return []
        else:
            tankmen = []
            for id, compDescr in data.get('compDescr', {}).items():
                descriptor = compDescr
                vehicleID = data['vehicle'].get(id, -1)
                tankmen.append(InventoryTankman(compactDescr=descriptor, id=id, vehicleID=vehicleID))

            return tankmen

    @staticmethod
    def parseModules(data, itemTypeID):
        if data is None:
            return []
        else:
            modules = []
            for descriptor, count in data.items():
                modules.append(InventoryItem(itemTypeName=ITEM_TYPE_NAMES[itemTypeID], compactDescr=descriptor, count=count))

            return modules

    @staticmethod
    def getParser(itemTypeID):
        if itemTypeID == 1:
            return InventoryParser.parseVehicles
        if itemTypeID == 8:
            return InventoryParser.parseTankmen
        return lambda data: InventoryParser.parseModules(data, itemTypeID)
