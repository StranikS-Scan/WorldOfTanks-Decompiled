# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/forbidden_vehicles_to_battle_config.py
from items.vehicles import makeVehicleTypeCompDescrByName
from realm_utils import ResMgr
CONFIG_FILE = 'scripts/item_defs/vehicles/common/forbidden_vehicles_to_battle_config.xml'
g_forbiddenVehiclesToBattle = None

def readConfig():
    section = ResMgr.openSection(CONFIG_FILE)
    config = set()
    if section is None:
        return frozenset(config)
    else:
        forbiddenVehiclesSection = section['forbiddenVehicles']
        if forbiddenVehiclesSection is not None:
            for vehicleSubsection in forbiddenVehiclesSection.values():
                config.add(makeVehicleTypeCompDescrByName(vehicleSubsection.asString))

        return frozenset(config)


def loadForbiddenVehiclesToBattleCfg():
    global g_forbiddenVehiclesToBattle
    g_forbiddenVehiclesToBattle = readConfig()


def getForbiddenForBattleVehicles():
    if g_forbiddenVehiclesToBattle is None:
        loadForbiddenVehiclesToBattleCfg()
    return g_forbiddenVehiclesToBattle
