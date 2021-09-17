# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/epic_missions_ctrl.py
from collections import defaultdict
from collections import namedtuple
import typing
import BigWorld
import Event
import BattleReplay
from ReplayEvents import g_replayEvents
from constants import PLAYER_RANK, SECTOR_STATE
from debug_utils import verify, LOG_ERROR, LOG_DEBUG
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from epic_constants import EPIC_BATTLE_TEAM_ID, IN_BATTLE_RESERVE_EVENTS
from gui.battle_control.controllers.game_messages_ctrl import PlayerMessageData
from gui.battle_control.view_components import IViewComponentsController
from gui.battle_control.controllers.game_notification_ctrl import EPIC_NOTIFICATION, OVERTIME_DURATION_WARNINGS
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, i18n
from skeletons.gui.battle_session import IBattleSessionProvider
from shared_utils import first
if typing.TYPE_CHECKING:
    from SectorBase import SectorBase
TIMER_WARNINGS = [(5, 0), (2, 0)]
RANK_TO_TRANSLATION = {0: '',
 1: EPIC_BATTLE.RANK_RANK1,
 2: EPIC_BATTLE.RANK_RANK2,
 3: EPIC_BATTLE.RANK_RANK3,
 4: EPIC_BATTLE.RANK_RANK4,
 5: EPIC_BATTLE.RANK_RANK5,
 6: EPIC_BATTLE.RANK_RANK6}
MSG_ID_TO_DURATION = defaultdict(lambda : 4.5)
MSG_ID_TO_DURATION.update({GAME_MESSAGES_CONSTS.OVERTIME: 4.5})
MSG_ID_TO_PRIORITY = defaultdict(lambda : GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_LOW)
MSG_ID_TO_PRIORITY.update({GAME_MESSAGES_CONSTS.WIN: GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_HIGH,
 GAME_MESSAGES_CONSTS.DEFEAT: GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_HIGH,
 GAME_MESSAGES_CONSTS.DRAW: GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_HIGH,
 GAME_MESSAGES_CONSTS.TIME_REMAINING: GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_HIGH,
 GAME_MESSAGES_CONSTS.TIME_REMAINING_POSITIVE: GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_HIGH,
 GAME_MESSAGES_CONSTS.OVERTIME: GAME_MESSAGES_CONSTS.GAME_MESSAGE_PRIORITY_HIGH})
HQ_DAMAGE_DEBOUNCE_PERIOD = 120
CONTESTED_DEBOUNCE_PERIOD = 120
CONTESTED_CAPTURE_POINTS_THRESHOLD = 0.1

class PlayerMission(object):
    PlayerMissionData = namedtuple('PlayerMissionData', ('objectiveType', 'objectiveID', 'missionText', 'subText'))

    def __init__(self):
        self.missionType = EPIC_CONSTS.PRIMARY_EMPTY_MISSION
        self.missionText = ''
        self.subText = ''
        self.id = -1

    def generateData(self):
        return {'objectiveType': self.missionType,
         'objectiveID': self.id,
         'missionText': i18n.makeString(self.missionText),
         'subText': self.subText}

    def isEmptyMission(self):
        return self.missionType == EPIC_CONSTS.PRIMARY_EMPTY_MISSION

    def isObjectivesMission(self):
        return self.missionType == EPIC_CONSTS.PRIMARY_HQ_MISSION

    def isBaseMission(self):
        return self.missionType == EPIC_CONSTS.PRIMARY_BASE_MISSION


MissionTriggerArgs = namedtuple('MissionTriggerArgs', ('forceMissionUpdate', 'callback'))

