# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_core_common/events_core_cgf/vehicle_buffs/__init__.py
import typing
from debug_utils import LOG_WARNING
from .components import vehicleBuffsComponents, factorComponentClasses
if typing.TYPE_CHECKING:
    from typing import Dict, Any
    from CGF import GameObject

def getVehicleBuffComponentType(buffKey):
    className = vehicleBuffsComponents.get(buffKey)
    return None if className is None else factorComponentClasses.get(className)


def applyVehicleBuffsSettings(go, settings):
    for buffKey, properties in settings.iteritems():
        componentType = getVehicleBuffComponentType(buffKey)
        if componentType is None:
            LOG_WARNING('[VehicleBuffs] Unknown vehicle buff key: {}'.format(buffKey))
            continue
        component = go.findComponentByType(componentType)
        if component is None:
            component = go.createComponent(componentType)
        for propertyName, propertyValue in properties.iteritems():
            if hasattr(component, propertyName):
                setattr(component, propertyName, propertyValue)
            LOG_WARNING('[VehicleBuffs] {} has no attribute {}'.format(componentType.__name__, propertyName))

    return
