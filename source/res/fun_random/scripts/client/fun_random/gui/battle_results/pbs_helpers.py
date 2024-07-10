# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/pbs_helpers.py
import typing
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from fun_random_common.fun_constants import UNKNOWN_EVENT_ID
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_random_reward_item_model import FunRewardTypes
from gui.impl import backport
from gui.battle_results.pbs_helpers.economics import getCreditsRecords
from gui.battle_results.settings import CurrenciesConstants
from gui.Scaleform.genConsts.BATTLE_RESULTS_PREMIUM_STATES import BATTLE_RESULTS_PREMIUM_STATES as BRPS
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IFunRandomController
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.impl.gen_utils import DynAccessor
    from fun_random.gui.feature.sub_modes.base_sub_mode import IFunSubMode
_CURRENCY_TO_PREM_BONUS_CAPS_MAP = {CurrenciesConstants.CREDITS: _CAPS.PREM_CREDITS,
 CurrenciesConstants.XP_COST: _CAPS.PREM_XP,
 CurrenciesConstants.FREE_XP: _CAPS.PREM_XP,
 CurrenciesConstants.TMEN_XP: _CAPS.PREM_TMEN_XP}
_ADD_XP_BONUS_AVAILABLE_STATUSES = {BRPS.PLUS_YOU_ROCK, BRPS.PREMIUM_BONUS, BRPS.PLUS_EARNINGS}
_ADD_XP_BONUS_AVAILABLE_STATUSES_FOR_PREM = {BRPS.PREMIUM_EARNINGS, BRPS.PLUS_INFO}

def isCreditsShown(value, hasFines, _, reusable):
    return value > 0 or hasFines and reusable.common.checkBonusCaps(_CAPS.CREDITS)


def isCrystalShown(value, hasFines, _, __):
    return value > 0


def isGoldShown(value, hasFines, rewardValues, reusable):
    return value > 0 and not isCreditsShown(rewardValues.get(FunRewardTypes.CREDITS, 0), hasFines, rewardValues, reusable)


def isXpShown(value, hasFines, _, reusable):
    return value > 0 or hasFines and reusable.common.checkBonusCaps(_CAPS.XP)


def isFreeXpShown(value, hasFines, rewardValues, reusable):
    hasXp = isXpShown(rewardValues.get(FunRewardTypes.XP, 0), hasFines, rewardValues, reusable)
    return not hasXp and (value > 0 or hasFines and reusable.common.checkBonusCaps(_CAPS.FREE_XP))


@dependency.replace_none_kwargs(funRandomCtrl=IFunRandomController)
def isTmenXpShown(value, _, __, reusable, funRandomCtrl=None):
    subMode = funRandomCtrl.subModesHolder.getSubMode(getEventID(reusable))
    return subMode.getSettings().client.postbattle.get('isCrewXpShown') if subMode is not None else False


def isPremiumAdvertisingShown(currencyType, battleResults):
    reusable = battleResults.reusable
    if reusable.isPostBattlePremiumPlus:
        return False
    else:
        bonusCaps = _CURRENCY_TO_PREM_BONUS_CAPS_MAP.get(currencyType)
        return reusable.common.checkBonusCaps(bonusCaps) if bonusCaps is not None else False


def getAdvertising(extractor, record, label, battleResults):
    records = extractor(battleResults.reusable).alternative
    premFactor = records.getFactor(record)
    return backport.text(label(), value=int((premFactor - 1.0) * 100))


def getEventID(reusable):
    return reusable.personal.avatar.extensionInfo.get('funEventID', UNKNOWN_EVENT_ID)


def getTmenXp(reusable):
    personalResults = reusable.personal
    intCD, _ = first(personalResults.getVehicleItemsIterator())
    return personalResults.xpProgress.get(intCD, {}).get('xpByTmen', [])


def getTotalTMenXPToShow(reusable, _=None, __=None):
    return sum((item[1] for item in getTmenXp(reusable)))


def getTotalGoldToShow(reusable):
    records = getCreditsRecords(reusable).extra
    return sum([ records.findRecord(recordName) for recordName in ('eventGoldList_',) ])


def isFunAddXpBonusStatusAcceptable(status, reusable, hasPremiumPlus):
    if status in _ADD_XP_BONUS_AVAILABLE_STATUSES:
        return True
    if status in _ADD_XP_BONUS_AVAILABLE_STATUSES_FOR_PREM and (hasPremiumPlus or reusable.personal.isPremiumPlus and reusable.isPersonalTeamWin()):
        return True
    return False
