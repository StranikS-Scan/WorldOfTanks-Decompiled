# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_core_common/events_core_cgf/vehicle_buffs/components.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
factorComponentClasses = {}

class FactorRegisterMeta(type):

    def __init__(cls, name, bases, attrs):
        super(FactorRegisterMeta, cls).__init__(name, bases, attrs)
        if attrs.get('_skipFactorComponentRegistry'):
            return
        factorComponentClasses[cls.__name__] = cls


class BuffComponent(object):
    __metaclass__ = FactorRegisterMeta
    _skipFactorComponentRegistry = True
    factorName = None


@registerComponent
class PeriodicHealthChangeComponent(BuffComponent):
    domain = CGF.DomainOption.DomainAll
    category = 'Events Core'
    editorTitle = 'Periodic Health Change'
    factorName = 'buffs/periodicHealthChange'
    healthChange = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Health Change', value=1.0)

    def __init__(self):
        super(PeriodicHealthChangeComponent, self).__init__()
        self.attackerVehicleID = None
        self.attackerInfo = None
        return


@registerComponent
class MovementBlockedComponent(BuffComponent):
    domain = CGF.DomainOption.DomainAll
    category = 'Events Core'
    editorTitle = 'Movement Blocked'
    factorName = 'buffs/movementBlocked'


class BaseFactorComponent(BuffComponent):
    domain = CGF.DomainOption.DomainAll
    category = 'Vehicle Factors'
    editorTitle = 'Base Factor Component'
    factorName = 'baseFactor'
    factorValue = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Factor Value', value=1.0)


def createFactorComponentClass(className, factorName, factorType=CGFMetaTypes.FLOAT, factorValue=1.0):
    classAttrs = {'editorTitle': className,
     'factorName': factorName,
     'factorValue': ComponentProperty(type=factorType, editorName='Factor Value', value=factorValue)}
    return FactorRegisterMeta(className, (BaseFactorComponent,), classAttrs)


factorsComponents = {'engine/power': 'EnginePowerFactorComponent',
 'gun/piercing': 'GunPiercingComponent',
 'gun/reloadTime': 'GunReloadTimeComponent',
 'gun/rotationSpeed': 'GunRotationSpeedComponent',
 'gun/aimingTime': 'GunAimingTimeComponent',
 'turret/rotationSpeed': 'TurretRotationSpeedComponent',
 'vehicle/maxSpeed': 'VehicleMaxSpeedComponent'}
for factorName, className in factorsComponents.iteritems():
    componentClass = createFactorComponentClass(className, factorName)
    registerComponent(componentClass)

vehicleBuffsComponents = dict(factorsComponents)
vehicleBuffsComponents.update({PeriodicHealthChangeComponent.factorName: PeriodicHealthChangeComponent.__name__,
 MovementBlockedComponent.factorName: MovementBlockedComponent.__name__})
