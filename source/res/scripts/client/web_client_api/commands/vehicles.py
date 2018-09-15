# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/vehicles.py
from collections import namedtuple
from command import SchemeValidator, CommandHandler, instantiateObject
_VehiclesCommand = namedtuple('_VehiclesCommand', ('action', 'vehicle_id'))
_VehiclesCommand.__new__.__defaults__ = (None, None)
_VehiclesCommandScheme = {'required': (('action', basestring),),
 'optional': (('vehicle_id', (int, long)),)}

class VehiclesCommand(_VehiclesCommand, SchemeValidator):
    """
    Represents web command for vehicles encyclopedia.
    """

    def __init__(self, *args, **kwargs):
        super(VehiclesCommand, self).__init__(_VehiclesCommandScheme)


def createVehiclesHandler(handlerFunc):
    data = {'name': 'vehicles',
     'cls': VehiclesCommand,
     'handler': handlerFunc}
    return instantiateObject(CommandHandler, data)
