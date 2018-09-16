# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/base/ArenaFootballMechanics.py
import cPickle
import zlib
import BigWorld
import Math
import database as db
from Arena import _ARENA_STATE
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from constants import ARENA_PERIOD, ARENA_UPDATE, FINISH_REASON, getTimeOnArena, getArenaStartTime
from debug_utils import LOG_DEBUG_DEV
from server_constants import KAFKA_LOG_OPERATION_TYPE, PERIPHERY, HIST_LOG_CONFIG
from wotdecorators import noexcept
BALL_ENTITY_TYPE = 'Ball'
GOAL_ENTITY_TYPE = 'Goal'
RED_GOAL_POS = 'redGoalPosition'
BLUE_GOAL_POS = 'blueGoalPosition'
FOOTBALL_DELAY = 1.0
FOOTBALL_OVERTIME_CONTROL_POINTS = 100
FOOTBALL_OVERTIME_DELTA = 1
BALL_DROP_TIMER_COUNT = 4
AFTER_GOAL_TIMER_COUNT = 6
ASSIST_TIME_LIMIT = 5
FOOTBALL_OVERTIME_PREP = 2
FOOTBALL_DELAY_FADE_GOAL = 3500
FOOTBALL_DELAY_FADE_WIN = 2000
FOOTBALL_DELAY_FADE_OT = 0
FOOTBALL_GOALS_TO_WIN = 3
OWN_GOAL_DIRECTION_DELTA = 0.05
SPEED_REQUIRED_FOR_OWN_GOAL = 3.0

