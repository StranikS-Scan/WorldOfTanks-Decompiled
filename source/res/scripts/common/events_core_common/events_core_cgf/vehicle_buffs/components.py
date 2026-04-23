# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_core_common/events_core_cgf/vehicle_buffs/components.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent

class BuffComponent(object):
    pass


@registerComponent
class PeriodicHealthChangeComponent(BuffComponent):
    domain = CGF.DomainOption.DomainAll
    category = 'Portal'
    editorTitle = 'Periodic Health Change'
    healthChange = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Health Change', value=1.0)


@registerComponent
class MovementBlockedComponent(BuffComponent):
    domain = CGF.DomainOption.DomainAll
    category = 'Portal'
    editorTitle = 'Movement Blocked'


factorComponentClasses = {}

class FactorRegisterMeta(type):

    def __init__(cls, name, bases, attrs):
        super(FactorRegisterMeta, cls).__init__(name, bases, attrs)
        factorComponentClasses[cls.__name__] = cls


class BaseFactorComponent(BuffComponent):
    __metaclass__ = FactorRegisterMeta
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


components = [('EnginePowerFactorComponent', 'engine/power')]
for componentArgs in components:
    componentClass = createFactorComponentClass(*componentArgs)
    registerComponent(componentClass)
