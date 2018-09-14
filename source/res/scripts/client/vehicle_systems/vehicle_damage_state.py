# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/vehicle_damage_state.py
import constants

class VehicleDamageState(object):
    MODEL_STATE_NAMES = ('undamaged', 'destroyed', 'exploded')
    __healthToStateMap = {0: 'destruction',
     constants.SPECIAL_VEHICLE_HEALTH.AMMO_BAY_DESTROYED: 'ammoBayBurnOff',
     constants.SPECIAL_VEHICLE_HEALTH.TURRET_DETACHED: 'ammoBayExplosion',
     constants.SPECIAL_VEHICLE_HEALTH.FUEL_EXPLODED: 'fuelExplosion',
     constants.SPECIAL_VEHICLE_HEALTH.DESTR_BY_FALL_RAMMING: 'rammingDestruction'}

    @staticmethod
    def getState(health, isCrewActive, isUnderWater):
        if health > 0:
            if not isCrewActive:
                if isUnderWater:
                    return 'submersionDeath'
                else:
                    return 'crewDeath'
            else:
                return 'alive'
        else:
            return VehicleDamageState.__healthToStateMap[health]

    __stateToModelEffectsMap = {'ammoBayExplosion': ('exploded', None),
     'ammoBayBurnOff': ('destroyed', None),
     'fuelExplosion': ('destroyed', 'fuelExplosion'),
     'destruction': ('destroyed', 'destruction'),
     'crewDeath': ('undamaged', 'crewDeath'),
     'rammingDestruction': ('destroyed', 'rammingDestruction'),
     'submersionDeath': ('undamaged', 'submersionDeath'),
     'alive': ('undamaged', 'empty')}

    @staticmethod
    def getStateParams(state):
        return VehicleDamageState.__stateToModelEffectsMap[state]

    state = property(lambda self: self.__state)
    modelState = property(lambda self: self.__model)
    isCurrentModelDamaged = property(lambda self: VehicleDamageState.isDamagedModel(self.modelState))
    isCurrentModelExploded = property(lambda self: VehicleDamageState.isExplodedModel(self.modelState))
    effect = property(lambda self: self.__effect)

    @staticmethod
    def isDamagedModel(model):
        return model != 'undamaged'

    @staticmethod
    def isExplodedModel(model):
        return model == 'exploded'

    def __init__(self):
        self.__state = None
        self.__model = None
        self.__effect = None
        return

    def update(self, health, isCrewActive, isUnderWater):
        self.__state = VehicleDamageState.getState(health, isCrewActive, isUnderWater)
        params = VehicleDamageState.getStateParams(self.__state)
        self.__model, self.__effect = params
