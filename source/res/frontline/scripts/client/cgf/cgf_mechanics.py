# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/cgf/cgf_mechanics.py
import BigWorld
import CGF
import Math
from GenericComponents import TransformComponent
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery, onProcessQuery
from constants import IS_CLIENT
from debug_utils import LOG_DEBUG
from items.vehicles import CAMOUFLAGE_KIND_INDICES
if IS_CLIENT:
    from helpers import dependency
    from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
    from skeletons.gui.battle_session import IBattleSessionProvider
    from GenericComponents import AnimatorComponent, RemoveGoDelayedComponent
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


@registerComponent
class SupplySpawnComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Supply Spawn Component'
    category = 'Frontline'
    camouflagePrefabPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='camouflage prefab path', value='')


@registerComponent
class SupplyCamouflage(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Supply Camouflage'
    category = 'Frontline'
    winter = ComponentProperty(type=CGFMetaTypes.STRING, editorName='winter sequence path', value='')
    summer = ComponentProperty(type=CGFMetaTypes.STRING, editorName='summer sequence path', value='')
    desert = ComponentProperty(type=CGFMetaTypes.STRING, editorName='desert sequence path', value='')

    def getSequencePath(self):
        return '' if BigWorld.player() is None else getattr(self, CAMOUFLAGE_KIND_INDICES[BigWorld.player().arena.arenaType.vehicleCamouflageKind])


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor, category='Frontline')
class EpicBattlesComponentManager(CGF.ComponentManager):

    def __init__(self, *args):
        super(EpicBattlesComponentManager, self).__init__(*args)
        self.__camouflageGOs = {}

    @onAddedQuery(CGF.GameObject, SupplySpawnComponent, TransformComponent)
    def onAddedSupplyComponent(self, go, supplySpawnComponent, transform):

        def setGO(newGameObject):
            self.__camouflageGOs[go.id] = newGameObject

        CGF.loadGameObject(supplySpawnComponent.camouflagePrefabPath, go.spaceID, transform.worldTransform, setGO)

    @onRemovedQuery(CGF.GameObject, SupplySpawnComponent)
    def onRemovedSupplyComponent(self, go, _):
        camouflageGO = self.__camouflageGOs.pop(go.id)
        if camouflageGO:
            animComponent = camouflageGO.findComponentByType(AnimatorComponent)
            if animComponent is not None:
                duration = animComponent.getDuration()
                animComponent.unpause()
                animComponent.start()
                camouflageGO.createComponent(RemoveGoDelayedComponent, duration)
            else:
                CGF.removeGameObject(camouflageGO)
        return

    @onAddedQuery(CGF.GameObject, SupplyCamouflage)
    def onAddedCamouflageGO(self, go, camouflage):
        for camouflageGO in self.__camouflageGOs.itervalues():
            if go.id == camouflageGO.id and camouflage.getSequencePath():
                go.createComponent(AnimatorComponent, camouflage.getSequencePath(), 0, 1, 1, True, '')
                return

    @onAddedQuery(CGF.GameObject, SupplyCamouflage, AnimatorComponent)
    def onAddedCamouflageAnimator(self, go, camouflage, animComponent):
        animComponent.start()
        animComponent.pause()
