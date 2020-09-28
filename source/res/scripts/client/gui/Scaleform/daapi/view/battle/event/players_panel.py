# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/players_panel.py
from constants import ARENA_PERIOD, IGR_TYPE
from gui.Scaleform.settings import ICONS_SIZES
from gui.battle_control.arena_info import team_overrides
from gui.battle_control.arena_info.settings import VEHICLE_STATUS
from gui.battle_control.controllers.team_health_bar_ctrl import ITeamHealthBarListener
from helpers import dependency
from messenger.m_constants import UserEntityScope, USER_TAG
from messenger.storage import storage_getter
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IBattleFieldController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE, INVALIDATE_OP
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.Scaleform.daapi.view.meta.EventPlayersPanelMeta import EventPlayersPanelMeta
from gui.Scaleform.genConsts.EVENT_CONSTS import EVENT_CONSTS
from gui.shared.badges import buildBadge
from gui.shared.gui_items.Vehicle import VEHICLE_EVENT_TYPE
from PlayerEvents import g_playerEvents

class EventPlayersPanel(EventPlayersPanelMeta, IBattleFieldController, ITeamHealthBarListener):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    MAX_HUNTER_LIVES = 3

    def __init__(self):
        super(EventPlayersPanel, self).__init__()
        self._battleCtx = None
        self._arenaVisitor = None
        self.__personalInfo = None
        self.__playerFormatter = None
        self.__bossVehID = None
        self.__reusable = {}
        self.__arenaDP = self.sessionProvider.getArenaDP()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.GUI

    def startControl(self, battleCtx, arenaVisitor):
        self.__personalInfo = team_overrides.PersonalInfo()
        self._battleCtx = battleCtx
        self._arenaVisitor = arenaVisitor
        self.__playerFormatter = self._battleCtx.createPlayerFullNameFormatter(showVehShortName=False)

    def stopControl(self):
        self._battleCtx = None
        self._arenaVisitor = None
        self.__personalInfo = None
        self.__playerFormatter = None
        self.__bossVehID = None
        return

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.INVITATIONS

    def acceptSquad(self, sessionID):
        self.sessionProvider.invitations.accept(sessionID)

    def addToSquad(self, sessionID):
        self.sessionProvider.invitations.send(sessionID)

    def invalidateVehiclesInfo(self, arenaDP):
        self.__updatePersonalPrebattleID(arenaDP)
        self.__updateAllTeammates()

    def invalidateArenaInfo(self):
        self.__updateAllTeammates()

    def invalidateVehicleStatus(self, flags, vInfo, arenaDP):
        self.__updateAllTeammates()

    def addVehicleInfo(self, vInfo, _):
        self.__updateTeammate(vInfo)

    def updateVehiclesInfo(self, updated, arenaDP):
        shared = INVALIDATE_OP.NONE
        for f, _ in updated:
            shared |= f

        if shared & INVALIDATE_OP.PREBATTLE_CHANGED > 0:
            self.__updatePersonalPrebattleID(arenaDP)
        for _, vInfo in updated:
            self.__updateTeammate(vInfo)

    def updateVehiclesStats(self, updated, arenaDP):
        for _, vStatsVO in updated:
            vInfoVO = self.__arenaDP.getVehicleInfo(vStatsVO.vehicleID)
            self.__updateTeammate(vInfoVO)

    def updateTeamHealthPercent(self, allyPercentage, enemyPercentage):
        if self.__bossVehID is not None:
            vInfo = self.__arenaDP.getVehicleInfo(self.__bossVehID)
            isEnemy = self.__arenaDP.isEnemyTeam(vInfo.team)
            self.as_setPlayerPanelHpS(self.__bossVehID, enemyPercentage if isEnemy else allyPercentage)
        return

    def invalidatePlayerStatus(self, flags, vInfoVO, arenaDP):
        self.__updateTeammate(vInfoVO)

    def invalidateVehiclesStats(self, arenaDP):
        self.__updateAllTeammates()

    def invalidateUsersTags(self):
        self.__updateAllTeammates()

    def invalidateInvitationsStatuses(self, vInfoVOs, _):
        for vInfoVO in vInfoVOs:
            self.__updateTeammate(vInfoVO)

    def invalidateUserTags(self, user):
        vehicleID = self.__arenaDP.getVehIDBySessionID(user.getID())
        self.__updateTeammate(self.__arenaDP.getVehicleInfo(vehicleID))

    def _populate(self):
        super(EventPlayersPanel, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            respawnCtrl.onTeammatesRespawnLivesUpdated += self.__onTeammatesRespawnLivesUpdated
        self.__updateAllTeammates()
        return

    def _dispose(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            respawnCtrl.onTeammatesRespawnLivesUpdated -= self.__onTeammatesRespawnLivesUpdated
        self.sessionProvider.removeArenaCtrl(self)
        self.__clearTeamOverrides()
        super(EventPlayersPanel, self)._dispose()
        return

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.PLAYER_INFO:
            arenaDP = self._battleCtx.getArenaDP()
            previousID = self.__personalInfo.changeSelected(value)
            self.invalidatePlayerStatus(0, arenaDP.getVehicleInfo(previousID), arenaDP)
            if value != previousID:
                self.invalidatePlayerStatus(0, arenaDP.getVehicleInfo(value), arenaDP)

    def __onTeammatesRespawnLivesUpdated(self, lives):
        for vehId, vehLives in lives.iteritems():
            self.as_setPlayerLivesS(vehId, vehLives)

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__updateAllTeammates()

    def __updateAllTeammates(self):
        leftTeam = []
        leftDeads = []
        rightTeam = []
        rightDeads = []
        for vInfo in self.__arenaDP.getVehiclesInfoIterator():
            playerInfo = self.__makePlayerInfo(vInfo)
            if playerInfo is not None:
                if playerInfo['isEnemy']:
                    if playerInfo['countLives'] > 0:
                        rightTeam.append(playerInfo)
                    else:
                        rightDeads.append(playerInfo)
                elif playerInfo['countLives'] > 0:
                    leftTeam.append(playerInfo)
                else:
                    leftDeads.append(playerInfo)

        leftTeam.extend(leftDeads)
        rightTeam.extend(rightDeads)
        self.as_setPlayersPanelDataS({'leftTeam': leftTeam,
         'rightTeam': rightTeam})
        return

    def __updateTeammate(self, vInfo):
        playerInfo = self.__makePlayerInfo(vInfo)
        if playerInfo is not None:
            self.as_setPlayerPanelInfoS(playerInfo)
        return

    def __makePlayerInfo(self, vInfo):
        if not {'event_boss', 'event_hunter'} & vInfo.vehicleType.tags:
            return
        else:
            playerVehicleID = avatar_getter.getPlayerVehicleID()
            playerSquad = self.__arenaDP.getVehicleInfo(playerVehicleID).squadIndex
            isSquad = False
            if playerSquad > 0 and playerSquad == vInfo.squadIndex or playerSquad == 0 and vInfo.vehicleID == playerVehicleID:
                isSquad = True
            vStats = self.__arenaDP.getVehicleStats(vInfo.vehicleID)
            frags = vStats.frags if vStats is not None else 0
            countLives = self.MAX_HUNTER_LIVES
            respawnCtrl = self.sessionProvider.dynamic.respawn
            if respawnCtrl is not None:
                countLives = respawnCtrl.teammatesLives.get(vInfo.vehicleID, 0)
            isEnemy, overrides = self.__getTeamOverrides(vInfo)
            playerVO = vInfo.player
            sessionID = playerVO.avatarSessionID
            isTeamKiller = playerVO.isTeamKiller or self._battleCtx.isTeamKiller(vInfo.vehicleID, sessionID) or overrides.isTeamKiller(vInfo)
            parts = self.__getPlayerFullName(vInfo)
            badge = buildBadge(vInfo.selectedBadge, vInfo.getBadgeExtraInfo())
            badgeVO = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True) if badge else None
            hpCurrent = 0
            eventRole = 0
            if VEHICLE_EVENT_TYPE.EVENT_BOSS in vInfo.vehicleType.tags:
                eventRole |= EVENT_CONSTS.BOSS
                if VEHICLE_EVENT_TYPE.EVENT_SPECIAL_BOSS in vInfo.vehicleType.tags:
                    eventRole |= EVENT_CONSTS.SPECIAL_BOSS
                self.__saveBossVehicleID(vInfo.vehicleID)
                percentages = avatar_getter.getHealthPercentage()
                if percentages is not None:
                    allyPercentage = 0
                    enemyPercentage = 0
                    listLength = len(percentages)
                    playerTeam = avatar_getter.getPlayerTeam()
                    for i in range(0, listLength):
                        if playerTeam == i + 1:
                            allyPercentage = percentages[i]
                        enemyPercentage += percentages[i]

                    hpCurrent = enemyPercentage if isEnemy else allyPercentage
            else:
                eventRole |= EVENT_CONSTS.HUNTER
            vehicleStatus = vInfo.vehicleStatus
            if countLives > 0:
                vehicleStatus |= VEHICLE_STATUS.IS_ALIVE
            return {'vehID': vInfo.vehicleID,
             'playerName': parts.playerName,
             'playerFakeName': parts.playerFakeName,
             'playerFullName': parts.playerFullName,
             'playerStatus': overrides.getPlayerStatus(vInfo, isTeamKiller),
             'clanAbbrev': playerVO.clanAbbrev,
             'region': parts.regionCode,
             'userTags': self.__getUserTags(sessionID, playerVO.igrType),
             'hpCurrent': hpCurrent,
             'isSquad': isSquad,
             'squadIndex': vInfo.squadIndex,
             'invitationStatus': overrides.getInvitationDeliveryStatus(vInfo),
             'vehicleAction': overrides.getAction(vInfo),
             'vehicleStatus': vehicleStatus,
             'isObserver': vInfo.isObserver(),
             'countLives': countLives,
             'eventRole': eventRole,
             'sessionID': sessionID,
             'kills': frags,
             'isPlayer': vInfo.vehicleID == playerVehicleID,
             'isEnemy': isEnemy,
             'badgeVO': badgeVO,
             'suffixBadgeIcon': 'badge_{}'.format(vInfo.selectedSuffixBadge) if vInfo.selectedSuffixBadge else ''}

    def __getTeamOverrides(self, vo):
        team = vo.team
        if team in self.__reusable:
            isEnemy, overrides = self.__reusable[team]
        else:
            isEnemy = self.__arenaDP.isEnemyTeam(team)
            overrides = team_overrides.makeOverrides(isEnemy, team, self.__personalInfo, self._arenaVisitor, isReplayPlaying=self.sessionProvider.isReplayPlaying)
            self.__reusable[team] = (isEnemy, overrides)
        return (isEnemy, overrides)

    def __clearTeamOverrides(self):
        while self.__reusable:
            _, (_, overrides) = self.__reusable.popitem()
            overrides.clear()

    def __updatePersonalPrebattleID(self, arenaDP):
        self.__personalInfo.prebattleID = arenaDP.getVehicleInfo().prebattleID

    def __saveBossVehicleID(self, vehID):
        if self.__bossVehID is None or self.__bossVehID != vehID:
            self.__bossVehID = vehID
        return

    def __getPlayerFullName(self, vInfoVO):
        return self.__playerFormatter.format(vInfoVO)

    @storage_getter('users')
    def __usersStorage(self):
        return None

    def __getUserTags(self, avatarSessionID, igrType):
        contact = self.__usersStorage.getUser(avatarSessionID, scope=UserEntityScope.BATTLE)
        if contact is not None:
            userTags = contact.getTags()
        else:
            userTags = set()
        return self.__addTagByIGRType(userTags, igrType)

    @staticmethod
    def __addTagByIGRType(userTags, igrType):
        if igrType == IGR_TYPE.BASE:
            userTags.add(USER_TAG.IGR_BASE)
        elif igrType == IGR_TYPE.PREMIUM:
            userTags.add(USER_TAG.IGR_PREMIUM)
        return userTags
