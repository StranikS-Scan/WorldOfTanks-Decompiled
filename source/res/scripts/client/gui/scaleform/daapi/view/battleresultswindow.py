# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/BattleResultsWindow.py
from collections import defaultdict
import re
import math
import operator
from functools import partial
import BigWorld
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.battle_control import arena_visitor
from gui.battle_results.VehicleProgressCache import g_vehicleProgressCache
from gui.battle_results.VehicleProgressHelper import VehicleProgressHelper, PROGRESS_ACTION
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showResearchView, showPersonalCase, showBattleResultsFromData
from gui.shared.utils.functions import getArenaSubTypeName
import nations
import potapov_quests
from account_helpers.AccountSettings import AccountSettings
from account_helpers import getAccountDatabaseID
from account_shared import getFairPlayViolationName
from debug_utils import LOG_DEBUG
from helpers import i18n, time_utils
from adisp import async, process
from CurrentVehicle import g_currentVehicle
from constants import ARENA_BONUS_TYPE, ARENA_GUI_TYPE, IGR_TYPE, EVENT_TYPE, FINISH_REASON as FR, FLAG_ACTION, TEAMS_IN_ARENA
from dossiers2.custom.records import RECORD_DB_IDS, DB_ID_TO_RECORD
from dossiers2.ui import achievements
from dossiers2.ui.achievements import ACHIEVEMENT_TYPE, MARK_ON_GUN_RECORD, MARK_OF_MASTERY_RECORD
from dossiers2.ui.layouts import IGNORED_BY_BATTLE_RESULTS, isAchievementRegistered
from gui import makeHtmlString, GUI_SETTINGS, SystemMessages
from gui.server_events import g_eventsCache, events_dispatcher as quests_events
from gui.shared import g_itemsCache, events
from gui.shared.utils import isVehicleObserver
from items import vehicles as vehicles_core, vehicles
from items.vehicles import VEHICLE_CLASS_TAGS
from shared_utils import findFirst, isDefaultDict
from gui.clubs import events_dispatcher as club_events
from gui.clubs.club_helpers import ClubListener
from gui.clubs.settings import getLeagueByDivision, getDivisionWithinLeague
from gui.shared.ClanCache import g_clanCache
from gui.shared.fortifications.FortBuilding import FortBuilding
from gui.shared.gui_items.dossier import getAchievementFactory
from gui.shared.gui_items.Vehicle import VEHICLE_BATTLE_TYPES_ORDER_INDICES
from gui.shared.gui_items.dossier.achievements.MarkOnGunAchievement import MarkOnGunAchievement
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.daapi.view.meta.BattleResultsMeta import BattleResultsMeta
from messenger.storage import storage_getter
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.shared.formatters import text_styles, icons
from gui.battle_results import formatters as battle_res_fmts
from gui.shared.utils.functions import makeTooltip
from gui.sounds.ambients import BattleResultsEnv
from gui.shared.money import Money, ZERO_MONEY
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils

def _wrapEmblemUrl(emblemUrl):
    return ' <IMG SRC="img://%s" width="24" height="24" vspace="-10"/>' % emblemUrl


RESULT_ = '#menu:finalStatistic/commonStats/resultlabel/{0}'
BATTLE_RESULTS_STR = '#battle_results:{0}'
FINISH_REASON = BATTLE_RESULTS_STR.format('finish/reason/{0}')
CLAN_BATTLE_FINISH_REASON_DEF = BATTLE_RESULTS_STR.format('finish/clanBattle_reason_def/{0}')
CLAN_BATTLE_FINISH_REASON_ATTACK = BATTLE_RESULTS_STR.format('finish/clanBattle_reason_attack/{0}')
RESULT_LINE_STR = BATTLE_RESULTS_STR.format('details/calculations/{0}')
STATS_KEY_BASE = BATTLE_RESULTS_STR.format('team/stats/labels_{0}')
TIME_STATS_KEY_BASE = BATTLE_RESULTS_STR.format('details/time/lbl_{0}')
XP_TITLE = BATTLE_RESULTS_STR.format('common/details/xpTitle')
XP_TITLE_DAILY = BATTLE_RESULTS_STR.format('common/details/xpTitleFirstVictory')
MILEAGE_STR_KEY = BATTLE_RESULTS_STR.format('team/stats/mileage')
TIME_DURATION_STR = BATTLE_RESULTS_STR.format('details/time/value')
XP_MULTIPLIER_SIGN_KEY = BATTLE_RESULTS_STR.format('common/xpMultiplierSign')
EFFICIENCY_ALLIES_STR = BATTLE_RESULTS_STR.format('common/battleEfficiency/allies')
UNKNOWN_PLAYER_NAME_VALUE = '#ingame_gui:players_panel/unknown_name'
UNKNOWN_VEHICLE_NAME_VALUE = '#ingame_gui:players_panel/unknown_vehicle'
ARENA_TYPE = '#arenas:type/{0}/name'
ARENA_SPECIAL_TYPE = '#menu:loading/battleTypes/{0}'
VEHICLE_ICON_FILE = '../maps/icons/vehicle/{0}.png'
VEHICLE_ICON_SMALL_FILE = '../maps/icons/vehicle/small/{0}.png'
VEHICLE_NO_IMAGE_FILE_NAME = 'noImage'
ARENA_SCREEN_FILE = '../maps/icons/map/stats/%s.png'
ARENA_NAME_PATTERN = '{0} - {1}'
LINE_BRAKE_STR = '<br/>'
STATS_KEYS = (('shots', True, None),
 ('hits', False, None),
 ('explosionHits', True, None),
 ('damageDealt', True, None),
 ('damageDealtByOrder', True, None),
 ('sniperDamageDealt', True, None),
 ('directHitsReceived', True, None),
 ('piercingsReceived', True, None),
 ('noDamageDirectHitsReceived', True, None),
 ('explosionHitsReceived', True, None),
 ('damageBlockedByArmor', True, None),
 ('teamHitsDamage', False, None),
 ('spotted', True, None),
 ('damagedKilled', False, None),
 ('killed', True, None),
 ('killsByOrder', True, None),
 ('damageAssisted', True, 'damageAssistedSelf'),
 ('capturePointsVal', False, None),
 ('mileage', False, None),
 ('flags', True, None),
 ('deaths', True, None))
TIME_STATS_KEYS = ('arenaCreateTimeOnlyStr', 'duration', 'playerKilled')
FALLOUT_ONLY_STATS = ('killed', 'killsByOrder', 'damageDealtByOrder', 'flags', 'deaths')
FALLOUT_ORDER_STATS = ('damageDealtByOrder', 'killsByOrder')
FALLOUT_EXCLUDE_VEHICLE_STATS = ('damagedKilled', 'sniperDamageDealt', 'capturePoints', 'droppedCapturePoints', 'capturePointsVal', 'mileage')

def _skip(a, b):
    return a


def _intSum(a, b):
    return a + b


def _intMax(a, b):
    return max(a, b)


def _listSum(a, b):
    return map(operator.add, a, b)


def _listCollect(a, b):
    return tuple(a) + tuple(b)


def _uniqueListCollect(a, b):
    result = list(a)
    result.extend([ j for j in b if j not in a ])
    return tuple(result)


def _calculateBaseParam(paramKey, pData, premFactor, isPremium):
    paramValue = pData.get(paramKey, 0)
    if isPremium:
        paramValue = int(paramValue / premFactor)
    return paramValue


def _calculateParamWithPrem(paramKey, pData, premFactor, isPremium):
    paramValue = pData.get(paramKey, 0)
    if not isPremium:
        paramValue = int(round(paramValue * premFactor))
    return paramValue


def _getFairPlayViolationName(pData):
    fairPlayViolationData = pData.get('fairplayViolations')
    return getFairPlayViolationName(fairPlayViolationData[1]) if fairPlayViolationData is not None else None


def _calculateDailyXP(originalData, data):
    return (data.get('originalXP', 0) - int(data.get('xpPenaltyBase', 0))) * originalData.get('dailyXPFactor10', 0) / 10.0


def _calculateDailyFreeXP(originalData, data):
    return data.get('originalFreeXP', 0) * originalData.get('dailyXPFactor10', 0) / 10.0


def _calculateBaseXpPenalty(originalData, data):
    aogasFactor = originalData.get('aogasFactor10', 10) / 10.0
    if not aogasFactor:
        return 0
    isPremium = originalData.get('isPremium', False)
    igrXpFactor = originalData.get('igrXPFactor10', 10) / 10.0
    premXpFactor = originalData.get('premiumXPFactor10', 10) / 10.0
    dailyXpFactor = data.get('dailyXPFactor10', 10) / 10.0
    xpPenalty = data.get('xpPenalty', 0)
    xpPenalty = math.ceil(int(xpPenalty / aogasFactor) / dailyXpFactor)
    if isPremium:
        xpPenalty = math.ceil(xpPenalty / premXpFactor)
    if igrXpFactor:
        xpPenalty = math.ceil(xpPenalty / igrXpFactor)
    return xpPenalty


def _calculateTotalXP(originalData, data, usePremFactor=False):
    fairPlayViolationName = _getFairPlayViolationName(originalData)
    hasViolation = fairPlayViolationName is not None
    if hasViolation:
        return 0
    else:
        isPremium = originalData.get('isPremium', False)
        igrXpFactor = originalData.get('igrXPFactor10', 10) / 10.0
        premXpFactor = originalData.get('premiumXPFactor10', 10) / 10.0
        aogasFactor = originalData.get('aogasFactor10', 10) / 10.0
        refSystemFactor = originalData.get('refSystemXPFactor10', 10) / 10.0
        dailyXpFactor = data.get('dailyXPFactor10', 10) / 10.0
        eventXP = int(data.get('eventXP', 0))
        xpPenalty = int(data.get('xpPenaltyBase', 0))
        baseXp = int(data['originalXP'])
        baseOrderXp = _calculateBaseParam('orderXP', data, premXpFactor, isPremium)
        baseBoosterXP = _calculateBaseParam('boosterXP', data, premXpFactor, isPremium)
        xp = originalData['xp']
        if isPremium != usePremFactor:
            premFactor = premXpFactor if usePremFactor else 1.0
            if isPremium:
                premiumVehicleXP = data['premiumVehicleXP'] / premXpFactor
            else:
                premiumVehicleXP = data['premiumVehicleXP'] * premXpFactor
            if isPremium:
                squadXP = data['squadXP'] / premXpFactor
            else:
                squadXP = data['squadXP'] * premXpFactor
            subtotalXp = int(round(int(round((baseXp - xpPenalty) * premFactor)) * igrXpFactor))
            resultXp = subtotalXp * dailyXpFactor
            if abs(refSystemFactor - 1.0) > 0.001:
                resultXp += int(round(subtotalXp * refSystemFactor))
            resultXp += squadXP
            xp = int(round((resultXp + int(round(baseOrderXp * premFactor)) + int(round(baseBoosterXP * premFactor)) + int(round(eventXP)) + int(round(premiumVehicleXP))) * aogasFactor))
        return xp


def _calculateTotalWithoutPremXP(oritinalData, data):
    return _calculateTotalXP(oritinalData, data)


def _calculateTotalWithPremXP(oritinalData, data):
    return _calculateTotalXP(oritinalData, data, True)


RELATED_ACCOUNT_DATA = {'dailyFreeXP': _calculateDailyFreeXP,
 'xpPenaltyBase': _calculateBaseXpPenalty,
 'xpWithoutPremTotal': _calculateTotalWithoutPremXP,
 'xpWithPremTotal': _calculateTotalWithPremXP}
COMMON_DATA = (('achievementCredits', (0, _intSum)),
 ('creditsContributionIn', (0, _intSum)),
 ('creditsToDraw', (0, _intSum)),
 ('creditsPenalty', (0, _intSum)),
 ('creditsContributionOut', (0, _intSum)),
 ('originalCredits', (0, _intSum)),
 ('orderCredits', (0, _intSum)),
 ('boosterCredits', (0, _intSum)),
 ('autoRepairCost', (0, _intSum)),
 ('autoLoadCost', (ZERO_MONEY, _listSum)),
 ('autoEquipCost', (ZERO_MONEY, _listSum)),
 ('histAmmoCost', (ZERO_MONEY, _listSum)),
 ('achievementXP', (0, _intSum)),
 ('achievementFreeXP', (0, _intSum)),
 ('xpPenalty', (0, _intSum)),
 ('originalXP', (0, _intSum)),
 ('originalFreeXP', (0, _intSum)),
 ('dossierPopUps', ((), _uniqueListCollect)),
 ('orderXP', (0, _intSum)),
 ('boosterXP', (0, _intSum)),
 ('orderFreeXP', (0, _intSum)),
 ('boosterFreeXP', (0, _intSum)),
 ('premiumVehicleXP', (0, _intSum)),
 ('squadXP', (0, _intSum)),
 ('xpPenaltyBase', (0, _intSum)),
 ('dailyXP', (0, _intSum)),
 ('dailyFreeXP', (0, _intSum)))
VEHICLE_DATA = (('credits', (0, _skip)),
 ('xp', (0, _skip)),
 ('freeXP', (0, _skip)),
 ('eventCredits', (0, _skip)),
 ('eventGold', (0, _skip)),
 ('eventXP', (0, _skip)),
 ('eventFreeXP', (0, _skip)),
 ('dailyXPFactor10', (10, _intMax)),
 ('xpWithoutPremTotal', (0, _intSum)),
 ('xpWithPremTotal', (0, _intSum)))
AVATAR_DATA = (('credits', (0, _intSum)),
 ('xp', (0, _intSum)),
 ('freeXP', (0, _intSum)),
 ('eventCredits', (0, _intSum)),
 ('eventGold', (0, _intSum)),
 ('eventXP', (0, _intSum)),
 ('eventFreeXP', (0, _intSum)))
CUMULATIVE_VEHICLE_DATA = list(COMMON_DATA + VEHICLE_DATA)
CUMULATIVE_ACCOUNT_DATA = list(COMMON_DATA + AVATAR_DATA)
CUMULATIVE_STATS_DATA = {'shots': (0, _intSum),
 'tkills': (0, _intSum),
 'damageDealt': (0, _intSum),
 'sniperDamageDealt': (0, _intSum),
 'tdamageDealt': (0, _intSum),
 'directHits': (0, _intSum),
 'explosionHits': (0, _intSum),
 'piercings': (0, _intSum),
 'directHitsReceived': (0, _intSum),
 'piercingsReceived': (0, _intSum),
 'noDamageDirectHitsReceived': (0, _intSum),
 'explosionHitsReceived': (0, _intSum),
 'damageBlockedByArmor': (0, _intSum),
 'damaged': (0, _intSum),
 'kills': (0, _intSum),
 'capturePoints': (0, _intSum),
 'droppedCapturePoints': (0, _intSum),
 'mileage': (0, _intSum),
 'flagActions': ([0] * len(FLAG_ACTION.RANGE), _listSum),
 'deathCount': (0, _intSum),
 'winPoints': (0, _intSum),
 'resourceAbsorbed': (0, _intSum),
 'damageAssistedTrack': (0, _intSum),
 'damageAssistedRadio': (0, _intSum),
 'spotted': (0, _intSum)}

