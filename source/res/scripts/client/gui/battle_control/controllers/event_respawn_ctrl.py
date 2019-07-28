# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_respawn_ctrl.py
import BigWorld
import Event
from gui.battle_control.controllers.respawn_ctrl import RespawnsController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class EventRespawnsController(RespawnsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    teammateRespawnLives = property(lambda self: self.__teammateRespawnLives)

    def __init__(self, setup):
        super(EventRespawnsController, self).__init__(setup)
        self.onTeammateRespawnLivesUpdated = Event.Event(Event.EventManager())
        self.__teammateRespawnLives = {}
        self.__eManager = Event.EventManager()
        self.onAddRespawnGroup = Event.Event(self.__eManager)
        self.__respawnGroups = {}

    def startControl(self):
        super(EventRespawnsController, self).startControl()
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        gameEventStorage = getattr(componentSystem, 'gameEventComponent', None)
        if gameEventStorage:
            self._respawnLivesComponent = gameEventStorage.getRespawnLives()
            self._respawnLivesComponent.onTeammateLivesUpdate += self.__onTeammateRespawnLivesUpdated
        return

    def stopControl(self):
        super(EventRespawnsController, self).stopControl()
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        gameEventStorage = getattr(componentSystem, 'gameEventComponent', None)
        if gameEventStorage:
            self._respawnLivesComponent.onTeammateLivesUpdate -= self.__onTeammateRespawnLivesUpdated
        self.__respawnGroups = {}
        return

    @property
    def respawnGroups(self):
        return self.__respawnGroups

    def addRespawnGroup(self, groupID, position, isSelected):
        self.__respawnGroups[groupID] = (position, isSelected)
        self.onAddRespawnGroup(groupID, position, isSelected)

    @staticmethod
    def selectRespawnGroup(groupID):
        BigWorld.player().changeSelectedRespawnGroupID(groupID)

    def __onTeammateRespawnLivesUpdated(self, diff):
        for vehID, lives in diff.items():
            self.onTeammateRespawnLivesUpdated(vehID, lives)

        self.__teammateRespawnLives.update(diff)
