# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/Radar.py
import BattleReplay
import BigWorld
import CGF
from Math import Vector3
from helpers import dependency
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider

class Radar(BigWorld.DynamicScriptComponent):
    __dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onEnterWorld(self, *args):
        pass

    def onLeaveWorld(self, *args):
        pass

    def set_radarReadinessTime(self, _=None):
        radarCtrl = self.entity.guiSessionProvider.dynamic.radar
        if radarCtrl:
            radarCtrl.updateRadarReadinessTime(self.radarReadinessTime)

    def set_radarReady(self, prev=None):
        radarCtrl = self.entity.guiSessionProvider.dynamic.radar
        if radarCtrl:
            radarCtrl.updateRadarReadiness(self.radarReady)

    def refreshRadar(self):
        self.set_radarReadinessTime()
        self.set_radarReady()

    def activatePatrickEffect(self):
        if BattleReplay.g_replayCtrl.isPlaying and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        self.__playEffect()

    def __playEffect(self):
        prefabPath = self.__dynObjectsCache.getConfig(self.__sessionProvider.arenaVisitor.getArenaGuiType()).getStPatrickLootEffect().effectPrefabPath
        CGF.loadGameObjectIntoHierarchy(prefabPath, self.entity.entityGameObject, Vector3(0))
