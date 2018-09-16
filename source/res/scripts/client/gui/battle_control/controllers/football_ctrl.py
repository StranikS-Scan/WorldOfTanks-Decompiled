# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/football_ctrl.py
import BigWorld
from constants import ARENA_PERIOD
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION, LOG_ERROR
from event_special_effects import EventEffectsStorage
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController, IArenaLoadController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.period_ctrl import IArenaPeriodController
from gui.battle_control.view_components import ViewComponentsController
from items.vehicles import getVehicleType

class _VehicleTags(object):
    ROLE_STRIKER = 'role_striker'
    ROLE_MIDFIELDER = 'role_midfielder'
    ROLE_DEFENDER = 'role_defender'


class IFootballView(object):

    def updateScore(self, teamScore, scoreInfo):
        pass

    def updateOvertimeScore(self, points):
        pass

    def updateGoalTimeline(self, data):
        pass

    def onReturnToPlay(self, data):
        pass

    def onFootballFadeOut(self, canFadeOut, delay):
        pass

    def onWinnerDeclared(self, winner, delay):
        pass

    def onArenaLoaded(self):
        pass


class IFootballEntitiesView(object):

    def onEntityRegistered(self, entityID):
        pass

    def onEntityUnregistered(self, entityID):
        pass

    def clear(self):
        pass


class IFootballPeriodListener(object):

    def onPrepareFootballOvertime(self):
        pass

    def onStartFootballOvertime(self):
        pass

    def onEndFootballOvertime(self):
        pass

    def onBallDrop(self):
        pass


