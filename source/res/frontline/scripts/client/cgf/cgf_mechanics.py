# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/cgf/cgf_mechanics.py
import BigWorld
import CGF
import Math
from GenericComponents import TransformComponent
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import autoregister, onProcessQuery
from constants import IS_CLIENT
from debug_utils import LOG_DEBUG
if IS_CLIENT:
    from helpers import dependency
    from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
    from skeletons.gui.battle_session import IBattleSessionProvider
BALOON_DEAD_PREFAB = 'content/CGFPrefabs/Frontline/Baloon_Crash.prefab'

@registerComponent
class DeadAirshipComponent(object):
    domain = CGF.DomainOption.DomainClient

    def __init__(self, velocity):
        self.velocity = velocity


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class DeadAirshipManager(CGF.ComponentManager):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def activate(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived

    def deactivate(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived

    @onProcessQuery(TransformComponent, DeadAirshipComponent, tickGroup='Simulation')
    def onProcessMoving(self, transform, deadAirship):
        transform.position += deadAirship.velocity * self.clock.gameDelta

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, _):
        if eventID != FEEDBACK_EVENT_ID.VEHICLE_DEAD:
            return
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle and vehicle.typeDescriptor.isAirCraft:
            velocity = vehicle.filter.velocity
            velocity.y = 0

            def _loadCb(go):
                go.createComponent(DeadAirshipComponent, velocity)
                LOG_DEBUG('[SupplyComponentManager] Baloon crashed prefab is loaded')

            CGF.loadGameObject(BALOON_DEAD_PREFAB, self.spaceID, Math.Matrix(vehicle.matrix), _loadCb)
