# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/thunder_strike.py
from __future__ import absolute_import
import CGF
import Math
from typing import List
from cgf_script.registration import ComponentProperty, registerComponent
from constants import IS_CLIENT
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
import BigWorld
if IS_CLIENT:
    from ThunderStrike import ThunderStrike
else:

    class ThunderStrike(object):
        pass


@registerComponent
class ThunderStrikeVisualizer(object):
    editorTitle = 'Thunder Strike Visualizer'
    group = 'Abilities'
    domain = CGF.Domain.Client
    strikePrefab = ComponentProperty(type=CGF.PropertyType.String, value='', editorName='strike prefab', annotations={'path': '*.prefab'})


class ThunderStrikeLoader(CallbackDelayer):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, thunderStrike, transform, go):
        CallbackDelayer.__init__(self)
        self.__thunderStrikeEntity = thunderStrike
        self.__transform = transform
        self.__go = go
        self.equipment = vehicles.g_cache.equipments()[self.__thunderStrikeEntity.equipmentID]
        self.__prefabGO = None
        self.__loadedEffectIsAlly = None
        return

    def activate(self):
        vehicle = BigWorld.player().getVehicleAttached()
        delay = self.__thunderStrikeEntity.delayEndTime - BigWorld.serverTime()
        if vehicle and self.__thunderStrikeEntity.attackerID == vehicle.id:
            self.__showGuiMarker(delay)
        self.delayCallback(delay, self.__launch)
        self.__guiSessionProvider.onUpdateObservedVehicleData += self.__onUpdateObservedVehicleData

    def deactivate(self):
        CallbackDelayer.destroy(self)
        if self.__thunderStrikeEntity and hasattr(self.__thunderStrikeEntity, 'onHit'):
            self.__thunderStrikeEntity.onHit -= self.__processHit
        self.__removePrefab()
        self.__guiSessionProvider.onUpdateObservedVehicleData -= self.__onUpdateObservedVehicleData

    def __launch(self):
        usagePrefab = self.equipment.usagePrefab
        self.__loadedEffectIsAlly = True
        if self.equipment.usagePrefabEnemy and self.equipment.usagePrefab != self.equipment.usagePrefabEnemy:
            if not self.__isAttackerAlly():
                usagePrefab = self.equipment.usagePrefabEnemy
                self.__loadedEffectIsAlly = False
        CGF.loadAndCreatePrefabWithParent(usagePrefab, self.__go, Math.Vector3(0, 0, 0), self.__onPrefabLoaded)

    def __showGuiMarker(self, delay):
        ctrl = self.__guiSessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.showMarker(self.equipment, self.__transform.worldPosition, (0, 0, 0), delay)
        return

    def __isAttackerAlly(self):
        attackerID = self.__thunderStrikeEntity.attackerID
        vehicle = BigWorld.entity(attackerID)
        if vehicle is None:
            return False
        else:
            arenaDP = self.__guiSessionProvider.getArenaDP()
            result = arenaDP.isAllyTeam(vehicle.publicInfo['team'])
            return result

    def __onPrefabLoaded(self, objects, queue):
        root = objects[0]
        self.__prefabGO = queue.gameObject(root)
        queue.assignComponent(root, self.equipment)
        self.__thunderStrikeEntity.onHit += self.__processHit

    def __processHit(self):
        if not self.__prefabGO:
            return
        visualizer = self.__prefabGO.findRead(ThunderStrikeVisualizer)
        if visualizer.strikePrefab:
            CGF.loadAndCreatePrefabWithParent(visualizer.strikePrefab, self.__prefabGO, Math.Vector3(0, 0, 0))

    def __removePrefab(self):
        if self.__prefabGO is not None:
            CGF.removeGameObject(self.__prefabGO)
            self.__prefabGO = None
        return

    def __onUpdateObservedVehicleData(self, *args):
        if not self.equipment.usagePrefabEnemy or self.equipment.usagePrefab == self.equipment.usagePrefabEnemy:
            return
        if self.__loadedEffectIsAlly == self.__isAttackerAlly():
            return
        self.deactivate()
        self.activate()


class ThunderStrikeSystem(CGF.System):
    ThunderStrikeActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(ThunderStrike), CGF.Ro(CGF.TransformComponent))
    ThunderLoaderActivated = CGF.ActivateReaction(CGF.ReactRw(ThunderStrikeLoader))
    ThunderLoaderDeactivated = CGF.DeactivateReaction(CGF.ReactRw(ThunderStrikeLoader))
    Reactions = CGF.Reactions(ThunderStrikeActivated, ThunderLoaderActivated, ThunderLoaderDeactivated)

    def update(self):
        q = CGF.CommandQueue(self.gom)
        for go, thunderStrike, transform in self.reaction(self.ThunderStrikeActivated):
            self.visualizeThunderStrike(thunderStrike, transform, go, q)

        for loader in self.reaction(self.ThunderLoaderDeactivated):
            loader.deactivate()

        for loader in self.reaction(self.ThunderLoaderActivated):
            loader.activate()

    def visualizeThunderStrike(self, _, __, go, queue):
        instance = ThunderStrikeLoader(CGF.ComponentLink(go, ThunderStrike), CGF.ComponentLink(go, CGF.TransformComponent), go)
        queue.assignComponent(go, instance)
