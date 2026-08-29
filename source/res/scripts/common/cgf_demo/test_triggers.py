# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_demo/test_triggers.py
from __future__ import absolute_import
import functools
import random
import math
import GenericComponents
import Triggers
import CGF
import Math
import logging
from typing import List
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.registration import ComponentProperty, registerComponent
from cgf_demo.test_movers import TestScriptAxisRotator
from HealthComponent import HealthComponent
from constants import IS_CLIENT
_logger = logging.getLogger(__name__)
if IS_CLIENT:
    from Vehicle import Vehicle
else:

    class Vehicle(object):
        pass


@registerComponent
class TestRotateWhileInTrigger(object):
    group = DEMO_CATEGORY
    editorTitle = 'Test Rotate While In Trigger'
    domain = CGF.Domain.Client
    rotationSpeed = ComponentProperty(type=CGF.PropertyType.Float, editorName='rotation speed when anyone is present', value=1.0)


@registerComponent
class TestComponentCreation(object):
    group = DEMO_CATEGORY
    editorTitle = 'Test Component Creation'
    domain = CGF.Domain.Client
    trigger = ComponentProperty(type=CGF.PropertyType.Link, editorName='AreaTrigger to subscribe', value=Triggers.AreaTriggerComponent)
    rotationSpeed = ComponentProperty(type=CGF.PropertyType.Float, editorName='rotation speed', value=0.0)


@registerComponent
class TestPrefabSpawner(object):
    group = DEMO_CATEGORY
    editorTitle = 'Test Prefab Spawner'
    domain = CGF.Domain.Client
    prefabPath = ComponentProperty(type=CGF.PropertyType.String, editorName='Prefab to spawn', value='content/Prefabs/1003_cgf_test/TestExplosion.prefab', annotations={'path': '*.prefab'})
    instancesCount = ComponentProperty(type=CGF.PropertyType.Int, editorName='Instances count', value=1)
    areaToSpawn = ComponentProperty(type=CGF.PropertyType.Link, editorName='Area to spawn', value=Triggers.CylinderAreaComponent)
    triggerToMonitor = ComponentProperty(type=CGF.PropertyType.Link, editorName='Trigger to monitor', value=Triggers.AreaTriggerComponent)
    transform = ComponentProperty(type=CGF.PropertyType.Link, editorName='transform', value=CGF.TransformComponent)
    attachToEntered = ComponentProperty(type=CGF.PropertyType.Bool, editorName='attach to entered', value=False)


