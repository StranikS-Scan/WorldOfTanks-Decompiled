# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/training_room.py
from constants import PREBATTLE_TYPE
from gui.Scaleform.daapi.view.lobby.trainings.TrainingRoomBase import TrainingRoomBase
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.training.legacy.ctx import TrainingSettingsCtx
from gui.prb_control.settings import PREBATTLE_ROSTER, REQUEST_TYPE
from gui.shared import events, EVENT_BUS_SCOPE
from gui.impl.gen import R

class TrainingRoom(TrainingRoomBase):

    def __init__(self, _=None):
        super(TrainingRoom, self).__init__()

    def _populate(self):
        funcState = self.prbDispatcher.getFunctionalState()
        if not funcState.isInLegacy(PREBATTLE_TYPE.TRAINING):
            g_eventDispatcher.removeTrainingFromCarousel(False)
            return
        super(TrainingRoom, self)._populate()

    def _addListeners(self):
        super(TrainingRoom, self)._addListeners()
        self.addListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self._updateTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        super(TrainingRoom, self)._removeListeners()
        self.removeListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self._updateTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)

    def showTrainingSettings(self):
        settings = TrainingSettingsCtx()
        self.fireEvent(events.LoadViewEvent(PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY, ctx={'isCreateRequest': False,
         'settings': settings}), scope=EVENT_BUS_SCOPE.LOBBY)

    def onRostersChanged(self, entity, rosters, full):
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1 in rosters:
            self.as_setTeam1S(self._makeAccountsData(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1], R.strings.menu.training.info.team1Label()))
        if PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2 in rosters:
            self.as_setTeam2S(self._makeAccountsData(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2], R.strings.menu.training.info.team2Label()))
        if PREBATTLE_ROSTER.UNASSIGNED in rosters:
            self.as_setOtherS(self._makeAccountsData(rosters[PREBATTLE_ROSTER.UNASSIGNED], R.strings.menu.training.info.otherLabel()))
        super(TrainingRoom, self).onRostersChanged(entity, rosters, full)

    def _handleSetPrebattleCoolDown(self, event):
        super(TrainingRoom, self)._handleSetPrebattleCoolDown(event)
        if event.requestID is REQUEST_TYPE.SWAP_TEAMS:
            self.as_startCoolDownSwapButtonS(event.coolDown)

    def _closeWindows(self):
        self._closeWindow(PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY)
        self._closeWindow(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY)

    def _showRosters(self, entity, rosters):
        accounts = rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1]
        self.as_setTeam1S(self._makeAccountsData(accounts, R.strings.menu.training.info.team1Label()))
        accounts = rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM2]
        self.as_setTeam2S(self._makeAccountsData(accounts, R.strings.menu.training.info.team2Label()))
        accounts = rosters[PREBATTLE_ROSTER.UNASSIGNED]
        self.as_setOtherS(self._makeAccountsData(accounts, R.strings.menu.training.info.otherLabel()))
        super(TrainingRoom, self)._showRosters(entity, rosters)

    def _updateTrainingRoom(self, event):
        self._closeWindow(PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY)
        super(TrainingRoom, self)._updateTrainingRoom(event)
