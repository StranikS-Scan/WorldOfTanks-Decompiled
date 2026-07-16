# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/adaptation_restore_health.py
import logging
from functools import partial
import typing
import BattleRoyaleAbilities
import BigWorld
import CGF
import GenericComponents
import Triggers
from battle_royale.gui.constants import BattleRoyaleEquipments
from cgf_script.registration import ComponentProperty, registerComponent
from constants import IS_CLIENT
from items import vehicles
from vehicle_systems.model_assembler import loadAppearancePrefab
if IS_CLIENT:
    from VehicleAdaptationHealthRestoreComponent import VehicleAdaptationHealthRestoreComponent
    from InBattleUpgrades import UpgradeInProgressComponent
    from Vehicle import Vehicle
else:

    class VehicleAdaptationHealthRestoreComponent(object):
        pass


    class UpgradeInProgressComponent(object):
        pass


    class Vehicle(object):
        pass


class ResourceLoaded(object):

    def __init__(self, elapsedTime):
        self.elapsedTime = elapsedTime


if typing.TYPE_CHECKING:
    from BattleRoyaleAbilities import HealthRestoreAbilityMappingEntry
    from battle_royale_artefacts import AdaptationHealthRestore
    from vehicle_systems.CompoundAppearance import CompoundAppearance
    from typing import Optional, List
_logger = logging.getLogger(__name__)
_START_ANIMATION_THRESHOLD = 0.2
_ROOT_NODE_NAME = 'AdaptationHealthRestoreAbility'

@registerComponent
class AdaptationHealthRestoreAbilityPart(object):
    domain = CGF.Domain.Client
    editorTitle = 'Adaptation Health Restore Ability Part'
    startAnimation = ComponentProperty(type=CGF.PropertyType.String, value='')
    cycleAnimation = ComponentProperty(type=CGF.PropertyType.String, value='')
    endAnimation = ComponentProperty(type=CGF.PropertyType.String, value='')


@registerComponent
class AdaptationHealthRestoreEffectArea(object):
    domain = CGF.Domain.Client
    editorTitle = 'Adaptation Health Restore Effect Area'
    teamMateRestoringRadius = ComponentProperty(type=CGF.PropertyType.Float, value=1.0, editorName='Teammate restoring radius')


