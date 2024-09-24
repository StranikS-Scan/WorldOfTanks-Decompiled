# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/player_satisfaction_rating/loggers.py
import json
import logging
import typing
from enum import Enum
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from uilogging.base.logger import MetricsLogger
from uilogging.player_satisfaction_rating.logging_constants import FEATURE, NO_MIN_VIEW_TIME, POST_BATTLE_CM_ACTION_TO_PLAYER_SATISFACTION_CM_ACTION, PlayerSatisfactionRatingLogActions, MIN_VIEW_TIME, PlayerSatisfactionRatingKeys, PlayerSatisfactionRatingCMActions, PlayerSatisfactionRatingInfoKeys, PlayerSatisfationRatingInviteSource, ARENA_PERIOD_TO_KEY, PlayerSatisfactionRatingRadialMenuActions, RADIAL_MENU_ACTIONS_TO_LOGGING_ACTIONS
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.lobby.lobby_constants import USER
    from uilogging.types import ParentScreenType, ItemType
    from typing import Optional, Any, Union
_logger = logging.getLogger(__name__)

def _serializeAdditionalInfo(sessionProvider):
    arenaVisitor = sessionProvider.arenaVisitor
    arenaPeriod = arenaVisitor.getArenaPeriod()
    arenaPeriodLength = arenaVisitor.getArenaPeriodLength()
    arenaPeriodEnd = arenaVisitor.getArenaPeriodEndTime()
    startTime = arenaPeriodEnd - arenaPeriodLength
    logTime = int(BigWorld.serverTime() - startTime)
    vehInfo = arenaVisitor.getArenaVehicles().get(BigWorld.player().playerVehicleID, None)
    if vehInfo is None:
        return
    else:
        isVehicleAlive = vehInfo['isAlive']
        return json.dumps({PlayerSatisfactionRatingInfoKeys.ARENA_ID_KEY: arenaVisitor.getArenaUniqueID(),
         PlayerSatisfactionRatingInfoKeys.BATTLE_PHASE_KEY: ARENA_PERIOD_TO_KEY[arenaPeriod],
         PlayerSatisfactionRatingInfoKeys.PHASE_TIME_KEY: logTime,
         PlayerSatisfactionRatingInfoKeys.IS_ALIVE_KEY: isVehicleAlive})


class PlayerSatisfactionRatingViewLogger(MetricsLogger):
    __slots__ = ('_viewParent', '_item', '__minViewTime')

    def __init__(self, parent, item, minViewTime=MIN_VIEW_TIME):
        super(PlayerSatisfactionRatingViewLogger, self).__init__(FEATURE)
        self._item = item
        self._viewParent = parent
        self.__minViewTime = minViewTime

    def onViewInitialize(self):
        self.startAction(action=PlayerSatisfactionRatingLogActions.VIEWED)

    @noexcept
    def onViewFinalize(self, itemState=None, additionalInfo=None):
        self.stopAction(action=PlayerSatisfactionRatingLogActions.VIEWED, item=self._item, parentScreen=self._viewParent, timeLimit=self.__minViewTime, itemState=itemState, info=additionalInfo)


class PostBattleContextMenuLogger(PlayerSatisfactionRatingViewLogger):
    __slots__ = ('_contextMenuAction',)

    def __init__(self):
        super(PostBattleContextMenuLogger, self).__init__(parent=PlayerSatisfactionRatingKeys.TEAM_SCORE_TAB, item=PlayerSatisfactionRatingKeys.CONTEXT_MENU)
        self._contextMenuAction = PlayerSatisfactionRatingCMActions.NO_ACTION

    def setContextMenuAction(self, optionId):
        self._contextMenuAction = POST_BATTLE_CM_ACTION_TO_PLAYER_SATISFACTION_CM_ACTION.get(optionId, PlayerSatisfactionRatingCMActions.UNTRACKED_ACTION)

    def onViewFinalize(self, **kwargs):
        super(PostBattleContextMenuLogger, self).onViewFinalize(self._contextMenuAction)


class BattleTeamStatsViewLogger(PlayerSatisfactionRatingViewLogger):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleTeamStatsViewLogger, self).__init__(parent=PlayerSatisfactionRatingKeys.BATTLE_GUI, item=PlayerSatisfactionRatingKeys.TEAM_VIEW)

    @noexcept
    def onViewFinalize(self, **kwargs):
        if PlayerSatisfactionRatingLogActions.VIEWED not in self._timedActions:
            return
        additionalInfo = _serializeAdditionalInfo(self._sessionProvider)
        if not additionalInfo:
            return
        super(BattleTeamStatsViewLogger, self).onViewFinalize(additionalInfo=additionalInfo)