class BattleResultsWindow(BattleResultsMeta, ClubListener):
    __sound_env__ = BattleResultsEnv
    RESEARCH_UNLOCK_TYPE = 'UNLOCK_LINK_TYPE'
    PURCHASE_UNLOCK_TYPE = 'PURCHASE_LINK_TYPE'
    NEW_SKILL_UNLOCK_TYPE = 'NEW_SKILL_LINK_TYPE'
    __playersNameCache = dict()
    __rated7x7Animations = set()
    __buyPremiumCache = set()

    def __init__(self, ctx=None):
        super(BattleResultsWindow, self).__init__()
        assert 'dataProvider' in ctx
        assert ctx['dataProvider'] is not None
        self.dataProvider = ctx['dataProvider']
        self.__premiumBonusesDiff = {}
        self.__isFallout = False
        return

    @storage_getter('users')
    def usersStorage(self):
        return None

    @process
    def _populate(self):
        super(BattleResultsWindow, self)._populate()
        self.addListener(events.LobbySimpleEvent.PREMIUM_BOUGHT, self.__onPremiumBought)
        self.addListener(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW, self.__onWindowClose, scope=EVENT_BUS_SCOPE.LOBBY)
        commonData = yield self.__getCommonData()
        self.as_setDataS(commonData)
        if commonData is not None:
            results = self.dataProvider.results
            if self._isRated7x7Battle():
                cur, prev = results.getDivisions()
                if cur != prev:
                    self.__showDivisionAnimation(cur, prev)
        return

    def _dispose(self):
        self.dataProvider.destroy()
        self.removeListener(events.LobbySimpleEvent.PREMIUM_BOUGHT, self.__onPremiumBought)
        self.removeListener(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW, self.__onWindowClose, scope=EVENT_BUS_SCOPE.LOBBY)
        super(BattleResultsWindow, self)._dispose()

    def onWindowClose(self):
        self.destroy()

    def getDenunciations(self):
        return g_itemsCache.items.stats.denunciationsLeft

    def showEventsWindow(self, eID, eventType):
        prbDispatcher = g_prbLoader.getDispatcher()
        return SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error) if prbDispatcher and prbDispatcher.getFunctionalState().isNavigationDisabled() else quests_events.showEventsWindow(eID, eventType)

    def saveSorting(self, iconType, sortDirection, bonusType):
        AccountSettings.setSettings('statsSorting' if bonusType != ARENA_BONUS_TYPE.SORTIE else 'statsSortingSortie', {'iconType': iconType,
         'sortDirection': sortDirection})

    def __getPlayerName(self, playerDBID, bots, vID=None):
        playerNameRes = self.__playersNameCache.get(playerDBID)
        if playerNameRes is None:
            botName = bots.get(vID, (None, None))[1]
            player = self.dataProvider.getPlayerData(playerDBID, botName)
            playerNameRes = (player.getFullName(), (player.name,
              player.clanAbbrev,
              player.getRegionCode(),
              player.igrType))
            if playerDBID is not None:
                self.__playersNameCache[playerDBID] = playerNameRes
        return playerNameRes

    def __getVehicleData(self, vehicleCompDesc):
        vehicleName = i18n.makeString(UNKNOWN_VEHICLE_NAME_VALUE)
        vehicleShortName = i18n.makeString(UNKNOWN_VEHICLE_NAME_VALUE)
        vehicleIcon = VEHICLE_ICON_FILE.format(VEHICLE_NO_IMAGE_FILE_NAME)
        vehicleIconSmall = VEHICLE_ICON_SMALL_FILE.format(VEHICLE_NO_IMAGE_FILE_NAME)
        nation = -1
        if vehicleCompDesc:
            vehicle = g_itemsCache.items.getItemByCD(vehicleCompDesc)
            vehicleName = vehicle.userName
            vehicleShortName = vehicle.shortUserName
            vehicleIcon = vehicle.icon
            vehicleIconSmall = vehicle.iconSmall
            nation = vehicle.nationID
        return (vehicleName,
         vehicleShortName,
         vehicleIcon,
         vehicleIconSmall,
         nation)

    def __vehiclesByVehIDComparator(self, item, other):
        iVId = item['vehicleId']
        iAccountDBID = self.dataProvider.getAccountDBID(iVId)
        iVehsData = self.dataProvider.getVehiclesData(iAccountDBID)
        oVId = other['vehicleId']
        oAccountDBID = self.dataProvider.getAccountDBID(oVId)
        oVehsData = self.dataProvider.getVehiclesData(oAccountDBID)
        if len(oVehsData) and len(iVehsData):
            return self.__vehiclesComparator(iVehsData[0], oVehsData[0])
        return -1 if len(iVehsData) else 1

    def __vehiclesComparator(self, iVehItem, oVehItem):
        cd = iVehItem.get('typeCompDescr')
        if cd is not None:
            iType = vehicles_core.getVehicleType(cd)
            iLevel = iType.level if iType else -1
            iWeight = VEHICLE_BATTLE_TYPES_ORDER_INDICES.get(list(VEHICLE_CLASS_TAGS & iType.tags).pop(), 10) if iType else 10
        else:
            iLevel = -1
            iWeight = 10
        _, iName, _, _, _ = self.__getVehicleData(cd)
        cd = oVehItem.get('typeCompDescr')
        if cd is not None:
            oType = vehicles_core.getVehicleType(cd)
            oLevel = oType.level if oType else -1
            oWeight = VEHICLE_BATTLE_TYPES_ORDER_INDICES.get(list(VEHICLE_CLASS_TAGS & oType.tags).pop(), 10) if oType else 10
        else:
            oLevel = -1
            oWeight = 10
        _, oName, _, _, _ = self.__getVehicleData(cd)
        res = cmp(oLevel, iLevel)
        if res:
            return res
        else:
            res = cmp(iWeight, oWeight)
            return res if res else cmp(iName, oName)

    def __getStatsLine(self, label=None, col1=None, col2=None, col3=None, col4=None):
        if col2 is not None:
            lineType = 'wideLine'
        else:
            lineType = 'normalLine'
        lbl = label + '\n' if label is not None else '\n'
        lblStripped = re.sub('<[^<]+?>', '', lbl)
        return {'label': lbl,
         'labelStripped': lblStripped,
         'col1': col1 if col1 is not None else '\n',
         'col2': col2 if col2 is not None else '\n',
         'col3': col3 if col3 is not None else '\n',
         'col4': col4 if col4 is not None else '\n',
         'lineType': None if label is None else lineType}

    def __resultLabel(self, label):
        return i18n.makeString(RESULT_LINE_STR.format(label))

    def __makeCreditsLabel(self, value, canBeFaded=False, isDiff=False):
        valStr = BigWorld.wg_getGoldFormat(int(value))
        if value < 0:
            valStr = self.__makeRedLabel(valStr)
        if isDiff:
            valStr = '+ %s' % valStr
        templateName = 'credits_small_inactive_label' if canBeFaded and value == 0 else 'credits_small_label'
        return makeHtmlString('html_templates:lobby/battle_results', templateName, {'value': valStr})

    def __makeXpLabel(self, value, canBeFaded=False, isDiff=False):
        valStr = BigWorld.wg_getIntegralFormat(int(value))
        if value < 0:
            valStr = self.__makeRedLabel(valStr)
        if isDiff:
            valStr = '+ %s' % valStr
        templateName = 'xp_small_inactive_label' if canBeFaded and value == 0 else 'xp_small_label'
        return makeHtmlString('html_templates:lobby/battle_results', templateName, {'value': valStr})

    def __makeResourceLabel(self, value, canBeFaded=False):
        valStr = BigWorld.wg_getIntegralFormat(int(value))
        if value < 0:
            valStr = self.__makeRedLabel(valStr)
        templateName = 'resource_small_inactive_label' if canBeFaded and value == 0 else 'resource_small_label'
        return makeHtmlString('html_templates:lobby/battle_results', templateName, {'value': valStr})

    def __makeFreeXpLabel(self, value, canBeFaded=False):
        valStr = BigWorld.wg_getIntegralFormat(int(value))
        templateName = 'free_xp_small_inactive_label' if canBeFaded and value == 0 else 'free_xp_small_label'
        return makeHtmlString('html_templates:lobby/battle_results', templateName, {'value': valStr})

    def __makeGoldLabel(self, value, canBeFaded=False):
        valStr = BigWorld.wg_getGoldFormat(value)
        templateName = 'gold_small_inactive_label' if canBeFaded and value == 0 else 'gold_small_label'
        return makeHtmlString('html_templates:lobby/battle_results', templateName, {'value': valStr})

    def __makePercentLabel(self, value):
        valStr = BigWorld.wg_getGoldFormat(int(value))
        templateName = 'percent'
        if value < 0:
            valStr = self.__makeRedLabel(valStr)
            templateName = 'negative_percent'
        return makeHtmlString('html_templates:lobby/battle_results', templateName, {'value': valStr})

    def __makeRedLabel(self, value):
        return makeHtmlString('html_templates:lobby/battle_results', 'negative_value', {'value': value})

    def __populateStatValues(self, node, isSelf=False):
        node = node.copy()
        if not self.__isFallout:
            node['damagedKilled'] = self.__makeSlashedValuesStr(node, 'damaged', 'kills')
            node['capturePointsVal'] = self.__makeSlashedValuesStr(node, 'capturePoints', 'droppedCapturePoints')
        else:
            node['killed'] = node['kills']
        node['teamHitsDamage'] = self.__makeTeamDamageStr(node)
        node['hits'] = self.__makeSlashedValuesStr(node, 'directHits', 'piercings')
        node['mileage'] = self.__makeMileageStr(node.get('mileage', 0))
        flagActions = node.get('flagActions', [0] * len(FLAG_ACTION.RANGE))
        node['flags'] = flagActions[FLAG_ACTION.CAPTURED]
        node['deaths'] = node.get('deathCount', 0)
        node['victoryScore'] = node.get('winPoints', 0)
        result = []
        for key, isInt, selfKey in STATS_KEYS:
            if not self.__isFallout and key in FALLOUT_ONLY_STATS:
                continue
            if self.__isFallout and key in FALLOUT_EXCLUDE_VEHICLE_STATS:
                continue
            if key in FALLOUT_ORDER_STATS and key not in node:
                continue
            if isInt:
                value = node.get(key, 0)
                valueFormatted = BigWorld.wg_getIntegralFormat(value)
                if not value:
                    valueFormatted = makeHtmlString('html_templates:lobby/battle_results', 'empty_stat_value', {'value': valueFormatted})
            else:
                valueFormatted = node.get(key, '')
            if isSelf and selfKey is not None:
                key = selfKey
            result.append({'label': i18n.makeString(STATS_KEY_BASE.format(key)),
             'value': valueFormatted})

        return result

    def __populateAccounting(self, commonData, personalCommonData, personalData, playersData, personalDataOutput, playerAvatarData):
        if self.dataProvider.getArenaUniqueID() in self.__buyPremiumCache:
            isPostBattlePremium = True
        else:
            isPostBattlePremium = personalCommonData.get('isPremium', False)
        isPremium = personalCommonData.get('isPremium', False)
        premCreditsFactor = personalCommonData.get('premiumCreditsFactor10', 10) / 10.0
        igrXpFactor = personalCommonData.get('igrXPFactor10', 10) / 10.0
        premXpFactor = personalCommonData.get('premiumXPFactor10', 10) / 10.0
        aogasFactor = personalCommonData.get('aogasFactor10', 10) / 10.0
        refSystemFactor = personalCommonData.get('refSystemXPFactor10', 10) / 10.0
        playerDBID = personalCommonData.get('accountDBID', 0)
        bonusType = commonData.get('bonusType', 0)
        isPlayerInSquad = bool(playersData.get(playerDBID, {}).get('prebattleID', 0))
        aogasValStr = ''
        personalDataOutput['xpTitleStrings'] = xpTitleStrings = []
        personalDataOutput['isPremium'] = isPostBattlePremium
        personalDataOutput['creditsNoPremValues'] = creditsNoPremValues = []
        personalDataOutput['creditsPremValues'] = creditsPremValues = []
        personalDataOutput['xpNoPremValues'] = xpNoPremValues = []
        personalDataOutput['xpPremValues'] = xpPremValues = []
        personalDataOutput['resValues'] = resValues = []
        personalDataOutput['resPremValues'] = resPremValues = []
        showIntermediateTotal = False
        fairPlayViolationName = _getFairPlayViolationName(personalCommonData)
        hasViolation = fairPlayViolationName is not None
        playerData = playersData.get(playerDBID, {'igrType': 0,
         'clanDBID': 0,
         'clanAbbrev': ''})
        personalDataOutput['isLegionnaire'] = False if playerData.get('clanDBID') else True
        igrType = playerData.get('igrType', 0)
        vehsCreditsData = []
        vehsXPData = []
        personalDataSource = self.__buildPersonalDataSource(personalData, playerAvatarData)
        dailyXPVehs = []
        multiplierLineIdxPos = 0
        for vehIntCD, sourceData in personalDataSource:
            dailyXpFactor = sourceData['dailyXPFactor10'] / 10.0
            creditsData = []
            creditsToDraw = _calculateBaseParam('creditsToDraw', sourceData, premCreditsFactor, isPremium)
            achievementCredits = sourceData['achievementCredits']
            creditsPenalty = self.__calculateBaseCreditsPenalty(sourceData, premCreditsFactor, isPremium)
            creditsCompensation = _calculateBaseParam('creditsContributionIn', sourceData, premCreditsFactor, isPremium)
            isNoPenalty = achievementCredits > 0
            creditsBase = sourceData['originalCredits']
            creditsCell = creditsBase - achievementCredits - creditsToDraw
            creditsCellPrem = int(round(creditsBase * premCreditsFactor)) - int(round(achievementCredits * premCreditsFactor)) - int(round(creditsToDraw * premCreditsFactor))
            creditsCellStr = self.__makeCreditsLabel(creditsCell, not isPostBattlePremium)
            creditsCellPremStr = self.__makeCreditsLabel(creditsCellPrem, isPostBattlePremium)
            creditsData.append(self.__getStatsLine(self.__resultLabel('base'), creditsCellStr, None, creditsCellPremStr, None))
            achievementCreditsPrem = 0
            if isNoPenalty:
                showIntermediateTotal = True
                achievementCreditsPrem = int(round(achievementCredits * premCreditsFactor))
                creditsData.append(self.__getStatsLine(self.__resultLabel('noPenalty'), self.__makeCreditsLabel(achievementCredits, not isPostBattlePremium), None, self.__makeCreditsLabel(achievementCreditsPrem, isPostBattlePremium), None))
            boosterCredits = _calculateBaseParam('boosterCredits', sourceData, premCreditsFactor, isPremium)
            boosterCreditsPrem = int(round(boosterCredits * premCreditsFactor))
            if boosterCredits > 0 or boosterCreditsPrem > 0:
                showIntermediateTotal = True
                boosterCreditsStr = self.__makeCreditsLabel(boosterCredits, not isPostBattlePremium) if boosterCredits else None
                boosterCreditsPremStr = self.__makeCreditsLabel(boosterCreditsPrem, isPostBattlePremium) if boosterCreditsPrem else None
                creditsData.append(self.__getStatsLine(self.__resultLabel('boosters'), boosterCreditsStr, None, boosterCreditsPremStr, None))
            orderCredits = _calculateBaseParam('orderCredits', sourceData, premCreditsFactor, isPremium)
            orderCreditsPrem = int(round(orderCredits * premCreditsFactor))
            if orderCredits > 0 or orderCreditsPrem > 0:
                showIntermediateTotal = True
                orderCreditsStr = self.__makeCreditsLabel(orderCredits, not isPostBattlePremium) if orderCredits else None
                orderCreditsPremStr = self.__makeCreditsLabel(orderCreditsPrem, isPostBattlePremium) if orderCreditsPrem else None
                creditsData.append(self.__getStatsLine(self.__resultLabel('battlePayments'), orderCreditsStr, None, orderCreditsPremStr, None))
            eventCredits = sourceData.get('eventCredits', 0)
            creditsEventStr = self.__makeCreditsLabel(eventCredits, not isPostBattlePremium) if eventCredits else None
            creditsEventPremStr = self.__makeCreditsLabel(eventCredits, isPostBattlePremium) if eventCredits else None
            eventGold = sourceData.get('eventGold', 0)
            goldEventStr = self.__makeGoldLabel(eventGold, not isPostBattlePremium) if eventGold else None
            goldEventPremStr = self.__makeGoldLabel(eventGold, isPostBattlePremium) if eventGold else None
            if eventCredits > 0 or eventGold > 0:
                showIntermediateTotal = True
                creditsData.append(self.__getStatsLine(self.__resultLabel('event'), creditsEventStr, goldEventStr, creditsEventPremStr, goldEventPremStr))
            creditsData.append(self.__getStatsLine())
            if hasViolation:
                penaltyValue = self.__makePercentLabel(int(-100))
                creditsData.append(self.__getStatsLine(self.__resultLabel('fairPlayViolation/' + fairPlayViolationName), penaltyValue, None, penaltyValue, None))
            creditsPenaltyStr = self.__makeCreditsLabel(int(-creditsPenalty), not isPostBattlePremium)
            creditsPenaltyPremStr = self.__makeCreditsLabel(int(-creditsPenalty * premCreditsFactor), isPostBattlePremium)
            creditsData.append(self.__getStatsLine(self.__resultLabel('friendlyFirePenalty'), creditsPenaltyStr, None, creditsPenaltyPremStr, None))
            creditsCompensationStr = self.__makeCreditsLabel(int(creditsCompensation), not isPostBattlePremium)
            creditsCompensationPremStr = self.__makeCreditsLabel(int(creditsCompensation * premCreditsFactor), isPostBattlePremium)
            creditsData.append(self.__getStatsLine(self.__resultLabel('friendlyFireCompensation'), creditsCompensationStr, None, creditsCompensationPremStr, None))
            creditsData.append(self.__getStatsLine())
            if creditsPenalty or creditsCompensation:
                showIntermediateTotal = True
            if aogasFactor < 1:
                showIntermediateTotal = True
                aogasValStr = ''.join([i18n.makeString(XP_MULTIPLIER_SIGN_KEY), BigWorld.wg_getFractionalFormat(aogasFactor)])
                aogasValStr = self.__makeRedLabel(aogasValStr)
                creditsData.append(self.__getStatsLine(self.__resultLabel('aogasFactor'), aogasValStr, None, aogasValStr, None))
                creditsData.append(self.__getStatsLine())
            creditsWithoutPremTotal = self.__calculateTotalCredits(sourceData, eventCredits, premCreditsFactor, isPremium, aogasFactor, creditsBase, orderCredits, boosterCredits, creditsToDraw, creditsPenalty, creditsCompensation, hasViolation, False)
            squadXP = sourceData['squadXP']
            showSquadLabels = isPlayerInSquad and bonusType == ARENA_BONUS_TYPE.REGULAR and g_eventsCache.isSquadXpFactorsEnabled()
            squadHasBonus = False
            if showSquadLabels:
                squadBonusInfo = playerAvatarData.get('squadBonusInfo', {})
                vehicles = squadBonusInfo.get('vehicles', {})
                squadSize = squadBonusInfo.get('size', 0)
                if squadSize > 1:
                    vehicleID = self.dataProvider.getVehicleID(playerDBID)
                    joinedOnArenaVehicles = squadBonusInfo.get('joinedOnArena', {})
                    if vehicleID in joinedOnArenaVehicles:
                        showSquadLabels = False
                    else:
                        vehiclesLevels = [ g_itemsCache.items.getItemByCD(cmpDescr).level for cmpDescr in vehicles ]
                        vehiclesLevels.sort()
                        distance = vehiclesLevels[-1] - vehiclesLevels[0]
                        vehData = self.dataProvider.getVehiclesData(playerDBID)[0]
                        typeCompDescr = vehData.get('typeCompDescr', None)
                        if typeCompDescr is not None:
                            level = g_itemsCache.items.getItemByCD(typeCompDescr).level
                            key = (distance, level)
                            showSquadLabels = key not in g_eventsCache.getSquadZeroBonuses()
                        squadHasBonus = distance in g_eventsCache.getSquadBonusLevelDistance()
                else:
                    showSquadLabels = False
            if dailyXpFactor == 1 and showSquadLabels and squadHasBonus:
                imgTag = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_PREBATTLEINVITEICON_1)
                xpTitleString = i18n.makeString(BATTLE_RESULTS.COMMON_DETAILS_XPTITLESQUAD, img=imgTag)
            else:
                xpTitleString = i18n.makeString(XP_TITLE)
            if dailyXpFactor > 1:
                xpTitleString = ' '.join((xpTitleString, i18n.makeString(XP_TITLE_DAILY, dailyXpFactor)))
            xpTitleStrings.append(xpTitleString)
            creditsWithPremTotal = self.__calculateTotalCredits(sourceData, eventCredits, premCreditsFactor, isPremium, aogasFactor, creditsBase, orderCredits, boosterCredits, creditsToDraw, creditsPenalty, creditsCompensation, hasViolation, True)
            if showIntermediateTotal:
                creditsData.append(self.__getStatsLine(self.__resultLabel('intermediateTotal'), self.__makeCreditsLabel(creditsWithoutPremTotal, not isPostBattlePremium), goldEventStr, self.__makeCreditsLabel(creditsWithPremTotal, isPostBattlePremium), goldEventPremStr))
                creditsData.append(self.__getStatsLine())
            creditsAutoRepair = sourceData['autoRepairCost']
            if creditsAutoRepair is None:
                creditsAutoRepair = 0
            creditsAutoRepairStr = self.__makeCreditsLabel(-creditsAutoRepair, not isPostBattlePremium)
            creditsAutoRepairPremStr = self.__makeCreditsLabel(-creditsAutoRepair, isPostBattlePremium)
            creditsData.append(self.__getStatsLine(self.__resultLabel('autoRepair'), creditsAutoRepairStr, None, creditsAutoRepairPremStr, None))
            autoLoadCost = Money(*sourceData['autoLoadCost'])
            if autoLoadCost is None:
                autoLoadCost = ZERO_MONEY
            creditsAutoLoad = autoLoadCost.credits
            goldAutoLoad = autoLoadCost.gold
            creditsAutoLoadStr = self.__makeCreditsLabel(-creditsAutoLoad, not isPostBattlePremium)
            creditsAutoLoadPremStr = self.__makeCreditsLabel(-creditsAutoLoad, isPostBattlePremium)
            goldAutoLoadStr = self.__makeGoldLabel(-goldAutoLoad, not isPostBattlePremium) if goldAutoLoad else None
            goldAutoLoadPremStr = self.__makeGoldLabel(-goldAutoLoad, isPostBattlePremium) if goldAutoLoad else None
            creditsData.append(self.__getStatsLine(self.__resultLabel('autoLoad'), creditsAutoLoadStr, goldAutoLoadStr, creditsAutoLoadPremStr, goldAutoLoadPremStr))
            autoEquipCost = Money(*sourceData['autoEquipCost'])
            if autoEquipCost is None:
                autoEquipCost = ZERO_MONEY
            creditsAutoEquip = autoEquipCost.credits
            goldAutoEquip = autoEquipCost.gold
            creditsAutoEquipStr = self.__makeCreditsLabel(-creditsAutoEquip, not isPostBattlePremium)
            creditsAutoEquipPremStr = self.__makeCreditsLabel(-creditsAutoEquip, isPostBattlePremium)
            goldAutoEquipStr = self.__makeGoldLabel(-goldAutoEquip, not isPostBattlePremium)
            goldAutoEquipPremStr = self.__makeGoldLabel(-goldAutoEquip, isPostBattlePremium)
            creditsData.append(self.__getStatsLine(self.__resultLabel('autoEquip'), creditsAutoEquipStr, goldAutoEquipStr, creditsAutoEquipPremStr, goldAutoEquipPremStr))
            creditsData.append(self.__getStatsLine())
            creditsWithoutPremTotalStr = self.__makeCreditsLabel(creditsWithoutPremTotal - creditsAutoRepair - creditsAutoEquip - creditsAutoLoad, not isPostBattlePremium and not hasViolation)
            creditsWithPremTotalStr = self.__makeCreditsLabel(creditsWithPremTotal - creditsAutoRepair - creditsAutoEquip - creditsAutoLoad, isPostBattlePremium and not hasViolation)
            if vehIntCD is not None:
                _, personalDataRecord = findFirst(lambda (vId, d): vId == vehIntCD, personalData, (None, None))
                if personalDataRecord is not None:
                    personalDataRecord['pureCreditsReceived'] = (creditsWithPremTotal if isPremium else creditsWithoutPremTotal) - creditsAutoRepair - creditsAutoEquip - creditsAutoLoad
            goldTotalStr = self.__makeGoldLabel(eventGold - goldAutoEquip - goldAutoLoad, not isPostBattlePremium and not hasViolation)
            goldTotalPremStr = self.__makeGoldLabel(eventGold - goldAutoEquip - goldAutoLoad, isPostBattlePremium and not hasViolation)
            totalLbl = makeHtmlString('html_templates:lobby/battle_results', 'lightText', {'value': self.__resultLabel('total')})
            creditsData.append(self.__getStatsLine(totalLbl, creditsWithoutPremTotalStr, goldTotalStr, creditsWithPremTotalStr, goldTotalPremStr))
            vehsCreditsData.append(creditsData)
            xpData = []
            achievementXP = int(sourceData['achievementXP'])
            achievementFreeXP = sourceData['achievementFreeXP']
            xpPenalty = int(sourceData.get('xpPenaltyBase', 0))
            xpBase = int(sourceData['originalXP'])
            xpCell = xpBase - achievementXP
            keys = ('originalXP', 'achievementXP')
            xpCellPrem = self.__getPremCellValue(vehIntCD, keys, personalDataSource, premXpFactor, isPremium)
            xpCellStr = self.__makeXpLabel(xpCell, not isPostBattlePremium)
            xpCellPremStr = self.__makeXpLabel(xpCellPrem, isPostBattlePremium)
            freeXpBase = sourceData['originalFreeXP']
            freeXpCell = freeXpBase - achievementFreeXP
            dailyFreeXP = sourceData['dailyFreeXP']
            freeXpBaseStr = self.__makeFreeXpLabel(freeXpCell, not isPostBattlePremium)
            keys = ('originalFreeXP', 'achievementFreeXP')
            freeXpBasePremStr = self.__makeFreeXpLabel(self.__getPremCellValue(vehIntCD, keys, personalDataSource, premXpFactor, isPremium), isPostBattlePremium)
            medals = sourceData['dossierPopUps']
            if RECORD_DB_IDS[('max15x15', 'maxXP')] in map(lambda (id, value): id, medals):
                label = makeHtmlString('html_templates:lobby/battle_results', 'xpRecord', {})
            else:
                label = self.__resultLabel('base')
            xpData.append(self.__getStatsLine(label, xpCellStr, freeXpBaseStr, xpCellPremStr, freeXpBasePremStr))
            if isNoPenalty:
                xpData.append(self.__getStatsLine(self.__resultLabel('noPenalty'), self.__makeXpLabel(achievementXP, not isPostBattlePremium), self.__makeFreeXpLabel(achievementFreeXP, not isPostBattlePremium), self.__makeXpLabel(int(round(achievementXP * premXpFactor)), isPostBattlePremium), self.__makeFreeXpLabel(int(round(achievementFreeXP * premXpFactor)), isPostBattlePremium)))
            if fairPlayViolationName is not None:
                penaltyXPVal = self.__makePercentLabel(int(-100))
                xpData.append(self.__getStatsLine(self.__resultLabel('fairPlayViolation/' + fairPlayViolationName), penaltyXPVal, penaltyXPVal, penaltyXPVal, penaltyXPVal))
            xpPenaltyStr = self.__makeXpLabel(-xpPenalty, not isPostBattlePremium)
            xpPenaltyPremStr = self.__makeXpLabel(int(round(-xpPenalty * premXpFactor)), isPostBattlePremium)
            xpData.append(self.__getStatsLine(self.__resultLabel('friendlyFirePenalty'), xpPenaltyStr, None, xpPenaltyPremStr, None))
            if igrXpFactor > 1:
                icon = makeHtmlString('html_templates:igr/iconSmall', 'premium' if igrType == IGR_TYPE.PREMIUM else 'basic')
                igrBonusLabelStr = i18n.makeString(BATTLE_RESULTS.DETAILS_CALCULATIONS_IGRBONUS, igrIcon=icon)
                igrBonusStr = makeHtmlString('html_templates:lobby/battle_results', 'igr_bonus', {'value': BigWorld.wg_getNiceNumberFormat(igrXpFactor)})
                xpData.append(self.__getStatsLine(igrBonusLabelStr, igrBonusStr, igrBonusStr, igrBonusStr, igrBonusStr))
            if dailyXpFactor > 1:
                if vehIntCD is not None:
                    dailyXPVehs.append(vehIntCD)
                else:
                    multiplierLineIdxPos = len(xpData)
                dailyXpStr = makeHtmlString('html_templates:lobby/battle_results', 'multy_xp_small_label', {'value': int(dailyXpFactor)})
                xpData.append(self.__getStatsLine(self.__resultLabel('firstWin'), dailyXpStr, dailyXpStr, dailyXpStr, dailyXpStr))
            boosterXP = _calculateBaseParam('boosterXP', sourceData, premXpFactor, isPremium)
            boosterXPPrem = _calculateParamWithPrem('boosterXP', sourceData, premXpFactor, isPremium)
            boosterFreeXP = _calculateBaseParam('boosterFreeXP', sourceData, premXpFactor, isPremium)
            boosterFreeXPPrem = _calculateParamWithPrem('boosterFreeXP', sourceData, premXpFactor, isPremium)
            if boosterXP > 0 or boosterFreeXP > 0:
                boosterXPStr = self.__makeXpLabel(boosterXP, not isPostBattlePremium) if boosterXP else None
                boosterXPPremStr = self.__makeXpLabel(boosterXPPrem, isPostBattlePremium) if boosterXPPrem else None
                boosterFreeXPStr = self.__makeFreeXpLabel(boosterFreeXP, not isPostBattlePremium) if boosterFreeXP else None
                boosterFreeXPPremStr = self.__makeFreeXpLabel(boosterFreeXPPrem, isPostBattlePremium) if boosterFreeXPPrem else None
                xpData.append(self.__getStatsLine(self.__resultLabel('boosters'), boosterXPStr, boosterFreeXPStr, boosterXPPremStr, boosterFreeXPPremStr))
            orderXP = _calculateBaseParam('orderXP', sourceData, premXpFactor, isPremium)
            orderXPPrem = _calculateParamWithPrem('orderXP', sourceData, premXpFactor, isPremium)
            if orderXP > 0:
                orderXPStr = self.__makeXpLabel(orderXP, not isPostBattlePremium) if orderXP else None
                orderXPPremStr = self.__makeXpLabel(orderXPPrem, isPostBattlePremium) if orderXPPrem else None
                xpData.append(self.__getStatsLine(self.__resultLabel('tacticalTraining'), orderXPStr, None, orderXPPremStr, None))
            orderFreeXP = _calculateBaseParam('orderFreeXP', sourceData, premXpFactor, isPremium)
            orderFreeXPPrem = _calculateParamWithPrem('orderFreeXP', sourceData, premXpFactor, isPremium)
            if orderFreeXP > 0:
                orderFreeXPStr = self.__makeFreeXpLabel(orderFreeXP, not isPostBattlePremium) if orderFreeXP else None
                orderFreeXPPremStr = self.__makeFreeXpLabel(orderFreeXPPrem, isPostBattlePremium) if orderFreeXPPrem else None
                xpData.append(self.__getStatsLine(self.__resultLabel('militaryManeuvers'), None, orderFreeXPStr, None, orderFreeXPPremStr))
            eventXP = sourceData.get('eventXP', 0)
            eventFreeXP = sourceData.get('eventFreeXP', 0)
            if eventXP > 0 or eventFreeXP > 0:
                eventXPStr = self.__makeXpLabel(eventXP, not isPostBattlePremium)
                eventXPPremStr = self.__makeXpLabel(eventXP, isPostBattlePremium)
                eventFreeXPStr = self.__makeFreeXpLabel(eventFreeXP, not isPostBattlePremium)
                eventFreeXPPremStr = self.__makeFreeXpLabel(eventFreeXP, isPostBattlePremium)
                xpData.append(self.__getStatsLine(self.__resultLabel('event'), eventXPStr, eventFreeXPStr, eventXPPremStr, eventFreeXPPremStr))
            if refSystemFactor > 1:
                refSysXpValue = xpBase * igrXpFactor * refSystemFactor
                refSysFreeXpValue = freeXpBase * refSystemFactor
                refSysXPStr = self.__makeXpLabel(refSysXpValue, not isPostBattlePremium)
                refSysFreeXPStr = self.__makeFreeXpLabel(refSysFreeXpValue, not isPostBattlePremium)
                refSysXPPremStr = self.__makeXpLabel(round(refSysXpValue * premXpFactor), isPostBattlePremium)
                refSysFreeXPPremStr = self.__makeFreeXpLabel(round(refSysFreeXpValue * premXpFactor), isPostBattlePremium)
                xpData.append(self.__getStatsLine(self.__resultLabel('referralBonus'), refSysXPStr, refSysFreeXPStr, refSysXPPremStr, refSysFreeXPPremStr))
            premiumVehicleXP = sourceData['premiumVehicleXP']
            if premiumVehicleXP > 0:
                xpData.append(self.__getPremiumVehicleXP(premiumVehicleXP, isPremium, premXpFactor))
            if showSquadLabels:
                xpData.append(self.__getSquadXPDetails(squadXP, isPremium, isPostBattlePremium, premXpFactor))
            if aogasFactor < 1:
                xpData.append(self.__getStatsLine(self.__resultLabel('aogasFactor'), aogasValStr, aogasValStr, aogasValStr, aogasValStr))
            if len(xpData) < 3:
                xpData.append(self.__getStatsLine())
            if len(xpData) < 7:
                xpData.append(self.__getStatsLine())
            xpWithoutPremTotal = sourceData['xpWithoutPremTotal']
            xpTotal = self.__makeXpLabel(xpWithoutPremTotal, not isPostBattlePremium and not hasViolation)
            xpWithPremTotal = sourceData['xpWithPremTotal']
            xpPremTotal = self.__makeXpLabel(xpWithPremTotal, isPostBattlePremium and not hasViolation)
            freeXpTotal = self.__makeFreeXpLabel(self.__calculateTotalFreeXp(sourceData, aogasFactor, premXpFactor, igrXpFactor, refSystemFactor, isPremium, freeXpBase, dailyFreeXP, orderFreeXP, boosterFreeXP, eventFreeXP, hasViolation, False), not isPostBattlePremium and not hasViolation)
            freeXpPremTotal = self.__makeFreeXpLabel(self.__calculateTotalFreeXp(sourceData, aogasFactor, premXpFactor, igrXpFactor, refSystemFactor, isPremium, freeXpBase, dailyFreeXP, orderFreeXP, boosterFreeXP, eventFreeXP, hasViolation, True), isPostBattlePremium and not hasViolation)
            xpData.append(self.__getStatsLine(totalLbl, xpTotal, freeXpTotal, xpPremTotal, freeXpPremTotal))
            vehsXPData.append(xpData)
            if 'xpStr' not in personalDataOutput and 'creditsStr' not in personalDataOutput:
                if fairPlayViolationName is not None:
                    personalDataOutput['xpStr'] = '0'
                    personalDataOutput['creditsStr'] = '0'
                else:
                    showPremium = isPremium or isPostBattlePremium
                    personalDataOutput['xpStr'] = BigWorld.wg_getIntegralFormat(xpWithPremTotal if showPremium else xpWithoutPremTotal)
                    personalDataOutput['creditsStr'] = BigWorld.wg_getIntegralFormat(creditsWithPremTotal if showPremium else creditsWithoutPremTotal)
            showDiffs = False
            personalDataOutput['hasGetPremBtn'] = False
            creditsDiff = creditsWithPremTotal - creditsWithoutPremTotal
            xpDiff = xpWithPremTotal - xpWithoutPremTotal
            self.__premiumBonusesDiff = {'xpDiff': xpDiff,
             'creditDiff': creditsDiff}
            if g_lobbyContext.getServerSettings().isPremiumInPostBattleEnabled() and not isPremium and not g_itemsCache.items.stats.isPremium and bonusType == ARENA_BONUS_TYPE.REGULAR and xpDiff > 0 and creditsDiff > 0:
                personalDataOutput['getPremVO'] = {'arenaUniqueID': g_lobbyContext.getClientIDByArenaUniqueID(self.dataProvider.getArenaUniqueID()),
                 'creditsDiff': creditsDiff,
                 'xpDiff': xpDiff}
                showDiffs = True
                personalDataOutput['hasGetPremBtn'] = True
            valString = xpWithPremTotal if not showDiffs else xpDiff
            xpNoPremValues.append(self.__makeXpLabel(xpWithoutPremTotal, not isPostBattlePremium))
            xpPremValues.append(self.__makeXpLabel(valString, isPostBattlePremium, showDiffs))
            valString = creditsWithPremTotal if not showDiffs else creditsDiff
            creditsNoPremValues.append(self.__makeCreditsLabel(creditsWithoutPremTotal, not isPostBattlePremium))
            creditsPremValues.append(self.__makeCreditsLabel(valString, isPostBattlePremium, showDiffs))

        personalDataOutput['creditsData'] = vehsCreditsData
        personalDataOutput['xpData'] = vehsXPData
        if bonusType == ARENA_BONUS_TYPE.SORTIE:
            clanDBID = playerData.get('clanDBID')
            resValue = personalCommonData.get('fortResource', 0) if clanDBID else 0
            resValue = 0 if resValue is None else resValue
            orderFortResource = personalCommonData.get('orderFortResource', 0) if clanDBID else 0
            baseResValue = resValue - orderFortResource
            personalDataOutput['fortResourceTotal'] = BigWorld.wg_getIntegralFormat(baseResValue)
            resValues.append(self.__makeResourceLabel(baseResValue, not isPostBattlePremium) if clanDBID else '-')
            resPremValues.append(self.__makeResourceLabel(baseResValue, isPostBattlePremium) if clanDBID else '-')
            resData = []
            resData.append(self.__getStatsLine(self.__resultLabel('base'), None, self.__makeResourceLabel(baseResValue, not isPostBattlePremium), None, self.__makeResourceLabel(baseResValue, isPostBattlePremium)))
            if orderFortResource:
                resData.append(self.__getStatsLine(self.__resultLabel('heavyTrucks'), None, self.__makeResourceLabel(orderFortResource, not isPostBattlePremium), None, self.__makeResourceLabel(orderFortResource, isPostBattlePremium)))
            if len(resData) > 1:
                resData.append(self.__getStatsLine())
            resData.append(self.__getStatsLine(self.__resultLabel('total'), None, self.__makeResourceLabel(resValue, not isPostBattlePremium), None, self.__makeResourceLabel(resValue, isPostBattlePremium)))
            personalDataOutput['resourceData'] = resData
        personalDataOutput['isMultiplierInfoVisible'] = False
        if self.__isFallout and dailyXPVehs:
            personalDataOutput['isMultiplierInfoVisible'] = True
            htmlLineBreak = '<br/>'
            prefixVehName = i18n.makeString(BATTLE_RESULTS.DETAILS_CALCULATIONS_MULTIPLIERINFO_VEHICLESEPARATOR)
            vehNamesList = []
            for vehIntCD in dailyXPVehs:
                vehicleName, _, _, _, _ = self.__getVehicleData(vehIntCD)
                vehNamesList.append(prefixVehName + vehicleName)

            vehNames = htmlLineBreak.join(vehNamesList)
            header = BATTLE_RESULTS.DETAILS_CALCULATIONS_MULTIPLIERINFO_HEADER
            body = i18n.makeString(BATTLE_RESULTS.DETAILS_CALCULATIONS_MULTIPLIERINFO_BODY) + htmlLineBreak + vehNames
            personalDataOutput['multiplierTooltipStr'] = makeTooltip(header, body)
            personalDataOutput['premiumMultiplierTooltipStr'] = makeTooltip(header, body)
            personalDataOutput['multiplierLineIdxPos'] = multiplierLineIdxPos
        return

    def __buildPersonalDataSource(self, personalData, playerAvatarData):
        totalData = {}
        data = {}
        self.__aggregateData(data, playerAvatarData, totalData, CUMULATIVE_ACCOUNT_DATA)
        personaDataSource = [(None, totalData)]
        for vehIntCD, pData in personalData:
            data = {}
            self.__aggregateData(data, pData, totalData, CUMULATIVE_VEHICLE_DATA)
            personaDataSource.append((vehIntCD, data))

        return personaDataSource

    def __aggregateData(self, data, pData, totalData, params):
        for k, (d, func) in params:
            if k in RELATED_ACCOUNT_DATA:
                v = RELATED_ACCOUNT_DATA[k](pData, data)
            else:
                v = pData.get(k, d)
            data[k] = v
            if func is not None:
                totalData.setdefault(k, d)
                totalData[k] = func(totalData[k], v)
            totalData[k] = d

        return

    def __buildEfficiencyDataSource(self, pData, pCommonData, playersData, commonData):
        totalEnemies = []
        totalTechniquesGroup = []
        totalBasesGroup = []
        efficiencyDataSource = [(totalTechniquesGroup, totalEnemies, totalBasesGroup)]
        playerTeam = pCommonData.get('team')
        playerDBID = pCommonData.get('accountDBID')
        emptyDetails = {'spotted': 0,
         'deathReason': -1,
         'directHits': 0,
         'explosionHits': 0,
         'piercings': 0,
         'damageDealt': 0,
         'damageAssistedTrack': 0,
         'damageAssistedRadio': 0,
         'crits': 0,
         'fire': 0,
         'targetKills': 0}
        totalVehsData = {}
        for vehIntCD, data in pData:
            enemiesGroup = []
            for (vId, vIntCD), iInfo in data.get('details', dict()).iteritems():
                accountDBID = self.dataProvider.getAccountDBID(vId)
                pInfo = playersData.get(accountDBID, dict())
                if accountDBID == playerDBID:
                    continue
                team = pInfo.get('team', data.get('team') % 2 + 1)
                if team == playerTeam:
                    continue
                if isDefaultDict(iInfo, emptyDetails):
                    continue
                if (vId, vIntCD) not in totalVehsData:
                    totalVehsData[vId, vIntCD] = iInfo.copy()
                else:
                    totalVehData = totalVehsData[vId, vIntCD]
                    for k, v in iInfo.iteritems():
                        if k == 'deathReason':
                            currentValue = totalVehData[k]
                            if v > currentValue:
                                totalVehData[k] = v
                        totalVehData[k] += v

                enemiesGroup.append(((vId, vIntCD), iInfo))

            techniquesGroup, basesGroup = self.__getBasesInfo(data, commonData, enemiesGroup)
            totalTechniquesGroup += techniquesGroup
            totalBasesGroup += basesGroup
            efficiencyDataSource.append((techniquesGroup, enemiesGroup, totalBasesGroup))

        for (vId, vIntCD), iInfo in totalVehsData.iteritems():
            totalEnemies.append(((vId, vIntCD), iInfo))

        return efficiencyDataSource

    def __getPremiumVehicleXP(self, premiumVehicleXP, isPremiumAccount, premAccFactor):
        if isPremiumAccount:
            xpWithPremium, xpWithoutPremium = premiumVehicleXP, premiumVehicleXP / premAccFactor
        else:
            xpWithPremium, xpWithoutPremium = premiumVehicleXP * premAccFactor, premiumVehicleXP
        freeXpWithoutPremium = 0
        freeXpWithPremium = 0
        xpWithoutPremiumColumn = self.__makeXpLabel(xpWithoutPremium, not isPremiumAccount)
        xpWithPremiumColumn = self.__makeXpLabel(xpWithPremium, isPremiumAccount)
        freeXpWithoutPremiumColumn = self.__makeFreeXpLabel(freeXpWithoutPremium, not isPremiumAccount)
        freeXpWithPremiumColumn = self.__makeFreeXpLabel(freeXpWithPremium, isPremiumAccount)
        return self.__getStatsLine(self.__resultLabel('premiumVehicleXP'), xpWithoutPremiumColumn, freeXpWithoutPremiumColumn, xpWithPremiumColumn, freeXpWithPremiumColumn)

    def __getSquadXPDetails(self, squadXP, isPremiumAccount, isPostBattlePremium, premAccFactor):
        if isPremiumAccount:
            xpWithPremium, xpWithoutPremium = squadXP, squadXP / premAccFactor
        else:
            xpWithPremium, xpWithoutPremium = squadXP * premAccFactor, squadXP
        xpWithoutPremiumColumn = self.__makeXpLabel(xpWithoutPremium, not isPostBattlePremium)
        xpWithPremiumColumn = self.__makeXpLabel(xpWithPremium, isPostBattlePremium)
        freeXpWithoutPremiumColumn = freeXpWithPremiumColumn = None
        if squadXP < 0:
            label = 'squadXPPenalty'
            if isPostBattlePremium:
                xpWithoutPremiumColumn = None
            else:
                xpWithPremiumColumn = None
        else:
            label = 'squadXP'
        return self.__getStatsLine(self.__resultLabel(label), xpWithoutPremiumColumn, freeXpWithoutPremiumColumn, xpWithPremiumColumn, freeXpWithPremiumColumn)

    @classmethod
    def _packAchievement(cls, achieve, isUnique=False):
        customData = []
        recordName = achieve.getRecordName()
        if recordName == MARK_ON_GUN_RECORD:
            customData.extend([achieve.getDamageRating(), achieve.getVehicleNationID()])
        if recordName == MARK_OF_MASTERY_RECORD:
            customData.extend([achieve.getPrevMarkOfMastery(), achieve.getCompDescr()])
        return AchievementsUtils.getBattleResultAchievementData(achieve, recordName[1], customData, isUnique)

    def __populatePersonalMedals(self, pData, personalDataOutput):
        personalDataOutput['achievementsLeft'] = achievementsLeft = []
        personalDataOutput['achievementsRight'] = achievementsRight = []
        for _, data in pData:
            achievementsData = data.get('dossierPopUps', [])
            for achievementId, achieveValue in achievementsData:
                record = DB_ID_TO_RECORD[achievementId]
                if record in IGNORED_BY_BATTLE_RESULTS or not isAchievementRegistered(record):
                    continue
                factory = getAchievementFactory(record)
                if factory is not None:
                    achieve = factory.create(value=achieveValue)
                    isMarkOnGun = record == MARK_ON_GUN_RECORD
                    if isMarkOnGun:
                        if 'typeCompDescr' in data:
                            achieve.setVehicleNationID(vehicles_core.parseIntCompactDescr(data['typeCompDescr'])[1])
                        if 'damageRating' in data:
                            achieve.setDamageRating(data['damageRating'])
                    achieveData = self._packAchievement(achieve, isUnique=True)
                    if achieve.getName() in achievements.BATTLE_ACHIEVES_RIGHT:
                        if achieveData not in achievementsRight:
                            achievementsRight.append(achieveData)
                    elif achieveData not in achievementsLeft:
                        achievementsLeft.append(achieveData)

            markOfMastery = data.get('markOfMastery', 0)
            factory = getAchievementFactory(('achievements', 'markOfMastery'))
            if markOfMastery > 0 and factory is not None:
                achieve = factory.create(value=markOfMastery)
                achieve.setPrevMarkOfMastery(data.get('prevMarkOfMastery', 0))
                achieve.setCompDescr(data.get('typeCompDescr'))
                achieveData = self._packAchievement(achieve)
                if achieveData not in achievementsLeft:
                    achievementsLeft.append(achieveData)
            achievementsRight.sort(key=lambda k: k['isEpic'], reverse=True)

        return

    def __populateEfficiency(self, pData, pCommonData, playersData, commonData, personalDataOutput):
        valsStr = makeHtmlString('html_templates:lobby/battle_results', 'tooltip_params_style', {'text': i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_PARAMS_VAL)})
        bots = commonData.get('bots', {})
        details = []
        for techniquesGroup, enemiesGroup, basesGroup in self.__buildEfficiencyDataSource(pData, pCommonData, playersData, commonData):
            enemies = []
            for (vId, vIdx), iInfo in enemiesGroup:
                result = {}
                accountDBID = self.dataProvider.getAccountDBID(vId)
                vehsData = self.dataProvider.getVehiclesData(accountDBID)
                vIntCD = None
                for vehData in vehsData:
                    if vehData['index'] == vIdx:
                        vIntCD = vehData['typeCompDescr']

                if vIntCD is None and accountDBID is None and vId in bots:
                    vIntCD = bots.get(vId, (None, None))[0]
                deathReason = iInfo.get('deathReason', -1)
                if vehsData:
                    vInfo = vehsData[0]
                    deathReason = vInfo.get('deathReason', -1)
                _, result['vehicleName'], _, result['tankIcon'], _ = self.__getVehicleData(vIntCD)
                result['deathReason'] = deathReason
                result['spotted'] = iInfo.get('spotted', 0)
                result['piercings'] = iInfo.get('piercings', 0)
                result['damageDealt'] = iInfo.get('damageDealt', 0)
                playerNameData = self.__getPlayerName(accountDBID, bots, vId)
                result['playerFullName'] = playerNameData[0]
                result['playerName'], result['playerClan'], result['playerRegion'], _ = playerNameData[1]
                result['vehicleId'] = vId
                result['typeCompDescr'] = vIntCD
                result['killCount'] = iInfo.get('targetKills', 0)
                result['isAlly'] = False
                result['isFake'] = False
                result.update(self.__getDamageInfo(iInfo, valsStr))
                result.update(self.__getArmorUsingInfo(iInfo, valsStr))
                result.update(self.__getAssistInfo(iInfo, valsStr))
                result.update(self.__getCritsInfo(iInfo))
                enemies.append(result)

            enemies = sorted(enemies, cmp=self.__vehiclesComparator)
            details.append(techniquesGroup + enemies + basesGroup)

        personalDataOutput['details'] = details
        return

    def __getDamageInfo(self, iInfo, valsStr):
        piercings = iInfo['piercings']
        damageInfo = {'damageTotalItems': piercings}
        if int(iInfo['damageDealt']) > 0:
            damageInfo['damageDealtVals'] = makeHtmlString('html_templates:lobby/battle_results', 'tooltip_two_liner', {'line1': BigWorld.wg_getIntegralFormat(iInfo['damageDealt']),
             'line2': BigWorld.wg_getIntegralFormat(piercings)})
            damageInfo['damageDealtNames'] = makeHtmlString('html_templates:lobby/battle_results', 'tooltip_two_liner', {'line1': i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_DAMAGE_PART1, vals=valsStr),
             'line2': i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_DAMAGE_PART2)})
        return damageInfo

    def __getArmorUsingInfo(self, iInfo, valsStr):
        usedArmorCount = iInfo.get('noDamageDirectHitsReceived', 0)
        damageBlocked = iInfo.get('damageBlockedByArmor', 0)
        armorUsingInfo = {'armorTotalItems': usedArmorCount}
        if usedArmorCount > 0 or damageBlocked > 0:
            armorUsingInfo['armorVals'] = makeHtmlString('html_templates:lobby/battle_results', 'tooltip_three_liner', {'line1': BigWorld.wg_getIntegralFormat(iInfo['rickochetsReceived']),
             'line2': BigWorld.wg_getIntegralFormat(iInfo['noDamageDirectHitsReceived']),
             'line3': BigWorld.wg_getIntegralFormat(damageBlocked)})
            armorUsingInfo['armorNames'] = makeHtmlString('html_templates:lobby/battle_results', 'tooltip_three_liner', {'line1': i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_ARMOR_PART1),
             'line2': i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_ARMOR_PART2),
             'line3': i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_ARMOR_PART3, vals=valsStr)})
        return armorUsingInfo

    def __getAssistInfo(self, iInfo, valsStr):
        damageAssisted = iInfo.get('damageAssistedTrack', 0) + iInfo.get('damageAssistedRadio', 0)
        assistInfo = {'damageAssisted': damageAssisted}
        if damageAssisted > 0:
            assistInfo['damageAssistedVals'] = makeHtmlString('html_templates:lobby/battle_results', 'tooltip_three_liner', {'line1': BigWorld.wg_getIntegralFormat(iInfo['damageAssistedRadio']),
             'line2': BigWorld.wg_getIntegralFormat(iInfo['damageAssistedTrack']),
             'line3': BigWorld.wg_getIntegralFormat(damageAssisted)})
            assistInfo['damageAssistedNames'] = makeHtmlString('html_templates:lobby/battle_results', 'tooltip_three_liner', {'line1': i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_ASSIST_PART1, vals=valsStr),
             'line2': i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_ASSIST_PART2, vals=valsStr),
             'line3': i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_ASSIST_TOTAL, vals=valsStr)})
        return assistInfo

    def __getCritsInfo(self, iInfo):
        destroyedTankmen = iInfo['crits'] >> 24 & 255
        destroyedDevices = iInfo['crits'] >> 12 & 4095
        criticalDevices = iInfo['crits'] & 4095
        critsCount = 0
        criticalDevicesList = []
        destroyedDevicesList = []
        destroyedTankmenList = []
        for shift in range(len(vehicles.VEHICLE_DEVICE_TYPE_NAMES)):
            if 1 << shift & criticalDevices:
                critsCount += 1
                criticalDevicesList.append(self.__makeTooltipModuleLabel(vehicles.VEHICLE_DEVICE_TYPE_NAMES[shift], 'Critical'))
            if 1 << shift & destroyedDevices:
                critsCount += 1
                destroyedDevicesList.append(self.__makeTooltipModuleLabel(vehicles.VEHICLE_DEVICE_TYPE_NAMES[shift], 'Destroyed'))

        for shift in range(len(vehicles.VEHICLE_TANKMAN_TYPE_NAMES)):
            if 1 << shift & destroyedTankmen:
                critsCount += 1
                destroyedTankmenList.append(self.__makeTooltipTankmenLabel(vehicles.VEHICLE_TANKMAN_TYPE_NAMES[shift]))

        return {'critsCount': BigWorld.wg_getIntegralFormat(critsCount),
         'criticalDevices': LINE_BRAKE_STR.join(criticalDevicesList),
         'destroyedDevices': LINE_BRAKE_STR.join(destroyedDevicesList),
         'destroyedTankmen': LINE_BRAKE_STR.join(destroyedTankmenList)}

    def __getBasesInfo(self, pData, commonData, enemies):
        capturePoints = pData.get('capturePoints', 0)
        defencePoints = pData.get('droppedCapturePoints', 0)
        techniquesGroup = []
        basesGroup = []
        if capturePoints > 0 or defencePoints > 0:
            arenaTypeID = commonData.get('arenaTypeID', None)
            arenaSubType = ''
            if arenaTypeID is not None:
                arenaSubType = getArenaSubTypeName(arenaTypeID)
            if len(enemies):
                techniqueLabelStr = BATTLE_RESULTS.COMMON_BATTLEEFFICIENCY_TECHNIQUE
                techniquesGroup = [{'groupLabel': text_styles.middleTitle(techniqueLabelStr)}]
            basesGroupLabelStr = BATTLE_RESULTS.COMMON_BATTLEEFFICIENCY_BASES
            basesGroup = [{'groupLabel': text_styles.middleTitle(basesGroupLabelStr)}]
            if arenaSubType == 'domination':
                label = i18n.makeString(BATTLE_RESULTS.COMMON_BATTLEEFFICIENCY_NEUTRALBASE)
                basesGroup.append(self.__makeBaseVO(label, capturePoints, defencePoints))
            else:
                if capturePoints > 0:
                    label = i18n.makeString(BATTLE_RESULTS.COMMON_BATTLEEFFICIENCY_ENEMYBASE)
                    basesGroup.append(self.__makeBaseVO(label, capturePoints, 0))
                if defencePoints > 0:
                    label = i18n.makeString(BATTLE_RESULTS.COMMON_BATTLEEFFICIENCY_ALLYBASE)
                    basesGroup.append(self.__makeBaseVO(label, 0, defencePoints))
        return (techniquesGroup, basesGroup)

    def __makeBaseVO(self, label, capturePoints, defencePoints):
        data = {'baseLabel': text_styles.standard(label),
         'captureTotalItems': capturePoints,
         'defenceTotalItems': defencePoints}
        if capturePoints > 0:
            data['captureVals'] = BigWorld.wg_getIntegralFormat(capturePoints)
            data['captureNames'] = i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_CAPTURE_TOTALPOINTS)
        if defencePoints > 0:
            data['defenceVals'] = BigWorld.wg_getIntegralFormat(defencePoints)
            data['defenceNames'] = i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_DEFENCE_TOTALPOINTS)
        return data

    def __makeTooltipModuleLabel(self, key, suffix):
        return makeHtmlString('html_templates:lobby/battle_results', 'tooltip_crit_label', {'image': '{0}{1}'.format(key, suffix),
         'value': i18n.makeString('#item_types:{0}/name'.format(key))})

    def __makeTooltipTankmenLabel(self, key):
        return makeHtmlString('html_templates:lobby/battle_results', 'tooltip_crit_label', {'image': '{0}Destroyed'.format(key),
         'value': i18n.makeString('#item_types:tankman/roles/{0}'.format(key))})

    def __populateResultStrings(self, commonData, pData, avatarData, commonDataOutput, isMultiTeamMode):
        bonusType = commonData.get('bonusType', 0)
        winnerTeam = commonData.get('winnerTeam', 0)
        playerTeam = pData.get('team')
        finishReason = commonData.get('finishReason', 0)
        gasAttackWinnerTeam = commonData.get('gasAttackWinnerTeam', -1)
        if not winnerTeam:
            status = 'tie'
            if isMultiTeamMode and self.__isFallout:
                status = 'ended'
        elif winnerTeam == playerTeam:
            status = 'win'
        else:
            status = 'lose'
            if isMultiTeamMode and self.__isFallout:
                status = 'ended'

        def _finishReasonFormatter(formatter, **kwargs):
            return i18n.makeString(formatter.format(''.join([str(finishReason), str(status)])), **kwargs) if finishReason == 1 else i18n.makeString(formatter.format(finishReason))

        if bonusType == ARENA_BONUS_TYPE.FORT_BATTLE:
            fortBuilding = avatarData.get('fortBuilding', {})
            buildTypeID, buildTeam = fortBuilding.get('buildTypeID'), fortBuilding.get('buildTeam')
            if status == 'tie':
                status = 'win' if buildTeam == playerTeam else 'lose'
            commonDataOutput['resultShortStr'] = 'clanBattle_%s' % status
            if buildTypeID is not None:
                buildingName = FortBuilding(typeID=buildTypeID).userName
            else:
                buildingName = ''
            if buildTeam == pData.get('team'):
                _frFormatter = lambda : i18n.makeString(CLAN_BATTLE_FINISH_REASON_DEF.format(''.join([str(1), str(status)])), buildingName=buildingName)
            else:
                _frFormatter = lambda : i18n.makeString(CLAN_BATTLE_FINISH_REASON_ATTACK.format(''.join([str(1), str(status)])), buildingName=buildingName)
        else:
            commonDataOutput['resultShortStr'] = status
            _frFormatter = lambda : _finishReasonFormatter(FINISH_REASON)
        if not self.__isFallout:
            commonDataOutput['finishReasonStr'] = _frFormatter()
        else:
            falloutSubMode = 'multiteam' if isMultiTeamMode else 'classic'
            resultTemplate = '#battle_results:fallout/{submode}/{status}'.format(submode=falloutSubMode, status=status)
            if status != 'tie' and status != 'ended':
                finishReasonStr = 'points'
                if finishReason in (FR.WIN_POINTS_CAP, FR.WIN_POINTS):
                    finishReasonStr = 'cap'
                elif finishReason == FR.EXTERMINATION:
                    finishReasonStr = 'extermination'
                resultTemplate += '/' + finishReasonStr
            commonDataOutput['finishReasonStr'] = i18n.makeString(resultTemplate)
        commonDataOutput['overtime'] = {'enabled': gasAttackWinnerTeam > -1,
         'mainTitle': BATTLE_RESULTS.COMMON_MAINFINISHREASONTITLE,
         'overtimeTitle': BATTLE_RESULTS.COMMON_OVERTIMEFINISHREASONTITLE,
         'overtimeFinishReason': BATTLE_RESULTS.FINISH_OVERTIME_WIN if gasAttackWinnerTeam == playerTeam else BATTLE_RESULTS.FINISH_OVERTIME_LOSE}
        commonDataOutput['resultStr'] = RESULT_.format(status)
        return

    def __populateTankSlot(self, commonDataOutput, pData, pCommonData, commonData):
        vehsData = []
        vehNames = []
        bots = commonData.get('bots', {})
        accountDBID = pCommonData.get('accountDBID', None)
        playerNameData = self.__getPlayerName(accountDBID, bots, self.dataProvider.getVehicleID(accountDBID))
        commonDataOutput['playerNameStr'], commonDataOutput['clanNameStr'], commonDataOutput['regionNameStr'], _ = playerNameData[1]
        commonDataOutput['playerFullNameStr'] = playerNameData[0]
        if len(pData) > 1 or self.__isFallout:
            vehNames.append(i18n.makeString(BATTLE_RESULTS.ALLVEHICLES))
            vehsData.append({'tankIcon': RES_ICONS.MAPS_ICONS_LIBRARY_FALLOUTVEHICLESALL})
        for vehTypeCompDescr, data in pData:
            curVeh = {}
            vehicleName, _, curVeh['tankIcon'], _, nation = self.__getVehicleData(vehTypeCompDescr)
            killerID = data.get('killerID', 0)
            curVeh['killerID'] = killerID
            deathReason = data.get('deathReason', -1)
            isPrematureLeave = data.get('isPrematureLeave', False)
            curVeh['isPrematureLeave'] = isPrematureLeave
            curVeh['flag'] = nations.NAMES[nation]
            if isPrematureLeave:
                curVeh['vehicleStateStr'] = i18n.makeString(BATTLE_RESULTS.COMMON_VEHICLESTATE_PREMATURELEAVE)
            elif deathReason > -1:
                if vehTypeCompDescr and not isVehicleObserver(vehTypeCompDescr) and killerID:
                    curVeh['vehicleStateStr'] = i18n.makeString('#battle_results:common/vehicleState/dead{0}'.format(deathReason))
                    killerPlayerId = self.dataProvider.getAccountDBID(killerID)
                    curVeh['vehicleStatePrefixStr'] = '{0} ('.format(curVeh['vehicleStateStr'])
                    curVeh['vehicleStateSuffixStr'] = ')'
                    playerNameData = self.__getPlayerName(killerPlayerId, bots, killerID)
                    curVeh['killerFullNameStr'] = playerNameData[0]
                    curVeh['killerNameStr'], curVeh['killerClanNameStr'], curVeh['killerRegionNameStr'], _ = playerNameData[1]
                else:
                    curVeh['vehicleStateStr'] = ''
                    curVeh['vehicleStatePrefixStr'], curVeh['vehicleStateSuffixStr'] = ('', '')
                    curVeh['killerFullNameStr'], curVeh['killerNameStr'] = ('', '')
                    curVeh['killerClanNameStr'], curVeh['killerRegionNameStr'] = ('', '')
            else:
                curVeh['vehicleStateStr'] = BATTLE_RESULTS.COMMON_VEHICLESTATE_ALIVE
            vehNames.append(vehicleName)
            vehsData.append(curVeh)

        commonDataOutput['playerVehicles'] = vehsData
        commonDataOutput['playerVehicleNames'] = vehNames
        return

    def __populateArenaData(self, commonData, pData, commonDataOutput, isMultiTeamMode, isResource):
        arenaType = self.dataProvider.getArenaType()
        arenaGuiType = self.dataProvider.getArenaGuiType()
        commonDataOutput['arenaType'] = arenaGuiType
        if arenaGuiType == ARENA_GUI_TYPE.SORTIE:
            arenaGuiName = i18n.makeString(BATTLE_RESULTS.COMMON_BATTLETYPE_SORTIE)
        elif arenaGuiType == ARENA_GUI_TYPE.RANDOM:
            arenaGuiName = ARENA_TYPE.format(arenaType.gameplayName)
        else:
            arenaGuiName = ARENA_SPECIAL_TYPE.format(arenaGuiType)
        commonDataOutput['arenaStr'] = ARENA_NAME_PATTERN.format(i18n.makeString(arenaType.name), i18n.makeString(arenaGuiName))
        createTime = commonData.get('arenaCreateTime')
        createTime = time_utils.makeLocalServerTime(createTime)
        commonDataOutput['arenaCreateTimeStr'] = BigWorld.wg_getShortDateFormat(createTime) + ' ' + BigWorld.wg_getShortTimeFormat(createTime)
        commonDataOutput['arenaCreateTimeOnlyStr'] = BigWorld.wg_getShortTimeFormat(createTime)
        commonDataOutput['arenaIcon'] = self.__arenaVisitor.getArenaIcon(ARENA_SCREEN_FILE)
        duration = commonData.get('duration', 0)
        minutes = int(duration / 60)
        seconds = int(duration % 60)
        commonDataOutput['duration'] = i18n.makeString(TIME_DURATION_STR, minutes, seconds)
        commonDataOutput['playerKilled'] = '-'
        if pData.get('killerID', 0):
            lifeTime = pData.get('lifeTime', 0)
            minutes = int(lifeTime / 60)
            seconds = int(lifeTime % 60)
            commonDataOutput['playerKilled'] = i18n.makeString(TIME_DURATION_STR, minutes, seconds)
        commonDataOutput['timeStats'] = []
        for key in TIME_STATS_KEYS:
            commonDataOutput['timeStats'].append({'label': i18n.makeString(TIME_STATS_KEY_BASE.format(key)),
             'value': commonDataOutput[key]})

    def __makeTeamDamageStr(self, data):
        tkills = data.get('tkills', 0)
        tdamageDealt = data.get('tdamageDealt', 0)
        tDamageStr = '/'.join([str(tkills), str(tdamageDealt)])
        if tkills > 0 or tdamageDealt > 0:
            tDamageStr = self.__makeRedLabel(tDamageStr)
        else:
            tDamageStr = makeHtmlString('html_templates:lobby/battle_results', 'empty_stat_value', {'value': tDamageStr})
        return tDamageStr

    def __makeSlashedValuesStr(self, data, firstKey, secondKey):
        val1 = data.get(firstKey, 0)
        val1Str = str(val1) if val1 else makeHtmlString('html_templates:lobby/battle_results', 'empty_stat_value', {'value': val1})
        val2 = data.get(secondKey, 0)
        val2Str = str(val2) if val2 else makeHtmlString('html_templates:lobby/battle_results', 'empty_stat_value', {'value': val2})
        if not val1 and not val2:
            slash = makeHtmlString('html_templates:lobby/battle_results', 'empty_stat_value', {'value': '/'})
        else:
            slash = '/'
        return slash.join([val1Str, val2Str])

    def __makeMileageStr(self, mileage):
        km = float(mileage) / 1000
        val = BigWorld.wg_getFractionalFormat(km) + i18n.makeString(MILEAGE_STR_KEY)
        if not mileage:
            val = makeHtmlString('html_templates:lobby/battle_results', 'empty_stat_value', {'value': val})
        return val

    def __populateTeamsData(self, pCommonData, playersData, commonData, commonDataOutput, avatarsData, isMultiTeamMode, isFlags):
        squads = defaultdict(dict)
        stat = defaultdict(list)
        teamsScore = defaultdict(int)
        lastSquadId = 0
        squadManCount = 0
        playerSquadId = 0
        arenaType = self.dataProvider.getArenaType()
        playerDBID = pCommonData.get('accountDBID')
        playerTeam = pCommonData.get('team')
        allTeams = set(range(1, arenaType.maxTeamsInArena + 1))
        enemyTeams = allTeams - {playerTeam}
        bonusType = self.dataProvider.getArenaBonusType()
        winnerTeam = commonData.get('winnerTeam', 0)
        finishReason = commonData.get('finishReason', 0)
        bots = commonData.get('bots', {})
        playerNamePosition = bonusType in (ARENA_BONUS_TYPE.FORT_BATTLE, ARENA_BONUS_TYPE.CYBERSPORT, ARENA_BONUS_TYPE.RATED_CYBERSPORT)
        isPlayerObserver = isVehicleObserver(pCommonData.get('typeCompDescr', 0))
        fairPlayViolationName = _getFairPlayViolationName(pCommonData)
        if self.__isFallout and not isMultiTeamMode:
            isSolo = findFirst(lambda pData: pData['team'] == playerTeam, playersData.itervalues()) is None
            pointsKill, pointsFlags, (damageLimit, pointsDamage) = self.__arenaVisitor.type.getWinPointsCosts(isSolo=isSolo)
            formatter = BigWorld.wg_getNiceNumberFormat
            scorePatterns = []
            if isFlags and pointsFlags:
                costFlagTextPatterns = []
                for c in pointsFlags:
                    costFlagTextPatterns.append(i18n.makeString(TOOLTIPS.BATTLERESULTS_VICTORYSCOREDESCRIPTION_COST, cost=formatter(c)))

                scorePatterns.append(i18n.makeString(TOOLTIPS.BATTLERESULTS_VICTORYSCOREDESCRIPTION_POINTSPATTERN, pointsFlag=', '.join(costFlagTextPatterns)))
            if pointsKill > 0:
                costKillText = i18n.makeString(TOOLTIPS.BATTLERESULTS_VICTORYSCOREDESCRIPTION_COST, cost=formatter(pointsKill))
                scorePatterns.append(i18n.makeString(TOOLTIPS.BATTLERESULTS_VICTORYSCOREDESCRIPTION_KILLSPATTERN, pointsKill=costKillText))
            if pointsDamage > 0:
                costDamageText = i18n.makeString(TOOLTIPS.BATTLERESULTS_VICTORYSCOREDESCRIPTION_COST, cost=formatter(pointsDamage))
                scorePatterns.append(i18n.makeString('#tooltips:battleResults/victoryScoreDescription/damagePattern', pointsDamage=costDamageText, damageLimit=formatter(damageLimit)))
            tooltipText = i18n.makeString(TOOLTIPS.BATTLERESULTS_VICTORYSCOREDESCRIPTION_BODY, scorePattern=';\n'.join(scorePatterns))
            isExtermination = finishReason == FR.EXTERMINATION
            playerVictory = playerTeam == winnerTeam
            enemyVictory = winnerTeam in enemyTeams
            alliesSpecialStatus = BATTLE_RESULTS.EXTERMINATIONVICTORY_ALLIES if playerVictory and isExtermination else ''
            enemiesSpecialStatus = BATTLE_RESULTS.EXTERMINATIONVICTORY_ENEMIES if enemyVictory and isExtermination else ''
            commonDataOutput['victoryScore'] = [{'score': 0,
              'victory': playerVictory,
              'tooltip': tooltipText,
              'specialStatusStr': alliesSpecialStatus}, {'score': 0,
              'victory': enemyVictory,
              'tooltip': tooltipText,
              'specialStatusStr': enemiesSpecialStatus}]
        isInfluencePointsAvailable = True
        teamResource = 0
        teamInfluence = 0
        processSquads = bonusType in (ARENA_BONUS_TYPE.REGULAR,
         ARENA_BONUS_TYPE.FALLOUT_MULTITEAM,
         ARENA_BONUS_TYPE.FALLOUT_CLASSIC,
         ARENA_BONUS_TYPE.EVENT_BATTLES)
        for pId, pInfo in playersData.iteritems():
            rawVehsData = self.dataProvider.getVehiclesData(pId)

            def comparator(xData, yData):
                xIntCD = xData.get('typeCompDescr', None)
                yIntCD = yData.get('typeCompDescr', None)
                xVeh = g_itemsCache.items.getItemByCD(xIntCD)
                yVeh = g_itemsCache.items.getItemByCD(yIntCD)
                return cmp(xVeh, yVeh)

            vehsData = sorted(rawVehsData, cmp=comparator)
            vId = self.dataProvider.getVehicleID(pId)
            row = {'vehicleId': vId}
            isSelf = playerDBID == pId
            damageAssisted = []
            totalDamageAssisted = 0
            statValues = []
            totalStatValues = defaultdict(int)
            xp = 0
            damageDealt = 0
            achievementsData = []
            for data in vehsData:
                assisted = data.get('damageAssistedTrack', 0) + data.get('damageAssistedRadio', 0)
                damageAssisted.append(assisted)
                totalDamageAssisted += assisted
                xp += data.get('xp', 0) - data.get('achievementXP', 0)
                damageDealt += data.get('damageDealt', 0)
                statValues.append(self.__populateStatValues(data, isSelf))
                for achievement in data.get('achievements', []):
                    if achievement not in achievementsData:
                        achievementsData.append(achievement)

                for k, (d, func) in CUMULATIVE_STATS_DATA.iteritems():
                    if self.__isFallout and k in FALLOUT_EXCLUDE_VEHICLE_STATS:
                        continue
                    if not self.__isFallout and k in FALLOUT_ONLY_STATS:
                        continue
                    v = data.get(k, d)
                    totalStatValues.setdefault(k, d)
                    totalStatValues[k] = func(totalStatValues[k], v)

            damageAssisted.insert(0, totalDamageAssisted)
            totalStatValues['damageAssisted'] = totalDamageAssisted
            row['kills'] = kills = totalStatValues['kills']
            row['tkills'] = teamKills = totalStatValues['tkills']
            row['realKills'] = kills - teamKills
            row['damageDealt'] = damageDealt
            hasPenalty = False
            if pId in avatarsData:
                curAvatarData = avatarsData[pId]
                fairplayViolations = curAvatarData.get('fairplayViolations', (0, 0, 0))
                hasPenalty = fairplayViolations[1] > 0
                self.__addOrderDataToTotalValue(avatarsData[pId], totalStatValues)
                row['damageDealt'] += curAvatarData['avatarDamageDealt']
                row['kills'] += curAvatarData['avatarKills']
                row['realKills'] += curAvatarData['avatarKills']
            row['xp'] = 0 if hasPenalty else xp
            statValues.insert(0, self.__populateStatValues(totalStatValues, isSelf))
            row['statValues'] = statValues
            vehs = []
            if len(vehsData):
                vInfo = vehsData[0]
            else:
                vInfo = {}
            team = pInfo['team']
            if len(vehsData) > 1 or self.__isFallout:
                vehs.append({'label': i18n.makeString(BATTLE_RESULTS.ALLVEHICLES),
                 'icon': RES_ICONS.MAPS_ICONS_LIBRARY_FALLOUTVEHICLESALL})
                for vInfo in vehsData:
                    _, vehicleName, tankIcon, _, nation = self.__getVehicleData(vInfo.get('typeCompDescr', None))
                    vehs.append({'label': vehicleName,
                     'icon': tankIcon,
                     'flag': nations.NAMES[nation]})

            else:
                row['vehicleFullName'], row['vehicleName'], tankIcon, row['tankIcon'], _ = self.__getVehicleData(vInfo.get('typeCompDescr', None))
                row['vehicleCD'] = vInfo.get('typeCompDescr', None)
                vehs.append({'icon': tankIcon})
            row['vehicles'] = vehs
            if bonusType == ARENA_BONUS_TYPE.SORTIE:
                row['showResources'] = True
                if pInfo.get('clanDBID'):
                    resourceCount = 0 if hasPenalty else vInfo.get('fortResource', 0)
                    row['resourceCount'] = resourceCount
                    if team == playerTeam:
                        teamResource += resourceCount
                else:
                    row['resourceCount'] = None
            else:
                row['showResources'] = False
            if team == playerTeam:
                influencePoints = vInfo.get('influencePoints')
                if influencePoints is not None and isInfluencePointsAvailable:
                    teamInfluence += influencePoints
                elif isInfluencePointsAvailable:
                    isInfluencePointsAvailable = False
            achievementsList = []
            if not (pId == playerDBID and fairPlayViolationName is not None):
                for achievementId in achievementsData:
                    record = DB_ID_TO_RECORD[achievementId]
                    factory = getAchievementFactory(record)
                    if factory is not None and isAchievementRegistered(record):
                        achive = factory.create(value=0)
                        if not achive.isApproachable():
                            achievementsList.append(self._packAchievement(achive, isUnique=True))

                achievementsList.sort(key=lambda k: k['isEpic'], reverse=True)
            row['achievements'] = achievementsList
            row['medalsCount'] = len(achievementsList)
            isVehObserver = isVehicleObserver(vInfo.get('typeCompDescr', 0))
            isPrematureLeave = vInfo.get('isPrematureLeave', False)
            isDead = findFirst(operator.itemgetter('stopRespawn'), vehsData) is not None and not isPrematureLeave
            row['isPrematureLeave'] = isPrematureLeave
            row['vehicleStateStr'] = ''
            row['killerID'] = 0
            if self.__isFallout:
                row['deathReason'] = 0 if isDead else -1
                if isPrematureLeave:
                    row['vehicleStateStr'] = i18n.makeString(BATTLE_RESULTS.COMMON_VEHICLESTATE_PREMATURELEAVE)
            elif not isVehObserver:
                killerID = vInfo.get('killerID', 0)
                row['killerID'] = killerID
                deathReason = vInfo.get('deathReason', -1)
                row['deathReason'] = deathReason
                row['isPrematureLeave'] = isPrematureLeave
                if isPrematureLeave:
                    row['vehicleStateStr'] = i18n.makeString(BATTLE_RESULTS.COMMON_VEHICLESTATE_PREMATURELEAVE)
                elif deathReason > -1:
                    row['vehicleStateStr'] = ''
                    if killerID:
                        row['vehicleStateStr'] = i18n.makeString('#battle_results:common/vehicleState/dead{0}'.format(deathReason))
                        killerPlayerId = self.dataProvider.getAccountDBID(killerID)
                        row['vehicleStatePrefixStr'] = '{0} ('.format(row['vehicleStateStr'])
                        row['vehicleStateSuffixStr'] = ')'
                        playerNameData = self.__getPlayerName(killerPlayerId, bots, killerID)
                        row['killerFullNameStr'] = playerNameData[0]
                        row['killerNameStr'], row['killerClanNameStr'], row['killerRegionNameStr'], _ = playerNameData[1]
                else:
                    row['vehicleStateStr'] = BATTLE_RESULTS.COMMON_VEHICLESTATE_ALIVE
            row['playerId'] = pId
            row['userName'] = pInfo.get('name')
            playerNameData = self.__getPlayerName(pId, bots, vId)
            playerName, playerClan, playerRegion, playerIgrType = playerNameData[1]
            row['playerName'] = playerName
            row['userVO'] = {'fullName': playerNameData[0],
             'userName': playerName,
             'clanAbbrev': playerClan,
             'region': playerRegion,
             'igrType': playerIgrType}
            row['playerNamePosition'] = playerNamePosition
            if self.__isFallout:
                flagActions = totalStatValues['flagActions']
                row['falloutResourcePoints'] = totalStatValues['resourceAbsorbed']
                row['flags'] = flagActions[FLAG_ACTION.CAPTURED]
                row['deaths'] = totalStatValues['deathCount']
                row['deathsStr'] = self.__formatDeathsString(totalStatValues['deathCount'], isDead)
                playerScore = totalStatValues['winPoints']
                row['victoryScore'] = playerScore
                if isMultiTeamMode:
                    teamsScore[team] += playerScore
                else:
                    teamIdx = 0 if team == playerTeam else 1
                    commonDataOutput['victoryScore'][teamIdx]['score'] += playerScore
            row['isSelf'] = isSelf
            prebattleID = pInfo.get('prebattleID', 0)
            row['prebattleID'] = prebattleID
            if playerDBID == pId:
                playerSquadId = prebattleID
            if processSquads and prebattleID:
                if not lastSquadId or lastSquadId != prebattleID:
                    squadManCount = 1
                    lastSquadId = prebattleID
                else:
                    squadManCount += 1
                if prebattleID not in squads[team].keys():
                    squads[team][prebattleID] = 1
                else:
                    squads[team][prebattleID] += 1
            if not (isPlayerObserver and isVehObserver):
                stat[team].append(row)

        for team, data in stat.iteritems():
            data = sorted(data, cmp=self.__vehiclesByVehIDComparator)
            sortIdx = len(data)
            if processSquads:
                squadsSorted = sorted(squads[team].iteritems(), cmp=lambda x, y: cmp(x[0], y[0]))
                teamSquads = [ id for id, num in squadsSorted if 1 < num < 4 ]
            for item in data:
                item['vehicleSort'] = sortIdx
                item['xpSort'] = item.get('xp', 0)
                sortIdx -= 1
                if processSquads:
                    prbID = item.get('prebattleID')
                    item['isOwnSquad'] = playerSquadId == prbID if playerSquadId != 0 else False
                    item['squadID'] = teamSquads.index(prbID) + 1 if prbID in teamSquads else 0
                item['squadID'] = 0
                item['isOwnSquad'] = False

            if team == playerTeam:
                commonDataOutput['totalFortResourceStr'] = makeHtmlString('html_templates:lobby/battle_results', 'teamResourceTotal', {'resourceValue': teamResource})
                if isInfluencePointsAvailable and teamInfluence > 0:
                    commonDataOutput['totalInfluenceStr'] = makeHtmlString('html_templates:lobby/battle_results', 'teamInfluenceTotal', {'resourceValue': teamInfluence})

        team1 = []
        team2 = []
        if isMultiTeamMode:
            squadIdx = 0
            for t in allTeams:
                teamData = stat.get(t, [])
                squadIdxIsSet = False
                for playerData in teamData:
                    if playerData['squadID'] > 0:
                        if not squadIdxIsSet:
                            squadIdx += 1
                            squadIdxIsSet = True
                        playerData['squadID'] = squadIdx
                    playerData['teamScore'] = teamsScore[t]

                team1.extend(teamData)

        else:
            team1 = stat[playerTeam]
            map(lambda teamID: team2.extend(stat[teamID]), enemyTeams)
        return (team1, team2)

    def __addOrderDataToTotalValue(self, avatarData, resultDict):
        if 'avatarDamageDealt' in avatarData and 'avatarKills' in avatarData:
            damageByOrder = avatarData['avatarDamageDealt']
            killsByOrder = avatarData['avatarKills']
            resultDict['damageDealt'] += damageByOrder
            resultDict['kills'] += killsByOrder
            resultDict['damaged'] = avatarData['totalDamaged']
            resultDict['damagedByOrder'] = avatarData['avatarDamaged']
            resultDict['damageDealtByOrder'] = damageByOrder
            resultDict['killsByOrder'] = killsByOrder

    def __formatDeathsString(self, deathCount, isDead):
        if isDead:
            result = text_styles.critical(str(deathCount))
        else:
            result = text_styles.standard(str(deathCount))
        return result

    def __calculateTotalCredits(self, pData, eventCredits, premCreditsFactor, isPremium, aogasFactor, baseCredits, baseOrderCredits, baseBoosterCredits, creditsToDraw, creditsPenalty, creditsCompensation, hasViolation, usePremFactor=False):
        premFactor = premCreditsFactor if usePremFactor else 1.0
        givenCredits = pData['credits']
        credits = int(givenCredits - round(creditsToDraw * premFactor))
        if isPremium != usePremFactor:
            givenCredits = 0
            if not hasViolation:
                givenCredits = (int(round(baseCredits * premFactor)) + int(round(baseOrderCredits * premFactor)) + int(round(baseBoosterCredits * premFactor)) + int(round(eventCredits))) * aogasFactor
            credits = int(givenCredits - round(creditsToDraw * premFactor * aogasFactor) - int(round(creditsPenalty * premFactor * aogasFactor)) + int(round(creditsCompensation * premFactor * aogasFactor)))
        return credits

    def __calculateTotalFreeXp(self, pData, aogasFactor, premXpFactor, igrXpFactor, refSystemFactor, isPremium, baseFreeXp, dailyFreeXp, baseOrderFreeXp, baseBoosterFreeXP, eventFreeXP, hasViolation, usePremFactor=False):
        if hasViolation:
            return 0
        freeXP = float(pData['freeXP'])
        if isPremium != usePremFactor:
            premXpFactor = premXpFactor if usePremFactor else 1.0
            subtotalXp = int(round(int(round(baseFreeXp * premXpFactor)) * igrXpFactor))
            resultXp = int(round(int(round(dailyFreeXp * premXpFactor)) * igrXpFactor))
            if abs(refSystemFactor - 1.0) > 0.001:
                resultXp += int(round(subtotalXp * refSystemFactor))
            freeXP = int(round((resultXp + int(round(baseOrderFreeXp * premXpFactor)) + int(round(baseBoosterFreeXP * premXpFactor)) + int(round(eventFreeXP))) * aogasFactor))
        return freeXP

    def __calculateBaseCreditsPenalty(self, pData, premFactor, isPremium):
        creditsPenalty = pData['creditsPenalty'] + pData['creditsContributionOut']
        if isPremium:
            creditsPenalty = math.ceil(creditsPenalty / premFactor)
        return creditsPenalty

    def selectVehicle(self, inventoryId):
        g_currentVehicle.selectVehicle(inventoryId)
        return g_currentVehicle.invID == inventoryId

    def __parseQuestsProgress(self, personalData, avatarData):
        questsProgress = avatarData.get('questsProgress', {})
        for _, data in personalData:
            questsProgress.update(data.get('questsProgress', {}))

        if not questsProgress:
            return
        else:

            def _isFortQuest(q):
                return q.getType() == EVENT_TYPE.FORT_QUEST

            def _sortCommonQuestsFunc(aData, bData):
                aQuest, aCurProg, aPrevProg, _, _ = aData
                bQuest, bCurProg, bPrevProg, _, _ = bData
                res = cmp(aQuest.isCompleted(aCurProg), bQuest.isCompleted(bCurProg))
                if res:
                    return -res
                res = cmp(_isFortQuest(aQuest), _isFortQuest(bQuest))
                if res:
                    return -res
                if aQuest.isCompleted() and bQuest.isCompleted(bCurProg):
                    res = aQuest.getBonusCount(aCurProg) - aPrevProg.get('bonusCount', 0) - (bQuest.getBonusCount(bCurProg) - bPrevProg.get('bonusCount', 0))
                    if not res:
                        return res
                return cmp(aQuest.getID(), bQuest.getID())

            from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
            quests = g_eventsCache.getQuests()
            commonQuests, potapovQuests = [], {}
            for qID, qProgress in questsProgress.iteritems():
                pGroupBy, pPrev, pCur = qProgress
                isCompleted = pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0
                if qID in quests:
                    quest = quests[qID]
                    isProgressReset = not isCompleted and quest.bonusCond.isInRow() and pCur.get('battlesCount', 0) == 0
                    if pPrev or max(pCur.itervalues()) != 0:
                        commonQuests.append((quest,
                         {pGroupBy: pCur},
                         {pGroupBy: pPrev},
                         isProgressReset,
                         isCompleted))
                if potapov_quests.g_cache.isPotapovQuest(qID):
                    pqID = potapov_quests.g_cache.getPotapovQuestIDByUniqueID(qID)
                    if self.__isFallout:
                        questsCache = g_eventsCache.fallout
                    else:
                        questsCache = g_eventsCache.random
                    quest = questsCache.getQuests()[pqID]
                    progress = potapovQuests.setdefault(quest, {})
                    progress.update({qID: isCompleted})

            formatted = []
            for e, data in sorted(potapovQuests.items(), key=operator.itemgetter(0)):
                if data.get(e.getAddQuestID(), False):
                    complete = (True, True)
                elif data.get(e.getMainQuestID(), False):
                    complete = (True, False)
                else:
                    complete = (False, False)
                info = events_helpers.getEventPostBattleInfo(e, quests, None, None, False, complete)
                if info is not None:
                    formatted.append(info)

            for e, pCur, pPrev, reset, complete in sorted(commonQuests, cmp=_sortCommonQuestsFunc):
                info = events_helpers.getEventPostBattleInfo(e, quests, pCur, pPrev, reset, complete)
                if info is not None:
                    formatted.append(info)

            return formatted

    @async
    @process
    def __getCommonData(self, callback):
        provider = yield self.dataProvider.request()
        if provider.isSynced():
            results = provider.getResults()
        else:
            results = None
        LOG_DEBUG('Player got battle results', self.dataProvider, results)
        if results:
            personalDataSource = results.get('personal', {}).copy()
            playerAvatarData = personalDataSource.pop('avatar', {})
            avatarsData = results.pop('avatars', {})
            personalCommonData = personalDataSource.values()[0]
            playerID = personalCommonData['accountDBID']

            def comparator(x, y):
                _, xData = x
                _, yData = y
                xIntCD = xData.get('typeCompDescr', None)
                yIntCD = yData.get('typeCompDescr', None)
                xVeh = g_itemsCache.items.getItemByCD(xIntCD)
                yVeh = g_itemsCache.items.getItemByCD(yIntCD)
                return cmp(xVeh, yVeh)

            personalData = sorted(personalDataSource.iteritems(), cmp=comparator)
            playersData = results.get('players', {}).copy()
            commonData = results.get('common', {}).copy()
            bonusType = commonData.get('bonusType', 0)
            personalDataOutput = {}
            commonDataOutput = {}
            textData = {'windowTitle': i18n.makeString(MENU.FINALSTATISTIC_WINDOW_TITLE),
             'shareButtonLabel': i18n.makeString(BATTLE_RESULTS.COMMON_RESULTSSHAREBTN),
             'shareButtonTooltip': i18n.makeString(TOOLTIPS.BATTLERESULTS_FORTRESOURCE_RESULTSSHAREBTN)}
            commonDataOutput['bonusType'] = bonusType
            if bonusType == ARENA_BONUS_TYPE.SORTIE or bonusType == ARENA_BONUS_TYPE.FORT_BATTLE:
                clanData = self.__processClanData(personalCommonData, playersData)
                commonDataOutput['clans'] = clanData
                textData['ownTitle'] = BATTLE_RESULTS.TEAM_STATS_OWNTEAM + ' ' + clanData['allies']['clanAbbrev']
                textData['enemyTitle'] = BATTLE_RESULTS.TEAM_STATS_ENEMYTEAM + ' ' + clanData['enemies']['clanAbbrev']
            else:
                commonDataOutput['clans'] = {'allies': {'clanDBID': -1,
                            'clanAbbrev': ''},
                 'enemies': {'clanDBID': -1,
                             'clanAbbrev': ''}}
                textData['ownTitle'] = BATTLE_RESULTS.TEAM_STATS_OWNTEAM
                textData['enemyTitle'] = BATTLE_RESULTS.TEAM_STATS_ENEMYTEAM
            commonDataOutput['battleResultsSharingIsAvailable'] = self._isSharingBtnEnabled()
            self.__arenaVisitor = arena_visitor.createSkeleton(arenaType=self.dataProvider.getArenaType(), guiType=self.dataProvider.getArenaGuiType(), bonusType=self.dataProvider.getArenaBonusType())
            self.__isFallout = self.__arenaVisitor.gui.isFalloutBattle()
            teams = {}
            for pInfo in playersData.itervalues():
                team = pInfo['team']
                if team not in teams:
                    teams[team] = pInfo['prebattleID']

            isMultiTeamMode = self.__arenaVisitor.gui.isFalloutMultiTeam()
            isFFA = isMultiTeamMode and findFirst(lambda prbID: prbID > 0, teams.itervalues()) is None
            isResource = self.__arenaVisitor.hasResourcePoints()
            isFlags = self.__arenaVisitor.hasFlags()
            statsSorting = AccountSettings.getSettings('statsSorting' if bonusType != ARENA_BONUS_TYPE.SORTIE else 'statsSortingSortie')
            if self.__isFallout:
                commonDataOutput['iconType'] = 'victoryScore'
                commonDataOutput['sortDirection'] = 'descending'
            else:
                commonDataOutput['iconType'] = statsSorting.get('iconType')
                commonDataOutput['sortDirection'] = statsSorting.get('sortDirection')
            damageAssisted = []
            totalDamageAssisted = 0
            statValues = []
            totalStatValues = defaultdict(int)
            for _, data in personalData:
                assisted = data.get('damageAssistedTrack', 0) + data.get('damageAssistedRadio', 0)
                damageAssisted.append(assisted)
                totalDamageAssisted += assisted
                statValues.append(self.__populateStatValues(data, True))
                for k, (d, func) in CUMULATIVE_STATS_DATA.iteritems():
                    if self.__isFallout and k in FALLOUT_EXCLUDE_VEHICLE_STATS:
                        continue
                    if not self.__isFallout and k in FALLOUT_ONLY_STATS:
                        continue
                    v = data.get(k, d)
                    totalStatValues.setdefault(k, d)
                    totalStatValues[k] = func(totalStatValues[k], v)

            damageAssisted.insert(0, totalDamageAssisted)
            totalStatValues['damageAssisted'] = totalDamageAssisted
            if playerID in avatarsData:
                self.__addOrderDataToTotalValue(avatarsData[playerID], totalStatValues)
            statValues.insert(0, self.__populateStatValues(totalStatValues, True))
            personalDataOutput['statValues'] = statValues
            self.__populateResultStrings(commonData, personalCommonData, playerAvatarData, commonDataOutput, isMultiTeamMode)
            self.__populatePersonalMedals(personalData, personalDataOutput)
            self.__populateArenaData(commonData, personalCommonData, commonDataOutput, isMultiTeamMode, isResource)
            self.__populateAccounting(commonData, personalCommonData, personalData, playersData, personalDataOutput, playerAvatarData)
            self.__populateTankSlot(commonDataOutput, personalData, personalCommonData, commonData)
            self.__populateEfficiency(personalData, personalCommonData, playersData, commonData, personalDataOutput)
            team1, team2 = self.__populateTeamsData(personalCommonData, playersData, commonData, commonDataOutput, avatarsData, isMultiTeamMode, isFlags)
            resultingVehicles = []
            falloutMode = ''
            if self.__isFallout:
                if isResource:
                    falloutMode = 'points'
                else:
                    falloutMode = 'flags'
            commonDataOutput['falloutMode'] = falloutMode
            commonDataOutput['wasInBattle'] = self.dataProvider.wasInBattle(getAccountDatabaseID())
            if isMultiTeamMode:
                tabInfo = [{'label': MENU.FINALSTATISTIC_TABS_COMMONSTATS,
                  'linkage': 'CommonStats',
                  'showWndBg': False}, {'label': MENU.FINALSTATISTIC_TABS_TEAMSTATS,
                  'linkage': 'MultiteamStatsUI',
                  'showWndBg': False}, {'label': MENU.FINALSTATISTIC_TABS_DETAILSSTATS,
                  'linkage': 'DetailsStatsViewUI',
                  'showWndBg': True}]
            else:
                tabInfo = [{'label': MENU.FINALSTATISTIC_TABS_COMMONSTATS,
                  'linkage': 'CommonStats',
                  'showWndBg': False}, {'label': MENU.FINALSTATISTIC_TABS_TEAMSTATS,
                  'linkage': 'TeamStatsUI',
                  'showWndBg': False}, {'label': MENU.FINALSTATISTIC_TABS_DETAILSSTATS,
                  'linkage': 'DetailsStatsViewUI',
                  'showWndBg': True}]
            if self.__arenaVisitor.gui.isNotRatedSandboxBattle():
                personalDataOutput['showNoIncomeAlert'] = True
                sandboxStrBuilder = text_styles.builder(delimiter='\n')
                sandboxStrBuilder.addStyledText(text_styles.middleTitle, BATTLE_RESULTS.COMMON_NOINCOME_ALERT_TITLE)
                sandboxStrBuilder.addStyledText(text_styles.standard, BATTLE_RESULTS.COMMON_NOINCOME_ALERT_TEXT)
                personalDataOutput['noIncomeAlert'] = {'icon': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON,
                 'text': sandboxStrBuilder.render()}
            selectedTeamMemberId = -1
            closingTeamMemberStatsEnabled = True
            if self.__arenaVisitor.gui.isSandboxBattle():
                selectedTeamMemberId = personalCommonData.get('accountDBID')
                closingTeamMemberStatsEnabled = False
            results = {'personal': personalDataOutput,
             'common': commonDataOutput,
             'team1': team1,
             'team2': team2,
             'textData': textData,
             'vehicles': resultingVehicles,
             'quests': self.__parseQuestsProgress(personalData, playerAvatarData),
             'unlocks': self.__getVehicleProgress(self.dataProvider.getArenaUniqueID(), personalData),
             'tabInfo': tabInfo,
             'isFreeForAll': isFFA,
             'closingTeamMemberStatsEnabled': closingTeamMemberStatsEnabled,
             'selectedTeamMemberId': selectedTeamMemberId}
            if self.dataProvider.results:
                self.dataProvider.results.updateViewData(results)
            callback(results)
        else:
            callback(None)
        return

    def getTeamEmblem(self, uid, clubDbID, isUseHtmlWrap):
        if self._isRated7x7Battle():
            results = self.dataProvider.results
            results.requestTeamInfo(clubDbID == results.getOwnClubDbID(), partial(self._onTeamInfoReceived, uid, isUseHtmlWrap))

    def _onTeamInfoReceived(self, uid, useWrap, teamInfo):
        if not self.isDisposed() and teamInfo:
            teamInfo.requestEmblemID(partial(self._onTeamEmblemReceived, uid, useWrap, teamInfo))

    def _onTeamEmblemReceived(self, uid, useWrap, teamInfo, emblemID):
        if not self.isDisposed() and emblemID:
            self.as_setTeamInfoS(uid, _wrapEmblemUrl(emblemID) if useWrap else emblemID, teamInfo.getUserName())

    @process
    def getClanEmblem(self, uid, clanDBID):
        clanEmblem = yield g_clanCache.getClanEmblemTextureID(clanDBID, False, uid)
        if not self.isDisposed():
            self.as_setClanEmblemS(uid, _wrapEmblemUrl(clanEmblem))

    def onTeamCardClick(self, teamDBID):
        club_events.showClubProfile(long(teamDBID))

    def onResultsSharingBtnPress(self):
        raise NotImplemented

    def _isSharingBtnEnabled(self):
        results = self.dataProvider.getResults()
        if results is not None:
            isSubUrlAvailable = 'uniqueSubUrl' in results and results['uniqueSubUrl'] is not None
            return GUI_SETTINGS.postBattleExchange.enabled and isSubUrlAvailable and results['common']['guiType'] not in (ARENA_GUI_TYPE.FORT_BATTLE,)
        else:
            return False

    def __processClanData(self, personalData, playersData):
        clans = []
        resClans = {'allies': {'clanDBID': -1,
                    'clanAbbrev': ''},
         'enemies': {'clanDBID': -1,
                     'clanAbbrev': ''}}
        for pId, pInfo in playersData.iteritems():
            clanDBID = pInfo.get('clanDBID')
            if clanDBID and clanDBID not in clans:
                clans.append(clanDBID)
                resClans['allies' if pInfo.get('team') == personalData.get('team') else 'enemies'] = {'clanDBID': clanDBID,
                 'clanAbbrev': i18n.makeString(BATTLE_RESULTS.COMMON_CLANABBREV, clanAbbrev=pInfo.get('clanAbbrev'))}

        return resClans

    def __showDivisionAnimation(self, curDivision, prevDivision):
        uniqueKey = (self.dataProvider.getArenaUniqueID(), curDivision, prevDivision)
        if uniqueKey in self.__rated7x7Animations:
            return
        self.__rated7x7Animations.add(uniqueKey)
        curLeague, prevLeague = getLeagueByDivision(curDivision), getLeagueByDivision(prevDivision)
        if curLeague < prevLeague:
            animationType = CYBER_SPORT_ALIASES.CS_ANIMATION_LEAGUE_UP
        elif curDivision > prevDivision:
            if getDivisionWithinLeague(curDivision) == 0:
                animationType = CYBER_SPORT_ALIASES.CS_ANIMATION_LEAGUE_DIVISION_UP_ALT
            else:
                animationType = CYBER_SPORT_ALIASES.CS_ANIMATION_LEAGUE_DIVISION_UP_ALT
        else:
            animationType = CYBER_SPORT_ALIASES.CS_ANIMATION_LEAGUE_DIVISION_DOWN
        if animationType != CYBER_SPORT_ALIASES.CS_ANIMATION_LEAGUE_DIVISION_DOWN:
            divAddSource = battle_res_fmts.getAnimationDivisionIcon(curLeague, curDivision)
        else:
            divAddSource = ''
        if curDivision > prevDivision:
            description = i18n.makeString(CYBERSPORT.CSANIMATION_DESCRIPTION)
        else:
            description = ''
        self.as_setAnimationS({'headerText': i18n.makeString(CYBERSPORT.CSANIMATION_HEADER),
         'descriptionText': description,
         'applyBtnLabel': CYBERSPORT.CSANIMATION_APPLYBTN_LABEL,
         'animationType': animationType,
         'leavesOldSource': battle_res_fmts.getAnimationLeavesIcon(prevLeague, prevDivision),
         'leavesNewSource': battle_res_fmts.getAnimationLeavesIcon(curLeague, curDivision),
         'ribbonOldSource': battle_res_fmts.getAnimationRibbonIcon(prevLeague, prevDivision),
         'ribbonNewSource': battle_res_fmts.getAnimationRibbonIcon(curLeague, curDivision),
         'divisionOldSource': battle_res_fmts.getAnimationDivisionIcon(prevLeague, prevDivision),
         'divisionNewSource': battle_res_fmts.getAnimationDivisionIcon(curLeague, curDivision),
         'logoOldSource': battle_res_fmts.getAnimationLogoIcon(prevLeague, prevDivision),
         'logoNewSource': battle_res_fmts.getAnimationLogoIcon(curLeague, curDivision),
         'divisionAdditionalSource': divAddSource})

    def startCSAnimationSound(self, soundEffectID='cs_animation_league_up'):
        self.app.soundManager.playEffectSound(soundEffectID)

    def _isRated7x7Battle(self):
        return self.dataProvider.getArenaBonusType() == ARENA_BONUS_TYPE.RATED_CYBERSPORT

    def __getVehicleProgress(self, arenaUniqueID, personalData):
        progressList = g_vehicleProgressCache.getVehicleProgressList(arenaUniqueID)
        if progressList is None:
            for _, data in personalData:
                vehTypeCompDescr = data.get('typeCompDescr')
                vehicleBattleXp = data.get('xp', 0)
                pureCreditsReceived = data.get('pureCreditsReceived', 0)
                tmenXps = dict(data.get('xpByTmen', []))
                progressHelper = VehicleProgressHelper(vehTypeCompDescr)
                progressList = progressHelper.getProgressList(vehicleBattleXp, pureCreditsReceived, tmenXps)
                progressHelper.clear()
                g_vehicleProgressCache.saveVehicleProgress(arenaUniqueID, progressList)

        return progressList

    def showUnlockWindow(self, itemId, unlockType):
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher and prbDispatcher.getFunctionalState().isNavigationDisabled():
            return SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error)
        if unlockType in (PROGRESS_ACTION.RESEARCH_UNLOCK_TYPE, PROGRESS_ACTION.PURCHASE_UNLOCK_TYPE):
            showResearchView(itemId)
            self.onWindowClose()
        elif unlockType == PROGRESS_ACTION.NEW_SKILL_UNLOCK_TYPE:
            showPersonalCase(itemId, 2, EVENT_BUS_SCOPE.LOBBY)

    def __onPremiumBought(self, event):
        arenaUniqueID = event.ctx.get('arenaUniqueID')
        if arenaUniqueID and arenaUniqueID not in self.__buyPremiumCache:
            self.__buyPremiumCache.add(arenaUniqueID)
            if arenaUniqueID == self.dataProvider.getArenaUniqueID():
                self.__showStats()
        elif event.ctx.get('becomePremium', False):
            self.__showStats()

    def __showStats(self):
        results = self.dataProvider.getResults()
        self.onWindowClose()
        showBattleResultsFromData(results)

    def __getPremCellValue(self, calcVehIntCD, keys, personalDataSource, premXpFactor, isPremium):
        premSum = 0
        xpKey, achievementKey = keys
        for vehIntCD, sourceData in personalDataSource:
            xpCell = sourceData[xpKey] - sourceData[achievementKey]
            if calcVehIntCD is not None and calcVehIntCD == vehIntCD:
                return int(round(xpCell * premXpFactor))
            if not isPremium and calcVehIntCD is None and calcVehIntCD == vehIntCD:
                return int(round(xpCell * premXpFactor))
            if vehIntCD is not None:
                premSum += int(round(xpCell * premXpFactor))

        return premSum

    def __onWindowClose(self, event):
        self.onWindowClose()
