# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/team_bases_recapturable_ctrl.py
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from TeamBaseRecapturable import ITeamBasesRecapturableListener

class TeamsBasesRecapturableController(IArenaLoadController, ViewComponentsController, ITeamBasesRecapturableListener):

    def __init__(self):
        super(TeamsBasesRecapturableController, self).__init__()
        self.__teamBases = {}
        self.__listeners = []
        self.__combinedListeners = []

    def getControllerID(self):
        return BATTLE_CTRL_ID.TEAM_BASE_RECAPTURABLE

    def startControl(self, battleCtx, arenaVisitor):
        pass

    def stopControl(self):
        self.__listeners = []

    def registerListener(self, listener):
        self.__listeners.append(listener)
        self.__updateListeners()

    def onCreated(self, teamBase):
        self.__teamBases[teamBase.baseID] = teamBase
        teamBase.registerListener(self)

    def onLeaveWorld(self, baseID):
        self.__teamBases.pop(baseID, None)
        return

    def onBaseCreated(self, teamBase):
        for listener in self.__combinedListeners:
            listener.onBaseCreated(teamBase)

    def onBaseCaptured(self, baseId, newTeam):
        for listener in self.__combinedListeners:
            listener.onBaseCaptured(baseId, newTeam)

    def onBaseProgress(self, baseId, team, points, invadersCount, timeLeft):
        for listener in self.__combinedListeners:
            listener.onBaseProgress(baseId, team, points, invadersCount, timeLeft)

    def onBaseCaptureStart(self, baseId, team, isPlayerTeam, invadersCount, timeLeft):
        for listener in self.__combinedListeners:
            listener.onBaseCaptureStart(baseId, team, isPlayerTeam, invadersCount, timeLeft)

    def onBaseCaptureStop(self, baseId):
        for listener in self.__combinedListeners:
            listener.onBaseCaptureStop(baseId)

    def onBaseTeamChanged(self, baseId, prevTeam, newTeam):
        for listener in self.__combinedListeners:
            listener.onBaseTeamChanged(baseId, prevTeam, newTeam)

    def onBaseInvadersTeamChanged(self, baseId, invadersTeam):
        for listener in self.__combinedListeners:
            listener.onBaseInvadersTeamChanged(baseId, invadersTeam)

    @property
    def teamBases(self):
        return self.__teamBases

    def setViewComponents(self, *components):
        super(TeamsBasesRecapturableController, self).setViewComponents(*components)
        self.__updateListeners()

    def clearViewComponents(self):
        super(TeamsBasesRecapturableController, self).clearViewComponents()
        self.__updateListeners()

    def __updateListeners(self):
        self.__combinedListeners = self.__listeners + list(self._viewComponents)
