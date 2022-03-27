# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/spawn_ctrl/ctrl.py
import logging
import typing
from collections import defaultdict
import BigWorld
import constants
from gui.battle_control.arena_info.interfaces import IRTSSpawnController
from gui.battle_control.controllers.commander.vos_collections import RTSVehicleInfoSortKey
from gui.battle_control.controllers.commander.spawn_ctrl.common import createPointData, createChosenPointData
from gui.battle_control.controllers.commander.spawn_ctrl.entities import SpawnEntity, SupplyContainerEntity
from gui.battle_control.controllers.commander.spawn_ctrl.interfaces import ISpawnEntity, ISupplyContainerEntity
from gui.battle_control.controllers.spawn_ctrl import SpawnController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Optional, List, Dict, DefaultDict, Any, Set
    from gui.battle_control.controllers.commander.spawn_ctrl.common import PointData
_logger = logging.getLogger(__name__)

class RTSSpawnController(SpawnController, IRTSSpawnController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _ANY_VEHICLE_TYPE = '<any>'

    def __init__(self):
        super(RTSSpawnController, self).__init__()
        self.__selectedEntity = None
        self.__vehiclesOrder = []
        self.__suppliesOrder = []
        self.__suppliesByClassTag = {}
        self.__placedEntities = {}
        self.__pointsByID = {}
        self.__pointsByEntityID = defaultdict(set)
        self.__unsuitablePoints = []
        return

    @property
    def placedEntities(self):
        return self.__placedEntities

    def stopControl(self):
        self.__clear()
        super(RTSSpawnController, self).stopControl()

    @property
    def selectedEntity(self):
        return self.__selectedEntity

    @property
    def selectedEntityID(self):
        selectedEntity = self.__selectedEntity
        return None if selectedEntity is None else selectedEntity.getID()

    @property
    def selectedEntityType(self):
        selectedEntity = self.__selectedEntity
        return None if selectedEntity is None else selectedEntity.getType()

    def updatePoints(self, chosenPoints, unsuitablePoints):
        oldChosenEntities = self.__placedEntities.copy()
        listUpdated = False
        arenaDP = self.__sessionProvider.getArenaDP()
        for point in chosenPoints:
            entityID = point['entityID']
            if entityID == arenaDP.getPlayerVehicleID():
                continue
            isUpdated = self._chooseEntityPoint(entityID, createChosenPointData(point))
            listUpdated |= isUpdated
            oldChosenEntities.pop(entityID, None)

        for entity in oldChosenEntities.itervalues():
            self.__changeEntityChosenPoint(entity, None)
            listUpdated = True

        if self.__unsuitablePoints != unsuitablePoints:
            self.__unsuitablePoints = unsuitablePoints
            listUpdated = True
        if listUpdated:
            _logger.debug('Server update from server with different data has been received')
            self.__selectAnotherItem()
            self.__sendViewPointsUpdate()
        return

    def iterAvailablePointsByEntityID(self, entityID):
        for pointID in self.__pointsByEntityID.get(entityID, set()):
            pointData = self.getPointDataByID(pointID, withChosen=False)
            if pointData is not None:
                yield (pointID, pointData)

        return

    def getPointDataByID(self, pointID, withChosen=True):
        if withChosen:
            for entity in self.__placedEntities.itervalues():
                chosenPointData = entity.chosenPointData
                if chosenPointData is None:
                    continue
                if chosenPointData.guid == pointID:
                    return chosenPointData

        return None if pointID in self.__unsuitablePoints else self.__pointsByID.get(pointID)

    def getSortedVehicleInfos(self):
        arenaDP = self.__sessionProvider.getArenaDP()
        return sorted(arenaDP.getVehiclesInfoIterator(), key=RTSVehicleInfoSortKey)

    def getSuppliesByClassTag(self, entityType):
        return self.__suppliesByClassTag.get(entityType)

    def updateAvailablePoints(self, availablePoints):
        self.__clear()
        reservedPointsTags = set()
        for p in availablePoints:
            pGuid = p['guid']
            self.__pointsByID[pGuid] = createPointData(p)
            reservedPointsTags.add(p['vehicleTag'])

        arenaDP = self.__sessionProvider.getArenaDP()
        for vInfo in self.getSortedVehicleInfos():
            if vInfo.isObserver() or vInfo.isCommander() or arenaDP.isEnemyTeam(vInfo.team):
                continue
            classTag = vInfo.vehicleType.classTag
            if classTag is None:
                continue
            suppliesContainer = self.__suppliesByClassTag.get(classTag)
            if suppliesContainer is None:
                suppliesContainer = SupplyContainerEntity(classTag)
                self.__suppliesOrder.append(suppliesContainer)
                self.__suppliesByClassTag[classTag] = suppliesContainer
            vehicleId = vInfo.vehicleID
            if vInfo.isSupply():
                suppliesContainer.addSupply(vehicleId)
            else:
                self.__vehiclesOrder.append(SpawnEntity(classTag, vehicleId))
            vehicleType = vInfo.vehicleType
            vehTags = vehicleType.tags
            for p in availablePoints:
                mainVtag = p['vehicleTag']
                if mainVtag:
                    isSuitableForSelection = mainVtag in vehTags
                else:
                    vehPrefType = p['vehiclePreferableType']
                    isSuitableForSelection = not reservedPointsTags.intersection(vehTags) and (vehPrefType == self._ANY_VEHICLE_TYPE or vehPrefType in vehTags)
                if isSuitableForSelection:
                    self.__pointsByEntityID[vehicleId].add(p['guid'])

        super(RTSSpawnController, self).showSpawnPoints(availablePoints)
        self.__selectAnotherItem()
        self.__sendViewPointsUpdate()
        return

    def selectSupplyByClassTag(self, classTag):
        suppliesContainer = self.getSuppliesByClassTag(classTag)
        if suppliesContainer is None:
            return
        else:
            if not self.__trySelectAnyNotPlacedEntity(suppliesContainer.supplies):
                self.selectEntity(suppliesContainer.getID())
            return

    def selectEntity(self, entityID):
        if self.selectedEntityID == entityID:
            return
        else:
            if entityID is None:
                self.__selectedEntity = None
            else:
                for entity in self.__iterSpawnEntities():
                    if entity.getID() == entityID:
                        if entity.isSupply:
                            suppliesContainer = self.__suppliesByClassTag[entity.getType()]
                            suppliesContainer.selectSupply(entity)
                        self.__selectedEntity = entity
                        break

            for vC in self._viewComponents:
                vC.onEntitySelected()

            return

    def unselectEntity(self):
        self.selectEntity(None)
        return

    def resetSelection(self):
        for entity in self.__iterSpawnEntities():
            self.__changeEntityChosenPoint(entity, None)

        self.__sendViewPointsUpdate()
        BigWorld.player().cell.autoChoosePoints(False)
        self.unselectEntity()
        self.__selectAnotherItem()
        return

    def autoChoosePoints(self):
        BigWorld.player().cell.autoChoosePoints(True)
        self.unselectEntity()

    def chooseSpawnKeyPoint(self, chosenPointID):
        pointData = self.getPointDataByID(chosenPointID)
        if pointData is None:
            _logger.error('Could not find data for provided point! pointID=%s', chosenPointID)
            return
        else:
            for entity in self.__iterSpawnEntities():
                chosenData = entity.chosenPointData
                if chosenData is not None and chosenPointID == chosenData.guid:
                    self.selectEntity(entity.getID())
                    return

            selectedEntityID = self.selectedEntityID
            if selectedEntityID is not None:
                for pointID, pointData in self.iterAvailablePointsByEntityID(selectedEntityID):
                    if pointID == chosenPointID:
                        self._invokeRemoteChooseMethod(chosenPointID, selectedEntityID)
                        self.__selectAnotherItem()
                        return

            _logger.error('Could not select a point id=%s! The point is not suitable for selected entity=%s', chosenPointID, self.__selectedEntity)
            return

    def _invokeRemoteChooseMethod(self, pointId, entityID=None):
        BigWorld.player().cell.rtsSpawnKeyPointAvatar.chooseSpawnKeyPoint(pointId, self.selectedEntityID)

    def _invokeRemoteApplyMethod(self):
        BigWorld.player().cell.rtsSpawnKeyPointAvatar.placeAllVehicles()

    def __clear(self):
        self.__vehiclesOrder = []
        self.__suppliesOrder = []
        self.__suppliesByClassTag.clear()
        self.__placedEntities.clear()
        self.__pointsByID.clear()
        self.__pointsByEntityID.clear()
        self.__unsuitablePoints = []
        self.__selectedEntity = None
        return

    def _chooseEntityPoint(self, entityID, pointData):
        for entity in self.__iterSpawnEntities():
            if entity.getID() != entityID:
                continue
            chosenPointData = entity.chosenPointData
            if chosenPointData is None or chosenPointData.guid != pointData.guid:
                self.__changeEntityChosenPoint(entity, pointData)
                return True

        return False

    def __changeEntityChosenPoint(self, entity, pointData):
        entity.chosenPointData = pointData
        if pointData is not None:
            self.__placedEntities[entity.getID()] = entity
        else:
            self.__placedEntities.pop(entity.getID(), None)
        return

    def __iterSpawnOrContainerEntities(self, startID=None):
        wasFound = startID is None
        tail = []
        entities = self.__suppliesOrder
        entities.extend(self.__vehiclesOrder)
        for entity in entities:
            if not wasFound:
                if entity.getID() != startID:
                    tail.append(entity)
                    continue
                wasFound = True
            yield entity

        for entity in tail:
            yield entity

        return

    def __iterSpawnEntities(self, startID=None):
        for entity in self.__iterSpawnOrContainerEntities(startID):
            if entity.isSupply:
                for supply in entity.supplies:
                    yield supply

            yield entity

    def __selectAnotherItem(self):
        if self.__sessionProvider.arenaVisitor.getArenaBonusType() == constants.ARENA_BONUS_TYPE.RTS_BOOTCAMP:
            return
        if not self.__trySelectAnyNotPlacedEntity(self.__iterSpawnEntities(self.selectedEntityID)):
            self.unselectEntity()

    def __trySelectEntity(self, entity):
        canSelect = not entity.isSettled
        if canSelect:
            self.selectEntity(entity.getID())
        return canSelect

    def __trySelectAnyNotPlacedEntity(self, entities):
        return any((self.__trySelectEntity(e) for e in entities))

    def __sendViewPointsUpdate(self):
        for vC in self._viewComponents:
            vC.updatePointsList()
