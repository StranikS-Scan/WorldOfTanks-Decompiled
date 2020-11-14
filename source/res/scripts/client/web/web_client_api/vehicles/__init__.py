# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/vehicles/__init__.py
import nations
from gui.shared.gui_items.processors.vehicle import SetEnhancementProcessor, DismountEnhancementProcessor
from gui.shared.items_parameters import params
from helpers import dependency
from items import vehicles
from skeletons.gui.shared import IItemsCache
from web.web_client_api import w2c, w2capi, Field, W2CSchema
from web.web_client_api.shop import ItemsWebApiMixin

class _VehicleInfoSchema(W2CSchema):
    vehicle_id = Field(type=(int, long))


class _VehicleEnhancementEquipSchema(W2CSchema):
    vehicle_int_cd = Field(required=True, type=int)
    slot = Field(required=True, type=int)
    enhancement_id = Field(required=True, type=int)


class _VehicleEnhancementDismountSchema(W2CSchema):
    vehicle_int_cd = Field(required=True, type=int)
    slot = Field(required=True, type=int)


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

    @w2c(_VehicleEnhancementEquipSchema, 'vehicle_enhancement_equip')
    def setVehicleEnhancement(self, cmd):
        success, error = False, ''
        vehicle = self.itemsCache.items.getItemByCD(cmd.vehicle_int_cd)
        if vehicle:
            processor = SetEnhancementProcessor(cmd.slot, cmd.enhancement_id, vehicle)
            response = yield processor.request()
            if response:
                success, error = response.success, response.userMsg
            else:
                error = 'Undefined server error'
        else:
            error = 'Vehicle not found'
        yield {'success': success,
         'error': error}

    @w2c(_VehicleEnhancementDismountSchema, 'vehicle_enhancement_dismount')
    def dismountVehicleEnhancement(self, cmd):
        success, error, serverResponse = False, '', {}
        vehicle = self.itemsCache.items.getItemByCD(cmd.vehicle_int_cd)
        if vehicle:
            processor = DismountEnhancementProcessor(cmd.slot, vehicle)
            response = yield processor.request()
            if response:
                success, error = response.success, response.userMsg
                if response.auxData:
                    dismountResult, enhancementID = response.auxData
                    serverResponse = {'dismount_result': dismountResult,
                     'enhancement_id': enhancementID}
            else:
                error = 'Undefined server error'
        else:
            error = 'Vehicle not found'
        yield {'success': success,
         'error': error,
         'response': serverResponse}

    @w2c(_VehicleInfoSchema, 'vehicle_params')
    def vehicleParams(self, cmd):
        if not vehicles.g_list.isVehicleExistingByCD(cmd.vehicle_id):
            res = {'error': 'vehicle_id is invalid.'}
        else:
            stockVehicle = self.itemsCache.items.getStockVehicle(cmd.vehicle_id)
            vehicle = self.itemsCache.items.getItemByCD(cmd.vehicle_id)
            vehicleParams = params.VehicleParams(stockVehicle)
            res = {'vehicle': {'vehicle_id': vehicle.compactDescr,
                         'type_user_name': vehicle.typeUserName,
                         'user_name': vehicle.userName,
                         'nation': vehicle.nationName,
                         'type': vehicle.type,
                         'level': vehicle.level,
                         'is_premium': vehicle.isPremium,
                         'health': vehicleParams.maxHealth,
                         'hull_armor': vehicleParams.hullArmor,
                         'turret_armor': vehicleParams.turretArmor,
                         'avg_damage': self.__getAvgDamageShells(vehicle.descriptor),
                         'piercing_power': self.__getPiercingPowerShells(vehicle.descriptor),
                         'reload_time': vehicleParams.reloadTime,
                         'clip_fire_rate': vehicleParams.clipFireRate}}
        return res

    @staticmethod
    def __getAvgDamageShells(vehDescr):
        result = []
        for gunShot in vehDescr.gun.shots:
            result.append(gunShot.shell.damage[0])

        return tuple(result)

    @staticmethod
    def __getPiercingPowerShells(vehDescr):
        result = []
        for gunShot in vehDescr.gun.shots:
            result.append(gunShot.piercingPower.x)

        return tuple(result)
