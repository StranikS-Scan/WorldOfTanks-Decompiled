# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/vehicle_components.py
from __future__ import absolute_import
import CGF
import Triggers
from cgf_script.registration import ComponentProperty, registerComponent

@registerComponent
class VehicleDestroyingComponent(object):
    category = 'Vehicle'
    editorTitle = 'Vehicle Destroying Component'
    domain = CGF.Domain.ServerEditor
    trigger = ComponentProperty(type=CGF.PropertyType.Link, editorName='AreaTrigger to subscribe', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        self.reactionID = None
        return


@registerComponent
class VehicleDamageLoggerComponent(object):
    category = 'Loggers'
    editorTitle = 'Vehicle Damage Logger Component'
    domain = CGF.Domain.ServerEditor

    def __init__(self):
        self.topMostParentName = None
        return


@registerComponent
class VehicleSequenceParamsAttachedComponent(object):
    category = 'Vehicle'
    editorTitle = 'Vehicle Sequence Params Attached Component'
    domain = CGF.Domain.All
