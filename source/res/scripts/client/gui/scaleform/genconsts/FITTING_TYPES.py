# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/genConsts/FITTING_TYPES.py


class FITTING_TYPES(object):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    null
    """
    OPTIONAL_DEVICE = 'optionalDevice'
    EQUIPMENT = 'equipment'
    SHELL = 'shell'
    VEHICLE = 'vehicle'
    MODULE = 'module'
    ORDER = 'order'
    STORE_SLOTS = [VEHICLE,
     MODULE,
     SHELL,
     OPTIONAL_DEVICE,
     EQUIPMENT]
    ARTEFACT_SLOTS = [OPTIONAL_DEVICE, EQUIPMENT]
    VEHICLE_GUN = 'vehicleGun'
    VEHICLE_TURRET = 'vehicleTurret'
    VEHICLE_CHASSIS = 'vehicleChassis'
    VEHICLE_ENGINE = 'vehicleEngine'
    VEHICLE_RADIO = 'vehicleRadio'
    MANDATORY_SLOTS = [VEHICLE_GUN,
     VEHICLE_TURRET,
     VEHICLE_CHASSIS,
     VEHICLE_ENGINE,
     VEHICLE_RADIO]
    TARGET_OTHER = 'other'
    TARGET_HANGAR = 'hangar'
    TARGET_HANGAR_CANT_INSTALL = 'hangarCantInstall'
    TARGET_VEHICLE = 'vehicle'
    ITEM_TARGETS = [TARGET_OTHER,
     TARGET_HANGAR,
     TARGET_HANGAR_CANT_INSTALL,
     TARGET_VEHICLE]
    OPTIONAL_DEVICE_FITTING_ITEM_RENDERER = 'OptDevFittingItemRendererUI'
    GUN_TURRET_FITTING_ITEM_RENDERER = 'GunTurretFittingItemRendererUI'
    ENGINE_CHASSIS_FITTING_ITEM_RENDERER = 'EngineChassisFittingItemRendererUI'
    RADIO_FITTING_ITEM_RENDERER = 'RadioFittingItemRendererUI'
    FITTING_RENDERERS = [OPTIONAL_DEVICE_FITTING_ITEM_RENDERER,
     GUN_TURRET_FITTING_ITEM_RENDERER,
     ENGINE_CHASSIS_FITTING_ITEM_RENDERER,
     RADIO_FITTING_ITEM_RENDERER]
    OPTIONAL_DEVICE_RENDERER_DATA_CLASS_NAME = 'net.wg.gui.lobby.modulesPanel.data.OptionalDeviceVO'
    MODULE_FITTING_RENDERER_DATA_CLASS_NAME = 'net.wg.gui.lobby.modulesPanel.data.ModuleVO'
    FITTING_RENDERER_DATA_NAMES = [OPTIONAL_DEVICE_RENDERER_DATA_CLASS_NAME, MODULE_FITTING_RENDERER_DATA_CLASS_NAME]
    HANGAR_POPOVER_MIN_AVAILABLE_HEIGHT = 455
    VEHPREVIEW_POPOVER_MIN_AVAILABLE_HEIGHT = 575
    LARGE_POPOVER_WIDTH = 540
    MEDUIM_POPOVER_WIDTH = 500
    SHORT_POPOVER_WIDTH = 440
