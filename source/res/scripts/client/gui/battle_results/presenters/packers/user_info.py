# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/user_info.py
import typing
from constants import DEATH_REASON_ALIVE
from gui.battle_results.pbs_helpers.common import isRealNameVisible, isPersonalBattleResult, getUserNames
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.battle_results.presenters.packers.interfaces import IBattleResultsPacker
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo

class PersonalInfo(IBattleResultsPacker):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, battleResults):
        reusable, results = battleResults.reusable, battleResults.results
        vehicleSumInfo = reusable.getPersonalVehiclesInfo(results[_RECORD.PERSONAL])
        UserNames.packBaseUserNames(model.userNames, reusable.getPlayerInfo(), vehicleSumInfo, battleResults)
        UserStatus.packUserStatus(model.userStatus, battleResults, vehicleSumInfo)


class UserNames(object):
    __slots__ = ()

    @classmethod
    def packBaseUserNames(cls, model, playerInfo, vehicleInfo, battleResults):
        cls._packNames(model, playerInfo, battleResults)
        model.setClanAbbrev(playerInfo.clanAbbrev)
        model.setIsTeamKiller(vehicleInfo.isTeamKiller)
        model.setIsKilled(vehicleInfo.deathReason > DEATH_REASON_ALIVE)

    @classmethod
    def packFullUserNames(cls, model, vehicleInfo, battleResults):
        playerInfo = vehicleInfo.player
        cls.packBaseUserNames(model, playerInfo, vehicleInfo, battleResults)
        model.setIgrType(playerInfo.igrType)
        if playerInfo.dbID:
            cls._setBadges(model, battleResults.reusable, playerInfo.dbID)

    @classmethod
    def _packNames(cls, model, playerInfo, battleResults):
        isRealNameShown = isRealNameVisible(battleResults.reusable, playerInfo)
        userNames = getUserNames(playerInfo, isRealNameShown)
        model.setUserName(userNames.displayedName)
        model.setHiddenUserName(userNames.hiddenName)
        model.setIsFakeNameVisible(userNames.isFakeNameVisible)

    @classmethod
    def _setBadges(cls, model, reusable, playerDbID):
        if not playerDbID:
            return
        else:
            avatarInfo = reusable.getAvatarInfo(playerDbID)
            if avatarInfo is None:
                return
            badgeInfo = avatarInfo.getFullBadgeInfo()
            suffixBadge = avatarInfo.suffixBadge
            cls._packBadges(model, badgeInfo, suffixBadge)
            return

    @classmethod
    def _packBadges(cls, model, badgeInfo, suffixBadge):
        if badgeInfo is not None:
            model.badge.setBadgeID(badgeInfo.getIconPostfix())
            level = badgeInfo.getDynamicContent()
            model.badge.setLevel(level if level is not None else '')
        model.suffixBadge.setBadgeID(str(suffixBadge) if suffixBadge else '')
        return


class AccountInfo(UserNames):
    __slots__ = ()

    @classmethod
    def _packNames(cls, model, playerInfo, battleResults):
        model.setUserName(playerInfo.realName)
        model.setFakeUserName(playerInfo.fakeName)
        model.setAnonymizer(playerInfo.isAnonymized())

    @classmethod
    def _packBadges(cls, model, badgeInfo, suffixBadge):
        if badgeInfo is not None:
            model.setBadge(badgeInfo.getIconPostfix())
        model.setSuffixBadge(str(suffixBadge) if suffixBadge else '')
        return


class UserStatus(object):
    _USER_INFO_PACKER = UserNames

    @classmethod
    def packUserStatus(cls, model, battleResults, vehicleSumInfo):
        reusable = battleResults.reusable
        model.setDeathReason(vehicleSumInfo.deathReason)
        model.setIsLeftBattle(reusable.personal.avatar.isPrematureLeave)
        killerVehicleID = vehicleSumInfo.killerID
        if killerVehicleID:
            killerInfo = reusable.getPlayerInfoByVehicleID(killerVehicleID)
            killerVehicleInfo = reusable.vehicles.getVehicleInfo(killerVehicleID)
            cls._USER_INFO_PACKER.packBaseUserNames(model.killer, killerInfo, killerVehicleInfo, battleResults)


class PlayerInfo(object):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, battleResults, vehicleSumInfo):
        playerInfo = vehicleSumInfo.player
        model.setSquadIndex(playerInfo.squadIndex)
        model.setDatabaseID(playerInfo.dbID)
        model.setIsPersonal(isPersonalBattleResult(vehicleSumInfo, battleResults))
        cls._packAccountInfo(model, battleResults, vehicleSumInfo)

    @classmethod
    def _packAccountInfo(cls, model, battleResults, vehicleSumInfo):
        UserNames.packFullUserNames(model.userNames, vehicleSumInfo, battleResults)
        UserStatus.packUserStatus(model.userStatus, battleResults, vehicleSumInfo)
