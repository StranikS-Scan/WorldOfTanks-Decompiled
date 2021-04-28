# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/points_of_interest_ctrl.py
from collections import namedtuple
from itertools import chain
import logging
import weakref
import BigWorld
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IPointsOfInterestController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, UNDEFINED_VEHICLE_ID, VEHICLE_VIEW_STATE
from gui.battle_control.view_components import ViewComponentsController
from gui.Scaleform.genConsts.WEEKEND_BRAWL_CONSTS import WEEKEND_BRAWL_CONSTS
import Event
from helpers import dependency
from shared_utils import first
from skeletons.gui.battle_session import IBattleSessionProvider
from soft_exception import SoftException
from weekend_brawl_common import POIActivityStatus, POITeamInfo
from weekend_brawl_common import VehiclePOIStatus, UNKNOWN_TIME
_logger = logging.getLogger(__name__)
_EQUIPMENT_TAGS = frozenset(['weekend_brawl'])
_PointProperties = namedtuple('_PointProperties', ('captureTime', 'cooldown', 'awards'))

class IPointOfInterestListener(object):

    def addPoint(self, pointID, status):
        pass

    def getPointProperties(self, properties):
        pass

    def updateState(self, pointID, status, startTime, vehicleID=UNDEFINED_VEHICLE_ID):
        pass

    def finishedCapturing(self, pointID, vehicleID):
        pass

    def updateAbilities(self, isAvailable=True):
        pass

    def selectedAbility(self, isSuccessfully):
        pass

    def usedAbility(self, equipmentCD, vehicleID):
        pass


