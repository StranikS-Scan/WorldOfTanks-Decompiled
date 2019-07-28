# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/team_info.py
from helpers import i18n
from items import vehicles
from gui.Scaleform.locale.EVENT import EVENT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.gui_items.Vehicle import getEventTypeIconPath, getLevelIconPath, getContourIconPath

def _makeVehicleVO(compDescr, data, vehicleID, itemsFactory, isInSquad):
    descr = vehicles.getVehicleType(compDescr)
    vehicle = itemsFactory.createVehicle(typeCompDescr=descr.compactDescr, inventoryID=0)
    return {'vehicleName': vehicle.shortUserName,
     'vehicleTypeIcon': getEventTypeIconPath(vehicle.type, data.get('enabled', True), isInSquad),
     'levelIcon': getLevelIconPath(vehicle.level),
     'vehicleIcon': getContourIconPath(vehicle.name),
     'isAlive': data.get('enabled', True),
     'selected': data.get('selected', False)}


def _makePlayerVO(general, vehicleList, arenaDP, isInSquad):
    vehInfo = arenaDP.getVehicleInfo(general.getVehicleID())
    vo = {'playerData': {'playerName': vehInfo.player.name,
                    'playerLevel': RES_ICONS.getGeneralLevelIcon(general.getLevel()),
                    'platoonType': RES_ICONS.getGeneralIcon(general.getID()),
                    'isAlive': any((veh['isAlive'] for veh in vehicleList)),
                    'isSquad': isInSquad}}
    for idx, vehicle in enumerate(vehicleList, start=1):
        fieldName = 'vehicle{}Data'.format(idx)
        vo[fieldName] = vehicle

    return vo


def makeTeamVehiclesInfo(generals, arenaDP, itemsFactory):
    allGenerals = generals and generals.getGeneralsInfo()
    if not allGenerals:
        return None
    else:
        vehiclesInfo = []
        for general in allGenerals.values():
            vehs = general.getVehicles()
            if not vehs:
                continue
            vehicleID = general.getVehicleID()
            isInSquad = arenaDP.getPlayerVehicleID() == vehicleID or arenaDP.isSquadMan(vehicleID)
            vehicleList = [ _makeVehicleVO(compDescr, data, general.getVehicleID(), itemsFactory, isInSquad) for compDescr, data in vehs.iteritems() ]
            vehiclesInfo.append(_makePlayerVO(general, vehicleList, arenaDP, isInSquad))

        return vehiclesInfo


def makeTeamMissionsInfo(checkpoints):
    return {'currentWave': checkpoints.getCurrentProgress(),
     'maxWave': checkpoints.getGoalValue(),
     'winDescription': i18n.makeString(EVENT.MISSION_TEAM_WIN_DESCRIPTION, goal=checkpoints.getGoalValue())}
