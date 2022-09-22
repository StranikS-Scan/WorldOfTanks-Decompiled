# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/escape_ability.py
import CGF
import GenericComponents
import Math
import Vehicle
from cgf_components import BossTag
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class AnimatorEventManager(CGF.ComponentManager):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(AnimatorEventManager, self).__init__()
        self.__reactions = {}

    @onAddedQuery(CGF.GameObject, GenericComponents.AnimatorComponent)
    def onAdded(self, gameObject, animatorComponent):
        self.__reactions[gameObject.id] = animatorComponent.addEventReaction(self.__onEventReaction)

    @onRemovedQuery(CGF.GameObject, GenericComponents.AnimatorComponent)
    def onRemoved(self, gameObject, animatorComponent):
        callbackID = self.__reactions.get(gameObject.id)
        if callbackID:
            animatorComponent.removeEventReaction(callbackID)

    def __onEventReaction(self, who, name, _):
        if name == 'hidden':
            vehicles = CGF.Query(who.spaceID, (BossTag, Vehicle.Vehicle))
            if not vehicles.empty():
                for _, vehicle in vehicles.values():
                    self.sessionProvider.shared.feedback.onVehicleMarkerErased(vehicle.id)
                    va = vehicle.appearance
                    va.changeVisibility(False)
                    va.clearUndamagedStateChildren()
                    va.compoundModel.matrix = Math.Matrix()
