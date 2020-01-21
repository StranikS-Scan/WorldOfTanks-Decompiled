# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/vehicles/__init__.py
import nations
from gui.shared.gui_items.processors.vehicle import SetEnhancementProcessor
from helpers import dependency
from items import vehicles
from skeletons.gui.shared import IItemsCache
from web.web_client_api import w2c, w2capi, Field, W2CSchema
from web.web_client_api.shop import ItemsWebApiMixin

class _VehicleInfoSchema(W2CSchema):
    vehicle_id = Field(type=(int, long))


class _VehicleEnhancementSchema(W2CSchema):
    vehicle_int_cd = Field(required=True, type=int)
    slot = Field(required=True, type=int)
    enhancement_id = Field(required=True, type=int)


@w2capi(name='vehicles', key='action')
class VehiclesWebApi(W2CSchema, ItemsWebApiMixin):
    itemsCache = dependency.descriptor(IItemsCache)

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

    @w2c(_VehicleEnhancementSchema, 'vehicle_enhancement')
    def setVehicleEnhancement(self, cmd):
        res = {'result': False}
        vehicle = self.itemsCache.items.getItemByCD(cmd.vehicle_int_cd)
        if vehicle:
            processor = SetEnhancementProcessor(cmd.slot, cmd.enhancement_id, vehicle)
            response = yield processor.request()
            if response:
                res['result'] = response.success
                if not response.success:
                    res['error'] = response.userMsg
            else:
                res['error'] = 'undefined server error'
        else:
            res['error'] = 'vehicleInvID not found'
        yield res