class PointsOfInterestController(IPointsOfInterestController, ViewComponentsController):
    __slots__ = ('__points', '__invaders', '__plugins', '__eManager', '__arenaDP')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, setup):
        super(PointsOfInterestController, self).__init__()
        self.__points = {}
        self.__invaders = {}
        self.__plugins = []
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__eManager = Event.EventManager()
        self.onArenaVehicleActivityUpdated = Event.Event(self.__eManager)

    def getControllerID(self):
        return BATTLE_CTRL_ID.POINTS_OF_INTEREST_CTRL

    def startControl(self):
        _logger.debug('PointsOfInterestController started')
        avatar = BigWorld.player()
        avatar.onVehicleEnterWorld += self.__onVehicleEnterWorld

    def stopControl(self):
        _logger.debug('PointsOfInterestController stopped')
        avatar = BigWorld.player()
        if avatar is not None:
            avatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld
        self.clearViewComponents()
        self.__points.clear()
        self.__invaders = None
        self.__arenaDP = None
        self.__eManager.clear()
        self.__eManager = None
        return

    def setViewComponents(self, *components):
        self._viewComponents = list(components)
        pointProperties = self.__getPointProperties()
        if pointProperties is not None:
            for view in self._viewComponents:
                view.getPointProperties(pointProperties)

        return

    def addPointOfInterest(self, point):
        pointID = point.id
        if pointID in self.__points:
            _logger.error('Point of interest with id=%s already added', pointID)
        self.__points[pointID] = weakref.proxy(point)

    def removePointOfInterest(self, pointID):
        if pointID in self.__points:
            del self.__points[pointID]
        else:
            _logger.error('There is not Point of interest with id=%s. Can not remove it', pointID)

    def addPlugin(self, plugin):
        if plugin in self.__plugins:
            _logger.warning('Plugin already added - %s', plugin)
        else:
            self.__plugins.append(plugin)

    def removePlugin(self, plugin):
        if plugin in self.__plugins:
            self.__plugins.remove(plugin)
        else:
            _logger.warning('Plugin has not been found')

    def clearViewComponents(self):
        super(PointsOfInterestController, self).clearViewComponents()
        self.__plugins = []

    def getPointsOfInterest(self):
        return [ (point.id, point.position, point.activityStatus.statusID) for point in self.__points.values() ]

    def getStartTime(self, pointID):
        point = self.__points.get(pointID)
        return point.activityStatus.startTime if point is not None else UNKNOWN_TIME

    def getPointStatus(self, pointID):
        point = self.__points.get(pointID)
        return point.activityStatus.statusID if point is not None else None

    def getCapturingPoints(self):
        teamInfo = BigWorld.player().arena.teamInfo
        if not teamInfo:
            return
        poiInfos = []
        for pointID in self.__points:
            pointTeamInfoComponent = teamInfo.dynamicComponents[POITeamInfo.getTeamInfoID(pointID)]
            capturingStatus = pointTeamInfoComponent.capturingStatus
            if capturingStatus.status == POIActivityStatus.CAPTURING:
                poiInfos.append((pointID, capturingStatus.vehicleID, capturingStatus.startTime))

        return poiInfos

    def invalidateCapturingState(self, pointID, invaders, state, startTime):
        vehicleID = invaders.current
        _logger.debug('Invalidate capturing status of the Point of Interest for vehicle with id=%s', vehicleID)
        for listener in self.__iterListeners():
            listener.updateState(pointID, state, startTime, vehicleID)

        vehicleInfos = self.__getCapturingVehicleStates(state, invaders)
        for vehicleState, vehicleID in vehicleInfos:
            self.__updateArenaInfo(vehicleState, vehicleID)

    def invalidateCapturedState(self, poiID, vehicleID):
        for listener in self.__iterListeners():
            listener.finishedCapturing(poiID, vehicleID)

    def invalidateInvaders(self, pointID, invaders):
        actualInvaders = set(invaders)
        oldInvaders = self.__invaders.get(pointID, set())
        removedInvaders = oldInvaders - actualInvaders
        addedInvaders = actualInvaders - oldInvaders
        playerInfo = chain([ (WEEKEND_BRAWL_CONSTS.INTEREST_POINT_STATE_NONE, invader) for invader in removedInvaders ], [ (WEEKEND_BRAWL_CONSTS.INTEREST_POINT_STATE_CAPTURED, invader) for invader in addedInvaders ])
        for info in playerInfo:
            self.__updateArenaInfo(*info)

        self.__invaders[pointID] = actualInvaders

    def isInPoint(self, poiID):
        vehiclePoiComponent = self.__getVehiclePoiComponent()
        return vehiclePoiComponent.insidePoiID == poiID if vehiclePoiComponent is not None else False

    def isAbilityAvailable(self):
        vehiclePoiComponent = self.__getVehiclePoiComponent()
        return vehiclePoiComponent.status.statusID == VehiclePOIStatus.CAPTURED if vehiclePoiComponent is not None else False

    def isInvader(self, pointID=None):
        vehiclePoiComponent = self.__getVehiclePoiComponent()
        return vehiclePoiComponent.status.statusID in VehiclePOIStatus.AFTER_CAPTURE_RANGE if vehiclePoiComponent is not None else False

    def selectAbility(self, abilityID):
        pointID = self.__getCapturedPoint()
        if pointID is None or not self.__maySelectAbility() or self.__sessionProvider.isReplayPlaying:
            return
        else:
            BigWorld.player().poiAvatar.cell.chooseEquipment(pointID, abilityID)
            return

    def getResponseOnChoiceAbility(self, isSuccessfully):
        for view in self._viewComponents:
            view.selectedAbility(isSuccessfully)

    def usedAbility(self, equipmentCD, vehicleID):
        for listener in self.__iterListeners():
            listener.usedAbility(equipmentCD, vehicleID)

    def __getCapturedPoint(self):
        vehicleID = avatar_getter.getPlayerVehicleID()
        for pointID, invaders in self.__invaders.iteritems():
            if vehicleID in invaders:
                return pointID

        return None

    def __onVehicleEnterWorld(self, vehicle):
        if vehicle.id == avatar_getter.getPlayerVehicleID():
            BigWorld.player().onVehicleEnterWorld -= self.__onVehicleEnterWorld
            self.__initPointsInfo()
            self.__updateAbilitiesInfo()

    def __getPointProperties(self):
        if self.__points is None:
            raise SoftException('Points of Interest are not initialized')
        point = first(self.__points.values())
        return _PointProperties(captureTime=point.captureTime, cooldown=point.cooldown, awards=point.equipmentCDs) if point is not None else None

    def __initPointsInfo(self):
        teamInfo = BigWorld.player().arena.teamInfo
        if teamInfo is None:
            raise SoftException('TeamInfo is not initialized.')
        vehiclesInfo = []
        for pointID in self.__points:
            pointTeamInfoComponent = teamInfo.dynamicComponents[POITeamInfo.getTeamInfoID(pointID)]
            self.__invaders[pointID] = set(pointTeamInfoComponent.prevInvaderIDs)
            vehiclesInfo.extend([ (WEEKEND_BRAWL_CONSTS.INTEREST_POINT_STATE_CAPTURED, invader) for invader in pointTeamInfoComponent.prevInvaderIDs ])
            capturingStatus = pointTeamInfoComponent.capturingStatus
            vehicleID = capturingStatus.vehicleID
            if capturingStatus.status == POIActivityStatus.CAPTURING:
                vehiclesInfo.append((WEEKEND_BRAWL_CONSTS.INTEREST_POINT_STATE_IS_CAPTURING, vehicleID))
            for view in self._viewComponents:
                view.addPoint(pointID, POIActivityStatus.ACTIVE)
                view.updateState(pointID, capturingStatus.status, capturingStatus.startTime, vehicleID)

            if self.isInPoint(pointID):
                self.__updatePlayerInPoint(pointID)

        for info in vehiclesInfo:
            self.__updateArenaInfo(*info)

        return

    def __updatePlayerInPoint(self, pointID):
        vehiclePoiComponent = self.__getVehiclePoiComponent()
        if vehiclePoiComponent is None:
            return
        else:
            params = vehiclePoiComponent.getParams()
            if params is not None:
                self.__sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.POINT_OF_INTEREST, params)
            point = self.__points.get(pointID)
            if point is None:
                raise SoftException('Point of interest is not found')
            if point.isCooldown:
                point.invalidateCooldownStatus(isCooldown=True)
            return

    def __updateAbilitiesInfo(self):
        if self.isAbilityAvailable():
            for listener in self.__iterListeners():
                listener.updateAbilities(isAvailable=True)

    def __iterListeners(self):
        for view in self._viewComponents:
            yield view

        for plugin in self.__plugins:
            yield plugin

    def __updateArenaInfo(self, state, vehicleID):
        if vehicleID == UNDEFINED_VEHICLE_ID:
            return
        else:
            updatedData = {'interestPointState': state}
            flag, vInfo = self.__arenaDP.updateGameModeSpecificStats(vehicleID, False, updatedData)
            if vInfo is not None:
                self.onArenaVehicleActivityUpdated([(flag, vInfo)], self.__arenaDP)
            return

    def __maySelectAbility(self):
        player = BigWorld.player()
        if player is None:
            return False
        else:
            vehicle = player.vehicle
            if vehicle is None:
                return False
            ctrl = self.__sessionProvider.shared.vehicleState
            return False if player.isObserver() or ctrl.isInPostmortem else True

    @staticmethod
    def __getVehiclePoiComponent():
        player = BigWorld.player()
        vehicle = player.vehicle
        if vehicle is None:
            vehicle = player.getVehicleAttached()
        return vehicle.dynamicComponents.get('poiVehicle', None) if vehicle is not None else None

    @staticmethod
    def __getCapturingVehicleStates(state, invaders):
        result = []
        if state == POIActivityStatus.CAPTURING:
            result.append((WEEKEND_BRAWL_CONSTS.INTEREST_POINT_STATE_IS_CAPTURING, invaders.current))
            if invaders.previous != UNDEFINED_VEHICLE_ID:
                result.append((WEEKEND_BRAWL_CONSTS.INTEREST_POINT_STATE_NONE, invaders.previous))
        elif state == POIActivityStatus.COOLDOWN:
            result.append((WEEKEND_BRAWL_CONSTS.INTEREST_POINT_STATE_CAPTURED, invaders.current))
        elif state == POIActivityStatus.ACTIVE and invaders.current == UNDEFINED_VEHICLE_ID:
            result.append((WEEKEND_BRAWL_CONSTS.INTEREST_POINT_STATE_NONE, invaders.previous))
        return result
