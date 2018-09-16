# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/vehicles.py
from command import Field, W2CSchema, createSubCommandsHandler, SubCommand

class VehiclesSchema(W2CSchema):
    action = Field(required=True, type=basestring)
    vehicle_id = Field(type=(int, long))


def createVehiclesHandler(vehicleInfoHandler):
    subCommands = {'vehicle_info': SubCommand(handler=vehicleInfoHandler)}
    return createSubCommandsHandler('vehicles', VehiclesSchema, 'action', subCommands)