class TestComponentCreationSystem(CGF.System):
    CreationActivated = CGF.ActivateReaction(CGF.ReactRw(TestComponentCreation))
    PrefabSpawnerActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(TestPrefabSpawner))
    TransformAccess = CGF.AccessReaction(CGF.Rw(CGF.TransformComponent))
    RotatorAccess = CGF.AccessReaction(CGF.Ro(TestScriptAxisRotator))
    RemoveDelayedAccess = CGF.AccessReaction(CGF.Rw(GenericComponents.RemoveGoDelayedComponent))
    VehicleAccess = CGF.AccessReaction(CGF.Rw(Vehicle))
    AreaTriggerAccess = CGF.AccessReaction(CGF.Rw(Triggers.AreaTriggerComponent))
    CylinderAreaAccess = CGF.AccessReaction(CGF.Rw(Triggers.CylinderAreaComponent))
    PrefabSpawnerAccess = CGF.AccessReaction(CGF.Ro(TestPrefabSpawner))
    Reactions = CGF.Reactions(CreationActivated, PrefabSpawnerActivated, TransformAccess, RotatorAccess, RemoveDelayedAccess, VehicleAccess, AreaTriggerAccess, CylinderAreaAccess, PrefabSpawnerAccess)

    def update(self):
        triggerAccess = self.reaction(self.AreaTriggerAccess)
        for testComponentCreation in self.reaction(self.CreationActivated):
            self._onTestComponentCreationAdded(testComponentCreation, triggerAccess)

        for go, prefabSpawner in self.reaction(self.PrefabSpawnerActivated):
            self._onPrefabSpawnerAdded(go, prefabSpawner, triggerAccess)

    def _onTestComponentCreationAdded(self, testComponentCreation, triggerAccess):
        trigger = triggerAccess.find(testComponentCreation.trigger)
        if trigger:
            trigger.addEnterReaction(functools.partial(self.__componentCreationEnter, testComponentCreation.rotationSpeed))
            trigger.addExitReaction(functools.partial(self.__componentCreationExit))

    def _onPrefabSpawnerAdded(self, spawnerObj, prefabSpawner, triggerAccess):
        trigger = triggerAccess.find(prefabSpawner.triggerToMonitor)
        if trigger:
            trigger.addEnterReaction(functools.partial(self.__onPrefabSpawnerEnter, spawnerObj))

    def __componentCreationEnter(self, rotationSpeed, who, where):
        _logger.debug('TestComponentCreation. Trigger entered')
        rotatorAccess = self.reaction(self.RotatorAccess)
        foundRotator = rotatorAccess.find(where)
        if foundRotator is not None:
            return
        else:
            q = CGF.CommandQueue(self.gom)
            rotator = q.createComponent(where, TestScriptAxisRotator)
            rotator.rotationSpeedYaw = rotationSpeed
            rotator.rotationSpeedPitch = 0
            rotator.rotationSpeedRoll = rotationSpeed
            rotator.transform = self.gom.gameObjectUuid(where)
            return

    def __componentCreationExit(self, who, where):
        rotatorAccess = self.reaction(self.RotatorAccess)
        scriptRotator = rotatorAccess.find(where)
        if scriptRotator is not None:
            q = CGF.CommandQueue(self.gom)
            q.removeComponent(where, scriptRotator)
        return

    def __onPrefabSpawnerEnter(self, spawnerObj, who, where):
        spawnerAccess = self.reaction(self.PrefabSpawnerAccess)
        spawner = spawnerAccess.find(spawnerObj)
        for _ in range(spawner.instancesCount):
            self.__spawn(spawner, who)

    def __spawn(self, spawner, who):
        if spawner.attachToEntered:

            def _onLoaded(objects, queue):
                root = objects[0]
                h = self.hierarchy
                vehicleAccess = self.reaction(self.VehicleAccess)
                vehicleGo = h.getTopMostParent(who)
                vehicle = vehicleAccess.find(vehicleGo)
                appearance = vehicle.appearance
                appearance.customizationGameObjects.append(queue.gameObject(root))
                queue.createComponent(root, GenericComponents.RedirectorComponent, who)
                queue.createComponent(root, GenericComponents.DynamicModelComponent, vehicle.model)

            CGF.loadAndCreatePrefabWithParent(spawner.prefabPath, who, Math.Vector3(0, 0, 0), _onLoaded)
            return
        cylinderAreaAccess = self.reaction(self.CylinderAreaAccess)
        area = cylinderAreaAccess.find(spawner.areaToSpawn)
        transformAccess = self.reaction(self.TransformAccess)
        transform = transformAccess.find(spawner.transform)
        if not area:
            return
        _logger.debug('TestPrefabSpawner. Create prefab = %s', spawner.prefabPath)
        u = random.random()
        yaw = 2 * math.pi * u
        pos = Math.Vector3(math.sin(yaw) * area.radius, 0, math.cos(yaw) * area.radius)
        pos.y = random.random() * area.height
        pos += transform.worldPosition

        def randomizeDestructionTime(objects, queue):
            remove = queue.component(objects[0], GenericComponents.RemoveGoDelayedComponent)
            remove.delay = 1 + random.random() * 9

        CGF.loadAndCreatePrefab(spawner.prefabPath, self.spaceID, pos, randomizeDestructionTime)


class TestTriggersSystem(CGF.System):
    RotatorIterate = CGF.IterateReaction(CGF.ActiveOnly, TestRotateWhileInTrigger, Triggers.AreaTriggerComponent, CGF.Rw(TestScriptAxisRotator))
    Reactions = CGF.Reactions(RotatorIterate)

    def update(self):
        for config, trigger, rotator in self.reaction(self.RotatorIterate):
            if trigger.getObjectsInProximity:
                rotator.rotationSpeedYaw = config.rotationSpeed
            rotator.rotationSpeedYaw = 0.0


@registerComponent
class TestVehicleAreaTriggerComponent(object):
    group = DEMO_CATEGORY
    editorTitle = 'Test Vehicle Area Trigger'
    domain = CGF.Domain.ServerEditor
    trigger = ComponentProperty(type=CGF.PropertyType.Link, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)
    health = ComponentProperty(type=CGF.PropertyType.Int, editorName='Health count', value=0)
    isDamageTrigger = ComponentProperty(type=CGF.PropertyType.Bool, editorName='Is Damage trigger', value=False)

    def __init__(self):
        self.reactionID = None
        return


@registerComponent
class TestHealthTriggersComponent(object):
    group = DEMO_CATEGORY
    editorTitle = 'Test Health Triggers'
    domain = CGF.Domain.ServerEditor
    healthComponent = ComponentProperty(type=CGF.PropertyType.Link, editorName='Health component link', value=HealthComponent)
    trigger = ComponentProperty(type=CGF.PropertyType.Link, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)
    health = ComponentProperty(type=CGF.PropertyType.Int, editorName='Health count', value=0)
    isDamageTrigger = ComponentProperty(type=CGF.PropertyType.Bool, editorName='Is Damage trigger', value=False)

    def __init__(self):
        self.reactionID = None
        return