class AdaptationHealthRestoreEffectSystem(CGF.System):
    VehicleAdaptationActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(VehicleAdaptationHealthRestoreComponent))
    ResourceActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(ResourceLoaded))
    HealthRestoreCreated = CGF.CreateReaction(CGF.GameObject, CGF.ReactRo(BattleRoyaleAbilities.HealthRestoreAbilityComponent))
    VehicleAdaptationDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRo(VehicleAdaptationHealthRestoreComponent))
    UpdateProgressDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRo(UpgradeInProgressComponent), CGF.Has(VehicleAdaptationHealthRestoreComponent))
    VehicleAdaptationAccess = CGF.AccessReaction(CGF.Rw(VehicleAdaptationHealthRestoreComponent))
    VehicleAccess = CGF.AccessReaction(CGF.Rw(Vehicle))
    RestoreAbilityPartAccess = CGF.AccessReaction(CGF.Rw(AdaptationHealthRestoreAbilityPart))
    RemoveDelayedAccess = CGF.AccessReaction(CGF.Ro(GenericComponents.RemoveGoDelayedComponent))
    TransformAccess = CGF.AccessReaction(CGF.Ro(CGF.TransformComponent))
    Reactions = CGF.Reactions(VehicleAdaptationActivated, ResourceActivated, HealthRestoreCreated, VehicleAdaptationDeactivated, UpdateProgressDeactivated, VehicleAdaptationAccess, VehicleAccess, RestoreAbilityPartAccess, RemoveDelayedAccess, TransformAccess)

    def update(self):
        vehicleAdaptationAccess = self.reaction(self.VehicleAdaptationAccess)
        vehicleAccess = self.reaction(self.VehicleAccess)
        transformAccess = self.reaction(self.TransformAccess)
        restoreAbilityAccess = self.reaction(self.RestoreAbilityPartAccess)
        q = CGF.CommandQueue(self.gom)
        for gameObject, _ in self.reaction(self.UpdateProgressDeactivated):
            self.inBattleUpgradeCompleted(gameObject, vehicleAccess)

        for entityGameObject, bwComponent in self.reaction(self.VehicleAdaptationDeactivated):
            self.hideHealthGlowEffect(bwComponent, entityGameObject, restoreAbilityAccess, transformAccess)

        for go, healthRestore in self.reaction(self.HealthRestoreCreated):
            self.initializeEffect(go, healthRestore, vehicleAdaptationAccess, q)

        for gameObject, _ in self.reaction(self.VehicleAdaptationActivated):
            self.onBWComponentAdded(gameObject, vehicleAccess)

        for effectRoot, resource in self.reaction(self.ResourceActivated):
            self.onResourcesLoadedAdded(resource, effectRoot, restoreAbilityAccess, vehicleAdaptationAccess)

    def onBWComponentAdded(self, gameObject, vehicleAccess):
        self.showHealthGlowEffect(gameObject, vehicleAccess)

    def inBattleUpgradeCompleted(self, gameObject, vehicleAccess):
        self.showHealthGlowEffect(gameObject, vehicleAccess)

    def hideHealthGlowEffect(self, bwComponent, entityGameObject, restoreAbilityAccess, transformAccess):
        effectRoots = self.findEffectRoots(entityGameObject)
        vehicle = bwComponent.entity
        for effectComponent in effectRoots:
            for partComponent, partGO in self.iterParts(effectComponent.object, restoreAbilityAccess):
                self.spawnEndAnimation(partComponent, partGO, effectComponent.object)

            if vehicle and not vehicle.isDestroyed and vehicle.health > 0:
                self.loadPostEffect(effectComponent.getPostEffectTarget, transformAccess)

    def showHealthGlowEffect(self, gameObject, vehicleAccess):
        appearance = self.getVehicleAppearance(gameObject, vehicleAccess)
        loadAppearancePrefab(self.getEquipment().usagePrefab, appearance, removeOnDeath=False)

    def initializeEffect(self, effectGO, effectComponent, vehicleAdaptationAccess, queue):
        result = CGF.findParentWithComponent(effectGO, Vehicle)
        if result is None:
            _logger.error('Unable to find parent Vehicle')
            return
        else:
            _, vehicleComp = result
            if vehicleComp.isDestroyed:
                return
            resourcesList = self.createParts(effectComponent.getMapping(), vehicleComp.appearance, queue)
            taskId = BigWorld.loadResourceListBG(resourcesList, partial(self.onResourcesLoaded, vehicleAdaptationAccess, effectGO))
            _logger.info('loadResourceListBG vehicle = (%d), task = (%d)', vehicleComp.id, taskId)
            return

    def onResourcesLoaded(self, vehicleAdaptationAccess, effectGO, *_):
        if not effectGO.valid:
            _logger.error('Effect Root GameObject is not valid')
            return
        else:
            result = CGF.findParentWithComponent(effectGO, Vehicle)
            if result is None:
                _logger.error('Unable to find parent Vehicle')
                return
            vehicleGo, _ = result
            bwComponent = vehicleAdaptationAccess.find(vehicleGo)
            q = CGF.CommandQueue(self.gom)
            q.createComponent(effectGO, ResourceLoaded, self.calculateEquipmentTime(bwComponent))
            return

    def onResourcesLoadedAdded(self, resource, effectRoot, restoreAbilityAccess, vehicleAdaptationAccess):
        if not self.findEquipComp(effectRoot, vehicleAdaptationAccess):
            return
        for partComponent, partGO in self.iterParts(effectRoot, restoreAbilityAccess):
            if resource.elapsedTime < _START_ANIMATION_THRESHOLD:
                self.spawnStartAnimation(partComponent, partGO)
            self.spawnCycleAnimation(partComponent, partGO)

    def createParts(self, config, appearance, queue):
        models = (appearance.typeDescriptor.hull.models.undamaged, appearance.typeDescriptor.turret.models.undamaged, appearance.typeDescriptor.gun.models.undamaged)
        resourcesList = []
        for entry in config:
            model = entry.get('modelPath')
            node = entry.get('targetNode')
            if node and model in models:
                start, cycle, end = entry['startSequence'], entry['cycleSequence'], entry['endSequence']
                success = queue.createComponent(node, AdaptationHealthRestoreAbilityPart, startAnimation=start, cycleAnimation=cycle, endAnimation=end)
                if success:
                    resourcesList.append(start)
                    resourcesList.append(cycle)
                    resourcesList.append(end)

        return resourcesList

    def spawnStartAnimation(self, partComponent, gameObject):
        q = CGF.CommandQueue(self.gom)
        animator = self.spawnEffect(partComponent.startAnimation, gameObject, q)
        if animator:
            duration = animator.getDuration()
            trigger = q.createComponent(gameObject, Triggers.TimeTriggerComponent, duration, 1)
            trigger.addFireReaction(lambda *args: self.spawnCycleAnimation(partComponent, gameObject))

    def spawnCycleAnimation(self, partComponent, gameObject):
        q = CGF.CommandQueue(self.gom)
        self.spawnEffect(partComponent.cycleAnimation, gameObject, q, loop=True)

    def spawnEndAnimation(self, partComponent, gameObject, effectRoot):
        q = CGF.CommandQueue(self.gom)
        animator = self.spawnEffect(partComponent.endAnimation, gameObject, q)
        if animator:
            duration = animator.getDuration()
            self.scheduleDestroy(effectRoot, duration, q)

    @classmethod
    def loadPostEffect(cls, postEffectTarget, transformAccess):
        if postEffectTarget is None or not postEffectTarget.valid:
            _logger.warning('postEffectTarget is not provided in HealthRestoreAbility Component')
            return
        else:

            def postloadSetup(objects, queue):
                postEffectGO = objects[0]
                queue.createComponent(postEffectGO, AdaptationHealthRestoreEffectArea, teamMateRestoringRadius=cls.getEquipment().teamMateRestoringRadius)

            transformComponent = transformAccess.find(postEffectTarget)
            CGF.loadAndCreatePrefab(cls.getEquipment().posteffectPrefab, postEffectTarget.spaceID, transformComponent.worldPosition, postloadSetup)
            return

    def scheduleDestroy(self, effectRoot, duration, queue):
        removeDelayedAccess = self.reaction(self.RemoveDelayedAccess)
        selfDestroy = removeDelayedAccess.find(effectRoot)
        if selfDestroy:
            selfDestroy.delay = max(selfDestroy.delay, duration)
        else:
            queue.createComponent(effectRoot, GenericComponents.RemoveGoDelayedComponent, duration)

    def iterParts(self, effectRoot, restoreAbilityAccess):
        for child in self.getChildren(effectRoot):
            part = restoreAbilityAccess.find(child)
            if part and any([part.startAnimation, part.cycleAnimation, part.endAnimation]):
                yield (part, child)

    @staticmethod
    def spawnEffect(effect, gameObject, queue, loop=False):
        if effect and gameObject and gameObject.valid:
            repeatCount = -1 if loop else 1
            queue.removeComponent(gameObject, GenericComponents.AnimatorComponent)
            animator = queue.createComponent(gameObject, GenericComponents.AnimatorComponent, effect, 0, 1, repeatCount, True, '')
            return animator
        else:
            return None

    @staticmethod
    def getVehicleAppearance(gameObject, vehicleAccess):
        vehicle = vehicleAccess.find(gameObject)
        return vehicle.appearance

    @staticmethod
    def getEquipment():
        equipmentID = vehicles.g_cache.equipmentIDs().get(BattleRoyaleEquipments.ADAPTATION_HEALTH_RESTORE)
        equipment = vehicles.g_cache.equipments()[equipmentID]
        return equipment

    @classmethod
    def calculateEquipmentTime(cls, bwComponent):
        timeLeft = bwComponent.finishTime - BigWorld.serverTime()
        elapsedTime = cls.getEquipment().duration - timeLeft
        return elapsedTime

    def findEffectRoots(self, gameObject):
        result = CGF.findInHierarchyWithComponent(gameObject, BattleRoyaleAbilities.HealthRestoreAbilityComponent)
        return result

    def findEquipComp(self, gameObject, vehicleAdaptationAccess):
        rootGameObject = self.hierarchy.getTopMostParent(gameObject)
        return bool(vehicleAdaptationAccess.find(rootGameObject))

    def getChildren(self, gameObject):
        return self.hierarchy.getDirectChildren(gameObject) or []