class InviteToPlatoonLogger(MetricsLogger):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(InviteToPlatoonLogger, self).__init__(FEATURE)

    @noexcept
    def logPlatoonInvite(self, source):
        if not source:
            return
        if source == PlayerSatisfationRatingInviteSource.FULL_STATS_VIEW:
            parentScreen = PlayerSatisfactionRatingKeys.TEAM_VIEW
        elif source == PlayerSatisfationRatingInviteSource.IN_BATTLE_GUI:
            parentScreen = PlayerSatisfactionRatingKeys.BATTLE_GUI
        else:
            _logger.warning('logPlatoonInvite: inwite source (%s) does not map to log key', source)
            return
        info = self._serializeShortAdditionalInfo()
        if not info:
            return
        self.log(action=PlayerSatisfactionRatingLogActions.CLICK, item=PlayerSatisfactionRatingKeys.CREATE_PLATOON, parentScreen=parentScreen, info=info)

    def _serializeShortAdditionalInfo(self):
        arenaVisitor = self._sessionProvider.arenaVisitor
        vehInfo = arenaVisitor.getArenaVehicles().get(BigWorld.player().playerVehicleID, None)
        if vehInfo is None:
            return
        else:
            prebattleID = vehInfo['prebattleID']
            return json.dumps({PlayerSatisfactionRatingInfoKeys.ARENA_ID_KEY: arenaVisitor.getArenaUniqueID(),
             PlayerSatisfactionRatingInfoKeys.PREBATTLE_ID_KEY: prebattleID})


class InBattleContextMenuLogger(PlayerSatisfactionRatingViewLogger):
    __slots__ = ('_contextMenuAction',)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(InBattleContextMenuLogger, self).__init__(parent=PlayerSatisfactionRatingKeys.BATTLE_GUI, item=PlayerSatisfactionRatingKeys.CONTEXT_MENU, minViewTime=NO_MIN_VIEW_TIME)
        self._contextMenuAction = PlayerSatisfactionRatingCMActions.NO_ACTION

    def setContextMenuAction(self, action):
        self._contextMenuAction = action

    def onViewFinalize(self, **kwargs):
        additionalInfo = _serializeAdditionalInfo(self._sessionProvider)
        if not additionalInfo:
            return
        super(InBattleContextMenuLogger, self).onViewFinalize(self._contextMenuAction, additionalInfo)


class RadialMenuLogger(PlayerSatisfactionRatingViewLogger):
    __slots__ = ('_radialMenuAction',)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RadialMenuLogger, self).__init__(parent=PlayerSatisfactionRatingKeys.BATTLE_GUI, item=PlayerSatisfactionRatingKeys.COMMAND_WHEEL, minViewTime=NO_MIN_VIEW_TIME)
        self._radialMenuAction = PlayerSatisfactionRatingRadialMenuActions.NO_ACTION

    def setRadialMenuAction(self, action):
        self._radialMenuAction = RADIAL_MENU_ACTIONS_TO_LOGGING_ACTIONS.get(action, PlayerSatisfactionRatingRadialMenuActions.UNTRACKED_ACTION)

    def onViewFinalize(self, **kwargs):
        arenaVisitor = self._sessionProvider.arenaVisitor
        super(RadialMenuLogger, self).onViewFinalize(self._radialMenuAction, str(arenaVisitor.getArenaUniqueID()))


class KeyboardShortcutLogger(MetricsLogger):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(KeyboardShortcutLogger, self).__init__(FEATURE)

    def logKeyboardShortcutAction(self, action):
        itemState = RADIAL_MENU_ACTIONS_TO_LOGGING_ACTIONS.get(action, PlayerSatisfactionRatingRadialMenuActions.UNTRACKED_ACTION)
        arenaVisitor = self._sessionProvider.arenaVisitor
        self.log(action=PlayerSatisfactionRatingLogActions.CLICK, item=PlayerSatisfactionRatingKeys.HOT_KEY, parentScreen=PlayerSatisfactionRatingKeys.BATTLE_GUI, itemState=itemState, info=str(arenaVisitor.getArenaUniqueID()))


class BattleResponseLogger(PlayerSatisfactionRatingViewLogger):
    __slots__ = ('_response',)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleResponseLogger, self).__init__(parent=PlayerSatisfactionRatingKeys.BATTLE_GUI, item=PlayerSatisfactionRatingKeys.RESPONSE)
        self._response = PlayerSatisfactionRatingRadialMenuActions.NO_ACTION

    def setResponse(self, action):
        self._response = RADIAL_MENU_ACTIONS_TO_LOGGING_ACTIONS.get(action, PlayerSatisfactionRatingRadialMenuActions.UNTRACKED_ACTION)

    def onViewFinalize(self, **kwargs):
        arenaVisitor = self._sessionProvider.arenaVisitor
        super(BattleResponseLogger, self).onViewFinalize(self._response, str(arenaVisitor.getArenaUniqueID()))
