# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/vehicle_specs/rts_supply_params.py
from gui.shared.gui_items.Vehicle import getVehicleClassTag
from gui.shared.items_parameters.params import VehicleParams, _ParamsDictProxy
from RTSShared import RTSSupply

class RtsSupplyParams(VehicleParams):
    SUPPLY_PARAMETERS_BY_TYPE = {RTSSupply.BARRICADES: ('supply_barricadesDamage',),
     RTSSupply.BUNKER: ('supply_avgDamage', 'supply_avgPiercingPower', 'supply_bunkerClipFireRate', 'supply_reloadTimeSecs', 'supply_shotDispersionAngle', 'supply_maxHealth', 'supply_armor', 'supply_circularVisionRadius'),
     RTSSupply.AT_GUN: ('supply_avgDamage', 'supply_avgPiercingPower', 'supply_reloadTimeSecs', 'supply_shotDispersionAngle', 'supply_maxHealth', 'supply_circularVisionRadius'),
     RTSSupply.PILLBOX: ('supply_avgDamage', 'supply_avgPiercingPower', 'supply_pillboxClipFireRate', 'supply_shotDispersionAngle', 'supply_maxHealth', 'supply_armor', 'supply_circularVisionRadius'),
     RTSSupply.WATCH_TOWER: ('supply_maxHealth', 'supply_circularVisionRadius'),
     RTSSupply.MORTAR: ('supply_avgDamage', 'supply_avgPiercingPower', 'supply_mortarClipFireRate', 'supply_shotDispersionAngle', 'supply_stunDuration', 'supply_maxHealth', 'supply_circularVisionRadius'),
     RTSSupply.FLAMER: ('supply_flamethrowerDamage', 'supply_flamethrowerClipFireRate', 'supply_maxHealth', 'supply_armor', 'supply_circularVisionRadius')}

    def __init__(self, vehicle):
        self.parameters = self.getParametersForSupply(vehicle)
        super(RtsSupplyParams, self).__init__(vehicle)

    def __getattr__(self, item):
        if item in self.parameters:
            vehicleParameterName = item.replace('supply_', '')
            return getattr(self, vehicleParameterName)

    @classmethod
    def getParametersForSupply(cls, vehicle):
        rtsSupplyType = RTSSupply.TAG_TO_SUPPLY[getVehicleClassTag(vehicle.tags)]
        return cls.SUPPLY_PARAMETERS_BY_TYPE.get(rtsSupplyType, [])

    def getParamsDict(self, preload=False):
        return _ParamsDictProxy(self, preload, conditions=((self.parameters, lambda v: v is not None),))

    @property
    def supply_stunDuration(self):
        maxStunDuration = self.stunMaxDuration
        if maxStunDuration:
            minStunDuration = self.stunMinDuration
            return (minStunDuration, maxStunDuration)
        else:
            return None

    @property
    def supply_armor(self):
        return self.hullArmor[0]

    @property
    def supply_barricadesDamage(self):
        return (self.avgDamage, 1)

    @property
    def supply_flamethrowerDamage(self):
        return self.avgDamage

    @property
    def supply_bunkerClipFireRate(self):
        return self.clipFireRate

    @property
    def supply_mortarClipFireRate(self):
        return self.clipFireRate

    @property
    def supply_flamethrowerClipFireRate(self):
        gunParams = self._itemDescr.gun
        if not gunParams.clip or not gunParams.burst:
            return None
        else:
            clipCount = gunParams.clip[0]
            burstCount, burstRate = gunParams.burst
            duration = (burstCount - 1) * burstRate
            jetsPerMagazine = clipCount / burstCount
            reloadTime = gunParams.reloadTime
            return (duration, jetsPerMagazine, reloadTime)

    @property
    def supply_pillboxClipFireRate(self):
        gunParams = self._itemDescr.gun
        if not gunParams.clip:
            return None
        else:
            reloadTime = gunParams.reloadTime
            return (reloadTime, gunParams.clip[1], gunParams.clip[0])
