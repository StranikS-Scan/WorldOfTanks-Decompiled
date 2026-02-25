# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/common/cosmic_event_common_cgf/boosters/components.py
import CGF
import Math
import Triggers
from collections import deque
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent, registerReplicableComponent

@registerComponent
class BoosterActivationComponent(object):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor
    category = 'Cosmic'
    editorTitle = 'Booster activation component'
    turnOnTime = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turn on periods', value='')
    turnOffTime = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Turn off periods', value='')

    def __init__(self):
        self.turnOnPeriodsLeft = deque()
        self.turnOffPeriodsLeft = deque()

    def destroy(self):
        self.turnOnPeriodsLeft = None
        self.turnOffPeriodsLeft = None
        return


@registerComponent
class ImpulseComponent(object):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor
    category = 'Cosmic'
    editorTitle = 'Impulse'
    impulseDirection = ComponentProperty(type=CGFMetaTypes.VECTOR3, value=Math.Vector3(1, 0, 0), editorName='Impulse direction')
    massCoef = ComponentProperty(type=CGFMetaTypes.INT, editorName='Mass coefficient', value=1)
    velocityLimit = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Velocity limit', value=200.0)
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        self.enterReactionID = None
        self.exitReactionID = None
        return


@registerComponent
class BoosterTypeComponent(object):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor
    category = 'Cosmic'
    editorTitle = 'Booster type'
    type = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Type', value='', annotations={'comboBox': {'board': 'board',
                  'geyser': 'geyser'}})


@registerReplicableComponent
class BoosterComponent(object):
    category = 'Cosmic'
    editorTitle = 'Booster replicable component'
