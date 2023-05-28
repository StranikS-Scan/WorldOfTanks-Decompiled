# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_config.py
import math
from Math import Vector3
from items.components import component_constants

class HangarConfig(object):
    __slots__ = ['cfg',
     'vStartAngles',
     'vStartPos',
     'emblemsAlphaDamaged',
     'emblemsAlphaUndamaged',
     'shadowLightDir',
     'shadowModelName',
     'shadowForwardYOffset',
     'shadowDeferredYOffset',
     'shadowDefaultTextureName',
     'shadowEmptyTextureName',
     'vehicleGunPitch',
     'vehicleTurretYaw']

    def __init__(self):
        self.cfg = {}
        self.vStartAngles = Vector3()
        self.vStartPos = Vector3()
        self.emblemsAlphaDamaged = component_constants.ZERO_FLOAT
        self.emblemsAlphaUndamaged = component_constants.ZERO_FLOAT
        self.shadowLightDir = Vector3()
        self.shadowModelName = component_constants.EMPTY_STRING
        self.shadowForwardYOffset = component_constants.ZERO_FLOAT
        self.shadowDeferredYOffset = component_constants.ZERO_FLOAT
        self.shadowDefaultTextureName = component_constants.EMPTY_STRING
        self.shadowEmptyTextureName = component_constants.EMPTY_STRING
        self.vehicleGunPitch = component_constants.ZERO_FLOAT
        self.vehicleTurretYaw = component_constants.ZERO_FLOAT

    def __iter__(self):
        return iter(self.cfg)

    def __getitem__(self, key):
        return self.cfg[key]

    def __setitem__(self, key, value):
        self.cfg[key] = value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def loadConfig(self, xml, defaultCfg=None):
        if defaultCfg is None:
            defaultCfg = self
        defaultFakeShadowOffsetsCfg = {'shadow_forward_y_offset': 0.0,
         'shadow_deferred_y_offset': 0.0}
        self.vStartAngles = self.loadConfigValue('v_start_angles', xml, xml.readVector3, defaultCfg)
        self.vStartPos = self.loadConfigValue('v_start_pos', xml, xml.readVector3, defaultCfg)
        self.emblemsAlphaDamaged = self.loadConfigValue('emblems_alpha_damaged', xml, xml.readFloat, defaultCfg)
        self.emblemsAlphaUndamaged = self.loadConfigValue('emblems_alpha_undamaged', xml, xml.readFloat, defaultCfg)
        self.shadowLightDir = self.loadConfigValue('shadow_light_dir', xml, xml.readVector3, defaultCfg)
        self.shadowModelName = self.loadConfigValue('shadow_model_name', xml, xml.readString, defaultCfg)
        self.shadowForwardYOffset = self.loadConfigValue('shadow_forward_y_offset', xml, xml.readFloat, defaultFakeShadowOffsetsCfg)
        self.shadowDeferredYOffset = self.loadConfigValue('shadow_deferred_y_offset', xml, xml.readFloat, defaultFakeShadowOffsetsCfg)
        self.shadowDefaultTextureName = self.loadConfigValue('shadow_default_texture_name', xml, xml.readString, defaultCfg)
        self.shadowEmptyTextureName = self.loadConfigValue('shadow_empty_texture_name', xml, xml.readString, defaultCfg)
        defaultVehicleAnglesCfg = {'vehicle_gun_pitch': 0.0,
         'vehicle_turret_yaw': 0.0}
        self.vehicleGunPitch = self.loadConfigValue('vehicle_gun_pitch', xml, xml.readFloat, defaultVehicleAnglesCfg)
        self.vehicleTurretYaw = self.loadConfigValue('vehicle_turret_yaw', xml, xml.readFloat, defaultVehicleAnglesCfg)
        for i in range(0, 3):
            self.vStartAngles[i] = self['v_start_angles'][i] = math.radians(self['v_start_angles'][i])

        return

    def loadDefaultHangarConfig(self, xml, hangarPathKey):
        self.shadowModelName = self.loadConfigValue('shadow_model_name', xml, xml.readString)
        self.shadowDefaultTextureName = self.loadConfigValue('shadow_default_texture_name', xml, xml.readString)
        self.shadowEmptyTextureName = self.loadConfigValue('shadow_empty_texture_name', xml, xml.readString)
        self.loadConfigValue(hangarPathKey, xml, xml.readString)

    def loadCustomizationConfig(self, xml):
        defaultFakeShadowOffsetsCfg = {'shadow_forward_y_offset': 0.0,
         'shadow_deferred_y_offset': 0.0}
        self.vStartPos = self.loadConfigValue('v_start_pos', xml, xml.readVector3, self)
        self.vStartAngles = self.loadConfigValue('v_start_angles', xml, xml.readVector3, self)
        self.shadowForwardYOffset = self.loadConfigValue('shadow_forward_y_offset', xml, xml.readFloat, defaultFakeShadowOffsetsCfg)
        self.shadowDeferredYOffset = self.loadConfigValue('shadow_deferred_y_offset', xml, xml.readFloat, defaultFakeShadowOffsetsCfg)

    def loadSecondaryConfig(self, xml):
        defaultShadowOffsetsCfg = {'shadow_forward_y_offset': 0.0,
         'shadow_deferred_y_offset': 0.0}
        self.vStartPos = self.loadConfigValue('v_start_pos', xml, xml.readVector3, self)
        self.vStartAngles = self.loadConfigValue('v_start_angles', xml, xml.readVector3, self)
        for i in range(0, 3):
            self.vStartAngles[i] = self['v_start_angles'][i] = math.radians(self['v_start_angles'][i])

        self.shadowForwardYOffset = self.loadConfigValue('shadow_forward_y_offset', xml, xml.readFloat, defaultShadowOffsetsCfg)
        self.shadowDeferredYOffset = self.loadConfigValue('shadow_deferred_y_offset', xml, xml.readFloat, defaultShadowOffsetsCfg)

    def loadConfigValue(self, name, xml, fn, defaultCfg=None):
        if xml.has_key(name):
            self[name] = fn(name)
        else:
            self[name] = defaultCfg.get(name) if defaultCfg is not None else None
        return self[name]
