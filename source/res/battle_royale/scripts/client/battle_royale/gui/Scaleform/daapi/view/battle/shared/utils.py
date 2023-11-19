# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/shared/utils.py
from items.vehicles import VehicleDescr

def getVehicleLevel(vType):
    descriptor = VehicleDescr(compactDescr=vType.strCompactDescr)
    return max(descriptor.chassis.level, descriptor.turret.level, descriptor.gun.level, descriptor.radio.level, descriptor.engine.level)
