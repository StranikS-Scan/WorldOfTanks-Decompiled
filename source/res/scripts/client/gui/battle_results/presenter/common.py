# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/common.py
from collections import namedtuple
import typing
from constants import DEATH_REASON_ALIVE
from frameworks.wulf import Array
from gui.battle_results.br_helper import getKillerID, isPlayerLeftBattle, getUserNames, isOwnSquad, isBot
from gui.impl.gen.view_models.views.lobby.postbattle.currency_model import CurrencyModel
from gui.impl.gen.view_models.views.lobby.postbattle.details_stats_model import DetailsStatsModel
from gui.impl.gen.view_models.views.lobby.postbattle.details_group_model import DetailsGroupModel
from gui.impl.gen.view_models.views.lobby.postbattle.details_record_model import DetailsRecordModel
from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.premium_benefit_model import PremiumBenefitModel
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.gui_items.Vehicle import getIconResourceName, getSimpleShortUserName
from helpers import dependency
from shared_utils import first
from soft_exception import SoftException
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import ReusableInfo
    from gui.battle_results.reusable.records import ReplayRecords
    from gui.battle_results.presenter.getter.detailed_stats import CurrencyField
    from gui.battle_results.presenter.getter.getter import PostbattleFieldsGetter
    from gui.impl.gen.view_models.views.lobby.postbattle.postbattle_screen_model import PostbattleScreenModel
    from gui.impl.gen.view_models.common.user_name_model import UserNameModel
    from gui.impl.gen.view_models.views.lobby.postbattle.enemy_with_one_param_model import EnemyWithOneParamModel
    from gui.impl.gen.view_models.views.lobby.postbattle.enemy_multi_params_model import EnemyMultiParamsModel
    from gui.impl.gen.view_models.views.lobby.postbattle.rewards_model import RewardsModel
    from gui.impl.gen.view_models.views.lobby.postbattle.user_status_model import UserStatusModel
    from gui.impl.lobby.postbattle.wrappers.user_detailed_stats_model import UserDetailedStatsModel
_FinancialRecords = namedtuple('_FinancialRecords', ('main', 'additional', 'alternative'))
_XpRecords = namedtuple('_XpRecords', ('xp', 'freeXP'))

def setAccountType(model, reusable, result):
    model.setAccountType(reusable.economics.getPremiumType())


def setArenaType(model, reusable, result):
    model.setArenaType(reusable.common.arenaBonusType)


def setUserStatus(model, reusable, result):
    playerId = reusable.getPlayerInfo().dbID
    vehicleId = reusable.vehicles.getVehicleID(playerId)
    vehicleInfo = reusable.vehicles.getVehicleInfo(vehicleId)
    setBaseUserInfo(model.user, reusable, vehicleId)
    killerVehicleID = getKillerID(result, vehicleInfo.intCD)
    if killerVehicleID:
        setBaseUserInfo(model.killer.user, reusable, killerVehicleID)
        isPersonal = killerVehicleID == vehicleId
        model.killer.setIsPersonal(isPersonal)
        model.killer.setIsSameSquad(isOwnSquad(reusable, killerVehicleID) and not isPersonal)
        killerInfo = reusable.getPlayerInfoByVehicleID(killerVehicleID)
        model.killer.setIsBot(isBot(killerInfo))
    model.setIsLeftBattle(isPlayerLeftBattle(reusable))
    model.setAttackReason(vehicleInfo.deathReason)


def setBaseUserInfo(model, reusable, vehicleID):
    playerInfo = reusable.getPlayerInfoByVehicleID(vehicleID)
    model.setClanAbbrev(playerInfo.clanAbbrev)
    model.setIgrType(playerInfo.igrType)
    userNames = getUserNames(reusable, vehicleID)
    model.setUserName(userNames.displayedName)
    model.setHiddenUserName(userNames.hiddenName)
    model.setIsFakeNameVisible(userNames.isFakeNameVisible)
    shortVehicleInfo = reusable.vehicles.getVehicleInfo(vehicleID)
    model.setIsTeamKiller(shortVehicleInfo.isTeamKiller)
    model.setIsKilled(shortVehicleInfo.deathReason > DEATH_REASON_ALIVE)
    if playerInfo.dbID:
        setBadges(model, reusable, playerInfo.dbID)


def setBadges(model, reusable, playerDbID):
    if not playerDbID:
        return
    else:
        avatar = reusable.getAvatarInfo(playerDbID)
        if avatar is None:
            return
        badgeInfo = avatar.getFullBadgeInfo()
        if badgeInfo is not None:
            model.badge.setBadgeID(badgeInfo.getIconPostfix())
            level = badgeInfo.getDynamicContent()
            model.badge.setLevel(level if level is not None else '')
        suffixBadge = avatar.suffixBadge
        model.suffixBadge.setBadgeID(str(suffixBadge) if suffixBadge else '')
        return