class FootballCtrl(IArenaVehiclesController, ViewComponentsController):

    @property
    def eventEffectsStorage(self):
        return self.__eventEffectsStorage

    def __init__(self):
        super(FootballCtrl, self).__init__()
        self.__goals = (0, 0)
        self.__goalEntries = None
        self.__entityViewsIDs = []
        self.__battleCtx = None
        self.__eventEffectsStorage = None
        return

    def startControl(self, battleCtx, arenaVisitor):
        self.__battleCtx = battleCtx
        self.__eventEffectsStorage = EventEffectsStorage()
        self.__eventEffectsStorage.readCfg()

    def stopControl(self):
        super(FootballCtrl, self).stopControl()
        self.__entityViewsIDs = []
        self.__battleCtx = None
        self.__eventEffectsStorage = None
        return

    def registerEntity(self, entity):
        entityId = entity.id
        if entity not in self.__entityViewsIDs:
            self.__entityViewsIDs.append(entityId)
        else:
            LOG_WARNING('Attempt to register entity which is already in the list. Item ID = {}'.format(entityId))
        self.__updateScoreAndTimeline(invalidateTimeline=False)

    def unregisterEntity(self, entity):
        entityId = entity.id
        if entity in self.__entityViewsIDs:
            self.__entityViewsIDs.remove(entityId)

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.LOAD

    def getControllerID(self):
        return BATTLE_CTRL_ID.FOOTBALL_CTRL

    def invalidateFootballOvertimePoints(self, arenaDP, data):
        for view in self._viewComponents:
            overtimePoints = data.get('overtimePoints')
            view.updateOvertimeScore(overtimePoints)

    def setViewComponents(self, *components):
        super(FootballCtrl, self).setViewComponents(*components)
        self.__updateScoreAndTimeline()
        for view in self._viewComponents:
            view.onReturnToPlay(self.__goalEntries)

    def invalidateGoalData(self, data):
        scoreInfo = data['scoreInfo']
        self.__updateScores(data['teamScore'], scoreInfo)
        vID, goalTime = data['goalTimelineEntry']
        vehPlayerInfo = self.__battleCtx.getVehicleInfo(vID)
        self.__updateGoalTimeline(self.__createTimelineData(bool(scoreInfo[0]), goalTime, vehPlayerInfo))

    def invalidateGoalTimeline(self, data):
        if data:
            self.__goalEntries = data
        self.__updateScoreAndTimeline()

    def onReturnToPlay(self, data):
        for view in self._viewComponents:
            view.onReturnToPlay(data)

    def onWinnerDeclared(self, data):
        delay = data['delay']
        winner = data['__winningTeam']
        for view in self._viewComponents:
            view.onWinnerDeclared(winner, delay)

    def onFadeOutOverlay(self, data):
        for view in self._viewComponents:
            view.onFootballFadeOut(data['canFadeOut'], data['delay'])

    def arenaLoadCompleted(self):
        for view in self._viewComponents:
            view.onArenaLoaded()

    def __getPossessionData(self, arenaDP):
        possessionPoints = arenaDP.getBallPossession()
        possessionVals = list(possessionPoints) if possessionPoints is not None else [0, 0]
        valsSum = sum(possessionVals)
        if valsSum > 0:
            for i, val in enumerate(possessionVals):
                possessionVals[i] = round(float(val) * 100 / valsSum)

        return possessionVals

    def __updateScores(self, teamScore, scoreInfo=None):
        if teamScore:
            for view in self._viewComponents:
                view.updateScore(teamScore, scoreInfo)

            for entityID in self.__entityViewsIDs:
                entity = BigWorld.entities.get(entityID)
                if entity:
                    entity.updateScore(teamScore, scoreInfo)

    def __updateGoalTimeline(self, data=None):
        if data:
            for view in self._viewComponents:
                view.updateGoalTimeline(data)

    def __updateScoreAndTimeline(self, invalidateTimeline=True):
        if self.__goalEntries and self._viewComponents is not None:
            goals = []
            teamScore = [0, 0]
            for vehID, (goalsTL, autoGoalsTL) in self.__goalEntries.iteritems():
                vehPlayerInfo = self.__battleCtx.getVehicleInfo(vehID)
                teamID = vehPlayerInfo.team
                teamScore[teamID - 1] += len(goalsTL)
                teamScore[2 - teamID] += len(autoGoalsTL)
                if invalidateTimeline:
                    self.__addGoalsTimelineData(vehPlayerInfo, goalsTL, goals)
                    self.__addGoalsTimelineData(vehPlayerInfo, autoGoalsTL, goals, True)

            goals.sort(key=lambda goal: goal['time'], reverse=False)
            for entry in goals:
                self.__updateGoalTimeline(entry)

            self.__updateScores(teamScore, None)
        return

    def __addGoalsTimelineData(self, vehPlayerInfo, vehTimeline, outList, selfGoal=False):
        for timeStamp in vehTimeline:
            outList.append(self.__createTimelineData(selfGoal, timeStamp, vehPlayerInfo))

    def __createTimelineData(self, selfGoal, timeStamp, vehPlayerInfo):
        vehIntCD = vehPlayerInfo.vehicleType.compactDescr
        vehType = ''
        if vehIntCD:
            vehicleType = getVehicleType(vehIntCD)
            if _VehicleTags.ROLE_STRIKER in vehicleType.tags:
                vehType = 'striker'
            elif _VehicleTags.ROLE_MIDFIELDER in vehicleType.tags:
                vehType = 'midfield'
            elif _VehicleTags.ROLE_DEFENDER in vehicleType.tags:
                vehType = 'defender'
            else:
                LOG_ERROR('The required tags have not been found in the vehicle descriptor!')
        else:
            LOG_ERROR('Invalid vehicle ID {}'.format(vehPlayerInfo))
        return {'time': timeStamp,
         'playerName': vehPlayerInfo.player.name,
         'weight': vehType,
         'teamID': 3 - vehPlayerInfo.team if selfGoal else vehPlayerInfo.team,
         'selfGoal': selfGoal}


