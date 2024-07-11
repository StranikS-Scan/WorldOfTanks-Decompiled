# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/battle/races_hud/player_list_component.py
import typing
from collections import namedtuple
from races.gui.impl.gen.view_models.views.battle.races_hud.player_record_model import PlayerRecordModel
import BigWorld
import CGF
import Math
from helpers import dependency
from races_common.races_common_cgf.races_path_mechanics import RacesPathController
from races_common.races_constants import PATH_DETECTOR_RADIUS, PATH_DETECTOR_HEIGHT, PATH_DETECTOR_DEEP
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Iterator
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
    from skeletons.gui.battle_session import IArenaDataProvider

class RacePlayerRecord(namedtuple('RacePlayerRecord', ['name',
 'clanAbbrev',
 'isReady',
 'vehicleGuiName',
 'weight'])):

    def __eq__(self, other):
        return isinstance(other, self.__class__) and (other.name, other.isReady) == (self.name, self.isReady)

    def getViewModel(self):
        model = PlayerRecordModel()
        model.setName(self.name if self.name else '')
        model.setClanAbbrev(self.clanAbbrev if self.clanAbbrev else '')
        model.setIsReady(self.isReady)
        model.setVehicleGuiName(self.vehicleGuiName)
        return model

    @classmethod
    def createFromVehicleInfoVO(cls, infoVO, weight):
        return cls(infoVO.player.name, infoVO.player.clanAbbrev, infoVO.isReady(), infoVO.vehicleType.guiName, weight)


class PlayerListComponent(object):
    __slots__ = ('__positionList', '__spaceID')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PlayerListComponent, self).__init__()
        self.__positionList = []
        self.__spaceID = -1

    def getSpaceID(self):
        if self.__spaceID == -1:
            player = BigWorld.player()
            if player:
                self.__spaceID = player.spaceID
        return self.__spaceID

    def __getArenaInfoComponent(self):
        arenaInfo = self.__sessionProvider.arenaVisitor.getArenaInfo()
        if arenaInfo is not None:
            if arenaInfo:
                return arenaInfo.dynamicComponents.get('arenaInfoRacesComponent', None)
        return

    def updatePlayerList(self, model):
        arenaDP = self.__sessionProvider.getArenaDP()
        vehicles = arenaDP.getVehiclesInfoIterator()
        positionList = [ RacePlayerRecord.createFromVehicleInfoVO(vInfo, self.__getVehicleWeight(vInfo.vehicleID)) for vInfo in vehicles ]
        positionList.sort(key=lambda x: x.weight)
        if positionList != self.__positionList:
            playerList = model.getPlayerList()
            playerList.clear()
            playerList.reserve(len(positionList))
            for item in positionList:
                playerList.addViewModel(item.getViewModel())

            playerList.invalidate()
            self.__positionList = positionList

    def __getVehicleWeight(self, vehicleID):
        return (self.__getFinishedVehiclePosition(vehicleID), self.__getVehicleDistanceToFinish(vehicleID))

    def __getVehicleDistanceToFinish(self, vehicleID):
        vehicle = BigWorld.entity(vehicleID)
        raceVehicle = vehicle.dynamicComponents.get('raceVehicleComponent') if BigWorld.entity(vehicleID) else None
        return raceVehicle.currentDistanceToFinish if raceVehicle else self.__getProjByArenaPosition(vehicleID)

    def __getFinishedVehiclePosition(self, vehicleID):
        arenaInfo = self.__getArenaInfoComponent()
        if arenaInfo is not None:
            position = arenaInfo.getPositionById(vehicleID)
            if position > 0:
                return position
            return float('inf')
        else:
            return float('inf')

    def __getProjByArenaPosition(self, vehicleID):
        vehiclePosition = self.__sessionProvider.arenaVisitor.getArenaPositions().get(vehicleID, None)
        if vehiclePosition is not None:
            positionManager = CGF.getManager(self.getSpaceID(), RacesPathController)
            if positionManager:
                vehiclePositionVector = Math.Vector3(vehiclePosition)
                proj = positionManager.getPathProject(vehiclePositionVector, vehiclePositionVector - Math.Vector3(0, -PATH_DETECTOR_DEEP, 0), PATH_DETECTOR_RADIUS, PATH_DETECTOR_HEIGHT)
                if proj is not None:
                    return proj.getDistanceToLastNode()
        return float('inf')
