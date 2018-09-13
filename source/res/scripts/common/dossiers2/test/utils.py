# Embedded file name: scripts/common/dossiers2/test/utils.py


def getVehicleNationID(vehTypeCompDescr):
    return vehTypeCompDescr >> 4 & 15


def isVehicleSPG(vehTypeCompDescr):
    return False


def getInBattleSeriesIndex(seriesName):
    return {'sniper': 0,
     'killing': 1,
     'piercing': 2}[seriesName]
