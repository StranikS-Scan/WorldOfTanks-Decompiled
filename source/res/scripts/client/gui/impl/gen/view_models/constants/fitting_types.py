# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/constants/fitting_types.py
from frameworks.wulf import ViewModel

class FittingTypes(ViewModel):
    __slots__ = ()
    OPTIONAL_DEVICE = 'optionalDevice'
    EQUIPMENT = 'equipment'
    SHELL = 'shell'
    VEHICLE = 'vehicle'
    MODULE = 'module'
    ORDER = 'order'
    BOOSTER = 'battleBooster'
    CREW_BOOKS = 'crewBooks'
    CUSTOMIZATION = 'customization'
    BATTLE_ABILITY = 'battleAbility'
    VEHICLE_GUN = 'vehicleGun'
    VEHICLE_DUAL_GUN = 'vehicleDualGun'
    VEHICLE_TURRET = 'vehicleTurret'
    VEHICLE_CHASSIS = 'vehicleChassis'
    VEHICLE_WHEELED_CHASSIS = 'vehicleWheeledChassis'
    VEHICLE_ENGINE = 'vehicleEngine'
    VEHICLE_RADIO = 'vehicleRadio'
    POST_PROGRESSION_MODIFICATION = 'postProgressionModification'
    POST_PROGRESSION_PAIR_MODIFICATION = 'postProgressionPairModification'

    def __init__(self, properties=0, commands=0):
        super(FittingTypes, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(FittingTypes, self)._initialize()
