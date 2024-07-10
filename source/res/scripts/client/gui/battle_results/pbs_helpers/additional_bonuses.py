# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/pbs_helpers/additional_bonuses.py
import typing
from constants import PREMIUM_TYPE
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from gui.impl.gen.view_models.views.lobby.battle_results.premium_plus_model import PremiumXpBonusRestriction
from gui.Scaleform.genConsts.BATTLE_RESULTS_PREMIUM_STATES import BATTLE_RESULTS_PREMIUM_STATES as BRPS
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
ACCOUNT_STATUS_TO_BRPS = {(False, False, False): {(True, True): BRPS.PLUS_INFO,
                         (False, True): BRPS.PLUS_INFO,
                         (True, False): BRPS.PREMIUM_INFO,
                         (False, False): BRPS.PREMIUM_INFO},
 (True, False, False): {(True, True): BRPS.PREMIUM_ADVERTISING,
                        (False, True): BRPS.PREMIUM_ADVERTISING,
                        (True, False): BRPS.PREMIUM_ADVERTISING,
                        (False, False): BRPS.PREMIUM_ADVERTISING},
 (False, True, False): {(True, True): BRPS.PREMIUM_BONUS,
                        (False, True): BRPS.PLUS_EARNINGS,
                        (True, False): BRPS.PREMIUM_BONUS,
                        (False, False): BRPS.PREMIUM_EARNINGS},
 (False, False, True): {(True, True): BRPS.PREMIUM_BONUS,
                        (False, True): BRPS.PLUS_EARNINGS,
                        (True, False): BRPS.PREMIUM_INFO,
                        (False, False): BRPS.PREMIUM_INFO},
 (True, True, False): {(True, True): BRPS.PREMIUM_BONUS,
                       (False, True): BRPS.PLUS_EARNINGS,
                       (True, False): BRPS.PREMIUM_BONUS,
                       (False, False): BRPS.PREMIUM_EARNINGS},
 (True, False, True): {(True, True): BRPS.PREMIUM_BONUS,
                       (False, True): BRPS.PLUS_EARNINGS,
                       (True, False): BRPS.PREMIUM_ADVERTISING,
                       (False, False): BRPS.PREMIUM_ADVERTISING},
 (False, True, True): {(True, True): BRPS.PREMIUM_BONUS,
                       (False, True): BRPS.PLUS_YOU_ROCK,
                       (True, False): BRPS.PREMIUM_BONUS,
                       (False, False): BRPS.PREMIUM_EARNINGS},
 (True, True, True): {(True, True): BRPS.PREMIUM_BONUS,
                      (False, True): BRPS.PLUS_YOU_ROCK,
                      (True, False): BRPS.PREMIUM_BONUS,
                      (False, False): BRPS.PREMIUM_EARNINGS}}
_ADDITIONAL_BONUS_AVAILABLE_STATUSES = {BRPS.PLUS_YOU_ROCK, BRPS.PREMIUM_BONUS, BRPS.PLUS_EARNINGS}

@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext, wotPlusController=IWotPlusController)
def getAccountStatusToBRPS(hadPremiumPlus, isBonusAppliedAlready, hasXpInBonusCaps, hasXpBonusInBonusCaps, negativeImpact=False, itemsCache=None, lobbyContext=None, wotPlusController=None):
    isWotPlusBonusEnabled = isWotPlusBonusEnabledInConfig()
    premiumPlusBonusesLeft = itemsCache.items.stats.applyAdditionalXPCount
    wotPlusBonusesLeft = itemsCache.items.stats.applyAdditionalWoTPlusXPCount
    if isWotPlusBonusEnabled and premiumPlusBonusesLeft <= 0 and wotPlusBonusesLeft <= 0:
        return BRPS.PLUS_YOU_ROCK
    if isBonusAppliedAlready:
        return BRPS.PREMIUM_BONUS
    hasPremiumPlus = itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
    if not hasXpInBonusCaps:
        state = BRPS.PREMIUM_BONUS
    elif not hasXpBonusInBonusCaps:
        if isWotPlusBonusEnabled:
            state = BRPS.PREMIUM_BONUS
        elif hasPremiumPlus:
            state = BRPS.PREMIUM_EARNINGS
        else:
            state = BRPS.PREMIUM_INFO
    else:
        isPremiumPlusBonusEnabled = lobbyContext.getServerSettings().getAdditionalBonusConfig().get('enabled', False)
        hasWotPlus = wotPlusController.isEnabled()
        bonusesAvailable = hasPremiumPlus and isPremiumPlusBonusEnabled and premiumPlusBonusesLeft > 0 or hasWotPlus and isWotPlusBonusEnabled and wotPlusBonusesLeft > 0
        hasBasicPremium = itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.BASIC)
        states = ACCOUNT_STATUS_TO_BRPS[hasBasicPremium, hasPremiumPlus, hasWotPlus]
        state = states[bonusesAvailable, isWotPlusBonusEnabled]
    if state in (BRPS.PREMIUM_INFO, BRPS.PREMIUM_ADVERTISING) and hadPremiumPlus:
        state = BRPS.PREMIUM_EARNINGS
    if state in (BRPS.PREMIUM_INFO,) and negativeImpact:
        state = BRPS.PREMIUM_ADVERTISING
    return state


