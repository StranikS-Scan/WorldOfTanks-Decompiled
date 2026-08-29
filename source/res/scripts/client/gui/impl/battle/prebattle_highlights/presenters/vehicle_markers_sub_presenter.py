# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/prebattle_highlights/presenters/vehicle_markers_sub_presenter.py
from __future__ import absolute_import
import BigWorld
import Math
import typing
import constants
import nations
from GUI import WGMarkerPositionController
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import isPremium
from gui.battle_control.controllers.prebattle_highlights.pbh_constants import MARKER_X_FACTOR, MARKER_Y_FACTOR
from gui.impl.gen.view_models.views.battle.prebattle_highlights.prebattle_highlights_marker_model import PrebattleHighlightsMarkerModel
from gui.prestige.prestige_helpers import fillPrestigeEmblemModel
from helpers import dependency
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from skeletons.gui.battle_session import IBattleContext
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO, VehicleTypeInfoVO, PlayerInfoVO
    from gui.impl.gen.view_models.common.user_name_model import UserNameModel
    from gui.impl.gen.view_models.common.badge_model import BadgeModel
    from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
    from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel
    from gui.battle_control.arena_info.player_format import PlayerFormatResult

class VehicleMarkersSubPresenter(SubModelPresenter):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, viewModel, parentView):
        super(VehicleMarkersSubPresenter, self).__init__(viewModel, parentView)
        self.__vehiclesData = None
        self.__markerCtrl = None
        self.__battleContext = None
        return

    def packModel(self):
        self.__vehiclesData = self.__sessionProvider.dynamic.prebattleHighlightsController.vehiclesData
        if not self.__vehiclesData:
            return
        self.__battleContext = self.__sessionProvider.getCtx()
        self.__initMarkers()

    def finalize(self):
        super(VehicleMarkersSubPresenter, self).finalize()
        self.__vehiclesData = None
        self.__battleContext = None
        if self.__markerCtrl is not None:
            self.__markerCtrl.clear()
            self.__markerCtrl = None
        return

    def __initMarkers(self):
        self.__markerCtrl = WGMarkerPositionController()
        self.__markerCtrl.clear()
        markers = self.getViewModel()
        markers.clear()
        for vID, vehData in self.__vehiclesData.items():
            markerModel = PrebattleHighlightsMarkerModel()
            markerModel.setPersonal(self.__battleContext.isCurrentPlayer(vID))
            markerModel.setVehId(vID)
            vehEntity = BigWorld.entities.get(vID)
            vehPos = vehData['translation']
            height, _ = vehEntity.appearance.computeVehicleHeight(vehEntity.appearance.collisions)
            markerPosition = Math.Vector3(vehPos[0] + MARKER_X_FACTOR, vehPos[1] + height + MARKER_Y_FACTOR, vehPos[2])
            self.__markerCtrl.add(markerModel.proxy, markerPosition)
            markerModel.setPosx(markerPosition[0])
            markerModel.setPosy(markerPosition[1])
            vehicle = vehData['info']
            self.__setVehicleInfo(markerModel.vehicle, vehicle)
            self.__setPrestigeInfo(markerModel.prestigeEmblem, vehicle)
            self.__setPlayerInfo(markerModel.userName, vehicle)
            markerModel.setSquadIndex(vehicle.squadIndex)
            markers.addViewModel(markerModel)

        markers.invalidate()

    def __setVehicleInfo(self, model, vehicle):
        vehicleType = vehicle.vehicleType
        model.setIsPremium(isPremium(vehicleType.tags))
        model.setName(vehicleType.shortNameWithPrefix)
        model.setLongName(vehicleType.name)
        model.setTechName(vehicleType.guiName)
        model.setTier(vehicleType.level)
        model.setRoleKey(constants.ROLE_TYPE_TO_LABEL.get(vehicleType.role))
        model.setType(set(vehicles.VEHICLE_CLASS_TAGS & vehicleType.tags).pop())
        model.setNation(nations.NAMES[vehicleType.nationID])
        model.setVehicleCD(vehicleType.compactDescr)
        model.setTags(','.join(vehicleType.tags))

    def __setPrestigeInfo(self, model, vehicle):
        fillPrestigeEmblemModel(model, vehicle.prestigeLevel, vehicle.vehicleType.compactDescr)

    def __setPlayerInfo(self, model, vehicle):
        playerInfo = vehicle.player
        battlePlayer = self.__battleContext.getPlayerFullNameParts(vehicle.vehicleID)
        model.setUserName(playerInfo.name)
        model.setClanAbbrev(battlePlayer.clanAbbrev)
        model.setHiddenUserName(playerInfo.fakeName)
        model.setIgrType(playerInfo.igrType)
        model.setIsTeamKiller(vehicle.isTeamKiller())
        personalVehId = avatar_getter.getPlayerVehicleID()
        personalPrebattleID = self.__battleContext.getVehicleInfo(personalVehId).prebattleID
        isCurrentPlayer = self.__battleContext.isCurrentPlayer(vehicle.vehicleID)
        validPrebattle = vehicle.prebattleID > 0 and vehicle.prebattleID == personalPrebattleID
        condition = isCurrentPlayer or validPrebattle
        model.setIsFakeNameVisible(False if condition else playerInfo.name != playerInfo.fakeName)
        model.setDatabaseID(playerInfo.accountDBID)
        badgeModel = model.badge
        badgeModel.setBadgeID(str(vehicle.selectedBadge))
        suffixBadgeModel = model.suffixBadge
        suffixBadgeModel.setBadgeID(str(vehicle.selectedSuffixBadge))
