# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/abilities/thunder_strike.py
import functools
import CGF
import Math
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
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


class ThunderStrikeVisualizer(CGFComponent):
    editorTitle = 'Thunder Strike Visualizer'
    category = 'Abilities'
    strikePrefab = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='strike prefab', annotations={'path': '*.prefab'})


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE)
class ThunderStrikeManager(CGF.ComponentManager, CallbackDelayer):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ThunderStrikeManager, self).__init__()
        CallbackDelayer.__init__(self)

    def deactivate(self):
        CallbackDelayer.destroy(self)

    @onAddedQuery(ThunderStrike, GenericComponents.TransformComponent, CGF.GameObject)
    def visualizeThunderStrike(self, thunderStrike, transform, go):
        equipment = vehicles.g_cache.equipments()[thunderStrike.equipmentID]
        delay = thunderStrike.delayEndTime - BigWorld.serverTime()
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle and thunderStrike.attackerID == vehicle.id:
            self.__showGuiMarker(equipment, transform.worldPosition, delay)
        self.delayCallback(delay, functools.partial(self.__launch, go, thunderStrike, equipment))

    def __launch(self, gameObject, thunderStrikeEntity, equipment):

        def postloadSetup(go):
            go.addComponent(equipment)
            thunderStrikeEntity.onHit += functools.partial(self.__processHit, go)

        CGF.loadGameObjectIntoHierarchy(equipment.usagePrefab, gameObject, Math.Vector3(0, 0, 0), postloadSetup)

    def __showGuiMarker(self, equipment, position, delay):
        ctrl = self.__guiSessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.showMarker(equipment, position, (0, 0, 0), delay)
        return

    def __processHit(self, visualizerGo):
        visualizer = visualizerGo.findComponentByType(ThunderStrikeVisualizer)
        if visualizer.strikePrefab:
            CGF.loadGameObjectIntoHierarchy(visualizer.strikePrefab, visualizerGo, Math.Vector3(0, 0, 0))
