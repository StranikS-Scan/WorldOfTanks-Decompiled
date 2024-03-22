# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/thunder_strike.py
import CGF
import Math
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery
from constants import IS_CLIENT
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
import GenericComponents
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
    category = 'Abilities'
    domain = CGF.DomainOption.DomainClient
    strikePrefab = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='strike prefab', annotations={'path': '*.prefab'})


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, CGF.DomainOption.DomainClient)
class ThunderStrikeManager(CGF.ComponentManager):

    @onAddedQuery(ThunderStrike, GenericComponents.TransformComponent, CGF.GameObject)
    def visualizeThunderStrike(self, thunderStrike, transform, go):
        go.createComponent(ThunderStrikeLoader, thunderStrike, transform, go)


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
        CGF.loadGameObjectIntoHierarchy(usagePrefab, self.__go, Math.Vector3(0, 0, 0), self.__onPrefabLoaded)

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

    def __onPrefabLoaded(self, prefabGO):
        self.__prefabGO = prefabGO
        prefabGO.addComponent(self.equipment)
        self.__thunderStrikeEntity.onHit += self.__processHit

    def __processHit(self):
        if not self.__prefabGO:
            return
        visualizer = self.__prefabGO.findComponentByType(ThunderStrikeVisualizer)
        if visualizer.strikePrefab:
            CGF.loadGameObjectIntoHierarchy(visualizer.strikePrefab, self.__prefabGO, Math.Vector3(0, 0, 0))

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
