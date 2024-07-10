# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/ArenaInfoBRComponent.py
import functools
import BigWorld
import CGF
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items import vehicles
import GenericComponents
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import AirDropEvent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from debug_utils import LOG_DEBUG_DEV

class ArenaInfoBRComponent(DynamicScriptComponent, CallbackDelayer):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        DynamicScriptComponent.__init__(self)
        CallbackDelayer.__init__(self)

    def _onAvatarReady(self):
        self.set_nextDropWave(None)
        self.set_defeatedTeams(None)
        return

    def onLeaveWorld(self, *args):
        self.destroy()

    def notifyLaunchPosition(self, equipmentId, position, launchTime, duration):
        delay = launchTime - BigWorld.serverTime()
        equipment = vehicles.g_cache.equipments()[equipmentId]
        self.__showGuiMarker(equipment, position, delay)
        self.delayCallback(delay, functools.partial(self.__launch, equipment, position, duration))

    @property
    def battleRoyaleComponent(self):
        return self.__guiSessionProvider.arenaVisitor.getComponentSystem().battleRoyaleComponent

    def __showGuiMarker(self, equipment, position, delay):
        ctrl = self.__guiSessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.showMarker(equipment, position, (0, 0, 0), delay)
        return

    def __launch(self, equipment, position, duration):

        def postloadSetup(go):
            go.addComponent(equipment)
            go.createComponent(GenericComponents.RemoveGoDelayedComponent, duration)

        CGF.loadGameObject(equipment.usagePrefab, self.entity.spaceID, position, postloadSetup)

    def set_nextDropWave(self, prev):
        LOG_DEBUG_DEV('set_nextDropWave', self.nextDropWave)
        event = AirDropEvent(AirDropEvent.AIR_DROP_NXT_SPAWNED, ctx={'timeout': self.nextDropWave})
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)

    def set_defeatedTeams(self, _prev):
        self.battleRoyaleComponent.setDefeatedTeams(self.defeatedTeams)

    def set_isRespawnTimeFinished(self, prev):
        if self.isRespawnTimeFinished:
            self.battleRoyaleComponent.onRespawnTimeFinished()
