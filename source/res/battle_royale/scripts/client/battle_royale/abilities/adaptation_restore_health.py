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
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from battle_royale.gui.constants import BattleRoyaleEquipments
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
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
    from items.artefacts import AdaptationHealthRestore
    from vehicle_systems.CompoundAppearance import CompoundAppearance
    from typing import Optional, List
_logger = logging.getLogger(__name__)
_START_ANIMATION_THRESHOLD = 0.2
_ROOT_NODE_NAME = 'AdaptationHealthRestoreAbility'

def findEffectRoots(gameObject):
    h = CGF.HierarchyManager(gameObject.spaceID)
    result = h.findComponentsInHierarchy(gameObject, BattleRoyaleAbilities.HealthRestoreAbilityComponent)
    return result


def findEquipComp(gameObject):
    h = CGF.HierarchyManager(gameObject.spaceID)
    rootGameObject = h.getTopMostParent(gameObject)
    return bool(rootGameObject.findComponentByType(VehicleAdaptationHealthRestoreComponent))


def getChildren(gameObject):
    return CGF.HierarchyManager(gameObject.spaceID).getChildren(gameObject) or []


@registerComponent
class AdaptationHealthRestoreAbilityPart(object):
    domain = CGF.DomainOption.DomainClient
    startAnimation = ComponentProperty(type=CGFMetaTypes.STRING, value='')
    cycleAnimation = ComponentProperty(type=CGFMetaTypes.STRING, value='')
    endAnimation = ComponentProperty(type=CGFMetaTypes.STRING, value='')


