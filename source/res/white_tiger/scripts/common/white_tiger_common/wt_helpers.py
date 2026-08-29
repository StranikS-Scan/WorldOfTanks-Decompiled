# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/wt_helpers.py


def getTankPortalActualPrice(tankPortalPrice, discountPerToken, discountTokenCount):
    totalDiscount = discountTokenCount * discountPerToken
    return tankPortalPrice - totalDiscount


def isHunterVehicle(vehicleCD, eventVehicles):
    return vehicleCD in eventVehicles.get('hunters', {})


def isBossVehicle(vehicleCD, eventVehicles):
    return vehicleCD in eventVehicles.get('bosses', {})


def isSpecialBossVehicle(vehicleCD, eventVehicles):
    return vehicleCD in eventVehicles.get('specialBosses', {})


def isAnyTypeBoss(vehicleCD, eventVehicles):
    return vehicleCD in eventVehicles.get('bosses', {}) or vehicleCD in eventVehicles.get('specialBosses', {})


def getBossVehicles(eventVehicles):
    return eventVehicles.get('bosses', {})


def getSpecialBossVehicleCDs(eventVehicles):
    return eventVehicles.get('specialBosses', {}).keys()


def getHunterVehicles(eventVehicles):
    return eventVehicles.get('hunters', {})


def isEventVehicle(config, vehCD):
    return vehCD in config['allEventVehicleCDs']


def getVehicleData(config, vehCD):
    if vehCD in config['allEventVehicleCDs']:
        hunters = config['eventVehicles'].get('hunters', {})
        if vehCD in hunters:
            return hunters[vehCD]
        bosses = config['eventVehicles'].get('bosses', {})
        if vehCD in bosses:
            return bosses[vehCD]
        specialBosses = config['eventVehicles'].get('specialBosses', {})
        if vehCD in specialBosses:
            return specialBosses[vehCD]
    return None
