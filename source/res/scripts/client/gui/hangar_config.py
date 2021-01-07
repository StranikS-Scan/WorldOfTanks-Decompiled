# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_config.py
import math
import Math
from Math import Vector2, Vector3
from items.components import component_constants

class HangarConfig(object):
    __slots__ = ['cfg',
     'vStartAngles',
     'vStartPos',
     'camDistConstPlatoon',
     'camStartDistPlatoon',
     'camStartAngles',
     'camStartAnglesPlatoon',
     'camStartTargetPos',
     'camStartDist',
     'camDistConstr',
     'camMinDistVehicleHullLengthK',
     'camPitchConstr',
     'camYawConstr',
     'camSens',
     'camDistSens',
     'camPivotPos',
     'camFluency',
     'emblemsAlphaDamaged',
     'emblemsAlphaUndamaged',
     'shadowLightDir',
     'shadowModelName',
     'shadowForwardYOffset',
     'shadowDeferredYOffset',
     'shadowDefaultTextureName',
     'shadowEmptyTextureName',
     'camCapsuleScale',
     'camCapsuleGunScale',
     'camIdlePitchConstr',
     'camIdleDistConstr',
     'camIdleYawPeriod',
     'camIdlePitchPeriod',
     'camIdleDistPeriod',
     'camIdleEasingInTime',
     'camParallaxDistance',
     'camParallaxAngles',
     'camParallaxSmoothing',
     'vehicleGunPitch',
     'vehicleTurretYaw']

    def __init__(self):
        self.cfg = {}
        self.camDistConstPlatoon = Vector2()
        self.camStartDistPlatoon = component_constants.ZERO_FLOAT
        self.camStartAngles = Vector2()
        self.camStartAnglesPlatoon = Vector2()
        self.vStartAngles = Vector3()
        self.vStartPos = Vector3()
        self.camStartTargetPos = Vector3()
        self.camStartDist = component_constants.ZERO_FLOAT
        self.camDistConstr = Vector2()
        self.camMinDistVehicleHullLengthK = component_constants.ZERO_FLOAT
        self.camPitchConstr = Vector2()
        self.camYawConstr = Vector2()
        self.camSens = component_constants.ZERO_FLOAT
        self.camDistSens = component_constants.ZERO_FLOAT
        self.camPivotPos = Vector3()
        self.camFluency = component_constants.ZERO_FLOAT
        self.emblemsAlphaDamaged = component_constants.ZERO_FLOAT
        self.emblemsAlphaUndamaged = component_constants.ZERO_FLOAT
        self.shadowLightDir = Vector3()
        self.shadowModelName = component_constants.EMPTY_STRING
        self.shadowForwardYOffset = component_constants.ZERO_FLOAT
        self.shadowDeferredYOffset = component_constants.ZERO_FLOAT
        self.shadowDefaultTextureName = component_constants.EMPTY_STRING
        self.shadowEmptyTextureName = component_constants.EMPTY_STRING
        self.camCapsuleScale = Vector3()
        self.camCapsuleGunScale = Vector3()
        self.camIdlePitchConstr = Vector2()
        self.camIdleDistConstr = Vector2()
        self.camIdleYawPeriod = component_constants.ZERO_FLOAT
        self.camIdlePitchPeriod = component_constants.ZERO_FLOAT
        self.camIdleDistPeriod = component_constants.ZERO_FLOAT
        self.camIdleEasingInTime = component_constants.ZERO_FLOAT
        self.camParallaxDistance = Vector2()
        self.camParallaxAngles = Vector2()
        self.camParallaxSmoothing = component_constants.ZERO_FLOAT
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
        self.camStartTargetPos = self.loadConfigValue('cam_start_target_pos', xml, xml.readVector3, defaultCfg)
        self.camStartDist = self.loadConfigValue('cam_start_dist', xml, xml.readFloat, defaultCfg)
        self.camStartDistPlatoon = self.loadConfigValue('cam_start_dist_platoon', xml, xml.readFloat, {'cam_start_dist_platoon': self.camStartDist})
        self.camStartAngles = self.loadConfigValue('cam_start_angles', xml, xml.readVector2, defaultCfg)
        self.camStartAnglesPlatoon = self.loadConfigValue('cam_start_angles_platoon', xml, xml.readVector2, {'cam_start_angles_platoon': self.camStartAngles})
        self.camDistConstr = self.loadConfigValue('cam_dist_constr', xml, xml.readVector2, defaultCfg)
        self.camDistConstPlatoon = self.loadConfigValue('cam_dist_constr_platoon', xml, xml.readVector2, {'cam_dist_constr_platoon': self.camDistConstr})
        self.camMinDistVehicleHullLengthK = self.loadConfigValue('cam_min_dist_vehicle_hull_length_k', xml, xml.readFloat, defaultCfg)
        self.camPitchConstr = self.loadConfigValue('cam_pitch_constr', xml, xml.readVector2, defaultCfg)
        self.camYawConstr = self.loadConfigValue('cam_yaw_constr', xml, xml.readVector2, defaultCfg)
        self.camSens = self.loadConfigValue('cam_sens', xml, xml.readFloat, defaultCfg)
        self.camDistSens = self.loadConfigValue('cam_dist_sens', xml, xml.readFloat, defaultCfg)
        self.camPivotPos = self.loadConfigValue('cam_pivot_pos', xml, xml.readVector3, defaultCfg)
        self.camFluency = self.loadConfigValue('cam_fluency', xml, xml.readFloat, defaultCfg)
        self.emblemsAlphaDamaged = self.loadConfigValue('emblems_alpha_damaged', xml, xml.readFloat, defaultCfg)
        self.emblemsAlphaUndamaged = self.loadConfigValue('emblems_alpha_undamaged', xml, xml.readFloat, defaultCfg)
        self.shadowLightDir = self.loadConfigValue('shadow_light_dir', xml, xml.readVector3, defaultCfg)
        self.shadowModelName = self.loadConfigValue('shadow_model_name', xml, xml.readString, defaultCfg)
        self.shadowForwardYOffset = self.loadConfigValue('shadow_forward_y_offset', xml, xml.readFloat, defaultFakeShadowOffsetsCfg)
        self.shadowDeferredYOffset = self.loadConfigValue('shadow_deferred_y_offset', xml, xml.readFloat, defaultFakeShadowOffsetsCfg)
        self.shadowDefaultTextureName = self.loadConfigValue('shadow_default_texture_name', xml, xml.readString, defaultCfg)
        self.shadowEmptyTextureName = self.loadConfigValue('shadow_empty_texture_name', xml, xml.readString, defaultCfg)
        self.camCapsuleScale = self.loadConfigValue('cam_capsule_scale', xml, xml.readVector3, defaultCfg)
        self.camCapsuleGunScale = self.loadConfigValue('cam_capsule_gun_scale', xml, xml.readVector3, defaultCfg)
        defaultIdleCfg = {'cam_idle_pitch_constr': Math.Vector2(0.0, 0.0),
         'cam_idle_dist_constr': Math.Vector2(10.0, 10.0),
         'cam_idle_yaw_period': 0.0,
         'cam_idle_pitch_period': 0.0,
         'cam_idle_dist_period': 0.0,
         'cam_idle_easing_in_time': 0.0}
        self.camIdlePitchConstr = self.loadConfigValue('cam_idle_pitch_constr', xml, xml.readVector2, defaultIdleCfg)
        self.camIdleDistConstr = self.loadConfigValue('cam_idle_dist_constr', xml, xml.readVector2, defaultIdleCfg)
        self.camIdleYawPeriod = self.loadConfigValue('cam_idle_yaw_period', xml, xml.readFloat, defaultIdleCfg)
        self.camIdlePitchPeriod = self.loadConfigValue('cam_idle_pitch_period', xml, xml.readFloat, defaultIdleCfg)
        self.camIdleDistPeriod = self.loadConfigValue('cam_idle_dist_period', xml, xml.readFloat, defaultIdleCfg)
        self.camIdleEasingInTime = self.loadConfigValue('cam_idle_easing_in_time', xml, xml.readFloat, defaultIdleCfg)
        defaultParallaxCfg = {'cam_parallax_distance': Math.Vector2(0.0, 0.0),
         'cam_parallax_angles': Math.Vector2(0.0, 0.0),
         'cam_parallax_smoothing': 0.0}
        self.camParallaxDistance = self.loadConfigValue('cam_parallax_distance', xml, xml.readVector2, defaultParallaxCfg)
        self.camParallaxAngles = self.loadConfigValue('cam_parallax_angles', xml, xml.readVector2, defaultParallaxCfg)
        self.camParallaxSmoothing = self.loadConfigValue('cam_parallax_smoothing', xml, xml.readFloat, defaultParallaxCfg)
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
        self.camStartDist = self.loadConfigValue('cam_start_dist', xml, xml.readFloat, self)
        self.camStartDistPlatoon = self.loadConfigValue('cam_start_dist_platoon', xml, xml.readFloat, {'cam_start_dist_platoon': self.camStartDist})
        self.camDistConstr = self.loadConfigValue('cam_dist_constr', xml, xml.readVector2, self)
        self.camDistConstPlatoon = self.loadConfigValue('cam_dist_constr_platoon', xml, xml.readVector2, {'cam_dist_constr_platoon': self.camDistConstr})
        self.camStartAngles = self.loadConfigValue('cam_start_angles', xml, xml.readVector2, self)
        self.camStartAnglesPlatoon = self.loadConfigValue('cam_start_angles_platoon', xml, xml.readVector2, {'cam_start_angles_platoon': self.camStartAngles})
        self.camPivotPos = self.loadConfigValue('cam_pivot_pos', xml, xml.readVector3, self)
        self.camStartTargetPos = self.loadConfigValue('cam_start_target_pos', xml, xml.readVector3, self)
        self.shadowForwardYOffset = self.loadConfigValue('shadow_forward_y_offset', xml, xml.readFloat, defaultFakeShadowOffsetsCfg)
        self.shadowDeferredYOffset = self.loadConfigValue('shadow_deferred_y_offset', xml, xml.readFloat, defaultFakeShadowOffsetsCfg)
        self.camFluency = self.loadConfigValue('cam_fluency', xml, xml.readFloat, self)

    def loadSecondaryConfig(self, xml):
        defaultShadowOffsetsCfg = {'shadow_forward_y_offset': 0.0,
         'shadow_deferred_y_offset': 0.0}
        self.vStartPos = self.loadConfigValue('v_start_pos', xml, xml.readVector3, self)
        self.vStartAngles = self.loadConfigValue('v_start_angles', xml, xml.readVector3, self)
        for i in range(0, 3):
            self.vStartAngles[i] = self['v_start_angles'][i] = math.radians(self['v_start_angles'][i])

        self.camStartDist = self.loadConfigValue('cam_start_dist', xml, xml.readFloat, self)
        self.camStartDistPlatoon = self.loadConfigValue('cam_start_dist_platoon', xml, xml.readFloat, {'cam_start_dist_platoon': self.camStartDist})
        self.camDistConstr = self.loadConfigValue('cam_dist_constr', xml, xml.readVector2, self)
        self.camDistConstPlatoon = self.loadConfigValue('cam_dist_constr_platoon', xml, xml.readVector2, {'cam_dist_constr_platoon': self.camDistConstr})
        self.camStartAngles = self.loadConfigValue('cam_start_angles', xml, xml.readVector2, self)
        self.camStartAnglesPlatoon = self.loadConfigValue('cam_start_angles_platoon', xml, xml.readVector2, {'cam_start_angles_platoon': self.camStartAngles})
        self.camPivotPos = self.loadConfigValue('cam_pivot_pos', xml, xml.readVector3, self)
        self.camStartTargetPos = self.loadConfigValue('cam_start_target_pos', xml, xml.readVector3, self)
        self.shadowForwardYOffset = self.loadConfigValue('shadow_forward_y_offset', xml, xml.readFloat, defaultShadowOffsetsCfg)
        self.shadowDeferredYOffset = self.loadConfigValue('shadow_deferred_y_offset', xml, xml.readFloat, defaultShadowOffsetsCfg)

    def loadConfigValue(self, name, xml, fn, defaultCfg=None):
        if xml.has_key(name):
            self[name] = fn(name)
        else:
            self[name] = defaultCfg.get(name) if defaultCfg is not None else None
        return self[name]
