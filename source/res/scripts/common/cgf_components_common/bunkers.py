# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/bunkers.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerReplicableComponent
from constants import ATTACK_REASON

@registerReplicableComponent
class BunkerLogicComponent(object):
    category = 'Bunker'
    editorTitle = 'Bunker Logic'
    domain = CGF.DomainOption.DomainAll
    destructibleEntityId = ComponentProperty(type=CGFMetaTypes.INT, editorName='Destructible Entity ID', value=0)
    transitionChild = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Transition', value=CGF.GameObject)
    destroyedChild = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Destroyed', value=CGF.GameObject)
    markerDistance = ComponentProperty(type=CGFMetaTypes.INT, editorName='Marker max distance', value=300)
    resistAttackReasons = ComponentProperty(type=CGFMetaTypes.STRING_LIST, editorName='Resist Attack Reasons', value=(ATTACK_REASON.RAM, ATTACK_REASON.BATTLESHIP, ATTACK_REASON.DESTROYER))

    def __init__(self):
        super(BunkerLogicComponent, self).__init__()
        self.vehicleIDs = []
