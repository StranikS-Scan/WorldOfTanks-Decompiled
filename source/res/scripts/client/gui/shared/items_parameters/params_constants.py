# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/params_constants.py
from gui.shared.gui_items import KPI
from items import ITEM_TYPES
ONE_HUNDRED_PERCENTS = 100
AUTOCANNON_SHOT_DISTANCE = 400
MAX_VISION_RADIUS = 500
MIN_VISION_RADIUS = 150
PIERCING_DISTANCES = (50, 500)
MIN_RELATIVE_VALUE = 1
EXTRAS_CAMOUFLAGE = 'camouflageExtras'
MAX_DAMAGED_MODULES_DETECTION_PERK_VAL = -4
MAX_ART_NOTIFICATION_DELAY_PERK_VAL = -2
METERS_PER_SECOND_TO_KILOMETERS_PER_HOUR = 3.6
MODULES = {ITEM_TYPES.vehicleRadio: lambda vehicleDescr: vehicleDescr.radio,
 ITEM_TYPES.vehicleEngine: lambda vehicleDescr: vehicleDescr.engine,
 ITEM_TYPES.vehicleChassis: lambda vehicleDescr: vehicleDescr.chassis,
 ITEM_TYPES.vehicleTurret: lambda vehicleDescr: vehicleDescr.turret,
 ITEM_TYPES.vehicleGun: lambda vehicleDescr: vehicleDescr.gun}
HIDDEN_PARAM_DEFAULTS = {KPI.Name.ART_NOTIFICATION_DELAY_FACTOR: 2.1,
 KPI.Name.DAMAGED_MODULES_DETECTION_TIME: 4.5}
