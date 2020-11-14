# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/BattleXP.py
import BigWorld

class BattleXP(BigWorld.DynamicScriptComponent):

    def onEnterWorld(self, *args):
        pass

    def onLeaveWorld(self, *args):
        pass

    def set_battleXP(self, _=None):
        ctrl = self.entity.guiSessionProvider.dynamic.progression
        if ctrl is not None and self.entity.id == BigWorld.player().playerVehicleID:
            ctrl.updateXP(self.battleXP)
        return

    def set_battleXpLvlData(self, _=None):
        ctrl = self.entity.guiSessionProvider.dynamic.progression
        if ctrl is not None and self.entity.id == BigWorld.player().playerVehicleID:
            ctrl.updateLevel(*self.battleXpLvlData)
        return
