# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/escape_ability.py
import CGF
import GenericComponents
import Math
from cgf_script.managers_registrator import onAddedQuery
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

def _getEntity(gameObject):
    hierarchy = CGF.HierarchyManager(gameObject.spaceID)
    parent = hierarchy.getTopMostParent(gameObject)
    from Vehicle import Vehicle
    from EmptyEntity import EmptyEntity
    return parent.findComponentByType(Vehicle) or parent.findComponentByType(EmptyEntity)


class AnimatorEventManager(CGF.ComponentManager):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @onAddedQuery(CGF.GameObject, GenericComponents.AnimatorEventComponent)
    def onAdded(self, gameObject, eventData):
        for _, eventName in eventData.events():
            if eventName == 'hidden':
                vehicle = _getEntity(gameObject)
                if vehicle is not None:
                    self.sessionProvider.shared.feedback.onVehicleMarkerErased(vehicle.id)
                    va = vehicle.appearance
                    va.changeVisibility(False)
                    va.clearUndamagedStateChildren()
                    va.compoundModel.matrix = Math.Matrix()

        return