@registerComponent
class AdaptationHealthRestoreEffectArea(object):
    domain = CGF.DomainOption.DomainClient
    teamMateRestoringRadius = ComponentProperty(type=CGFMetaTypes.FLOAT, value=1.0, editorName='Teammate restoring radius')


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE)
class AdaptationHealthRestoreEffectManager(CGF.ComponentManager):

    @onAddedQuery(VehicleAdaptationHealthRestoreComponent, CGF.GameObject)
    def onBWComponentAdded(self, bwComponent, gameObject):
        self.showHealthGlowEffect(bwComponent, gameObject)

    @onRemovedQuery(VehicleAdaptationHealthRestoreComponent, CGF.GameObject, UpgradeInProgressComponent)
    def inBattleUpgradeCompleted(self, bwComponent, gameObject, _):
        self.showHealthGlowEffect(bwComponent, gameObject)

    @onRemovedQuery(VehicleAdaptationHealthRestoreComponent, CGF.GameObject)
    def hideHealthGlowEffect(self, bwComponent, entityGameObject):
        effectRoots = findEffectRoots(entityGameObject)
        vehicle = bwComponent.entity
        for effectRoot, effectComponent in effectRoots:
            for partComponent, partGO in self.iterParts(effectRoot):
                self.spawnEndAnimation(partComponent, partGO, effectRoot)

            if vehicle and not vehicle.isDestroyed and vehicle.health > 0:
                self.loadPostEffect(effectComponent.getPostEffectTarget())

    @classmethod
    def showHealthGlowEffect(cls, bwComponent, gameObject):
        appearance = cls.getVehicleAppearance(gameObject)
        loadAppearancePrefab(cls.getEquipment().usagePrefab, appearance, partial(cls.initializeEffect, bwComponent=bwComponent, entityGameObject=gameObject))

    @classmethod
    def initializeEffect(cls, effectRoot, bwComponent, entityGameObject):
        appearance = cls.getVehicleAppearance(entityGameObject)
        effectComponent = effectRoot.findComponentByType(BattleRoyaleAbilities.HealthRestoreAbilityComponent)
        resourcesList = cls.createParts(effectComponent.getMapping(), appearance)
        BigWorld.loadResourceListBG(resourcesList, partial(cls.onResourcesLoaded, effectRoot, bwComponent))

    @classmethod
    def onResourcesLoaded(cls, effectRoot, bwComponent, *_):
        if not effectRoot.isValid():
            return
        effectRoot.createComponent(ResourceLoaded, cls.calculateEquipmentTime(bwComponent))

    @onAddedQuery(ResourceLoaded, CGF.GameObject)
    def onResourcesLoadedAdded(self, resource, effectRoot):
        if not findEquipComp(effectRoot):
            return
        for partComponent, partGO in self.iterParts(effectRoot):
            if resource.elapsedTime < _START_ANIMATION_THRESHOLD:
                self.spawnStartAnimation(partComponent, partGO)
            self.spawnCycleAnimation(partComponent, partGO)

    @staticmethod
    def createParts(config, appearance):
        models = (appearance.typeDescriptor.hull.models.undamaged, appearance.typeDescriptor.turret.models.undamaged, appearance.typeDescriptor.gun.models.undamaged)
        resourcesList = []
        for entry in config:
            model = entry.get('modelPath')
            node = entry.get('targetNode')
            if node and model in models:
                start, cycle, end = entry['startSequence'], entry['cycleSequence'], entry['endSequence']
                success = node.createComponent(AdaptationHealthRestoreAbilityPart, startAnimation=start, cycleAnimation=cycle, endAnimation=end)
                if success:
                    resourcesList.append(start)
                    resourcesList.append(cycle)
                    resourcesList.append(end)

        return resourcesList

    @classmethod
    def spawnStartAnimation(cls, partComponent, gameObject):
        animator = cls.spawnEffect(partComponent.startAnimation, gameObject)
        if animator:
            duration = animator.getDuration()
            trigger = gameObject.createComponent(Triggers.TimeTriggerComponent, duration, 1)
            trigger.addFireReaction(lambda *args: cls.spawnCycleAnimation(partComponent, gameObject))

    @classmethod
    def spawnCycleAnimation(cls, partComponent, gameObject):
        cls.spawnEffect(partComponent.cycleAnimation, gameObject, loop=True)

    @classmethod
    def spawnEndAnimation(cls, partComponent, gameObject, effectRoot):
        animator = cls.spawnEffect(partComponent.endAnimation, gameObject)
        if animator:
            duration = animator.getDuration()
            cls.scheduleDestroy(effectRoot, duration)

    @classmethod
    def loadPostEffect(cls, postEffectTarget):
        if postEffectTarget is None or not postEffectTarget.isValid():
            _logger.warning('postEffectTarget is not provided in HealthRestoreAbility Component')
            return
        else:

            def postloadSetup(postEffectGO):
                postEffectGO.createComponent(AdaptationHealthRestoreEffectArea, teamMateRestoringRadius=cls.getEquipment().teamMateRestoringRadius)

            transformComponent = postEffectTarget.findComponentByType(GenericComponents.TransformComponent)
            CGF.loadGameObject(cls.getEquipment().posteffectPrefab, postEffectTarget.spaceID, transformComponent.worldPosition, postloadSetup)
            return

    @staticmethod
    def scheduleDestroy(effectRoot, duration):
        selfDestroy = effectRoot.findComponentByType(GenericComponents.RemoveGoDelayedComponent)
        if selfDestroy:
            selfDestroy.delay = max(selfDestroy.delay, duration)
        else:
            effectRoot.createComponent(GenericComponents.RemoveGoDelayedComponent, duration)

    @staticmethod
    def iterParts(effectRoot):
        for child in getChildren(effectRoot):
            part = child.findComponentByType(AdaptationHealthRestoreAbilityPart)
            if part and any([part.startAnimation, part.cycleAnimation, part.endAnimation]):
                yield (part, child)

    @staticmethod
    def spawnEffect(effect, gameObject, loop=False):
        if effect and gameObject and gameObject.isValid():
            repeatCount = -1 if loop else 1
            gameObject.removeComponentByType(GenericComponents.AnimatorComponent)
            animator = gameObject.createComponent(GenericComponents.AnimatorComponent, effect, 0, 1, repeatCount, True, '')
            return animator
        else:
            return None

    @staticmethod
    def getVehicleAppearance(gameObject):
        vehicle = gameObject.findComponentByType(Vehicle)
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
