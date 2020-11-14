# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/Radar.py
import BigWorld

class Radar(BigWorld.DynamicScriptComponent):

    def onEnterWorld(self, *args):
        pass

    def onLeaveWorld(self, *args):
        pass

    def set_radarReadinessTime(self, _=None):
        radarCtrl = self.__getRadarCtrl()
        if radarCtrl:
            radarCtrl.updateRadarReadinessTime(self.radarReadinessTime)

    def set_radarReady(self, prev):
        radarCtrl = self.__getRadarCtrl()
        if radarCtrl:
            radarCtrl.updateRadarReadiness(self.radarReady)

    def __getRadarCtrl(self):
        if self.entity.id == BigWorld.player().playerVehicleID:
            if self.entity.guiSessionProvider.dynamic.radar:
                return self.entity.guiSessionProvider.dynamic.radar
        return None