class FootballPeriodCtrl(IArenaPeriodController, IArenaVehiclesController, ViewComponentsController):

    def __init__(self):
        super(FootballPeriodCtrl, self).__init__()
        self._period = None
        self.__isOvertime = False
        self.__isPreOvertime = False
        self.__ballPossession = None
        self.__overtimePoints = None
        return

    def stopControl(self):
        self._period = None
        self.__isOvertime = False
        self.__ballPossession = None
        return

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.PERIOD

    def getControllerID(self):
        return BATTLE_CTRL_ID.FOOTBALL_PERIOD_CTRL

    def setViewComponents(self, *components):
        super(FootballPeriodCtrl, self).setViewComponents(*components)
        self._update()

    def isOvertime(self):
        return self.__isOvertime

    def invalidateOnBallDrop(self, data):
        for view in self._viewComponents:
            view.onBallDrop()

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        super(FootballPeriodCtrl, self).invalidatePeriodInfo(period, endTime, length, additionalInfo)
        self._period = period
        self._update()

    def invalidateFootballOvertimePoints(self, arenaDP, data):
        self.__ballPossession = data.get('ballPossession')
        self.__overtimePoints = data.get('overtimePoints')
        self._update()

    def _update(self):
        if not self.__isPreOvertime:
            if self._period == ARENA_PERIOD.PREBATTLE:
                if self.__ballPossession and self.__ballPossession != (0, 0) or self.__overtimePoints is not None:
                    self.__isPreOvertime = True
                    for view in self._viewComponents:
                        view.onPrepareFootballOvertime()

        if not self.__isOvertime:
            if self._period == ARENA_PERIOD.BATTLE:
                if self.__overtimePoints is not None:
                    self.__isOvertime = True
                    for view in self._viewComponents:
                        view.onStartFootballOvertime()

        return


class FootballEntitiesController(IArenaLoadController, ViewComponentsController):

    def __init__(self):
        super(FootballEntitiesController, self).__init__()
        self.__entitiesIDs = []

    def startControl(self, *args):
        BigWorld.player().onVehicleEnterWorld += self.__onVehicleEnterWorld
        BigWorld.player().onVehicleLeaveWorld += self.__onVehicleLeaveWorld

    def stopControl(self):
        BigWorld.player().onVehicleEnterWorld -= self.__onVehicleEnterWorld
        BigWorld.player().onVehicleLeaveWorld -= self.__onVehicleLeaveWorld

    def getControllerID(self):
        return BATTLE_CTRL_ID.FOOTBALL_ENTITIES_CTRL

    def getCtrlScope(self):
        return _SCOPE.LOAD

    def registerEntity(self, entity):
        entityId = entity.id
        if entity not in self.__entitiesIDs:
            self.__entitiesIDs.append(entityId)
            for view in self._viewComponents:
                view.onEntityRegistered(entityId)

        else:
            LOG_WARNING('Attempt to register entity which is already in the list. Item ID = {}'.format(entityId))

    def unregisterEntity(self, entity):
        entityId = entity.id
        if entity in self.__entitiesIDs:
            self.__entitiesIDs.remove(entityId)
            for view in self._viewComponents:
                view.onEntityUnregistered(entityId)

    def clearViewComponents(self):
        for view in self._viewComponents:
            try:
                view.clear()
            except ReferenceError:
                LOG_CURRENT_EXCEPTION()

        super(FootballEntitiesController, self).clearViewComponents()

    def setViewComponents(self, *components):
        super(FootballEntitiesController, self).setViewComponents(*components)
        for view in self._viewComponents:
            for entityID in self.__entitiesIDs:
                view.onEntityRegistered(entityID)

    def __onVehicleEnterWorld(self, vehicle):
        if avatar_getter.getPlayerVehicleID() == vehicle.id:
            self.registerEntity(vehicle)

    def __onVehicleLeaveWorld(self, vehicle):
        if avatar_getter.getPlayerVehicleID() == vehicle.id:
            self.unregisterEntity(vehicle)
