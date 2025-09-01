# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_results/pbs_helpers.py
import typing
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from white_tiger_common.wt_constants import UNKNOWN_EVENT_ID
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_results.components.progress import isQuestCompleted
from gui.impl import backport
from gui.battle_results.pbs_helpers.economics import getDirectMoneyRecords
from gui.battle_results.settings import CurrenciesConstants
from gui.Scaleform.genConsts.BATTLE_RESULTS_PREMIUM_STATES import BATTLE_RESULTS_PREMIUM_STATES as BRPS
from gui.impl.backport import TooltipData
from helpers import dependency
from white_tiger_common.wt_constants import WT_PROGRESSION_ACHIEVEMENT
from white_tiger.gui.white_tiger_gui_constants import WT_BATTLE_QUEST_PREFIX
from helpers.dependency import replace_none_kwargs
from white_tiger.gui.wt_bonus_packers import getWTEventBonusPacker
from shared_utils import findFirst, first
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.impl.gen_utils import DynAccessor
    from gui.shared.gui_items.dossier.achievements.abstract.regular import RegularAchievement
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
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
    return value > 0 and not isCreditsShown(rewardValues.get(CURRENCIES_CONSTANTS.CREDITS, 0), hasFines, rewardValues, reusable)


def isXpShown(value, hasFines, _, reusable):
    return value > 0 or hasFines and reusable.common.checkBonusCaps(_CAPS.XP)


def isFreeXpShown(value, hasFines, rewardValues, reusable):
    hasXp = isXpShown(rewardValues.get(CURRENCIES_CONSTANTS.XP_COST, 0), hasFines, rewardValues, reusable)
    return not hasXp and (value > 0 or hasFines and reusable.common.checkBonusCaps(_CAPS.FREE_XP))


@dependency.replace_none_kwargs(wtRandomCtrl=IWhiteTigerController)
def isTmenXpShown(value, _, __, reusable, wtRandomCtrl=None):
    return False


def isPremiumAdvertisingShown(currencyType, battleResults):
    reusable = battleResults.reusable
    if reusable.isPostBattlePremiumPlus:
        return False
    else:
        bonusCaps = _CURRENCY_TO_PREM_BONUS_CAPS_MAP.get(currencyType)
        return reusable.common.checkBonusCaps(bonusCaps) if bonusCaps is not None else False


def isNonZeroValue(value, hasFines, _, __):
    return value > 0


def getAdvertising(extractor, record, label, battleResults):
    records = extractor(battleResults.reusable).alternative
    premFactor = records.getFactor(record)
    return backport.text(label(), value=int((premFactor - 1.0) * 100))


def getEventID(reusable):
    return reusable.personal.avatar.extensionInfo.get('wtEventID', UNKNOWN_EVENT_ID)


def getTmenXp(reusable):
    personalResults = reusable.personal
    intCD, _ = first(personalResults.getVehicleItemsIterator())
    return personalResults.xpProgress.get(intCD, {}).get('xpByTmen', [])


def getTotalTMenXPToShow(reusable, _=None, __=None):
    return sum((item[1] for item in getTmenXp(reusable)))


def getTotalGoldToShow(reusable):
    records = getDirectMoneyRecords(reusable).extraValue
    return sum([ records.findRecord(recordName) for recordName in ('eventGoldList_',) ])


def isWhiteTigerAddXpBonusStatusAcceptable(status, reusable, hasPremiumPlus):
    if status in _ADD_XP_BONUS_AVAILABLE_STATUSES:
        return True
    if status in _ADD_XP_BONUS_AVAILABLE_STATUSES_FOR_PREM and (hasPremiumPlus or reusable.personal.isPremiumPlus and reusable.isPersonalTeamWin()):
        return True
    return False


def packAchievementTooltipData(achievement, tooltipData, tooltipIdx):
    tooltipData[str(tooltipIdx)] = TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS, specialArgs=[achievement.getBlock(), achievement.getName(), achievement.getValue()])
    return


def getWTAchievement(battleResults):

    def isWTAchievement(achievementData):
        return None if achievementData is None else achievementData[0].getName() == WT_PROGRESSION_ACHIEVEMENT

    reusable, results = battleResults.reusable, battleResults.results
    leftAchievements, _ = reusable.personal.getAchievements(results['personal'])
    achievementData = findFirst(isWTAchievement, leftAchievements, None)
    return None if achievementData is None else achievementData[0]


def _getTokenCount(reusable, tokenName):
    questTokens = reusable.personal.avatar.extensionInfo.get('questTokensCount', {})
    return 0 if tokenName not in questTokens else questTokens[tokenName].get('diff', 0)


def getEquipCoin(reusable):
    return reusable.personal.avatar.extensionInfo.get('eventEquipCoin', 0)


def getBattlepassPoints(reusable):
    return reusable.battlePassProgress.questPoints


def _wtBattleQuestPredicate(idSubset, quest):
    ourQuest = quest.getID() in idSubset
    return ourQuest and quest.isCompleted()


def _extractWtBattleQuests(questProgress):
    return [ questId for questId, qProgress in questProgress.iteritems() if questId.startswith(WT_BATTLE_QUEST_PREFIX) and isQuestCompleted(*qProgress) ]


@replace_none_kwargs(eventsCache=IEventsCache)
def getQuestRewards(reusable, tooltipData, ignoreList=None, eventsCache=None):
    wtQuestIds = _extractWtBattleQuests(reusable.personal.avatar.extensionInfo.get('questsProgress', {}))
    if not wtQuestIds:
        return {}
    else:
        quests = eventsCache.getAllQuests(lambda quest: quest.getID() in wtQuestIds)
        packer = getWTEventBonusPacker()
        if ignoreList is None:
            ignoreList = []
        bonusIndexTotal = len(tooltipData) if tooltipData else 0
        bonusTooltipList = []
        processedBonuses = {}
        for quest in quests.values():
            for bonus in quest.getBonuses():
                if bonus.isShowInGUI() and bonus.getName() not in ignoreList:
                    bonusList = packer.pack(bonus)
                    if bonusList and tooltipData is not None:
                        bonusTooltipList = packer.getToolTip(bonus)
                    for bonusIndex, item in enumerate(bonusList):
                        tooltipIdx = str(bonusIndexTotal)
                        item.setTooltipId(tooltipIdx)
                        if tooltipData is not None:
                            tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                        bonusIndexTotal += 1
                        bonusModel = processedBonuses.get(item.getName())
                        if bonusModel:
                            bonusModel.setValue(str(int(bonusModel.getValue() or 0) + int(item.getValue() or 0)))
                        processedBonuses[item.getName()] = item

        return processedBonuses
