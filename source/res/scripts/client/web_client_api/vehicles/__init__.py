# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/vehicles/__init__.py
import nations
from items import vehicles
from web_client_api import w2c, w2capi, Field, W2CSchema
from web_client_api.shop import ItemsWebApiMixin

class _VehicleInfoSchema(W2CSchema):
    vehicle_id = Field(type=(int, long))


@w2capi(name='vehicles', key='action')
class VehiclesWebApi(W2CSchema, ItemsWebApiMixin):

    @w2c(_VehicleInfoSchema, 'vehicle_info')
    def vehicleInfo(self, cmd):
        try:
            vehicle = vehicles.getVehicleType(cmd.vehicle_id)
        except Exception:
            res = {'error': 'vehicle_id is invalid.'}
        else:
            res = {'vehicle': {'vehicle_id': vehicle.compactDescr,
                         'tag': vehicle.name,
                         'name': vehicle.userString,
                         'short_name': vehicle.shortUserString,
                         'nation': nations.NAMES[vehicle.id[0]],
                         'type': vehicles.getVehicleClassFromVehicleType(vehicle),
                         'tier': vehicle.level,
                         'is_premium': bool('premium' in vehicle.tags)}}

        return res
