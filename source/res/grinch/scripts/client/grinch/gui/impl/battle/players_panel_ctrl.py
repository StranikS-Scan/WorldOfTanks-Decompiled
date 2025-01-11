# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/battle/players_panel_ctrl.py
import logging
from typing import TYPE_CHECKING
from constants import IS_DEVELOPMENT
from grinch.cgf.presents import getScoreComponent
from grinch.gui.impl.battle import getTeamColorModelData
from grinch.gui.impl.gen.view_models.views.battle import grinch_player_model as grModel
from grinch.gui.impl.gen.view_models.views.battle.grinch_player_model import VehicleTypeEnum
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.shared.badges import buildBadge
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if TYPE_CHECKING:
    from typing import Tuple, Sequence, List
    import gui.shared.gui_items.badge as badges
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO
    from grinch.gui.impl.gen.view_models.views.battle.grinch_hud_view_model import GrinchHudViewModel
    from skeletons.gui.battle_session import IArenaDataProvider
_logger = logging.getLogger(__name__)
_VEH_TYPES_SORT_ORDER = (VehicleTypeEnum.HEAVYTANK, VehicleTypeEnum.MEDIUMTANK, VehicleTypeEnum.LIGHTTANK)

class PlayersPanelCtrl(IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hudRef, teamGuiOrder):
        super(PlayersPanelCtrl, self).__init__()
        self._points = dict()
        self.__hudRef = hudRef
        self.__teamGuiOrder = teamGuiOrder
        self.__init()

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        self.__updateTeam(vo.team)

    def updateVehiclesInfo(self, updated, arenaDP):
        self.__updateByVoSet(tuple([ vo for _, vo in updated ]))

    def invalidateArenaInfo(self):
        self.__updateTeamInfo()
        self.__updateAllTeams()

    def addVehicleInfo(self, vInfo, _):
        if not IS_DEVELOPMENT:
            return
        self.__updateTeam(vInfo.team)

    def dispose(self):
        self.__hudRef = None
        self.__teamGuiOrder = None
        self.sessionProvider.removeArenaCtrl(self)
        scoreCmp = getScoreComponent()
        if scoreCmp:
            scoreCmp.onVehiclePointsUpdated -= self.__onVehiclePointsUpdated
            scoreCmp.onVehiclesTotalScoreUpdated -= self.__onVehiclesTotalScoreUpdated
        return

    def __init(self):
        self.sessionProvider.addArenaCtrl(self)
        scoreCmp = getScoreComponent()
        if scoreCmp:
            scoreCmp.onVehiclePointsUpdated += self.__onVehiclePointsUpdated
            scoreCmp.onVehiclesTotalScoreUpdated += self.__onVehiclesTotalScoreUpdated
        else:
            _logger.warning("Couldn't find GrinchScoreComponent at the initialization!")

    def __onVehiclesTotalScoreUpdated(self, diff):
        self.__updateByDict(diff)

    def __onVehiclePointsUpdated(self, diff):
        self.__updateByDict(diff)

    def __updateByDict(self, diff):
        voSet = []
        arenaDP = self.sessionProvider.getArenaDP()
        for vehID in diff.keys():
            vInfo = arenaDP.getVehicleInfo(vehID)
            if vInfo:
                voSet.append(vInfo)

        if voSet:
            self.__updateByVoSet(voSet)

    def __updateByVoSet(self, vInfos):
        teamsIDsToUpdate = set()
        for vInfo in vInfos:
            if vInfo.team in self.__teamGuiOrder:
                teamsIDsToUpdate.add(vInfo.team)
                if teamsIDsToUpdate == len(self.__teamGuiOrder):
                    self.__updateAllTeams()
                    return

        for team in teamsIDsToUpdate:
            self.__updateTeam(team)

    def __updateTeam(self, team):
        groupName = self.__getTeamPropName(team)
        if groupName:
            playerModels = []
            playerVehicleID = avatar_getter.getPlayerVehicleID()
            arenaDP = self.sessionProvider.getArenaDP()
            for vInfo in arenaDP.getVehiclesInfoIterator():
                if 'spawned' in vInfo.vehicleType.tags:
                    continue
                if vInfo.team != team:
                    continue
                playerModels.append(self.__createPlayerModel(vInfo, playerVehicleID, arenaDP))

            self.__updateModelWithPlayers(groupName, playerModels)

    def __updateAllTeams(self):
        playerModels = {}
        arenaDP = self.sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            if 'spawned' in vInfo.vehicleType.tags:
                continue
            groupData = self.__getTeamPropName(vInfo.team)
            if groupData:
                playerVehicleID = avatar_getter.getPlayerVehicleID()
                playerModels.setdefault(groupData, []).append(self.__createPlayerModel(vInfo, playerVehicleID, arenaDP))

        for groupName, models in playerModels.iteritems():
            self.__updateModelWithPlayers(groupName, models)

    def __updateModelWithPlayers(self, propName, playerModels):
        playerModels.sort(key=lambda item: _VEH_TYPES_SORT_ORDER.index(item.getVehicleType()))
        with self.__hudRef.viewModel.transaction() as model:
            playersGroup = model.__getattribute__(propName)
            playersModel = playersGroup.getPlayers()
            playersModel.clear()
            playersModel.reserve(len(playerModels))
            for pM in playerModels:
                playersModel.addViewModel(pM)

            playersModel.invalidate()

    def __createPlayerModel(self, vInfo, playerVehicleID, arenaDP):
        pModel = grModel.GrinchPlayerModel()
        pModel.setUserName(vInfo.player.name)
        pModel.setClanAbbrev(vInfo.player.clanAbbrev)
        pfn = self.sessionProvider.getCtx().getPlayerFullNameParts(vInfo.vehicleID, showVehShortName=False)
        fakeName = pfn.playerFakeName
        pModel.setHiddenUserName(fakeName)
        pModel.setIsFakeNameVisible(fakeName and fakeName != vInfo.player.name)
        pModel.setIgrType(not vInfo.player.igrType)
        pModel.setIsTeamKiller(vInfo.player.isTeamKiller)
        pModel.setIsKilled(not vInfo.isAlive())
        pModel.setDatabaseID(vInfo.player.accountDBID)
        if any((member.value == vInfo.vehicleType.classTag for member in grModel.VehicleTypeEnum)):
            vehTypeEnum = grModel.VehicleTypeEnum(vInfo.vehicleType.classTag)
        else:
            vehTypeEnum = grModel.VehicleTypeEnum.LIGHTTANK
            _logger.warning('Unexpected vehicle type: %s for %s', vInfo.vehicleType.classTag, vInfo.player.name)
        pModel.setVehicleType(vehTypeEnum)
        pModel.setVehicleName(vInfo.vehicleType.shortName)
        isCurrentPlatoon = False
        platoon = grModel.PlatoonEnum.NONE
        if vInfo.squadIndex > 0:
            platoon = grModel.PlatoonEnum('platoon{}'.format(vInfo.squadIndex))
            playerSquad = arenaDP.getVehicleInfo(playerVehicleID).squadIndex
            if playerSquad == vInfo.squadIndex:
                isCurrentPlatoon = True
        pModel.setPlatoon(platoon)
        pModel.setIsCurrentPlatoon(isCurrentPlatoon)
        badgeID = vInfo.selectedBadge
        badge = buildBadge(badgeID, vInfo.getBadgeExtraInfo())
        if badge:
            pModel.badge.setBadgeID(badge.getIconPostfix())
            level = badge.getDynamicContent()
            pModel.badge.setLevel(level if level is not None else '')
        suffixBadge = vInfo.selectedSuffixBadge
        pModel.suffixBadge.setBadgeID(str(suffixBadge) if suffixBadge else '')
        scoreCmp = getScoreComponent()
        if scoreCmp:
            itemsCount, _ = scoreCmp.getVehiclePoints(vInfo.vehicleID)
            totalScore = scoreCmp.getVehicleTotalScore(vInfo.vehicleID)
            pModel.setCarryingItems(itemsCount)
            pModel.setScore(totalScore)
            pModel.setIsCurrentPlayer(vInfo.vehicleID == playerVehicleID)
        else:
            _logger.warning("Couldn't display Score for vehicleID={}! GrinchScoreComponent could not be found!")
        return pModel

    def __updateTeamInfo(self):
        with self.__hudRef.viewModel.transaction() as model:
            for team in self.__teamGuiOrder:
                propName = self.__getTeamPropName(team)
                playersGroup = model.__getattribute__(propName)
                playersGroup.setTeamColor(getTeamColorModelData(team))

    def __getTeamPropName(self, team):
        if team in self.__teamGuiOrder:
            index = self.__teamGuiOrder.index(team)
            if index == 0:
                return 'allies'
            return 'enemies{}'.format(index)
        else:
            return None
