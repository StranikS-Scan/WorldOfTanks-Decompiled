# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/AvatarBattleRoyaleComponent.py
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
import BattleReplay
from BattleReplay import g_replayEvents
from Event import EventsSubscriber

class AvatarBattleRoyaleComponent(BigWorld.DynamicScriptComponent, EventsSubscriber):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(AvatarBattleRoyaleComponent, self).__init__()
        if BattleReplay.g_replayCtrl.isPlaying:
            BattleReplay.g_replayCtrl.useSyncroniusResourceLoading(True)
            self.subscribeToEvent(g_replayEvents.onTimeWarpStart, self.__onTimeWarpStart)
            self.subscribeToEvent(g_replayEvents.onTimeWarpFinish, self.__onTimeWarpFinish)

    def onLeaveWorld(self):
        self.unsubscribeFromAllEvents()

    def set_playerPlace(self, _prev):
        self.sessionProvider.arenaVisitor.getComponentSystem().battleRoyaleComponent.setBattleRoyalePlace(self.playerPlace)

    def set_defeatedTeams(self, _prev):
        self.sessionProvider.arenaVisitor.getComponentSystem().battleRoyaleComponent.setDefeatedTeams(self.defeatedTeams)

    def __onTimeWarpStart(self):
        BigWorld.worldDrawEnabled(False)

    def __onTimeWarpFinish(self):
        BigWorld.worldDrawEnabled(True)