def setBaseEnemyVehicleInfo(model, enemy):
    model.setTankType(replaceHyphenToUnderscore(enemy.vehicle.type))
    model.setTankName(replaceHyphenToUnderscore(getIconResourceName(enemy.vehicle.name)))
    model.setShortTankName(getSimpleShortUserName(enemy.vehicle))
    model.setVehicleIconName(getIconResourceName(enemy.vehicle.name))
    model.setVehicleLevel(enemy.vehicle.level)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, eventsCache=IEventsCache)
def getPremiumBenefits(getter, lobbyContext=None, eventsCache=None):
    premiumBenefits = Array()
    for field in getter.getPremiumBenefits():
        values = field.getFieldValues(lobbyContext.getServerSettings(), eventsCache)
        if not values:
            continue
        benefitItem = PremiumBenefitModel()
        benefitItem.setStringID(field.stringID)
        benefitItem.setValue(values)
        premiumBenefits.addViewModel(benefitItem)

    return premiumBenefits


def getCreditsRecords(reusable):
    baseCredits, premiumCredits, _, additionalRecords = first(reusable.economics.getMoneyRecords())
    if reusable.economics.hasAnyPremium:
        creditRecords, alternativeRecords = premiumCredits, baseCredits
    else:
        creditRecords, alternativeRecords = baseCredits, premiumCredits
    return _FinancialRecords(main=creditRecords, additional=additionalRecords, alternative=alternativeRecords)


def getCrystalsRecords(reusable):
    _, _, _, additionalRecords = first(reusable.economics.getMoneyRecords())
    crystalsRecords = reusable.economics.getUnpackedCrystalRecords()
    return None if not crystalsRecords or not reusable.economics.haveCrystalsChanged() else _FinancialRecords(main=crystalsRecords, additional=additionalRecords, alternative=None)


def getXpRecords(reusable):
    baseXP, premiumXP, baseFreeXP, premiumFreeXP = first(reusable.economics.getXPRecords())
    if reusable.economics.hasAnyPremium:
        xpRecord = premiumXP
        freeXpRecord = premiumFreeXP
    else:
        xpRecord = baseXP
        freeXpRecord = baseFreeXP
    if reusable.economics.hasAnyPremium:
        alternativeXpRecord, alternativeFreeXpRecord = baseXP, baseFreeXP
    else:
        alternativeXpRecord, alternativeFreeXpRecord = premiumXP, premiumFreeXP
    return _FinancialRecords(main=_XpRecords(xp=xpRecord, freeXP=freeXpRecord), additional=None, alternative=_XpRecords(xp=alternativeXpRecord, freeXP=alternativeFreeXpRecord))


def getTotalXPToShow(reusable, records, hasPremium):
    return reusable.economics.getXPToShow()[0] if hasPremium else records.getRecord('xpToShow')


def getTotalFreeXPToShow(records):
    return records.getRecord('freeXP')


def getTotalCreditsToShow(reusable, records, hasPremium):
    return reusable.economics.getCreditsToShow()[0] if hasPremium else records.getRecord('credits', 'originalCreditsToDraw')


def getRecordItems(records):
    if not records:
        return None
    else:
        recordItems = Array()
        recordItems.reserve(len(records))
        for record in records:
            recordItems.addViewModel(record)

        return recordItems


def createGroupModel(blockIdx, groupType):
    group = DetailsGroupModel()
    group.setBlockIdx(blockIdx.value)
    group.setType(groupType)
    return group


def createRecord(field, records):
    values = field.getFieldValues(*records)
    if not values:
        return None
    else:
        item = DetailsRecordModel()
        item.setType(DetailsStatsModel.RECORD_TYPE)
        item.setBlockIdx(field.blockIdx.value)
        item.setStringID(field.stringID)
        item.setTooltipStringID(field.tooltipStringID)
        tags = Array()
        for tag in field.tags:
            tags.addString(tag)

        item.setTags(tags)
        item.setCurrencies(values)
        return item


def setPremiumBonuses(model, reusable):
    premiumBonuses = _createPremiumBonusModel(reusable)
    if premiumBonuses is not None:
        model.setPremiumBonus(premiumBonuses)
    return


def getCurrencies(values, currencyTypes):
    if len(values) != len(currencyTypes):
        raise SoftException('Array lengths must match: {} and {}', len(values), len(currencyTypes))
    record = Array()
    record.reserve(len(values))
    for value, valueType in zip(values, currencyTypes):
        valueModel = CurrencyModel()
        valueModel.setAmount(value)
        valueModel.setType(valueType)
        record.addViewModel(valueModel)

    return record


def _createPremiumBonusModel(reusable):
    return None if reusable.economics.isPremiumPlus or reusable.economics.isActivePremiumPlus() else getCurrencies((reusable.economics.getCreditsDiff(), reusable.economics.getXPDiff()), (CurrencyModel.CREDITS, CurrencyModel.XP))
