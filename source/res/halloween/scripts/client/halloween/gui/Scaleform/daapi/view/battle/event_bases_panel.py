# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/event_bases_panel.py
import BigWorld
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.EventBasesPanelMeta import EventBasesPanelMeta
from gui.Scaleform.daapi.view.battle.classic.battle_end_warning_panel import BattleEndWarningPanel
from TeamBaseRecapturable import ITeamBasesRecapturableListener
from helpers import dependency, time_utils
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import GRAPHICS
from debug_utils import LOG_ERROR

class _PanelTeamBase(object):

    def __init__(self, setBaseID, setBaseState, setBaseProgress):
        self.setBaseID = setBaseID
        self.setBaseState = setBaseState
        self.setBaseProgress = setBaseProgress
        self.teamBase = None
        return

    @property
    def inited(self):
        return self.teamBase is not None

    @property
    def baseID(self):
        return self.teamBase.baseID if self.inited else 0


_TEAM_BASES_IDENTIFIERS_COUNT = 7
_CAPTURE_POINTS_LIMIT = 100
_SHOW_DELAY = 1

class EventBasesPanel(EventBasesPanelMeta, ITeamBasesRecapturableListener):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(EventBasesPanel, self).__init__()
        self._leftIcon = _PanelTeamBase(self.as_setBase1IDS, self.as_setBase1StateS, self.as_setBase1ProgressS)
        self._rightIcon = _PanelTeamBase(self.as_setBase2IDS, self.as_setBase2StateS, self.as_setBase2ProgressS)
        self._iconByBaseID = [None] * (_TEAM_BASES_IDENTIFIERS_COUNT + 1)
        self._playerTeam = self._sessionProvider.getArenaDP().getNumberOfTeam()
        self._basesWaitsForInit = []
        self._showCallback = None
        if self.teamBaseController:
            self.teamBaseController.registerListener(self)
            for teamBase in self.teamBaseController.teamBases.itervalues():
                self._initTeamBase(teamBase)

        return

    def _populate(self):
        super(EventBasesPanel, self)._populate()
        self._updateColorBlind()
        if self.arenaPeriodController:
            self.arenaPeriodController.onPreBattleTimerHide += self._onPreBattleTimerHide
            if self.arenaPeriodController.getPeriod() != ARENA_PERIOD.BATTLE:
                self._hide()
        BattleEndWarningPanel.onBattleEndWarningShow += self._hide
        BattleEndWarningPanel.onBattleEndWarningHide += self._showWithDelay
        self._settingsCore.onSettingsChanged += self._onSettingChanged

    def _dispose(self):
        self._leftIcon = None
        self._rightIcon = None
        self._iconByBaseID = None
        if self.arenaPeriodController:
            self.arenaPeriodController.onPreBattleTimerHide -= self._onPreBattleTimerHide
        BattleEndWarningPanel.onBattleEndWarningShow -= self._hide
        BattleEndWarningPanel.onBattleEndWarningHide -= self._showWithDelay
        self._settingsCore.onSettingsChanged -= self._onSettingChanged
        self._clearShowCallback()
        super(EventBasesPanel, self)._dispose()
        return

    def onBaseCreated(self, teamBase):
        self._initTeamBase(teamBase)

    def onBaseCaptured(self, baseId, newTeam):
        self._updateTeamBaseStatus(baseId, True, 0.0)

    def onBaseProgress(self, baseId, team, points, invadersCount, timeLeft):
        if baseId > _TEAM_BASES_IDENTIFIERS_COUNT:
            LOG_ERROR('Wrong baseID: {}'.format(baseId))
            return
        handler = self._getMethodsHandler(baseId)
        normalizedPoints = points / _CAPTURE_POINTS_LIMIT
        if team != 0:
            normalizedPoints = 1 - normalizedPoints
        normalizedPoints = max(normalizedPoints, 0.01)
        handler.setBaseProgress(normalizedPoints, self._getTimeLeftStr(timeLeft))

    def onBaseCaptureStart(self, baseId, team, isPlayerTeam, invadersCount, timeLeft):
        if baseId > _TEAM_BASES_IDENTIFIERS_COUNT:
            LOG_ERROR('Wrong baseID: {}'.format(baseId))
            return
        reverse = team != 0
        points = 1.0 if reverse else 0.0
        timeLeft = timeLeft if reverse else 0.0
        self._updateTeamBaseStatus(baseId, team != 0, points, timeLeft)

    def onBaseCaptureStop(self, baseId):
        self._updateTeamBaseStatus(baseId)

    def onBaseTeamChanged(self, baseId, prevTeam, newTeam):
        self._updateTeamBaseStatus(baseId)

    def onBaseInvadersTeamChanged(self, baseId, invadersTeam):
        self._updateTeamBaseStatus(baseId, points=0.0)

    def _initTeamBase(self, teamBase):
        baseID = teamBase.baseID
        if baseID > _TEAM_BASES_IDENTIFIERS_COUNT:
            LOG_ERROR('Unsupported baseID: {}'.format(baseID))
            return
        if not self._leftIcon.inited:
            self._leftIcon.teamBase = teamBase
            self._fillTeamBase(self._leftIcon)
        elif not self._rightIcon.inited:
            self._rightIcon.teamBase = teamBase
            if self._rightIcon.baseID < self._leftIcon.baseID:
                self._leftIcon.teamBase, self._rightIcon.teamBase = self._rightIcon.teamBase, self._leftIcon.teamBase
                self._fillTeamBase(self._leftIcon)
            self._fillTeamBase(self._rightIcon)
        else:
            LOG_ERROR("{} can't be added to EventBasesPanel. Only 2 slots available.".format(baseID))
            return

    def _fillTeamBase(self, panelTeamBase):
        self._iconByBaseID[panelTeamBase.baseID] = panelTeamBase
        panelTeamBase.setBaseID(panelTeamBase.baseID)
        panelTeamBase.setBaseState(self._convertTeam(panelTeamBase.teamBase.team), self._convertTeam(panelTeamBase.teamBase.invadersTeam))

    @property
    def teamBaseController(self):
        return self._sessionProvider.dynamic.teamBaseRecapturable

    @property
    def arenaPeriodController(self):
        return self._sessionProvider.shared.arenaPeriod

    def _convertTeam(self, team):
        if team == 0:
            return 'none'
        return 'ally' if team == self._playerTeam else 'enemy'

    def _updateTeamBaseStatus(self, baseId, reverse=False, points=1.0, timeLeft=0):
        if baseId > _TEAM_BASES_IDENTIFIERS_COUNT:
            LOG_ERROR('Wrong baseID: {}'.format(baseId))
            return
        handler = self._getMethodsHandler(baseId)
        teamBase = self.teamBaseController.teamBases[baseId]
        handler.setBaseState(self._convertTeam(teamBase.team), self._convertTeam(teamBase.team if reverse else teamBase.invadersTeam))
        handler.setBaseProgress(points, self._getTimeLeftStr(timeLeft))

    def _getMethodsHandler(self, baseId):
        if baseId > _TEAM_BASES_IDENTIFIERS_COUNT:
            LOG_ERROR('Wrong baseID: {}'.format(baseId))
            return
        return self._iconByBaseID[baseId]

    def _getTimeLeftStr(self, timeLeft):
        return '' if timeLeft <= 0 else time_utils.getTimeLeftFormat(timeLeft)

    def _onPreBattleTimerHide(self):
        self._showWithDelay()

    def _hide(self):
        self.as_setVisibilityS(False)

    def _showWithDelay(self):
        self._showCallback = BigWorld.callback(_SHOW_DELAY, self._show)

    def _clearShowCallback(self):
        if self._showCallback is not None:
            BigWorld.cancelCallback(self._showCallback)
            self._showCallback = None
        return

    def _show(self):
        self.as_setVisibilityS(True)
        self._showCallback = None
        return

    def _onSettingChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            self._updateColorBlind()

    def _updateColorBlind(self):
        self.as_setColorBlindS(self._settingsCore.getSetting(GRAPHICS.COLOR_BLIND))
