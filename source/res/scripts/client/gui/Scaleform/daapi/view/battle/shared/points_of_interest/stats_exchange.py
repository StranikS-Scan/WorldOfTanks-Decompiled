# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/points_of_interest/stats_exchange.py
import logging
import enum
import typing
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.points_of_interest.constants import POI_TYPE_UI_MAPPING
from gui.Scaleform.daapi.view.battle.shared.points_of_interest.poi_helpers import getPoiEquipmentByType
from helpers import dependency
from points_of_interest.mixins import PointsOfInterestListener
from points_of_interest_shared import ENEMY_VEHICLE_ID
from skeletons.gui.battle_session import IBattleSessionProvider
from points_of_interest_shared import PoiStatus
if typing.TYPE_CHECKING:
    from points_of_interest.components import PoiStateComponent
_logger = logging.getLogger(__name__)

class PoiStatusItemUpdateResult(enum.IntEnum):
    VALID = 1
    INVALID = 2
    UPDATED = 3


class PointsOfInterestStatsController(PointsOfInterestListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, statsDataController):
        super(PointsOfInterestStatsController, self).__init__()
        self.__statsDataController = statsDataController
        self.__poiStatusItems = {}

    def startControl(self, *_, **__):
        self._registerPoiListener()
        poiCtrl = self.__sessionProvider.dynamic.pointsOfInterest
        if poiCtrl is not None:
            poiCtrl.onPoiEquipmentUsed += self.__onPoiEquipmentUsed
            poiCtrl.onPoiCaptured += self.__onPoiCaptured
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onVehicleKilled += self.__onVehicleKilled
        return

    def stopControl(self):
        self._unregisterPoiListener()
        poiCtrl = self.__sessionProvider.dynamic.pointsOfInterest
        if poiCtrl is not None:
            poiCtrl.onPoiEquipmentUsed -= self.__onPoiEquipmentUsed
            poiCtrl.onPoiCaptured -= self.__onPoiCaptured
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onVehicleKilled -= self.__onVehicleKilled
        return

    def onPoiAdded(self, poiState):
        poiTeamInfo = BigWorld.player().arena.teamInfo.PoiTeamInfoComponent
        for vehId, points in poiTeamInfo.capturedPoints.iteritems():
            if vehId != ENEMY_VEHICLE_ID and poiState.id in points:
                self.__addCapturedPoint(poiState.id, vehId, poiState)

    def onProcessPoi(self, poiState):
        poiID = poiState.id
        invader = poiState.invader
        for vehicleID, statusItems in self.__poiStatusItems.iteritems():
            item = statusItems.get(poiID)
            if item is None:
                continue
            result = item.update()
            if result == PoiStatusItemUpdateResult.VALID:
                continue
            if result == PoiStatusItemUpdateResult.INVALID:
                self.__statsDataController.as_removePointOfInterestS(vehicleID=vehicleID, type=item.type)
                del statusItems[poiID]
            if result == PoiStatusItemUpdateResult.UPDATED:
                self.__statsDataController.as_updatePointOfInterestS(data=item.getVO())

        if invader:
            statusItems = self.__poiStatusItems.setdefault(invader, {})
            if poiID not in statusItems:
                statusItems[poiID] = item = PoiStatusItem(poiState)
                self.__statsDataController.as_updatePointOfInterestS(data=item.getVO())
        return

    def __onPoiEquipmentUsed(self, equipment, vehicleID):
        statusItems = self.__poiStatusItems.get(vehicleID, {})
        for item in statusItems.itervalues():
            poiEquipment = getPoiEquipmentByType(item.state.type)
            if poiEquipment is not None and poiEquipment.id == equipment.id:
                item.setCaptured(isCaptured=False)

        return

    def __onPoiCaptured(self, poiID, vehicleID):
        if vehicleID == ENEMY_VEHICLE_ID:
            return
        poiState = self.__sessionProvider.dynamic.pointsOfInterest.getPoiState(poiID)
        self.__addCapturedPoint(poiID, vehicleID, poiState)

    def __addCapturedPoint(self, poiID, vehicleID, poiState):
        item = self.__poiStatusItems.setdefault(vehicleID, {}).get(poiID)
        if item is None:
            if poiState is None:
                _logger.warning('PoiStateComponent not found when POI captured')
                return
            self.__poiStatusItems[vehicleID][poiID] = item = PoiStatusItem(poiState)
        item.setCaptured(isCaptured=True)
        item.setInvader(vehicleID)
        self.__statsDataController.as_updatePointOfInterestS(data=item.getVO())
        return

    def __onVehicleKilled(self, victimID, *_):
        statusItems = self.__poiStatusItems.pop(victimID, {})
        for item in statusItems.values():
            self.__statsDataController.as_removePointOfInterestS(vehicleID=victimID, type=item.type)


class PoiStatusItem(object):

    def __init__(self, poiState):
        self.__state = poiState
        self.__invader = poiState.invader
        self.__type = POI_TYPE_UI_MAPPING[poiState.type]
        self.__progress = poiState.progress
        self.__status = poiState.status.statusID
        self.__isCaptured = False

    @property
    def state(self):
        return self.__state

    @property
    def invader(self):
        return self.__invader

    @property
    def type(self):
        return self.__type

    @property
    def progress(self):
        return self.__progress

    @property
    def isCaptured(self):
        return self.__isCaptured

    def update(self):
        if self.__status is PoiStatus.CAPTURING and self.__state.status.statusID is PoiStatus.COOLDOWN:
            self.setCaptured(True)
        self.__status = self.__state.status.statusID
        if self.isCaptured:
            return PoiStatusItemUpdateResult.VALID
        if self.__state.invader != self.__invader:
            self.__invader = self.__state.invader
            return PoiStatusItemUpdateResult.INVALID
        if self.__state.progress != self.__progress:
            self.__progress = self.__state.progress
            return PoiStatusItemUpdateResult.UPDATED
        return PoiStatusItemUpdateResult.VALID

    def setCaptured(self, isCaptured):
        self.__isCaptured = isCaptured

    def setInvader(self, vehId):
        self.__invader = vehId

    def getVO(self):
        return {'vehicleID': self.invader,
         'type': self.type,
         'progress': 1 if self.isCaptured else self.progress / 100}