class EpicMissionsController(IViewComponentsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, setup):
        super(EpicMissionsController, self).__init__()
        self.__sessionProvider = setup.sessionProvider
        self.__ready = False
        self.__ui = None
        self.__currentMission = PlayerMission()
        self.__activeMissionData = {'lane': 0,
         'bases': 0,
         'hqActive': False,
         'destroyedHQs': 0,
         'endTime': -1,
         'sectorGroup': 0,
         'isInHQSector': False}
        self.__numDestructiblesToDestroy = None
        self.__currentEndTime = 0
        self.__currentLane = 0
        self.__nearestObjective = -1
        self.__nearestObjectiveDistance = -1
        self.__objMsgSent = False
        self.__generalRankMsgSent = False
        self.__overtimeCB = None
        self.__overTimeEnd = None
        self.__orderBattleAbilities = list()
        self.__isLaneContested = [False, False, False]
        self.__contestedEndTime = [0, 0, 0]
        self.__lastTimeHQDamaged = defaultdict(lambda : 0)
        self.__retreatMissionResults = {}
        self.__activeMessages = [0] * (max(EPIC_NOTIFICATION.ALL()) + 1)
        self.__eManager = Event.EventManager()
        self.__capturedBases = set()
        self.onPlayerMissionUpdated = Event.Event(self.__eManager)
        self.onPlayerMissionReset = Event.Event(self.__eManager)
        self.onPlayerMissionTimerSet = Event.Event(self.__eManager)
        self.onNearestObjectiveChanged = Event.Event(self.__eManager)
        self.onObjectiveBattleStarted = Event.Event(self.__eManager)
        self.onIngameMessageReady = Event.Event(self.__eManager)
        self._notificationTypeToMissionTriggerArgs = {EPIC_NOTIFICATION.ZONE_CAPTURED: MissionTriggerArgs(forceMissionUpdate=True, callback=lambda : self.__setNearestObjective() if self.__activeMissionData['bases'] == 0 else None),
         EPIC_NOTIFICATION.HQ_ACTIVE: MissionTriggerArgs(forceMissionUpdate=True, callback=self.__setNearestObjective),
         EPIC_NOTIFICATION.BASE_ACTIVE: MissionTriggerArgs(forceMissionUpdate=True, callback=None),
         EPIC_NOTIFICATION.HQ_DESTROYED: MissionTriggerArgs(forceMissionUpdate=False, callback=None),
         EPIC_NOTIFICATION.RETREAT: MissionTriggerArgs(forceMissionUpdate=False, callback=None)}
        return

    def setViewComponents(self, *components):
        self.__ui = components[0]
        ctrl = self.__sessionProvider.dynamic.gameNotifications
        ctrl.onGameNotificationRecieved += self.__onGameNotificationRecieved
        self.__ui.start()

    def clearViewComponents(self):
        self.__ui = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.EPIC_MISSIONS

    def startControl(self):
        self.__numDestructiblesToDestroy = avatar_getter.getArena().arenaType.numDestructiblesToDestroyForWin
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is None:
            LOG_ERROR('Expected SectorBaseComponent not present!')
            return
        else:
            playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
            if playerDataComp is None:
                LOG_ERROR('Expected PlayerDataComponent not present!')
                return
            destructibleEntityComp = getattr(componentSystem, 'destructibleEntityComponent', None)
            if destructibleEntityComp is None:
                LOG_ERROR('Expected DestructibleEntityComponent not present!')
                return
            sectorComp = getattr(componentSystem, 'sectorComponent', None)
            if sectorComp is None:
                LOG_ERROR('Expected SectorComponent not present!')
                return
            overTimeComp = getattr(componentSystem, 'overtimeComponent', None)
            if overTimeComp is None:
                LOG_ERROR('Expected OvertimeComponent not present!')
                return
            sectorBaseComp.onSectorBaseActiveStateChanged += self.__onSectorBaseActiveStateChanged
            sectorBaseComp.onSectorBasePointsUpdate += self.__onSectorBasePointsUpdate
            playerDataComp.onPlayerPhysicalLaneUpdated += self.__onPlayerPhysicalLaneUpdated
            destructibleEntityComp.onDestructibleEntityHealthChanged += self.__onDestructibleEntityHealthChanged
            destructibleEntityComp.onDestructibleEntityIsActiveChanged += self.__onDestructibleEntityIsActiveChanged
            sectorComp.onWaypointsForPlayerActivated += self.__onWaypointsForPlayerActivated
            sectorComp.onPlayerSectorGroupChanged += self.__onPlayerSectorGroupChanged
            sectorComp.onSectorTransitionTimeChanged += self.__onSectorTransitionTimeChanged
            playerDataComp.onPlayerRankUpdated += self.__onPlayerRankUpdated
            playerDataComp.onVehicleRanksUpdated += self.__onVehicleRanksUpdated
            overTimeComp.onOvertimeStart += self.__onOvertimeStart
            overTimeComp.onOvertimeOver += self.__onOvertimeOver
            hqs = destructibleEntityComp.destructibleEntities
            if hqs:
                firstHQ = first(hqs.values())
                self.__activeMissionData['hqActive'] = firstHQ.isActive
                self.__objMsgSent = firstHQ.isActive
            arenaDP = self.__sessionProvider.getArenaDP()
            if arenaDP:
                self.__generalRankMsgSent = any((arenaDP.isAllyTeam(arenaDP.getVehicleInfo(vID).team) and arenaDP.isGeneral(vID) for vID in avatar_getter.getArena().vehicles))
            arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
            if arena is not None:
                arena.onPositionsUpdated += self.__updatePositions
            eqCtrl = self.__sessionProvider.shared.equipments
            if eqCtrl is not None:
                eqCtrl.onEquipmentAdded += self.__onEquipmentAdded
                eqCtrl.onEquipmentReset += self.__onEquipmentReset
                eqCtrl.onEquipmentsCleared += self.__onEquipmentsCleared
            if BattleReplay.g_replayCtrl.isPlaying:
                g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
                g_replayEvents.onTimeWarpFinish += self.__onReplayTimeWarpFinished
            self.__capturedBases.clear()
            return

    def getUI(self):
        return self.__ui

    def stopControl(self):
        self.__eManager.clear()
        self.__eManager = None
        if self.__overtimeCB:
            BigWorld.cancelCallback(self.__overtimeCB)
            self.__overtimeCB = None
            self.__overTimeEnd = None
        ctrl = self.__sessionProvider.dynamic.gameNotifications
        if ctrl:
            ctrl.onGameNotificationRecieved -= self.__onGameNotificationRecieved
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBasePointsUpdate -= self.__onSectorBaseActiveStateChanged
            sectorBaseComp.onSectorBasePointsUpdate -= self.__onSectorBasePointsUpdate
        playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
        if playerDataComp is not None:
            playerDataComp.onPlayerPhysicalLaneUpdated -= self.__onPlayerPhysicalLaneUpdated
            playerDataComp.onPlayerRankUpdated -= self.__onPlayerRankUpdated
            playerDataComp.onVehicleRanksUpdated -= self.__onVehicleRanksUpdated
        destructibleEntityComp = getattr(componentSystem, 'destructibleEntityComponent', None)
        if destructibleEntityComp is not None:
            destructibleEntityComp.onDestructibleEntityHealthChanged -= self.__onDestructibleEntityHealthChanged
            destructibleEntityComp.onDestructibleEntityHealthChanged -= self.__onDestructibleEntityIsActiveChanged
        sectorComp = getattr(componentSystem, 'sectorComponent', None)
        if sectorComp is not None:
            sectorComp.onWaypointsForPlayerActivated -= self.__onWaypointsForPlayerActivated
            sectorComp.onPlayerSectorGroupChanged -= self.__onPlayerSectorGroupChanged
            sectorComp.onSectorTransitionTimeChanged -= self.__onSectorTransitionTimeChanged
        component = getattr(componentSystem, 'overtimeComponent', None)
        if component is not None:
            component.onOvertimeStart -= self.__onOvertimeStart
            component.onOvertimeOver -= self.__onOvertimeOver
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarpStart
            g_replayEvents.onTimeWarpFinish -= self.__onReplayTimeWarpFinished
        if self.__nearestObjective != -1:
            arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
            if arena is not None:
                arena.onPositionsUpdated -= self.__updatePositions
        eqCtrl = self.__sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentAdded -= self.__onEquipmentAdded
            eqCtrl.onEquipmentReset -= self.__onEquipmentReset
            eqCtrl.onEquipmentsCleared -= self.__onEquipmentsCleared
        self.__sessionProvider = None
        self._notificationTypeToMissionTriggerArgs.clear()
        return

    def getCurrentMission(self):
        return self.__currentMission

    def getNearestObjectiveData(self):
        return (self.__nearestObjective, self.__nearestObjectiveDistance)

    def __isAttacker(self):
        return avatar_getter.getPlayerTeam() == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER

    def __onReady(self):
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        sectorComp = getattr(componentSystem, 'sectorComponent', None)
        if sectorBaseComp is not None and sectorComp is not None:
            for sectorBase in sectorBaseComp.sectorBases:
                if sectorBase.isCaptured:
                    sector = sectorComp.getSectorById(sectorBase.sectorID)
                    if sector.state not in (SECTOR_STATE.TRANSITION, SECTOR_STATE.BOMBING) or self.__currentLane == sector.playerGroup and not self.__isInRetreatArea():
                        self.__retreatMissionResults[sector.groupID] = False

        else:
            LOG_ERROR('Expected SectorComponent and/or SectorBaseComponent not present!')
        if not self.__isWaitingForNotification():
            self.__invalidateMissionStatus()
        periodCtrl = self.__sessionProvider.shared.arenaPeriod
        for m, s in TIMER_WARNINGS:
            periodCtrl.addRemainingTimeNotification(m, s, self.__onSpecificTimeReached)

        return

    def __onGameNotificationRecieved(self, notificationType, data):
        if len(self.__activeMessages) > notificationType:
            self.__activeMessages[notificationType] -= 1
            verify(not any((count < 0 for count in self.__activeMessages)))
        missionTriggerArgs = self._notificationTypeToMissionTriggerArgs.get(notificationType, None)
        if missionTriggerArgs and not any((self.__activeMessages[notificationId] != 0 for notificationId in self._notificationTypeToMissionTriggerArgs)):
            self.__invalidateMissionStatus(force=missionTriggerArgs.forceMissionUpdate)
            if missionTriggerArgs.callback is not None:
                missionTriggerArgs.callback()
        if notificationType == EPIC_NOTIFICATION.HQ_BATTLE_START:
            self.onObjectiveBattleStarted()
        return

    def __onBeforeMissionInvalidation(self):
        if self.__currentMission.missionType == EPIC_CONSTS.PRIMARY_WAYPOINT_MISSION:
            vehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
            vehicleIsAlive = vehicle is not None and vehicle.isStarted and vehicle.isAlive()
            if vehicleIsAlive and self.__activeMissionData['lane'] == self.__currentLane:
                if not self.__isInRetreatArea() and self.__retreatMissionResults.get(self.__activeMissionData['sectorGroup'], None) is None:
                    self.__retreatMissionResults[self.__activeMissionData['sectorGroup']] = True
                    LOG_DEBUG('[MissionsCtrl] Retreat Successful!')
                    self.__sendNotification(GAME_MESSAGES_CONSTS.RETREAT_SUCCESSFUL)
            else:
                self.__retreatMissionResults[self.__activeMissionData['sectorGroup']] = False
        return

    def __onSectorBasePointsUpdate(self, baseId, isPlayerTeam, points, capturingStopped, invadersCount, expectedCaptureTime):
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is None:
            LOG_ERROR('Expected SectorBaseComponent not present!')
            return
        else:
            sectorComp = getattr(componentSystem, 'sectorComponent', None)
            if sectorComp is None:
                LOG_ERROR('Expected SectorComponent not present!')
                return
            baseLane = sectorBaseComp.getSectorForSectorBase(baseId).playerGroup
            baseLaneIdx = baseLane - 1
            sectorIdToCapture = sectorComp.playerGroups[baseLane].sectors[sectorBaseComp.getNumCapturedBasesByLane(baseLane) + 1]
            validBase = sectorBaseComp.getBaseBySectorId(sectorIdToCapture)
            onPlayerLane = baseLaneIdx == self.__currentLane - 1
            time = BigWorld.serverTime()
            if validBase and baseId == validBase.baseID and points and baseId not in self.__capturedBases:
                if self.__isLaneContested[baseLaneIdx]:
                    endTime = self.__contestedEndTime[baseLaneIdx]
                    if endTime < time:
                        self.__isLaneContested[baseLaneIdx] = False
                    else:
                        self.__contestedEndTime[baseLaneIdx] = time + CONTESTED_DEBOUNCE_PERIOD
                elif points >= CONTESTED_CAPTURE_POINTS_THRESHOLD:
                    self.__contestedEndTime[baseLaneIdx] = time + CONTESTED_DEBOUNCE_PERIOD
                    self.__isLaneContested[baseLaneIdx] = True
                    if not onPlayerLane:
                        self.__showBaseContestedMessage(points, baseId)
            return

    def __showBaseContestedMessage(self, points, baseId):
        self.__sendIngameMessage(self.__makeMessageData(GAME_MESSAGES_CONSTS.BASE_CONTESTED_POSITIVE if self.__isAttacker() else GAME_MESSAGES_CONSTS.BASE_CONTESTED, {'baseID': baseId,
         'title': EPIC_BATTLE.BASE_CONTESTED_ATK if self.__isAttacker() else EPIC_BATTLE.BASE_CONTESTED_DEF,
         'progress': points}))

    def __onPlayerPhysicalLaneUpdated(self, laneID):
        if not self.__ready:
            self.__ready = True
            self.__currentLane = laneID
            self.__onReady()
        invalidateMission = False
        if laneID != self.__currentLane:
            self.__currentLane = laneID
            invalidateMission = True
        if not invalidateMission:
            componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
            playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
            if playerDataComp is None:
                LOG_ERROR('Expected PlayerDataComponent not present!')
                return
            invalidateMission = playerDataComp.getPlayerInHQSector() != self.__activeMissionData['isInHQSector']
        if invalidateMission and not self.__isWaitingForNotification():
            self.__invalidateMissionStatus()
        return

    def __invalidateMissionStatus(self, force=False):
        self.__onBeforeMissionInvalidation()
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is None:
            LOG_ERROR('Expected SectorBaseComponent not present!')
            return
        else:
            destructibleEntityComp = getattr(componentSystem, 'destructibleEntityComponent', None)
            if destructibleEntityComp is None:
                LOG_ERROR('Expected DestructibleEntityComponent not present!')
                return
            sectorComp = getattr(componentSystem, 'sectorComponent', None)
            if sectorComp is None:
                LOG_ERROR('Expected SectorComponent not present!')
                return
            playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
            if destructibleEntityComp is None:
                LOG_ERROR('Expected PlayerDataComponent not present!')
                return
            laneID = self.__currentLane
            nonCapturedBases = sectorBaseComp.getNumNonCapturedBasesByLane(laneID)
            baseID = next(iter(sectorBaseComp.getCapturedSectorBaseIdsByLane(laneID)[-1:]), None)
            sectorGroupID = sectorBaseComp.getSectorForSectorBase(baseID).groupID if baseID else None
            hqActive = False
            destroyedHQs = 0
            hqs = destructibleEntityComp.destructibleEntities
            if hqs:
                hqActive = first(hqs.values()).isActive
                destroyedHQs = destructibleEntityComp.getNumDestroyedEntities()
                if destroyedHQs >= self.__numDestructiblesToDestroy:
                    return
            if nonCapturedBases == 0 and self.__isAttacker():
                if hqActive:
                    endTime = 0
                else:
                    criticalEndTimes = []
                    sector = sectorComp.getSectorById(playerDataComp.hqSectorID)
                    if sector is not None:
                        hqIdInPlayerGroup = sector.IDInPlayerGroup
                        for sector in sectorComp.sectors:
                            if sector.state == SECTOR_STATE.TRANSITION and sector.IDInPlayerGroup == hqIdInPlayerGroup - 1:
                                criticalEndTimes.append(sector.endOfTransitionPeriod)

                    endTime = min(criticalEndTimes) if criticalEndTimes else 0
            else:
                _, _, endTime = sectorComp.getActiveWaypointSectorGroupForPlayerGroup(self.__currentLane)
            if endTime - BigWorld.serverTime() > 0.5 and self.__currentEndTime != endTime:
                self.__currentEndTime = endTime
                self.onPlayerMissionTimerSet(self.__currentEndTime)
            isInHQSector = playerDataComp.getPlayerInHQSector()
            if self.__activeMissionData['lane'] == laneID and self.__activeMissionData['bases'] == nonCapturedBases and self.__activeMissionData['hqActive'] == hqActive and self.__activeMissionData['destroyedHQs'] == destroyedHQs and self.__activeMissionData['endTime'] == endTime and self.__activeMissionData['sectorGroup'] == sectorGroupID and self.__activeMissionData['isInHQSector'] == isInHQSector and not force:
                return
            self.__activeMissionData['lane'] = laneID
            self.__activeMissionData['bases'] = nonCapturedBases
            self.__activeMissionData['hqActive'] = hqActive
            destroyedHQUpdate = self.__activeMissionData['destroyedHQs'] != destroyedHQs
            self.__activeMissionData['destroyedHQs'] = destroyedHQs
            self.__activeMissionData['endTime'] = endTime
            self.__activeMissionData['sectorGroup'] = sectorGroupID
            self.__activeMissionData['isInHQSector'] = isInHQSector
            mission, additionalDescription = self.__generateMissionFromData()
            if mission.missionType == EPIC_CONSTS.PRIMARY_HQ_MISSION and self.__currentMission.missionType == EPIC_CONSTS.PRIMARY_HQ_MISSION and not destroyedHQUpdate and not force:
                return
            if mission.missionType != EPIC_CONSTS.PRIMARY_EMPTY_MISSION:
                self.__currentMission = mission
                self.onPlayerMissionUpdated(mission, additionalDescription)
            return

    def __generateMissionFromData(self):
        mission = PlayerMission()
        additionalDescription = None
        hqActive = self.__activeMissionData['hqActive']
        isInHQSector = self.__activeMissionData['isInHQSector']
        sectorGroup = self.__activeMissionData['sectorGroup']
        nonCapturedBases = self.__activeMissionData['bases']
        endTime = self.__activeMissionData['endTime']
        vehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
        vehicleIsAlive = vehicle is not None and vehicle.isStarted and vehicle.isAlive()
        if vehicleIsAlive and not self.__isAttacker() and endTime - BigWorld.serverTime() > 0 and self.__isInRetreatArea() and self.__retreatMissionResults.get(sectorGroup, None) is None:
            mission.missionType = EPIC_CONSTS.PRIMARY_WAYPOINT_MISSION
            mission.missionText = EPIC_BATTLE.RETREAT_MISSION_TXT
            mission.subText = EPIC_BATTLE.MISSION_ZONE_CLOSING_DEF
        elif isInHQSector and hqActive or nonCapturedBases == 0:
            componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
            destructibleEntityComp = getattr(componentSystem, 'destructibleEntityComponent', None)
            if destructibleEntityComp is None:
                LOG_ERROR('Expected DestructibleEntityComponent not present!')
                return
            mission.missionType = EPIC_CONSTS.PRIMARY_HQ_MISSION
            destroyed = destructibleEntityComp.getNumDestroyedEntities()
            toDestroy = self.__numDestructiblesToDestroy
            if endTime > 0 and not hqActive:
                mission.subText = EPIC_BATTLE.MISSION_ZONE_CLOSING_ATK if self.__isAttacker() else EPIC_BATTLE.MISSION_ZONE_CLOSING_DEF
            else:
                mission.subText = EPIC_BATTLE.MISSIONS_PRIMARY_ATK_HQ_SUB_TITLE if self.__isAttacker() else EPIC_BATTLE.MISSIONS_PRIMARY_DEF_HQ_SUB_TITLE
                additionalDescription = makeHtmlString(path='html_templates:battle/epicBattle/additionalHqMissionInfo', key='attacker' if self.__isAttacker() else 'defender', ctx={'destroyed': destroyed,
                 'toDestroy': toDestroy})
            mission.missionText = EPIC_BATTLE.MISSIONS_PRIMARY_ATK_HQ if self.__isAttacker() else EPIC_BATTLE.MISSIONS_PRIMARY_DEF_HQ
        else:
            if endTime > 0:
                mission.subText = EPIC_BATTLE.MISSION_ZONE_CLOSING_ATK if self.__isAttacker() else EPIC_BATTLE.MISSION_ZONE_CLOSING_DEF
            mission.missionType = EPIC_CONSTS.PRIMARY_BASE_MISSION
            mission.missionText = EPIC_BATTLE.MISSIONS_PRIMARY_ATK_BASE if self.__isAttacker() else EPIC_BATTLE.MISSIONS_PRIMARY_DEF_BASE
            componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
            sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
            if sectorBaseComp is not None:
                mission.id = next(iter(sectorBaseComp.getNonCapturedSectorBaseIdsByLane(self.__currentLane)), None)
            else:
                LOG_ERROR('Expected SectorBaseComponent not present!')
        return (mission, additionalDescription)

    def __onWaypointsForPlayerActivated(self, waypointSectorTimeTuple):
        _, _, currentEndTime = waypointSectorTimeTuple
        if currentEndTime == 0:
            self.__currentEndTime = currentEndTime
            self.onPlayerMissionTimerSet(self.__currentEndTime)
        if self.__isAttacker() and self.__ready:
            componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
            sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
            if sectorBaseComp is not None:
                nonCapturedBases = sectorBaseComp.getNumNonCapturedBasesByLane(self.__currentLane)
                if nonCapturedBases == 0:
                    self.__sendNotification(GAME_MESSAGES_CONSTS.DESTROY_OBJECTIVE)
            else:
                LOG_ERROR('Expected SectorBaseComponent not present!')
                return
        return

    def __onPlayerSectorGroupChanged(self, *_):
        if self.__currentMission.missionType == EPIC_CONSTS.PRIMARY_WAYPOINT_MISSION and self.__activeMissionData['lane'] == self.__currentLane and not self.__isInRetreatArea():
            self.__nextObjectiveMessage(self.__isAttacker())

    def __onSectorTransitionTimeChanged(self, sectorId, oldTime, newTime):
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        sectorComp = getattr(componentSystem, 'sectorComponent', None)
        if sectorComp is None:
            LOG_ERROR('Expected SectorComponent not present!')
            return
        else:
            if self.__currentMission.missionType == EPIC_CONSTS.PRIMARY_WAYPOINT_MISSION:
                baseSector = sectorComp.getSectorById(sectorId)
                if baseSector.playerGroup == self.__currentLane and self.__isInRetreatArea():
                    self.__nextObjectiveMessage(self.__isAttacker())
            return

    def onSectorBaseCaptured(self, baseId, vehiclesUnlocked=False):
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is None:
            LOG_ERROR('Expected SectorBaseComponent not present!')
            return
        else:
            sectorComp = getattr(componentSystem, 'sectorComponent', None)
            if sectorComp is None:
                LOG_ERROR('Expected SectorComponent not present!')
                return
            epicPlayerDataComp = getattr(componentSystem, 'playerDataComponent', None)
            if epicPlayerDataComp is None:
                LOG_ERROR('Expected EpicPlayerDataComponent not present!')
                return
            self.__capturedBases.add(baseId)
            sectorBase = sectorBaseComp.getSectorBaseById(baseId)
            baseSectorId = sectorBase.sectorID
            sector = sectorComp.getSectorById(baseSectorId)
            baseLane = sector.playerGroup
            onPlayerLane = baseLane == self.__currentLane
            capturedBasesInCompanentSystem = sectorBaseComp.getCapturedBaseIDs()
            self.__capturedBases.update(capturedBasesInCompanentSystem)
            seconds = epicPlayerDataComp.getGameTimeToAddPerCapture(sector.IDInPlayerGroup)
            if len(self.__capturedBases) == len(sectorBaseComp.sectorBases):
                seconds += epicPlayerDataComp.getGameTimeToAddWhenAllCaptured()
            minutes = int(seconds / 60)
            seconds -= minutes * 60
            self.__sendIngameMessage(self.__makeMessageData(GAME_MESSAGES_CONSTS.BASE_CAPTURED_POSITIVE if self.__isAttacker() else GAME_MESSAGES_CONSTS.BASE_CAPTURED, {'baseID': baseId,
             'title': EPIC_BATTLE.ZONE_CAPTURED_TEXT if self.__isAttacker() else EPIC_BATTLE.ZONE_LOST_TEXT,
             'timerText': backport.text(R.strings.epic_battle.zone.time_added(), minutes=':'.join(('{:02d}'.format(int(minutes)), '{:02d}'.format(int(seconds))))),
             'descriptionText': backport.text(R.strings.epic_battle.missions.unlockTankLevel()) if vehiclesUnlocked else ''}))
            if onPlayerLane:
                if self.__isAttacker():
                    self.__nextObjectiveMessage(self.__isAttacker())
                elif sectorComp.getSectorById(sectorComp.currentPlayerSectorId).IDInPlayerGroup <= sector.IDInPlayerGroup:
                    self.__sendIngameMessage(self.__makeMessageData(GAME_MESSAGES_CONSTS.RETREAT, {'title': EPIC_BATTLE.ZONE_LEAVE_ZONE}))
                else:
                    self.__nextObjectiveMessage(self.__isAttacker())
            self.__contestedEndTime[baseLane - 1] = 0
            self.__isLaneContested[baseLane - 1] = False
            return

    def __nextObjectiveMessage(self, isAttacker):
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is None:
            LOG_ERROR('Expected SectorBaseComponent not present!')
            return
        else:
            nonCapturedBases = sectorBaseComp.getNumNonCapturedBasesByLane(self.__currentLane)
            if nonCapturedBases == 0:
                msgType = GAME_MESSAGES_CONSTS.DESTROY_OBJECTIVE if isAttacker else GAME_MESSAGES_CONSTS.DEFEND_OBJECTIVE
            else:
                msgType = GAME_MESSAGES_CONSTS.CAPTURE_BASE if isAttacker else GAME_MESSAGES_CONSTS.DEFEND_BASE
            ctrl = self.sessionProvider.dynamic.gameNotifications
            if ctrl is not None:
                notificationId = ctrl.translateMsgId(msgType)
                if notificationId != -1 and self.__activeMessages[notificationId] != 0:
                    return
            self.__sendNotification(msgType)
            return

    def __onSectorBaseActiveStateChanged(self, baseId, isActive):
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is None:
            LOG_ERROR('Expected SectorBaseComponent not present!')
            return
        else:
            baseSector = sectorBaseComp.getSectorForSectorBase(baseId)
            if not isActive or baseSector.IDInPlayerGroup > 2:
                return
            onPlayerLane = baseSector.playerGroup == self.__currentLane
            if onPlayerLane:
                self.__sendNotification(GAME_MESSAGES_CONSTS.CAPTURE_BASE if self.__isAttacker() else GAME_MESSAGES_CONSTS.DEFEND_BASE)
            return

    def __onDestructibleEntityIsActiveChanged(self, destructibleEntityID, isActive):
        if not isActive or self.__objMsgSent:
            return
        self.__sendNotification(GAME_MESSAGES_CONSTS.HQ_BATTLE_STARTED_POSITIVE if self.__isAttacker() else GAME_MESSAGES_CONSTS.HQ_BATTLE_STARTED)
        self.__objMsgSent = True

    def __onDestructibleEntityHealthChanged(self, objID, newHealth, maxHealth, attackerID, attackReason, hitFlags):
        if newHealth == 0:
            msgType = GAME_MESSAGES_CONSTS.OBJECTIVE_DESTROYED_POSITIVE if self.__isAttacker() else GAME_MESSAGES_CONSTS.OBJECTIVE_DESTROYED
            msgData = {'hqID': objID,
             'title': EPIC_BATTLE.ZONE_DESTROYED_TEXT if self.__isAttacker() else EPIC_BATTLE.ZONE_LOST_TEXT}
        elif self.__lastTimeHQDamaged[objID] + CONTESTED_DEBOUNCE_PERIOD <= BigWorld.serverTime():
            self.__lastTimeHQDamaged[objID] = BigWorld.serverTime()
            msgType = GAME_MESSAGES_CONSTS.OBJECTIVE_UNDER_ATTACK_POSITIVE if self.__isAttacker() else GAME_MESSAGES_CONSTS.OBJECTIVE_UNDER_ATTACK
            msgData = {'hqID': objID,
             'title': EPIC_BATTLE.HQ_UNDER_ATTACK_ATK if self.__isAttacker() else EPIC_BATTLE.HQ_UNDER_ATTACK_DEF,
             'destroyedProgress': newHealth / maxHealth}
        else:
            return
        self.__sendIngameMessage(self.__makeMessageData(msgType, msgData))

    def __updatePositions(self):
        if self.__currentMission.missionType == EPIC_CONSTS.PRIMARY_HQ_MISSION or self.__activeMissionData['hqActive']:
            self.__setNearestObjective()

    def __setNearestObjective(self):
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        destructibleEntityComp = getattr(componentSystem, 'destructibleEntityComponent', None)
        if destructibleEntityComp is None:
            LOG_ERROR('Expected DestructibleEntityComponent not present!')
            return
        else:
            position = BigWorld.player().position
            objID, objDistance = destructibleEntityComp.getNearestDestructibleEntityID(position)
            if objID is None:
                return
            self.__nearestObjectiveDistance = objDistance
            if objID == self.__nearestObjective:
                return
            self.__nearestObjective = objID
            self.onNearestObjectiveChanged(objID, objDistance)
            return

    def __onSpecificTimeReached(self, minutes, seconds):
        self.__sendIngameMessage(self.__makeMessageData(GAME_MESSAGES_CONSTS.TIME_REMAINING if self.__isAttacker() else GAME_MESSAGES_CONSTS.TIME_REMAINING_POSITIVE, {'title': i18n.makeString(EPIC_BATTLE.ZONE_TIME_LEFT, minutes=minutes)}))

    def __onPlayerRankUpdated(self, rank):
        subTitleText = ''
        updateType, updateInfo = self.__getRankUpdateData(rank)
        eqCtrl = self.__sessionProvider.shared.equipments
        if updateType is not None and eqCtrl is not None and eqCtrl.hasEquipment(updateInfo):
            equipmentName = eqCtrl.getEquipment(updateInfo).getDescriptor().userString
            if updateType == IN_BATTLE_RESERVE_EVENTS.SLOT_EVENT_ACTIONS.UNLOCKED:
                subTitleText = backport.text(R.strings.epic_battle.rank.recerveUnlocked(), reserveName=equipmentName)
            elif updateType == IN_BATTLE_RESERVE_EVENTS.SLOT_EVENT_ACTIONS.UPGRADED:
                subTitleText = backport.text(R.strings.epic_battle.rank.reserveUpgraded(), reserveName=equipmentName)
        self.__sendIngameMessage(self.__makeMessageData(GAME_MESSAGES_CONSTS.RANK_UP, {'rank': rank + 1,
         'title': RANK_TO_TRANSLATION[rank + 1],
         'subTitle': subTitleText}))
        if rank == PLAYER_RANK.GENERAL:
            self.__generalRankMsgSent = True
        return

    def __onVehicleRanksUpdated(self, teamRanks):
        if self.__generalRankMsgSent:
            return
        if avatar_getter.getPlayerTeam() in teamRanks:
            playerTeamRanks = teamRanks[avatar_getter.getPlayerTeam()]
            for vehID, rank in playerTeamRanks.iteritems():
                if rank == PLAYER_RANK.GENERAL:
                    self.__sendIngameMessage(self.__makeMessageData(GAME_MESSAGES_CONSTS.GENERAL_RANK_REACHED, {'title': self.__sessionProvider.getCtx().getPlayerFullName(vID=vehID, showVehShortName=False, showClan=True, showRegion=False),
                     'subTitle': i18n.makeString(EPIC_BATTLE.RANK_PROMOTION, rank=i18n.makeString(RANK_TO_TRANSLATION[rank]))}))
                    self.__generalRankMsgSent = True

    def __onOvertimeStart(self, endTime):
        self.__overTimeEnd = endTime
        timeLeft = int(endTime - BigWorld.serverTime())
        self.__sendIngameMessage(self.__makeMessageData(GAME_MESSAGES_CONSTS.OVERTIME, {'timestamp': timeLeft,
         'title': EPIC_BATTLE.OVERTIME_LABEL}))
        self.__overtimeCB = BigWorld.callback(1, self.__overtimeTick)

    def __onOvertimeOver(self):
        if self.__overtimeCB:
            BigWorld.cancelCallback(self.__overtimeCB)
            self.__overtimeCB = None
            self.__overTimeEnd = None
        return

    def __overtimeTick(self):
        timeLeft = int(self.__overTimeEnd - BigWorld.serverTime())
        if timeLeft in OVERTIME_DURATION_WARNINGS:
            self.__sendIngameMessage(self.__makeMessageData(GAME_MESSAGES_CONSTS.OVERTIME, {'timestamp': timeLeft,
             'title': EPIC_BATTLE.OVERTIME_LABEL}))
        if timeLeft > 0:
            self.__overtimeCB = BigWorld.callback(1, self.__overtimeTick)
        else:
            self.__overtimeCB = None
        return

    def __makeMessageData(self, msgType, data):
        return PlayerMessageData(messageType=str(msgType), length=MSG_ID_TO_DURATION[msgType], priority=MSG_ID_TO_PRIORITY[msgType], msgData=data)

    def __sendNotification(self, messageType):
        ctrl = self.sessionProvider.dynamic.gameNotifications
        if ctrl is not None:
            notificationId = ctrl.translateMsgId(messageType)
            if notificationId != -1:
                self.__activeMessages[notificationId] += 1
            ctrl.notify(messageType, {})
        return

    def __sendIngameMessage(self, msgData):
        ctrl = self.sessionProvider.dynamic.gameNotifications
        if ctrl is not None:
            notificationId = ctrl.translateMsgId(msgData.messageType)
            if notificationId != -1:
                self.__activeMessages[notificationId] += 1
            if not BattleReplay.g_replayCtrl.isTimeWarpInProgress and notificationId in self._notificationTypeToMissionTriggerArgs:
                self.__resetMission()
        self.onIngameMessageReady(msgData)
        return

    def __isWaitingForNotification(self):
        return any((self.__activeMessages[notificationId] > 0 for notificationId in self._notificationTypeToMissionTriggerArgs))

    def __onReplayTimeWarpStart(self):
        self.__resetMission()

    def __onReplayTimeWarpFinished(self):
        self.__invalidateMissionStatus(force=True)

    def __resetMission(self):
        self.onPlayerMissionReset()

    def __isInRetreatArea(self):
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is None:
            LOG_ERROR('Expected SectorBaseComponent not present!')
            return
        else:
            baseID = next(iter(sectorBaseComp.getCapturedSectorBaseIdsByLane(self.__currentLane)[-1:]), None)
            if baseID:
                sectorComp = getattr(componentSystem, 'sectorComponent', None)
                if sectorComp is None:
                    LOG_ERROR('Expected SectorComponent not present!')
                    return
                lastCapturedBaseSector = sectorBaseComp.getSectorForSectorBase(baseID)
                currentIDInPlayerGroup = sectorComp.getSectorById(sectorComp.currentPlayerSectorId).IDInPlayerGroup
                return currentIDInPlayerGroup <= lastCapturedBaseSector.IDInPlayerGroup
            return False

    def __onEquipmentAdded(self, intCD, item):
        if item and item.isAvatar():
            self.__orderBattleAbilities.append(intCD)

    def __onEquipmentReset(self, oldIntCD, newIntCD, _):
        if oldIntCD in self.__orderBattleAbilities:
            self.__orderBattleAbilities[self.__orderBattleAbilities.index(oldIntCD)] = newIntCD

    def __onEquipmentsCleared(self):
        self.__orderBattleAbilities = []

    def __getRankUpdateData(self, newRank):
        if not self.__orderBattleAbilities:
            return (None, None)
        else:
            arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
            if arena is None:
                return (None, None)
            inBattleReserves = arena.settings.get('epic_config', {}).get('epicMetaGame', {}).get('inBattleReservesByRank')
            if not inBattleReserves:
                return (None, None)
            if newRank not in range(0, len(inBattleReserves['events'])):
                return (None, None)
            _, updateEvent = inBattleReserves['events'][newRank]
            for updateType, updateSet in updateEvent.iteritems():
                for updateIdx in updateSet:
                    if 0 <= updateIdx < len(self.__orderBattleAbilities):
                        return (updateType, self.__orderBattleAbilities[updateIdx])

            return (None, None)