@dependency.replace_none_kwargs(battleResults=IBattleResultsService, lobbyContext=ILobbyContext)
def isAdditionalXpBonusAvailable(arenaUniqueID, reusable, hasPremiumPlus, statusChecker, battleResults=None, lobbyContext=None):
    if battleResults.isAddXPBonusApplied(arenaUniqueID):
        return True
    commonInfo = reusable.common
    hasXpInBonusCaps = commonInfo.checkBonusCaps(_CAPS.XP)
    hasXpBonusInBonusCaps = commonInfo.checkBonusCaps(_CAPS.ADDITIONAL_XP_POSTBATTLE)
    isAddXpBonusEnabled = lobbyContext.getServerSettings().getAdditionalBonusConfig().get('enabled', False)
    if not hasXpInBonusCaps or not hasXpBonusInBonusCaps or not isAddXpBonusEnabled and not isWotPlusBonusEnabledInConfig():
        return False
    status = getAccountStatusToBRPS(hadPremiumPlus=reusable.isPostBattlePremiumPlus, isBonusAppliedAlready=False, hasXpInBonusCaps=hasXpInBonusCaps, hasXpBonusInBonusCaps=hasXpBonusInBonusCaps)
    return statusChecker(status, reusable, hasPremiumPlus)


def isAddXpBonusStatusAcceptable(status, _, __):
    return status in _ADDITIONAL_BONUS_AVAILABLE_STATUSES


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isGoldPiggyBankAvailaible(reusable, lobbyContext=None):
    arenaTypes = lobbyContext.getServerSettings().getArenaTypesWithGoldReserve(reusable.common.battleModifiers)
    return reusable.common.arenaBonusType in arenaTypes


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isWotPlusBonusEnabledInConfig(lobbyContext=None):
    serverSettings = lobbyContext.getServerSettings()
    return serverSettings.getAdditionalWoTPlusXPCount() > 0 and serverSettings.isAdditionalWoTPlusEnabled()


@dependency.replace_none_kwargs(battleResults=IBattleResultsService)
def getAdditionalXpBonusDiff(arenaUniqueID, battleResults=None):
    return battleResults.getAdditionalXPValue(arenaUniqueID)


def getAdditionalXPFactor10FromResult(result, reusable):
    vehicleId = reusable.vehicles.getVehicleID(reusable.getPlayerInfo().dbID)
    vehicleInfo = reusable.vehicles.getVehicleInfo(vehicleId)
    additionalXPFactor10 = result.get(vehicleInfo.intCD, {}).get('additionalXPFactor10', 1)
    return int(additionalXPFactor10 / 10) if additionalXPFactor10 else 1


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, itemsCache=IItemsCache)
def getLeftAdditionalBonus(hasWotPlus, hasPremiumPlus, wasPremiumPlus=False, lobbyContext=None, itemsCache=None):
    applyAdditionalXPCount, leftWotPremAdditionalXPCount = (0, 0)
    hasAccessToAdditionalBonus = False
    if lobbyContext.getServerSettings().getAdditionalBonusConfig().get('enabled', False):
        leftCount = itemsCache.items.stats.applyAdditionalXPCount
        if hasPremiumPlus:
            applyAdditionalXPCount += leftCount
            hasAccessToAdditionalBonus = True
        elif wasPremiumPlus:
            hasAccessToAdditionalBonus = True
            leftWotPremAdditionalXPCount = leftCount
    if hasWotPlus and isWotPlusBonusEnabledInConfig():
        applyAdditionalXPCount += itemsCache.items.stats.applyAdditionalWoTPlusXPCount
        hasAccessToAdditionalBonus = True
    return (hasAccessToAdditionalBonus, applyAdditionalXPCount, leftWotPremAdditionalXPCount)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, battleResults=IBattleResultsService)
def getAdditionalXpBonusStatus(arenaUniqueID, isPersonalTeamWin, vehicleCD, isBonusAvailable, itemsCache=None, battleResults=None):
    if battleResults.isAddXPBonusApplied(arenaUniqueID):
        return PremiumXpBonusRestriction.ISAPPLIED
    if not isBonusAvailable:
        return PremiumXpBonusRestriction.INVALIDBATTLETYPE
    if not isPersonalTeamWin:
        return PremiumXpBonusRestriction.ISNOTVICTORY
    if not battleResults.isAddXPBonusEnabled(arenaUniqueID):
        return PremiumXpBonusRestriction.DEPRECATEDRESULTS
    item = itemsCache.items.getItemByCD(vehicleCD)
    if not item.isInInventory or not item.activeInNationGroup:
        return PremiumXpBonusRestriction.NOVEHICLE
    if not battleResults.isXPToTManSameForArena(arenaUniqueID):
        if battleResults.getVehicleForArena(arenaUniqueID).isXPToTman:
            return PremiumXpBonusRestriction.FASTEREDUCATIONCREWACTIVE
        return PremiumXpBonusRestriction.FASTEREDUCATIONCREWNOTACTIVE
    return PremiumXpBonusRestriction.NOCREW if not battleResults.isCrewSameForArena(arenaUniqueID) else PremiumXpBonusRestriction.NORESTRICTION
