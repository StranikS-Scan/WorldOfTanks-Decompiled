# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/common/grinch_common/cgf/heal_ability.py
import typing
import BigWorld
import CGF
import Triggers
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
if typing.TYPE_CHECKING:
    from typing import List, Optional

@registerComponent
class GrinchHealZoneTriggerComponent(object):
    category = 'Grinch'
    domain = CGF.DomainOption.DomainAll
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)

    def __init__(self):
        self.enterReactionId = None
        self.exitReactionId = None
        self._affectedVehicles = []
        return

    def affectedVehicles(self):
        for vehicleID in self._affectedVehicles:
            vehicle = BigWorld.entities.get(vehicleID)
            if vehicle:
                yield vehicle

    def addAffectedVehicle(self, vehicleID):
        self._affectedVehicles.append(vehicleID)

    def removeAffectedVehicle(self, vehicleID):
        if vehicleID in self._affectedVehicles:
            self._affectedVehicles.remove(vehicleID)


@registerComponent
class GrinchHealZoneConfigComponent(object):
    category = 'Grinch'
    editorTitle = 'Grinch Heal Config Component'
    domain = CGF.DomainOption.DomainAll
    team = ComponentProperty(type=CGFMetaTypes.INT, editorName='team', value=-1)
    ownerID = ComponentProperty(type=CGFMetaTypes.INT, editorName='ownerID', value=-1)
    healAmount = ComponentProperty(type=CGFMetaTypes.INT, editorName='healAmount', value=-1)
    blockers = ComponentProperty(type=CGFMetaTypes.STRING_LIST, editorName='blockers', value=-1)
    factorNames = ComponentProperty(type=CGFMetaTypes.STRING_LIST, editorName='factorNames', value=[])
    factorOperations = ComponentProperty(type=CGFMetaTypes.STRING_LIST, editorName='factorOperations', value=[])
    factorValues = ComponentProperty(type=CGFMetaTypes.FLOAT_LIST, editorName='factorValues', value=[])

    def getFactors(self):
        return zip(self.factorNames, self.factorOperations, self.factorValues)
