# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/Mine.py
import BigWorld
from battleground.mines_object import loadMines
from entity_game_object import EntityGameObject
from gui.battle_control import avatar_getter
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from PlayerEvents import g_playerEvents

class Mine(EntityGameObject):
    battleSession = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(Mine, self).__init__()
        self.__callbackID = None
        self.__ownerTeam = self.battleSession.getArenaDP().getVehicleInfo(self.ownerVehicleID).team
        player = BigWorld.player()
        if player is not None and player.userSeesWorld():
            self.__currentObservedVehicleID = avatar_getter.getVehicleIDAttached()
        else:
            self.__currentObservedVehicleID = None
            g_playerEvents.onAvatarReady += self.__onAvatarReady
        return

    def onEnterWorld(self, *args):
        super(Mine, self).onEnterWorld(*args)
        if BigWorld.player().isObserver():
            self.__callbackID = BigWorld.callback(0, self.__tick)

    def onLeaveWorld(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        super(Mine, self).onLeaveWorld()
        return

    def set_isDetonated(self, prev=None):
        if self.isDetonated:
            if self.gameObject is not None:
                self.gameObject.detonate()
        return

    def _loadGameObject(self):
        return loadMines(self.ownerVehicleID, self._registerGameObject)

    def _registerGameObject(self, gameObject):
        self.gameObject.setPosition(self.position)
        self.gameObject.setIsEnemyMarkerEnabled(True)
        super(Mine, self)._registerGameObject(gameObject)

    def __onAvatarReady(self):
        self.__currentObservedVehicleID = avatar_getter.getVehicleIDAttached()

    def __onObservedVehicleChanged(self, observedVehicleID):
        observedVehicleTeam = self.battleSession.getArenaDP().getVehicleInfo(observedVehicleID).team
        observerIsAlly = observedVehicleTeam == self.__ownerTeam
        if observerIsAlly and not self.gameObject.isAllyMine or not observerIsAlly and self.gameObject.isAllyMine:
            self.gameObject.destroy()
            self.gameObject = loadMines(self.ownerVehicleID, self._registerGameObject, startEffectEnabled=False)

    def __tick(self):
        observedVehicleID = avatar_getter.getVehicleIDAttached()
        if observedVehicleID != self.__currentObservedVehicleID:
            self.__currentObservedVehicleID = observedVehicleID
            self.__onObservedVehicleChanged(observedVehicleID)
        self.__callbackID = BigWorld.callback(0.5, self.__tick)