class ArenaFootballMechanics(BigWorld.ScriptComponent):

    def __init__(self):
        BigWorld.Base.__init__(self)
        (LOG_DEBUG_DEV('[ArenaFootballMechanics] - __init__'), self.entity.id)
        if not self.isFootballEvent():
            return
        self.__makeProperties()
        self.__registerForArenaEvents()
        self.entity._Arena__p['winnerProcessor'] = self

    def onRestore(self):
        if not self.isFootballEvent():
            return
        self.__makeProperties()
        self.__cleanup()

    def onDestroy(self):
        if not self.isFootballEvent():
            return
        self.__cleanup()

    @noexcept
    def reuse(self, gameplayID, guiType, bonusType, extraData, roundLength, creator, roster, voipChannels, fogOfWar, vehicleLockMode, vehicleLockTimeFactors, webID, webEmitterID, observeBothTeams):
        if not self.isFootballEvent():
            return
        self.__resetProperties()
        self.__registerForArenaEvents()
        self.entity._Arena__p['winnerProcessor'] = self

    def __cleanup(self):
        self.__unregisterForArenaEvents()
        self.__resetTimers()
        self.__goalEntries.clear()
        self.__destroyBall()
        self.__destroyGoals()
        self.__destroyCage()
        self.__initialized = False

    def __isInitialized(self):
        return hasattr(self, '_ArenaFootballMechanics__initialized') and self.__initialized

    def __resetTimers(self):
        fp = self.__fp
        fp['ballPositionTimerID'] = self.__cancelTimer(fp.get('ballPositionTimerID', None))
        fp['prepareOvertimeDelay'] = self.__cancelTimer(fp.get('prepareOvertimeDelay', None))
        fp['startFootballOvertimeTimerID'] = self.__cancelTimer(fp.get('startFootballOvertimeTimerID', None))
        fp['checkBallIdleTimerID'] = self.__cancelTimer(fp.get('checkBallIdleTimerID', None))
        fp['afterGoalTimerID'] = self.__cancelTimer(fp.get('afterGoalTimerID', None))
        fp['ballDropTimerID'] = self.__cancelTimer(fp.get('ballDropTimerID', None))
        return

    def __makeProperties(self):
        self.__initialized = True
        self.__ballDropping = False
        self.__ball = None
        self.__goals = [None, None]
        self.__cage = None
        self.__arenaType = self.entity.arenaType
        self.__settings = self.entity.arenaType.football
        self.__pointsToWin = 3
        self.__isPreparingOT = False
        self.__inOT = False
        self.__winningTeam = 0
        self.__points = 0
        self.__isGoal = False
        self.curTime = 0
        self.__goalEntries = dict()
        self.__fp = {'teamScore': [0, 0],
         'scoreInfo': [0, 0],
         'overtimePoints': [None, 0, 0],
         'ballPossession': [None, 0, 0],
         'ballSides': [0, 0],
         'redGoalMatrix': Math.Matrix(),
         'blueGoalMatrix': Math.Matrix(),
         'lastAttackerID': 0,
         'assistID': 0,
         'ownGoalVehID': 0,
         'potentialOwnGoal': False,
         'ballPositionTimerID': None,
         'startFootballOvertimeTimerID': None,
         'checkBallIdleTimerID': None,
         'afterGoalTimerID': None,
         'ballDropTimerID': None,
         'prepareOvertimeDelay': None}
        return

    def __resetProperties(self):
        fp = self.__fp
        redGoalMatrix = fp['redGoalMatrix']
        blueGoalMatrix = fp['blueGoalMatrix']
        self.__makeProperties()
        fp = self.__fp
        fp['redGoalMatrix'] = redGoalMatrix
        fp['blueGoalMatrix'] = blueGoalMatrix

    def __onArenaCleanup(self):
        if self.isFootballEvent():
            self.__cleanup()

    @property
    def ball(self):
        return self.__ball

    @property
    def redGoal(self):
        return self.__goals[0]

    @property
    def blueGoal(self):
        return self.__goals[1]

    @property
    def isOT(self):
        return self.__inOT

    @property
    def footballSettings(self):
        return self.__settings

    def __getBallSpawnPosition(self):
        return self.__settings.ballSpawnPoint

    def __setBallSpawnPosition(self, pos):
        self.__settings.ballSpawnPoint = pos

    @property
    def score(self):
        return self.__fp['teamScore']

    @property
    def scoreInfo(self):
        return self.__fp['scoreInfo']

    def spawnFootballEntities(self):
        if not self.isFootballEvent():
            return
        else:
            for pos, prefType, visibilityMask, bonusMask, isLowLevel in self.entity.getProperty('allSpawnPoints').get((3, 1), []):
                self.spawnBall(pos[0])
                break

            self.spawnGoals()
            if self.__cage is None:
                self.__cage = BigWorld.createBaseLocally('Cage', {'position': (0, 0, 0),
                 'arenaTypeID': self.entity.typeID})
                self.__cage.createCellNearHere(self.entity.cell)
            return

    def spawnBall(self, ballpos):
        if not self.isFootballEvent():
            return
        else:
            self.__setBallSpawnPosition(ballpos)
            if self.__ball is None:
                self.__ball = BigWorld.createBaseLocally(BALL_ENTITY_TYPE, {'position': self.__getBallSpawnPosition(),
                 'arena': self.entity,
                 'arenaTypeID': self.entity.typeID,
                 'arenaUniqueID': self.entity.bp['uniqueID']})
                self.__ball.createCellNearHere(self.entity.cell)
                for vehicle in self.entity.bp['vehicles'].values():
                    vehicle.cell.VehicleFootball.updateBallID(self.__ball.id)

                self.entity.cell.ArenaFootballMechanics.updateBallID(self.__ball.id)
            self.__resetState()
            self.offsetBall()
            return

    def addGoal(self, team, matrix):
        if not self.isFootballEvent():
            return
        if team == 1:
            self.__setGoalSpawnPositions(RED_GOAL_POS, matrix)
        elif team == 2:
            self.__setGoalSpawnPositions(BLUE_GOAL_POS, matrix)

    def createEntity(self, section, matrix):
        if not self.isFootballEvent():
            return
        type = section.readString('type')
        if type == 'Goal':
            self.addGoal(section['properties'].readInt('team', 0), matrix)

    def spawnGoals(self):
        if not self.isFootballEvent():
            return
        else:
            redGoalPosition = self.__getGoalSpawnPositions(RED_GOAL_POS)
            blueGoalPosition = self.__getGoalSpawnPositions(BLUE_GOAL_POS)
            if self.__goals[0] is None:
                self.__goals[0] = BigWorld.createBaseLocally('Goal', {'position': redGoalPosition,
                 'team': 1,
                 'arena': self.entity})
                self.__goals[0].createCellNearHere(self.entity.cell)
            if self.__goals[1] is None:
                self.__goals[1] = BigWorld.createBaseLocally('Goal', {'position': blueGoalPosition,
                 'team': 2,
                 'arena': self.entity})
                self.__goals[1].createCellNearHere(self.entity.cell)
            self.redGoal.cell.setTeam(1)
            self.blueGoal.cell.setTeam(2)
            return

    def teleportBallToCenter(self):
        if not self.isFootballEvent():
            return
        self.__ball.cell.teleportTo(Math.Vector3(self.__getBallSpawnPosition()))
        self.__fp['ballSides'] = [0, 0]

    def offsetBall(self):
        if not self.isFootballEvent():
            return
        self.__ball.cell.teleportTo(self.__getBallSpawnPosition())

    def onFootballGoal(self, scoringTeamID):
        if not self.isFootballEvent():
            return
        elif self.entity.state != _ARENA_STATE.RUNNING or self.__isGoal:
            return
        else:
            arena = self.entity
            currentPeriod = arena.getCurrentPeriod()
            if currentPeriod != ARENA_PERIOD.BATTLE:
                return
            elif BigWorld.time() >= self.entity.getProperty('periodEndTime'):
                return
            self.__isGoal = True
            ownGoalVehPlayerInfo = self.entity._Arena__p['vehPlayersInfo'].get(self.__fp['ownGoalVehID'], None)
            if not ownGoalVehPlayerInfo:
                LOG_DEBUG_DEV('[onFootballGoal] - ownGoalVehPlayerInfo not set!')
                ownGoalTeamID = 3
            else:
                ownGoalTeamID = ownGoalVehPlayerInfo['team']
            attackerPlayerInfo = self.entity._Arena__p['vehPlayersInfo'].get(self.__fp['lastAttackerID'], None)
            if not attackerPlayerInfo:
                LOG_DEBUG_DEV('[onFootballGoal] - attackerPlayerInfo not set!')
                attackerTeamID = None
            else:
                attackerTeamID = attackerPlayerInfo['team']
            selfGoal = False
            if self.__fp['potentialOwnGoal']:
                selfGoal = scoringTeamID != ownGoalTeamID
            elif attackerTeamID != 3:
                selfGoal = scoringTeamID != attackerTeamID
            self.__fp['teamScore'][scoringTeamID - 1] += 1
            self.__fp['scoreInfo'][0] = selfGoal
            self.__fp['scoreInfo'][1] = scoringTeamID
            self.broadcastStatUpdate()
            self.entity.postponeWinnerCheck()
            if self.score[scoringTeamID - 1] == self.__pointsToWin or self.__inOT:
                LOG_DEBUG_DEV('[ArenaFootballMechanics]::onFootballGoal set wonTeam to ' + str(scoringTeamID))
            else:
                self.afterGoalScored()
            self.__ball.cell.waitAndExplodeBall()
            return

    def afterGoalScored(self):
        if not self.isFootballEvent():
            return
        self.__fp['lastAttackerID'] = 0
        self.__fp['assistID'] = 0
        self.__fp['ownGoalVehID'] = 0
        data = {'canFadeOut': self.__isGoal,
         'delay': FOOTBALL_DELAY_FADE_GOAL}
        for av in self.entity.avatars:
            self.__notifyFadeOutOverlay(av, data)

        self.__fp['afterGoalTimerID'] = BigWorld.addTimer(self.__onBallDropTimer, AFTER_GOAL_TIMER_COUNT)
        self.curTime = self.entity.getProperty('periodEndTime') - BigWorld.time()

    def getWinner(self, arena, isArenaRunning, timeoutTime):
        if not self.isFootballEvent() or not self.__isInitialized():
            return (0, FINISH_REASON.FAILURE)
        else:
            result = None
            score = self.score
            if len(arena.bp['avatars']) == 0:
                result = (0, FINISH_REASON.TECHNICAL)
            elif self.isOT:
                if score[0] != score[1]:
                    result = (1 if score[0] > score[1] else 2, FINISH_REASON.EXTERMINATION)
                else:
                    points = self.__fp['overtimePoints']
                    if max(points) >= FOOTBALL_OVERTIME_CONTROL_POINTS or BigWorld.time() >= timeoutTime:
                        result = (1 if points[1] > points[2] else 2, FINISH_REASON.EXTERMINATION)
            elif BigWorld.time() >= timeoutTime and not self.__ballDropping:
                if score[0] != score[1]:
                    result = (1 if score[0] > score[1] else 2, FINISH_REASON.EXTERMINATION)
            elif max(score) >= FOOTBALL_GOALS_TO_WIN:
                result = (1 if score[0] == FOOTBALL_GOALS_TO_WIN else 2, FINISH_REASON.EXTERMINATION)
            if arena.state == _ARENA_STATE.FINISHING:
                if result is None:
                    result = (0, FINISH_REASON.FAILURE)
                self.__winningTeam = result[0]
            elif result is None and BigWorld.time() >= timeoutTime and not self.__isPreparingOT and not self.isOT:
                self.__startPreparingFootballOvertime()
            return result

    def pushIdleBall(self):
        if not self.isFootballEvent():
            return
        self.__ball.cell.pushIfIdle()

    def __onFinishArena(self):
        if not self.isFootballEvent() or not self.__isInitialized():
            return
        winnerData = {'__winningTeam': self.__winningTeam,
         'delay': FOOTBALL_DELAY_FADE_WIN}
        for av in self.entity.avatars:
            self.__notifyWinnerDeclared(av, winnerData)

        self.__inOT = False
        self.__resetTimers()

    def updateGameplayIDs(self, attackerID, assistID, bRammedBall, bSplash, attackerSpeed, attackerDirection):
        if not self.isFootballEvent() or self.entity.getCurrentPeriod() != ARENA_PERIOD.BATTLE:
            return
        else:
            fp = self.__fp
            vehPlayersInfo = self.entity.getProperty('vehPlayersInfo')
            attackerPlayerInfo = vehPlayersInfo.get(attackerID, None)
            if attackerPlayerInfo is None:
                return
            attackerTeam = attackerPlayerInfo['team']
            bSelfGoalSideOfField = attackerTeam == fp['ballSides'][0]
            if bRammedBall:
                if bSelfGoalSideOfField:
                    if fp['lastAttackerID'] == 0:
                        fp['potentialOwnGoal'] = False
                        fp['lastAttackerID'] = attackerID
                        fp['ownGoalVehID'] = attackerID
                        fp['assistID'] = assistID
                else:
                    fp['potentialOwnGoal'] = False
                    fp['lastAttackerID'] = attackerID
                    fp['ownGoalVehID'] = attackerID
                    fp['assistID'] = assistID
            elif bSplash:
                if bSelfGoalSideOfField:
                    if fp['lastAttackerID']:
                        if fp['lastAttackerID'] == attackerID:
                            return
                        lastAttackerPlayerInfo = vehPlayersInfo.get(fp['lastAttackerID'], None)
                        lastAttackerTeam = lastAttackerPlayerInfo['team']
                        if lastAttackerTeam == attackerTeam:
                            fp['potentialOwnGoal'] = True
                            fp['ownGoalVehID'] = attackerID
                            fp['lastAttackerID'] = attackerID
                            fp['assistID'] = assistID
                        else:
                            fp['potentialOwnGoal'] = False
                            fp['ownGoalVehID'] = 0
                    else:
                        fp['potentialOwnGoal'] = True
                        fp['ownGoalVehID'] = attackerID
                        fp['lastAttackerID'] = attackerID
                        fp['assistID'] = assistID
                else:
                    fp['potentialOwnGoal'] = True
                    fp['ownGoalVehID'] = attackerID
                    fp['lastAttackerID'] = attackerID
                    fp['assistID'] = assistID
            else:
                fp['potentialOwnGoal'] = True
                fp['ownGoalVehID'] = attackerID
                fp['lastAttackerID'] = attackerID
                fp['assistID'] = assistID
            return

    def broadcastFootballUpdate(self):
        if not self.isFootballEvent():
            return
        for av in self.entity.avatars:
            self.__sendFootballInfoTo(av)

    def broadcastStatUpdate(self):
        if not self.isFootballEvent():
            return
        else:
            fp = self.__fp
            attackerID = fp['lastAttackerID']
            assistID = fp['assistID']
            ownGoalVehID = fp['ownGoalVehID']
            selfGoal = self.scoreInfo[0]
            vehPlayersInfo = self.entity.getProperty('vehPlayersInfo')
            if selfGoal:
                lastInteractionPlayerInfo = vehPlayersInfo.get(ownGoalVehID, None)
                lastInteractionID = ownGoalVehID
            else:
                lastInteractionPlayerInfo = vehPlayersInfo.get(attackerID, None)
                lastInteractionID = attackerID
            if lastInteractionPlayerInfo:
                self.__encodeFootballScoreToFrags(lastInteractionPlayerInfo, selfGoal)
                self.entity._Arena__sendStatisticsUpdate(lastInteractionID, lastInteractionPlayerInfo)
                self.__getVehicleFootballComponent(lastInteractionPlayerInfo).onFootballGoal(selfGoal)
            for vehicleInfo in vehPlayersInfo.itervalues():
                self.__getVehicleFootballComponent(vehicleInfo).removeAmmoOnReset()

            assistPlayerInfo = vehPlayersInfo.get(assistID, None)
            if assistPlayerInfo and lastInteractionPlayerInfo:
                attackerAssistSameTeam = lastInteractionPlayerInfo['team'] == assistPlayerInfo['team']
                if attackerAssistSameTeam and not selfGoal:
                    self.__getVehicleFootballComponent(assistPlayerInfo).onFootballAssist()
            goalData = dict()
            goalData['teamScore'] = self.score
            goalData['scoreInfo'] = self.scoreInfo
            goalTime = getTimeOnArena(self.entity.bp['uniqueID'])
            goalData['goalTimelineEntry'] = (lastInteractionID, goalTime)
            self.__trackGoalEntries(goalTime, lastInteractionID, selfGoal)
            for av in self.entity.avatars:
                self.__updateScoreForClient(av, goalData)

            return

    def __encodeFootballScoreToFrags(self, attackerPlayerInfo, isSelfGoal):
        frags = attackerPlayerInfo['frags']
        selfGoals = attackerPlayerInfo['frags']
        goals = frags & 65535
        selfGoals = selfGoals >> 16
        selfGoals = selfGoals & 65535
        if isSelfGoal:
            selfGoals += 1
            selfGoals = selfGoals << 16
            attackerPlayerInfo['frags'] = goals + selfGoals
        else:
            goals += 1
            selfGoals = selfGoals << 16
            attackerPlayerInfo['frags'] = goals + selfGoals

    def updateCommonBattleResults(self, commonBattleResults):
        if not self.isFootballEvent():
            return
        teamScore = self.__fp['teamScore']
        commonBattleResults['footballScore'] = '%d - %d' % (teamScore[0], teamScore[1])

    @noexcept
    def __prepareFootballOvertime(self):
        arena = self.entity
        fp = self.__fp
        self.__resetTimers()
        periodLength = self.__getFootballSettings().OVERTIME_PREBATTLE_DURATION
        arena._Arena__startPeriod(ARENA_PERIOD.PREBATTLE, periodLength)
        arena._Arena__sendPeriodInfo()
        self.redGoal.cell.resetState()
        self.blueGoal.cell.resetState()
        self.__resetFootballPlayers()
        self.teleportBallToCenter()
        self.__ball.cell.freezeBall(True)
        fp['startFootballOvertimeTimerID'] = BigWorld.addTimer(self.__onStartFootballOvertime, periodLength)

    @noexcept
    def hasFootballOvertime(self):
        return BONUS_CAPS.checkAny(self.entity.bonusType, BONUS_CAPS.FOOTBALL, BONUS_CAPS.FOOTBALL_OVERTIME_MECHANICS)

    def __onOneSecondFootball(self, timerID, _=0):
        if not self.isFootballEvent():
            return
        else:
            fp = self.__fp
            side = fp['ballSides'][0]
            if side == 0:
                return
            fp['ballPossession'][side] += 1
            points = fp['overtimePoints']
            winningTeam = 3 - side
            points[winningTeam] = min(FOOTBALL_OVERTIME_CONTROL_POINTS, points[winningTeam] + FOOTBALL_OVERTIME_DELTA)
            if points[winningTeam] == FOOTBALL_OVERTIME_CONTROL_POINTS:
                fp['ballPositionTimerID'] = self.__cancelTimer(fp.get('ballPositionTimerID', None))
                self.entity.postponeWinnerCheck()
            self.broadcastFootballUpdate()
            return

    def __onStartFootballOvertime(self, timerID, _=0):
        if not self.isFootballEvent():
            return
        self.__inOT = True
        fp = self.__fp
        settings = self.__getFootballSettings()
        self.__isGoal = False
        self.redGoal.cell.resetState()
        self.blueGoal.cell.resetState()
        self.__ball.cell.freezeBall(False)
        self.entity._Arena__p['period'] = ARENA_PERIOD.BATTLE
        self.entity.updatePeriodInfo(settings.OVERTIME_BATTLE_DURATION)
        fp['startFootballOvertimeTimerID'] = self.__cancelTimer(fp['startFootballOvertimeTimerID'])
        fp['checkBallIdleTimerID'] = BigWorld.addTimer(self.__onCheckBallIdle, settings.OVERTIME_BALL_IDLE)
        fp['ballPositionTimerID'] = BigWorld.addTimer(self.__onOneSecondFootball, FOOTBALL_DELAY, FOOTBALL_DELAY)
        for vi in self.entity.getProperty('vehPlayersInfo').itervalues():
            self.__getVehicleFootballComponent(vi).onResumePlay()

        self.broadcastFootballUpdate()
        argStr = zlib.compress(cPickle.dumps({}, -1))
        for avatar in self.entity.avatars:
            avatar.updateArena(ARENA_UPDATE.FOOTBALL_RETURN_TO_PLAY, argStr, [])

    def __onBallDropTimer(self, timerID, _=0):
        if not self.isFootballEvent():
            return
        else:
            self.__fp['afterGoalTimerID'] = self.__cancelTimer(self.__fp['afterGoalTimerID'])
            arena = self.entity
            info = {'goalScored': self.__isGoal}
            self.__isGoal = False
            self.teleportBallToCenter()
            self.__ball.cell.freezeBall(True)
            self.redGoal.cell.resetState()
            self.blueGoal.cell.resetState()
            self.__resetFootballPlayers()
            if self.__fp['ballDropTimerID'] is not None:
                self.__fp['ballDropTimerID'] = self.__cancelTimer(self.__fp['ballDropTimerID'])
            self.__fp['ballDropTimerID'] = BigWorld.addTimer(self.__onBallDropped, BALL_DROP_TIMER_COUNT)
            self.__ballDropping = True
            arena._Arena__startPeriod(ARENA_PERIOD.PREBATTLE, BALL_DROP_TIMER_COUNT)
            arena._Arena__sendPeriodInfo()
            argStr = zlib.compress(cPickle.dumps(info, -1))
            for avatar in self.entity.avatars:
                avatar.updateArena(ARENA_UPDATE.FOOTBALL_BALL_DROP, argStr, [])

            return

    def __onBallDropped(self, timerID, _=0):
        if not self.isFootballEvent():
            return
        self.__fp['ballDropTimerID'] = self.__cancelTimer(self.__fp['ballDropTimerID'])
        for vehID, vehInfo in self.entity.getProperty('vehPlayersInfo').iteritems():
            self.__getVehicleFootballComponent(vehInfo).onResumePlay()

        if self.curTime <= 0.1:
            self.curTimer = 2.5
        self.entity._Arena__startPeriod(ARENA_PERIOD.BATTLE, self.curTime)
        self.entity._Arena__sendPeriodInfo()
        self.__ballDropping = False
        self.__ball.cell.freezeBall(False)
        argStr = zlib.compress(cPickle.dumps({}, -1))
        for avatar in self.entity.avatars:
            avatar.updateArena(ARENA_UPDATE.FOOTBALL_RETURN_TO_PLAY, argStr, [])

    def __onCheckBallIdle(self, timerID, _=0):
        if not self.isFootballEvent():
            return
        self.__fp['checkBallIdleTimerID'] = self.__cancelTimer(self.__fp['checkBallIdleTimerID'])
        self.pushIdleBall()

    def __sendFootballInfoTo(self, avatar):
        if not self.isFootballEvent():
            return
        fp = self.__fp
        footballInfo = {'ballPossession': fp['ballPossession']}
        if self.isOT:
            footballInfo['overtimePoints'] = fp['overtimePoints']
        argStr = zlib.compress(cPickle.dumps(footballInfo, -1))
        avatar.updateArena(ARENA_UPDATE.FOOTBALL_OVERTIME_POINTS, argStr, [])

    def __updateScoreForClient(self, avatar, goalData):
        scoreArg = zlib.compress(cPickle.dumps(goalData, -1))
        avatar.updateArena(ARENA_UPDATE.FOOTBALL_GOAL_SCORED, scoreArg, [])

    def __notifyWinnerDeclared(self, avatar, winnerData):
        winnerArg = zlib.compress(cPickle.dumps(winnerData, -1))
        avatar.updateArena(ARENA_UPDATE.FOOTBALL_WINNER_DECLARED, winnerArg, [])

    def __notifyFadeOutOverlay(self, avatar, fadeData):
        fadeArg = zlib.compress(cPickle.dumps(fadeData, -1))
        avatar.updateArena(ARENA_UPDATE.FOOTBALL_FADE_OUT_OVERLAY, fadeArg, [])

    def __sendAllTimelineData(self, avatar):
        scoreArg = zlib.compress(cPickle.dumps(self.__goalEntries, -1))
        avatar.updateArena(ARENA_UPDATE.FOOTBALL_GOAL_TIMELINE, scoreArg, [])

    def __destroyBall(self):
        if self.__ball is not None:
            self.__ball.smartDestroy()
            self.__ball = None
        return

    def __destroyGoals(self):
        if self.__goals[0] is not None:
            self.__goals[0].smartDestroy()
        if self.__goals[1] is not None:
            self.__goals[1].smartDestroy()
        self.__goals = [None, None]
        return

    def __destroyCage(self):
        if self.__cage is not None:
            self.__cage.smartDestroy()
            self.__cage = None
        return

    def __setGoalSpawnPositions(self, goalType, matrix):
        if goalType == RED_GOAL_POS:
            self.__fp['redGoalMatrix'] = matrix
        elif goalType == BLUE_GOAL_POS:
            self.__fp['blueGoalMatrix'] = matrix

    def __getGoalSpawnPositions(self, goalType):
        if goalType == RED_GOAL_POS:
            return self.__fp['redGoalMatrix'].translation
        else:
            return self.__fp['blueGoalMatrix'].translation

    def __startPreparingFootballOvertime(self):
        fp = self.__fp
        fp['prepareOvertimeDelay'] = BigWorld.addTimer(self.__prepareOvertime, FOOTBALL_OVERTIME_PREP)
        self.__isPreparingOT = True
        info = {'canFadeOut': self.__isPreparingOT,
         'delay': FOOTBALL_DELAY_FADE_OT}
        for av in self.entity.avatars:
            self.__notifyFadeOutOverlay(av, info)

    def __prepareOvertime(self, timerID, _=0):
        self.__prepareFootballOvertime()
        self.broadcastFootballUpdate()

    def __resetFootballPlayers(self):
        for vehID, vehInfo in self.entity.getProperty('vehPlayersInfo').iteritems():
            position = vehInfo['spawnPosition']
            self.__getVehicleFootballComponent(vehInfo).onResetAndLock(position[0], position[1], self.__isPreparingOT)

    def __getFootballSettings(self):
        return self.__settings

    def __resetState(self):
        fp = self.__fp
        self.__pointsToWin = 3
        self.__isPreparingOT = False
        self.__inOT = False
        self.__isGoal = False
        self.__winningTeam = 0
        self.__points = 0
        self.curTime = 0
        fp['ballSides'] = [0, 0]
        fp['teamScore'] = [0, 0]
        fp['scoreInfo'] = [0, 0]
        fp['overtimePoints'] = [None, 0, 0]
        fp['ballPossession'] = [None, 0, 0]
        fp['lastAttackerID'] = 0
        fp['assistID'] = 0
        fp['ownGoalVehID'] = 0
        return

    def receiveBallPositionUpdate(self, ballSide):
        if not self.isFootballEvent():
            return
        ballSides = self.__fp['ballSides']
        ballSides[0], ballSides[1] = ballSide, ballSides[0]
        if ballSides[0] == 0:
            ballSides[0] = ballSides[1]

    def getFieldPosition(self):
        return None if not self.isFootballEvent() else self.__settings.getFieldPosition()

    def __cancelTimer(self, timerID):
        if timerID is not None:
            BigWorld.delTimer(timerID)
        return

    def __getVehicleFootballComponent(self, vehInfo):
        return vehInfo['vehicle'].cell.components['VehicleFootball']

    @noexcept
    def sendArenaStateTo(self, avatar, avatarTeam):
        if self.isFootballEvent():
            self.__sendAllTimelineData(avatar)

    @noexcept
    def isFootballEvent(self):
        return BONUS_CAPS.checkAny(self.entity.bonusType, BONUS_CAPS.FOOTBALL, BONUS_CAPS.FOOTBALL_OVERTIME_MECHANICS)

    def __registerForArenaEvents(self):
        arena = self.entity
        arena.onAddEntity += self.__onArenaAddEntity
        arena.onFinishArena += self.__onFinishArena
        arena.onResetProperties += self.__onArenaResetProperties
        arena.onCreateVehicles += self.__onArenaCreateVehicles
        arena.onArenaReset += self.__onArenaCleanup
        arena.onArenaCleanup += self.__onArenaCleanup
        arena.onVehicleInfoCreation += self.__onArenaVehicleInfoCreation
        arena.onLogArenaResults += self.__onLogArenaResults

    def __unregisterForArenaEvents(self):
        arena = self.entity
        arena.onAddEntity -= self.__onArenaAddEntity
        arena.onFinishArena -= self.__onFinishArena
        arena.onResetProperties -= self.__onArenaResetProperties
        arena.onCreateVehicles -= self.__onArenaCreateVehicles
        arena.onArenaReset -= self.__onArenaCleanup
        arena.onArenaCleanup -= self.__onArenaCleanup
        arena.onVehicleInfoCreation -= self.__onArenaVehicleInfoCreation
        arena.onLogArenaResults -= self.__onLogArenaResults

    def __onArenaAddEntity(self, section, matrix):
        if self.isFootballEvent():
            self.createEntity(section, matrix)

    def __onArenaResetProperties(self):
        if self.isFootballEvent():
            self.entity._Arena__p['winnerProcessor'] = self

    def __onArenaCreateVehicles(self):
        if self.isFootballEvent():
            self.spawnFootballEntities()
            self.entity.cell.ArenaFootballMechanics.onCreateVehicles()

    def __onArenaVehicleInfoCreation(self, vehPlayerInfo, pos):
        if self.isFootballEvent():
            vehPlayerInfo['spawnPosition'] = pos

    def __makeArenaValues(self, arena, arenaUniqueID):
        p = arena._Arena__p
        return {'arena_id': arenaUniqueID,
         'web_emitter_id': arena.webEmitterID,
         'periphery_id': PERIPHERY.ID,
         'start_dt': getArenaStartTime(arenaUniqueID),
         'duration': int(p['finishTime'] - p['startTime']),
         'map_type_id': arena.typeID & 65535,
         'winner_team_id': p['winnerTeam']}

    def __onLogArenaResults(self):
        if not self.isFootballEvent() or not HIST_LOG_CONFIG.isLogEnabled('football_arena_results', BigWorld.globalData):
            return
        else:
            arena = self.entity
            p = arena._Arena__p
            bp = arena.bp
            arenaUniqueID = bp['uniqueID']
            vehPlayersInfo = p['vehPlayersInfo']
            vehResultsValues = []
            for vehID, vehPlayerInfo in vehPlayersInfo.iteritems():
                accountDBID = vehPlayerInfo['accountDBID']
                if accountDBID == 0:
                    continue
                vehFullResults = p['vehBattleResults'].get(vehID, None)
                if vehFullResults is None:
                    continue
                for vehTypeCompDescr, vehInfo in vehPlayerInfo['vehiclesInfo'].iteritems():
                    results = vehFullResults.get(vehTypeCompDescr, None)
                    if results is None:
                        continue
                    vehResultsValue = {'arena_id': arenaUniqueID,
                     'periphery_id': PERIPHERY.ID,
                     'account_db_id': accountDBID,
                     'attrs_mask': vehPlayerInfo['attrs'],
                     'prebattle_id': vehPlayerInfo['prebattleID'],
                     'vehicle_type_cd': vehInfo['typeCompDescr'],
                     'team_id': vehPlayerInfo['team'],
                     'goals': results['goals'],
                     'auto_goals': results['selfGoals'],
                     'scored_balls': results['assists'],
                     'returned_balls': results['blocks'],
                     'score': results['productivityPoints']}
                    vehResultsValues.append(vehResultsValue)

            arenaValues = self.__makeArenaValues(arena, arenaUniqueID)
            if arenaValues or vehResultsValues:
                BigWorld.services['KafkaReliablePublisher'].publish('log_football_arena_results', {'object_id': arenaUniqueID,
                 'data': {'opType': KAFKA_LOG_OPERATION_TYPE.FOOTBALL_ARENA_RESULTS,
                          'body': {'arena': arenaValues,
                                   'vehicles_results': vehResultsValues}}})
                db.insert('ins_log_football_arena_results', None, None, None, **arenaValues)
                if vehResultsValues:
                    db.insertMany('ins_log_football_arena_vehicle_results', vehResultsValues)
            return

    def __trackGoalEntries(self, goalTime, scoringVehID, isSelfGoal):
        if scoringVehID not in self.__goalEntries:
            self.__goalEntries[scoringVehID] = [[], []]
        timelineToAppend = self.__goalEntries[scoringVehID][1] if isSelfGoal else self.__goalEntries[scoringVehID][0]
        timelineToAppend.append(goalTime)
