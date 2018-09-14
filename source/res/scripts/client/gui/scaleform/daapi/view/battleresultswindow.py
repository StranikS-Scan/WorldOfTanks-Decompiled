# Embedded file name: scripts/client/gui/Scaleform/daapi/view/BattleResultsWindow.py
from collections import defaultdict
import re
import math
import operator
from functools import partial
import BigWorld
import ArenaType
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.battle_results.VehicleProgressCache import g_vehicleProgressCache
from gui.battle_results.VehicleProgressHelper import VehicleProgressHelper, PROGRESS_ACTION
from gui.shared.event_dispatcher import showResearchView, showPersonalCase
from gui.shared.utils.functions import getArenaSubTypeName
from gui.shared.view_helpers.FalloutInfoPanelHelper import getCosts
import nations
import potapov_quests
from account_helpers.AccountSettings import AccountSettings
from account_shared import getFairPlayViolationName, packPostBattleUniqueSubUrl
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from helpers import i18n, time_utils
from adisp import async, process
from CurrentVehicle import g_currentVehicle
from constants import ARENA_BONUS_TYPE, IS_DEVELOPMENT, ARENA_GUI_TYPE, IGR_TYPE, EVENT_TYPE, FINISH_REASON as FR, FLAG_ACTION
from dossiers2.custom.records import RECORD_DB_IDS, DB_ID_TO_RECORD
from dossiers2.ui import achievements
from dossiers2.ui.achievements import ACHIEVEMENT_TYPE, MARK_ON_GUN_RECORD, MARK_OF_MASTERY_RECORD
from dossiers2.ui.layouts import IGNORED_BY_BATTLE_RESULTS
from gui import makeHtmlString, SystemMessages, GUI_SETTINGS
from gui.server_events import g_eventsCache, events_dispatcher as quests_events
from gui.shared import g_itemsCache
from gui.shared.utils import isVehicleObserver, copyToClipboard, functions, findFirst
from items import vehicles as vehicles_core, vehicles
from items.vehicles import VEHICLE_CLASS_TAGS
from gui.clubs import events_dispatcher as club_events
from gui.clubs.club_helpers import ClubListener
from gui.clubs.settings import getLeagueByDivision, getDivisionWithinLeague
from gui.shared.ClanCache import g_clanCache
from gui.shared.fortifications.FortBuilding import FortBuilding
from gui.shared.gui_items.dossier import getAchievementFactory
from gui.shared.gui_items.Vehicle import VEHICLE_BATTLE_TYPES_ORDER_INDICES, getShortUserName
from gui.shared.gui_items.dossier.achievements.MarkOnGunAchievement import MarkOnGunAchievement
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.BattleResultsMeta import BattleResultsMeta
from messenger.storage import storage_getter
from gui.Scaleform.framework import AppRef
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.shared.formatters import text_styles
from gui.battle_results import formatters as battle_res_fmts

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
ARENA_SCREEN_FILE = '../maps/icons/map/stats/{0}.png'
ARENA_NAME_PATTERN = '{0} - {1}'
LINE_BRAKE_STR = '<br/>'
STATS_KEYS = (('shots', True, None),
 ('hits', False, None),
 ('explosionHits', True, None),
 ('damageDealt', True, None),
 ('sniperDamageDealt', True, None),
 ('directHitsReceived', True, None),
 ('piercingsReceived', True, None),
 ('noDamageDirectHitsReceived', True, None),
 ('explosionHitsReceived', True, None),
 ('damageBlockedByArmor', True, None),
 ('teamHitsDamage', False, None),
 ('spotted', True, None),
 ('damagedKilled', False, None),
 ('damageAssisted', True, 'damageAssistedSelf'),
 ('capturePointsVal', False, None),
 ('mileage', False, None),
 ('flags', True, None),
 ('deaths', True, None))
TIME_STATS_KEYS = ('arenaCreateTimeOnlyStr', 'duration', 'playerKilled')
FALLOUT_ONLY_STATS = ('flags', 'deaths')
FALLOUT_EXCLUDE_ACCOUNT_STATS = ('creditsContributionIn', 'creditsToDraw', 'creditsPenalty', 'creditsContributionOut', 'xpPenalty', 'playerKilled')
FALLOUT_EXCLUDE_VEHICLE_STATS = ('sniperDamageDealt', 'tkills', 'tdamageDealt', 'capturePoints', 'droppedCapturePoints', 'capturePointsVal', 'teamHitsDamage')

def _intSum(a, b):
    return a + b


def _listSum(a, b):
    return map(operator.add, a, b)


def _listCollect(a, b):
    return tuple(a) + tuple(b)


CUMULATIVE_ACCOUNT_DATA = {'credits': (0, _intSum),
 'achievementCredits': (0, _intSum),
 'creditsContributionIn': (0, _intSum),
 'creditsToDraw': (0, _intSum),
 'creditsPenalty': (0, _intSum),
 'creditsContributionOut': (0, _intSum),
 'originalCredits': (0, _intSum),
 'eventCredits': (0, _intSum),
 'eventGold': (0, _intSum),
 'orderCredits': (0, _intSum),
 'boosterCredits': (0, _intSum),
 'autoRepairCost': (0, _intSum),
 'autoLoadCost': ((0, 0), _listSum),
 'autoEquipCost': ((0, 0), _listSum),
 'histAmmoCost': ((0, 0), _listSum),
 'xp': (0, _intSum),
 'freeXP': (0, _intSum),
 'achievementXP': (0, _intSum),
 'achievementFreeXP': (0, _intSum),
 'xpPenalty': (0, _intSum),
 'originalXP': (0, _intSum),
 'originalFreeXP': (0, _intSum),
 'dossierPopUps': ((), _listCollect),
 'orderXP': (0, _intSum),
 'boosterXP': (0, _intSum),
 'orderFreeXP': (0, _intSum),
 'boosterFreeXP': (0, _intSum),
 'eventXP': (0, _intSum),
 'eventFreeXP': (0, _intSum),
 'premiumVehicleXP': (0, _intSum)}
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
 'damageAssistedTrack': (0, _intSum),
 'damageAssistedRadio': (0, _intSum),
 'spotted': (0, _intSum)}

class BattleResultsWindow(View, AbstractWindowView, BattleResultsMeta, AppRef, ClubListener):
    RESEARCH_UNLOCK_TYPE = 'UNLOCK_LINK_TYPE'
    PURCHASE_UNLOCK_TYPE = 'PURCHASE_LINK_TYPE'
    NEW_SKILL_UNLOCK_TYPE = 'NEW_SKILL_LINK_TYPE'
    __playersNameCache = dict()
    __rated7x7Animations = set()

    def __init__(self, ctx = None):
        super(BattleResultsWindow, self).__init__()
        raise 'dataProvider' in ctx or AssertionError
        raise ctx['dataProvider'] is not None or AssertionError
        self.dataProvider = ctx['dataProvider']
        return

    @storage_getter('users')
    def usersStorage(self):
        return None

    @process
    def _populate(self):
        super(BattleResultsWindow, self)._populate()
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
        super(BattleResultsWindow, self)._dispose()

    def onWindowClose(self):
        import MusicController
        MusicController.g_musicController.setAccountAttrs(g_itemsCache.items.stats.attributes, True)
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        self.destroy()

    def getDenunciations(self):
        return g_itemsCache.items.stats.denunciationsLeft

    def showEventsWindow(self, eID, eventType):
        return quests_events.showEventsWindow(eID, eventType)

    def saveSorting(self, iconType, sortDirection, bonusType):
        AccountSettings.setSettings('statsSorting' if bonusType != ARENA_BONUS_TYPE.SORTIE else 'statsSortingSortie', {'iconType': iconType,
         'sortDirection': sortDirection})

    def __getPlayerName(self, playerDBID):
        playerNameRes = self.__playersNameCache.get(playerDBID)
        if playerNameRes is None:
            player = self.dataProvider.getPlayerData(playerDBID)
            playerNameRes = self.__playersNameCache[playerDBID] = (player.getFullName(), (player.name,
              player.clanAbbrev,
              player.getRegionCode(),
              player.igrType))
        return playerNameRes

    def __getVehicleData(self, vehicleCompDesc):
        vehicleName = i18n.makeString(UNKNOWN_VEHICLE_NAME_VALUE)
        vehicleShortName = i18n.makeString(UNKNOWN_VEHICLE_NAME_VALUE)
        vehicleIcon = VEHICLE_ICON_FILE.format(VEHICLE_NO_IMAGE_FILE_NAME)
        vehicleIconSmall = VEHICLE_ICON_SMALL_FILE.format(VEHICLE_NO_IMAGE_FILE_NAME)
        vehicleBalanceWeight = 0
        nation = -1
        if vehicleCompDesc:
            vt = vehicles_core.getVehicleType(vehicleCompDesc)
            vehicleName = vt.userString
            vehicleShortName = getShortUserName(vt)
            nameReplaced = vt.name.replace(':', '-')
            vehicleIcon = VEHICLE_ICON_FILE.format(nameReplaced)
            vehicleIconSmall = VEHICLE_ICON_SMALL_FILE.format(nameReplaced)
            _, nation, nId = vehicles_core.parseIntCompactDescr(vehicleCompDesc)
            vDescr = vehicles_core.VehicleDescr(typeID=(nation, nId))
            vehicleBalanceWeight = vDescr.balanceWeight
        return (vehicleName,
         vehicleShortName,
         vehicleIcon,
         vehicleIconSmall,
         vehicleBalanceWeight,
         nation)

    def __vehiclesComparator(self, item, other):
        res = 0
        iKiller = item.get('killerID', 0)
        cd = item.get('typeCompDescr')
        if cd is not None:
            iType = vehicles_core.getVehicleType(cd)
            iLevel = iType.level if iType else -1
            iWeight = VEHICLE_BATTLE_TYPES_ORDER_INDICES.get(set(VEHICLE_CLASS_TAGS.intersection(iType.tags)).pop(), 10) if iType else 10
        else:
            iLevel = -1
            iWeight = 10
        oKiller = other.get('killerID', 0)
        cd = other.get('typeCompDescr')
        if cd is not None:
            oType = vehicles_core.getVehicleType(other.get('typeCompDescr', None))
            oLevel = oType.level if oType else -1
            oWeight = VEHICLE_BATTLE_TYPES_ORDER_INDICES.get(set(VEHICLE_CLASS_TAGS.intersection(oType.tags)).pop(), 10) if oType else 10
        else:
            oLevel = -1
            oWeight = 10
        if iKiller == 0 and oKiller == 0 or iKiller != 0 and oKiller != 0:
            res = cmp(oLevel, iLevel) or cmp(iWeight, oWeight) or cmp(item.get('vehicleName', ''), other.get('vehicleName', ''))
        elif not iKiller:
            res = -1
        else:
            res = 1
        return res

    def __getStatsLine(self, label = None, col1 = None, col2 = None, col3 = None, col4 = None):
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

    def __makeCreditsLabel(self, value, canBeFaded = False):
        valStr = BigWorld.wg_getGoldFormat(int(value))
        if value < 0:
            valStr = self.__makeRedLabel(valStr)
        templateName = 'credits_small_inactive_label' if canBeFaded and value == 0 else 'credits_small_label'
        return makeHtmlString('html_templates:lobby/battle_results', templateName, {'value': valStr})

    def __makeXpLabel(self, value, canBeFaded = False):
        valStr = BigWorld.wg_getIntegralFormat(int(value))
        if value < 0:
            valStr = self.__makeRedLabel(valStr)
        templateName = 'xp_small_inactive_label' if canBeFaded and value == 0 else 'xp_small_label'
        return makeHtmlString('html_templates:lobby/battle_results', templateName, {'value': valStr})

    def __makeResourceLabel(self, value, canBeFaded = False):
        valStr = BigWorld.wg_getIntegralFormat(int(value))
        if value < 0:
            valStr = self.__makeRedLabel(valStr)
        templateName = 'resource_small_inactive_label' if canBeFaded and value == 0 else 'resource_small_label'
        return makeHtmlString('html_templates:lobby/battle_results', templateName, {'value': valStr})

    def __makeFreeXpLabel(self, value, canBeFaded = False):
        valStr = BigWorld.wg_getIntegralFormat(int(value))
        templateName = 'free_xp_small_inactive_label' if canBeFaded and value == 0 else 'free_xp_small_label'
        return makeHtmlString('html_templates:lobby/battle_results', templateName, {'value': valStr})

    def __makeGoldLabel(self, value, canBeFaded = False):
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

    def __populateStatValues(self, node, isFallout, isSelf = False):
        node = node.copy()
        if not isFallout:
            node['teamHitsDamage'] = self.__makeTeamDamageStr(node)
            node['capturePointsVal'] = self.__makeSlashedValuesStr(node, 'capturePoints', 'droppedCapturePoints')
        node['hits'] = self.__makeSlashedValuesStr(node, 'directHits', 'piercings')
        node['damagedKilled'] = self.__makeSlashedValuesStr(node, 'damaged', 'kills')
        node['mileage'] = self.__makeMileageStr(node.get('mileage', 0))
        flagActions = node.get('flagActions', [0] * len(FLAG_ACTION.RANGE))
        node['flags'] = flagActions[FLAG_ACTION.CAPTURED]
        node['deaths'] = node.get('deathCount', 0)
        node['victoryScore'] = node.get('winPoints', 0)
        result = []
        for key, isInt, selfKey in STATS_KEYS:
            if not isFallout and key in FALLOUT_ONLY_STATS:
                continue
            if isFallout and key in FALLOUT_EXCLUDE_VEHICLE_STATS:
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

    def __populateAccounting(self, commonData, personalCommonData, personalData, playersData, personalDataOutput):
        isPremium = personalCommonData.get('isPremium', False)
        isFallout = commonData.get('guiType', 0) == ARENA_GUI_TYPE.EVENT_BATTLES
        premCreditsFactor = personalCommonData.get('premiumCreditsFactor10', 10) / 10.0
        personalDataOutput['xpTitleStr'] = i18n.makeString(XP_TITLE)
        personalDataOutput['isPremium'] = isPremium
        dailyXpFactor = personalCommonData.get('dailyXPFactor10', 10) / 10.0
        igrXpFactor = personalCommonData.get('igrXPFactor10', 10) / 10.0
        premXpFactor = personalCommonData.get('premiumXPFactor10', 10) / 10.0
        aogasFactor = personalCommonData.get('aogasFactor10', 10) / 10.0
        refSystemFactor = personalCommonData.get('refSystemXPFactor10', 10) / 10.0
        aogasValStr = ''
        if dailyXpFactor > 1:
            personalDataOutput['xpTitleStr'] += i18n.makeString(XP_TITLE_DAILY, dailyXpFactor)
        showIntermediateTotal = False
        fairPlayViolationName = self.__getFairPlayViolationName(personalCommonData)
        playerData = playersData.get(personalCommonData.get('accountDBID', 0), {'igrType': 0,
         'clanDBID': 0,
         'clanAbbrev': ''})
        personalDataOutput['isLegionnaire'] = False if playerData.get('clanDBID') else True
        igrType = playerData.get('igrType', 0)
        vehsCreditsData = []
        vehsXPData = []
        for vehIntCD, sourceData in self.__buildPersonalDataSource(personalData, commonData):
            creditsData = []
            creditsToDraw = self.__calculateBaseParam('creditsToDraw', sourceData, premCreditsFactor, isPremium)
            achievementCredits = sourceData['achievementCredits']
            creditsPenalty = self.__calculateBaseCreditsPenalty(personalCommonData, isPremium)
            creditsCompensation = self.__calculateBaseParam('creditsContributionIn', sourceData, premCreditsFactor, isPremium)
            isNoPenalty = achievementCredits > 0
            creditsBase = sourceData['originalCredits']
            creditsCell = creditsBase - achievementCredits + creditsPenalty - creditsCompensation - creditsToDraw
            creditsCellPrem = int(creditsBase * premCreditsFactor) - int(achievementCredits * premCreditsFactor) + int(creditsPenalty * premCreditsFactor) - int(round(creditsToDraw * premCreditsFactor)) - int(round(creditsCompensation * premCreditsFactor))
            creditsCellStr = self.__makeCreditsLabel(creditsCell, not isPremium)
            creditsCellPremStr = self.__makeCreditsLabel(creditsCellPrem, isPremium)
            creditsData.append(self.__getStatsLine(self.__resultLabel('base'), creditsCellStr, None, creditsCellPremStr, None))
            achievementCreditsPrem = 0
            if isNoPenalty:
                showIntermediateTotal = True
                achievementCreditsPrem = int(achievementCredits * premCreditsFactor)
                creditsData.append(self.__getStatsLine(self.__resultLabel('noPenalty'), self.__makeCreditsLabel(achievementCredits, not isPremium), None, self.__makeCreditsLabel(achievementCreditsPrem, isPremium), None))
            boosterCredits = self.__calculateBaseParam('boosterCredits', sourceData, premCreditsFactor, isPremium)
            boosterCreditsPrem = int(round(boosterCredits * premCreditsFactor))
            if boosterCredits > 0 or boosterCreditsPrem > 0:
                showIntermediateTotal = True
                boosterCreditsStr = self.__makeCreditsLabel(boosterCredits, not isPremium) if boosterCredits else None
                boosterCreditsPremStr = self.__makeCreditsLabel(boosterCreditsPrem, isPremium) if boosterCreditsPrem else None
                creditsData.append(self.__getStatsLine(self.__resultLabel('boosters'), boosterCreditsStr, None, boosterCreditsPremStr, None))
            orderCredits = self.__calculateBaseParam('orderCredits', sourceData, premCreditsFactor, isPremium)
            orderCreditsPrem = int(round(orderCredits * premCreditsFactor))
            if orderCredits > 0 or orderCreditsPrem > 0:
                showIntermediateTotal = True
                orderCreditsStr = self.__makeCreditsLabel(orderCredits, not isPremium) if orderCredits else None
                orderCreditsPremStr = self.__makeCreditsLabel(orderCreditsPrem, isPremium) if orderCreditsPrem else None
                creditsData.append(self.__getStatsLine(self.__resultLabel('battlePayments'), orderCreditsStr, None, orderCreditsPremStr, None))
            eventCredits = sourceData['eventCredits']
            eventGold = sourceData['eventGold']
            creditsEventStr = self.__makeCreditsLabel(eventCredits, not isPremium) if eventCredits else None
            creditsEventPremStr = self.__makeCreditsLabel(eventCredits, isPremium) if eventCredits else None
            goldEventStr = self.__makeGoldLabel(eventGold, not isPremium) if eventGold else None
            goldEventPremStr = self.__makeGoldLabel(eventGold, isPremium) if eventGold else None
            if eventCredits > 0 or eventGold > 0:
                showIntermediateTotal = True
                creditsData.append(self.__getStatsLine(self.__resultLabel('event'), creditsEventStr, goldEventStr, creditsEventPremStr, goldEventPremStr))
            creditsData.append(self.__getStatsLine())
            hasViolation = fairPlayViolationName is not None
            if hasViolation:
                penaltyValue = self.__makePercentLabel(int(-100))
                creditsData.append(self.__getStatsLine(self.__resultLabel('fairPlayViolation/' + fairPlayViolationName), penaltyValue, None, penaltyValue, None))
            if not isFallout:
                creditsPenaltyStr = self.__makeCreditsLabel(int(-creditsPenalty), not isPremium)
                creditsPenaltyPremStr = self.__makeCreditsLabel(int(-creditsPenalty * premCreditsFactor), isPremium)
                creditsData.append(self.__getStatsLine(self.__resultLabel('friendlyFirePenalty'), creditsPenaltyStr, None, creditsPenaltyPremStr, None))
                creditsCompensationStr = self.__makeCreditsLabel(int(round(creditsCompensation)), not isPremium)
                creditsCompensationPremStr = self.__makeCreditsLabel(int(round(creditsCompensation * premCreditsFactor)), isPremium)
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
            creditsWithoutPremTotal = self.__calculateTotalCredits(sourceData, eventCredits, premCreditsFactor, isPremium, aogasFactor, creditsBase, orderCredits, boosterCredits, creditsToDraw, hasViolation, False)
            creditsWithPremTotal = self.__calculateTotalCredits(sourceData, eventCredits, premCreditsFactor, isPremium, aogasFactor, creditsBase, orderCredits, boosterCredits, creditsToDraw, hasViolation, True)
            if showIntermediateTotal:
                creditsData.append(self.__getStatsLine(self.__resultLabel('intermediateTotal'), self.__makeCreditsLabel(creditsWithoutPremTotal), goldEventStr, self.__makeCreditsLabel(creditsWithPremTotal), goldEventPremStr))
                creditsData.append(self.__getStatsLine())
            creditsAutoRepair = sourceData['autoRepairCost']
            if creditsAutoRepair is None:
                creditsAutoRepair = 0
            creditsAutoRepairStr = self.__makeCreditsLabel(-creditsAutoRepair, not isPremium)
            creditsAutoRepairPremStr = self.__makeCreditsLabel(-creditsAutoRepair, isPremium)
            creditsData.append(self.__getStatsLine(self.__resultLabel('autoRepair'), creditsAutoRepairStr, None, creditsAutoRepairPremStr, None))
            autoLoadCost = sourceData['autoLoadCost']
            if autoLoadCost is None:
                autoLoadCost = (0, 0)
            creditsAutoLoad, goldAutoLoad = autoLoadCost
            creditsAutoLoadStr = self.__makeCreditsLabel(-creditsAutoLoad, not isPremium)
            creditsAutoLoadPremStr = self.__makeCreditsLabel(-creditsAutoLoad, isPremium)
            goldAutoLoadStr = self.__makeGoldLabel(-goldAutoLoad, not isPremium) if goldAutoLoad else None
            goldAutoLoadPremStr = self.__makeGoldLabel(-goldAutoLoad, isPremium) if goldAutoLoad else None
            creditsData.append(self.__getStatsLine(self.__resultLabel('autoLoad'), creditsAutoLoadStr, goldAutoLoadStr, creditsAutoLoadPremStr, goldAutoLoadPremStr))
            autoEquipCost = sourceData['autoEquipCost']
            if autoEquipCost is None:
                autoEquipCost = (0, 0)
            creditsAutoEquip, goldAutoEquip = autoEquipCost
            creditsAutoEquipStr = self.__makeCreditsLabel(-creditsAutoEquip, not isPremium)
            creditsAutoEquipPremStr = self.__makeCreditsLabel(-creditsAutoEquip, isPremium)
            goldAutoEquipStr = self.__makeGoldLabel(-goldAutoEquip, not isPremium)
            goldAutoEquipPremStr = self.__makeGoldLabel(-goldAutoEquip, isPremium)
            creditsData.append(self.__getStatsLine(self.__resultLabel('autoEquip'), creditsAutoEquipStr, goldAutoEquipStr, creditsAutoEquipPremStr, goldAutoEquipPremStr))
            creditsData.append(self.__getStatsLine())
            creditsWithoutPremTotalStr = self.__makeCreditsLabel(creditsWithoutPremTotal - creditsAutoRepair - creditsAutoEquip - creditsAutoLoad, not isPremium)
            creditsWithPremTotalStr = self.__makeCreditsLabel(creditsWithPremTotal - creditsAutoRepair - creditsAutoEquip - creditsAutoLoad, isPremium)
            if vehIntCD is not None:
                _, personalDataRecord = findFirst(lambda (vId, d): vId == vehIntCD, personalData, (None, None))
                if personalDataRecord is not None:
                    personalDataRecord['pureCreditsReceived'] = (creditsWithPremTotal if isPremium else creditsWithoutPremTotal) - creditsAutoRepair - creditsAutoEquip - creditsAutoLoad
            goldTotalStr = self.__makeGoldLabel(eventGold - goldAutoEquip - goldAutoLoad, not isPremium)
            goldTotalPremStr = self.__makeGoldLabel(eventGold - goldAutoEquip - goldAutoLoad, isPremium)
            totalLbl = makeHtmlString('html_templates:lobby/battle_results', 'lightText', {'value': self.__resultLabel('total')})
            creditsData.append(self.__getStatsLine(totalLbl, creditsWithoutPremTotalStr, goldTotalStr, creditsWithPremTotalStr, goldTotalPremStr))
            vehsCreditsData.append(creditsData)
            xpData = []
            achievementXP = int(sourceData['achievementXP'])
            achievementFreeXP = sourceData['achievementFreeXP']
            xpPenalty = int(self.__calculateBaseXpPenalty(sourceData, aogasFactor, dailyXpFactor, premXpFactor, igrXpFactor, isPremium))
            xpBase = int(sourceData['originalXP'])
            xpCell = xpBase - achievementXP + xpPenalty
            xpCellPrem = int((xpBase - achievementXP + xpPenalty) * premXpFactor)
            xpCellStr = self.__makeXpLabel(xpCell, not isPremium)
            xpCellPremStr = self.__makeXpLabel(xpCellPrem, isPremium)
            freeXpBase = sourceData['originalFreeXP']
            freeXpBaseStr = self.__makeFreeXpLabel(freeXpBase - achievementFreeXP, not isPremium)
            freeXpBasePremStr = self.__makeFreeXpLabel(int((freeXpBase - achievementFreeXP) * premXpFactor), isPremium)
            if 'xpStr' not in personalDataOutput and 'creditsStr' not in personalDataOutput:
                if fairPlayViolationName is not None:
                    personalDataOutput['xpStr'] = 0
                    personalDataOutput['creditsStr'] = 0
                else:
                    personalDataOutput['xpStr'] = BigWorld.wg_getIntegralFormat((xpCellPrem if isPremium else xpCell) * igrXpFactor * dailyXpFactor)
                    personalDataOutput['creditsStr'] = BigWorld.wg_getIntegralFormat(creditsCellPrem if isPremium else creditsCell)
            medals = sourceData['dossierPopUps']
            if RECORD_DB_IDS[('max15x15', 'maxXP')] in map(lambda (id, value): id, medals):
                label = makeHtmlString('html_templates:lobby/battle_results', 'xpRecord', {})
            else:
                label = self.__resultLabel('base')
            xpData.append(self.__getStatsLine(label, xpCellStr, freeXpBaseStr, xpCellPremStr, freeXpBasePremStr))
            if isNoPenalty:
                xpData.append(self.__getStatsLine(self.__resultLabel('noPenalty'), self.__makeXpLabel(achievementXP, not isPremium), self.__makeFreeXpLabel(achievementFreeXP, not isPremium), self.__makeXpLabel(int(achievementXP * premXpFactor), isPremium), self.__makeFreeXpLabel(int(achievementFreeXP * premXpFactor), isPremium)))
            if fairPlayViolationName is not None:
                penaltyXPVal = self.__makePercentLabel(int(-100))
                xpData.append(self.__getStatsLine(self.__resultLabel('fairPlayViolation/' + fairPlayViolationName), penaltyXPVal, penaltyXPVal, penaltyXPVal, penaltyXPVal))
            if not isFallout:
                xpPenaltyStr = self.__makeXpLabel(-xpPenalty, not isPremium)
                xpPenaltyPremStr = self.__makeXpLabel(int(-xpPenalty * premXpFactor), isPremium)
                xpData.append(self.__getStatsLine(self.__resultLabel('friendlyFirePenalty'), xpPenaltyStr, None, xpPenaltyPremStr, None))
            if igrXpFactor > 1:
                icon = makeHtmlString('html_templates:igr/iconSmall', 'premium' if igrType == IGR_TYPE.PREMIUM else 'basic')
                igrBonusLabelStr = i18n.makeString(BATTLE_RESULTS.DETAILS_CALCULATIONS_IGRBONUS, igrIcon=icon)
                igrBonusStr = makeHtmlString('html_templates:lobby/battle_results', 'igr_bonus', {'value': BigWorld.wg_getNiceNumberFormat(igrXpFactor)})
                xpData.append(self.__getStatsLine(igrBonusLabelStr, igrBonusStr, igrBonusStr, igrBonusStr, igrBonusStr))
            if dailyXpFactor > 1:
                dailyXpStr = makeHtmlString('html_templates:lobby/battle_results', 'multy_xp_small_label', {'value': int(dailyXpFactor)})
                xpData.append(self.__getStatsLine(self.__resultLabel('firstWin'), dailyXpStr, dailyXpStr, dailyXpStr, dailyXpStr))
            boosterXP = self.__calculateBaseParam('boosterXP', sourceData, premXpFactor, isPremium)
            boosterXPPrem = self.__calculateParamWithPrem('boosterXP', sourceData, premXpFactor, isPremium)
            boosterFreeXP = self.__calculateBaseParam('boosterFreeXP', sourceData, premXpFactor, isPremium)
            boosterFreeXPPrem = self.__calculateParamWithPrem('boosterFreeXP', sourceData, premXpFactor, isPremium)
            if boosterXP > 0 or boosterFreeXP > 0:
                boosterXPStr = self.__makeXpLabel(boosterXP, not isPremium) if boosterXP else None
                boosterXPPremStr = self.__makeXpLabel(boosterXPPrem, isPremium) if boosterXPPrem else None
                boosterFreeXPStr = self.__makeFreeXpLabel(boosterFreeXP, not isPremium) if boosterFreeXP else None
                boosterFreeXPPremStr = self.__makeFreeXpLabel(boosterFreeXPPrem, isPremium) if boosterFreeXPPrem else None
                xpData.append(self.__getStatsLine(self.__resultLabel('boosters'), boosterXPStr, boosterFreeXPStr, boosterXPPremStr, boosterFreeXPPremStr))
            orderXP = self.__calculateBaseParam('orderXP', sourceData, premXpFactor, isPremium)
            orderXPPrem = self.__calculateParamWithPrem('orderXP', sourceData, premXpFactor, isPremium)
            if orderXP > 0:
                orderXPStr = self.__makeXpLabel(orderXP, not isPremium) if orderXP else None
                orderXPPremStr = self.__makeXpLabel(orderXPPrem, isPremium) if orderXPPrem else None
                xpData.append(self.__getStatsLine(self.__resultLabel('tacticalTraining'), orderXPStr, None, orderXPPremStr, None))
            orderFreeXP = self.__calculateBaseParam('orderFreeXP', sourceData, premXpFactor, isPremium)
            orderFreeXPPrem = self.__calculateParamWithPrem('orderFreeXP', sourceData, premXpFactor, isPremium)
            if orderFreeXP > 0:
                orderFreeXPStr = self.__makeFreeXpLabel(orderFreeXP, not isPremium) if orderFreeXP else None
                orderFreeXPPremStr = self.__makeFreeXpLabel(orderFreeXPPrem, isPremium) if orderFreeXPPrem else None
                xpData.append(self.__getStatsLine(self.__resultLabel('militaryManeuvers'), None, orderFreeXPStr, None, orderFreeXPPremStr))
            eventXP = sourceData['eventXP']
            eventFreeXP = sourceData['eventFreeXP']
            if eventXP > 0 or eventFreeXP > 0:
                eventXPStr = self.__makeXpLabel(eventXP, not isPremium)
                eventXPPremStr = self.__makeXpLabel(eventXP, isPremium)
                eventFreeXPStr = self.__makeFreeXpLabel(eventFreeXP, not isPremium)
                eventFreeXPPremStr = self.__makeFreeXpLabel(eventFreeXP, isPremium)
                xpData.append(self.__getStatsLine(self.__resultLabel('event'), eventXPStr, eventFreeXPStr, eventXPPremStr, eventFreeXPPremStr))
            if refSystemFactor > 1:
                refSysXpValue = xpBase * igrXpFactor * refSystemFactor
                refSysFreeXpValue = freeXpBase * refSystemFactor
                refSysXPStr = self.__makeXpLabel(refSysXpValue, not isPremium)
                refSysFreeXPStr = self.__makeFreeXpLabel(refSysFreeXpValue, not isPremium)
                refSysXPPremStr = self.__makeXpLabel(refSysXpValue * premXpFactor, isPremium)
                refSysFreeXPPremStr = self.__makeFreeXpLabel(refSysFreeXpValue * premXpFactor, isPremium)
                xpData.append(self.__getStatsLine(self.__resultLabel('referralBonus'), refSysXPStr, refSysFreeXPStr, refSysXPPremStr, refSysFreeXPPremStr))
            premiumVehicleXP = sourceData['premiumVehicleXP']
            if premiumVehicleXP > 0:
                xpData.append(self.__getPremiumVehicleXP(premiumVehicleXP, isPremium, premXpFactor))
            if aogasFactor < 1:
                xpData.append(self.__getStatsLine(self.__resultLabel('aogasFactor'), aogasValStr, aogasValStr, aogasValStr, aogasValStr))
            if len(xpData) < 3:
                xpData.append(self.__getStatsLine())
            if len(xpData) < 7:
                xpData.append(self.__getStatsLine())
            xpTotal = self.__makeXpLabel(self.__calculateTotalXp(sourceData, aogasFactor, dailyXpFactor, premXpFactor, igrXpFactor, refSystemFactor, isPremium, xpBase, orderXP, boosterXP, eventXP, hasViolation), not isPremium)
            xpPremTotal = self.__makeXpLabel(self.__calculateTotalXp(sourceData, aogasFactor, dailyXpFactor, premXpFactor, igrXpFactor, refSystemFactor, isPremium, xpBase, orderXP, boosterXP, eventXP, hasViolation, True), isPremium)
            freeXpTotal = self.__makeFreeXpLabel(self.__calculateTotalFreeXp(sourceData, aogasFactor, dailyXpFactor, premXpFactor, igrXpFactor, refSystemFactor, isPremium, freeXpBase, orderFreeXP, boosterFreeXP, eventFreeXP, hasViolation), not isPremium)
            freeXpPremTotal = self.__makeFreeXpLabel(self.__calculateTotalFreeXp(sourceData, aogasFactor, dailyXpFactor, premXpFactor, igrXpFactor, refSystemFactor, isPremium, freeXpBase, orderFreeXP, boosterFreeXP, eventFreeXP, hasViolation, True), isPremium)
            xpData.append(self.__getStatsLine(totalLbl, xpTotal, freeXpTotal, xpPremTotal, freeXpPremTotal))
            vehsXPData.append(xpData)

        personalDataOutput['creditsData'] = vehsCreditsData
        personalDataOutput['xpData'] = vehsXPData
        if commonData.get('bonusType', 0) == ARENA_BONUS_TYPE.SORTIE:
            resValue = personalCommonData.get('fortResource', 0) if playerData.get('clanDBID') else 0
            resValue = 0 if resValue is None else resValue
            orderFortResource = personalCommonData.get('orderFortResource', 0) if playerData.get('clanDBID') else 0
            baseResValue = resValue - orderFortResource
            personalDataOutput['fortResourceTotal'] = baseResValue
            personalDataOutput['resStr'] = self.__makeResourceLabel(baseResValue, not isPremium) if playerData.get('clanDBID') else '-'
            personalDataOutput['resPremStr'] = self.__makeResourceLabel(baseResValue, isPremium) if playerData.get('clanDBID') else '-'
            resData = []
            resData.append(self.__getStatsLine(self.__resultLabel('base'), None, self.__makeResourceLabel(baseResValue, not isPremium), None, self.__makeResourceLabel(baseResValue, isPremium)))
            if orderFortResource:
                resData.append(self.__getStatsLine(self.__resultLabel('heavyTrucks'), None, self.__makeResourceLabel(orderFortResource, not isPremium), None, self.__makeResourceLabel(orderFortResource, isPremium)))
            if len(resData) > 1:
                resData.append(self.__getStatsLine())
            resData.append(self.__getStatsLine(self.__resultLabel('total'), None, self.__makeResourceLabel(resValue, not isPremium), None, self.__makeResourceLabel(resValue, isPremium)))
            personalDataOutput['resourceData'] = resData
        return

    def __buildPersonalDataSource(self, personalData, commonData):
        totalData = {}
        personaDataSource = [(None, totalData)]
        isFallout = commonData.get('guiType', 0) == ARENA_GUI_TYPE.EVENT_BATTLES
        for vehIntCD, pData in personalData:
            data = {}
            for k, (d, func) in CUMULATIVE_ACCOUNT_DATA.iteritems():
                if isFallout and k in FALLOUT_EXCLUDE_ACCOUNT_STATS:
                    continue
                v = pData.get(k, d)
                data[k] = v
                totalData.setdefault(k, d)
                totalData[k] = func(totalData[k], v)

            personaDataSource.append((vehIntCD, data))

        return personaDataSource

    def __buildEfficiencyDataSource(self, pData, pCommonData, playersData, commonData):
        totalEnemies = []
        totalTechniquesGroup = []
        totalBasesGroup = []
        efficiencyDataSource = [(totalTechniquesGroup, totalEnemies, totalBasesGroup)]
        playerTeam = pCommonData.get('team')
        playerDBID = pCommonData.get('accountDBID')
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
                if (vId, vIntCD) not in totalVehsData:
                    totalVehsData[vId, vIntCD] = iInfo.copy()
                else:
                    totalVehData = totalVehsData[vId, vIntCD]
                    for k, v in iInfo.iteritems():
                        if k == 'deathReason':
                            currentValue = totalVehData[k]
                            if v > currentValue:
                                totalVehData[k] = v
                        else:
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

    @classmethod
    def _packAchievement(cls, achieve, isUnique = False):
        rank, i18nValue = (None, None)
        if achieve.getType() != ACHIEVEMENT_TYPE.SERIES:
            rank, i18nValue = achieve.getValue(), achieve.getI18nValue()
        icons = achieve.getIcons()
        specialIcon = icons.get(MarkOnGunAchievement.IT_95X85, None)
        customData = []
        recordName = achieve.getRecordName()
        if recordName == MARK_ON_GUN_RECORD:
            customData.extend([achieve.getDamageRating(), achieve.getVehicleNationID()])
        if recordName == MARK_OF_MASTERY_RECORD:
            customData.extend([achieve.getPrevMarkOfMastery(), achieve.getCompDescr()])
        return {'type': recordName[1],
         'block': achieve.getBlock(),
         'inactive': False,
         'icon': achieve.getSmallIcon() if specialIcon is None else '',
         'rank': rank,
         'localizedValue': i18nValue,
         'unic': isUnique,
         'rare': False,
         'title': achieve.getUserName(),
         'description': achieve.getUserDescription(),
         'rareIconId': None,
         'isEpic': achieve.hasRibbon(),
         'specialIcon': specialIcon,
         'customData': customData}

    def __populatePersonalMedals(self, pData, personalDataOutput):
        personalDataOutput['dossierType'] = None
        personalDataOutput['dossierCompDescr'] = None
        personalDataOutput['achievementsLeft'] = []
        personalDataOutput['achievementsRight'] = []
        for _, data in pData:
            achievementsData = data.get('dossierPopUps', [])
            for achievementId, achieveValue in achievementsData:
                record = DB_ID_TO_RECORD[achievementId]
                if record in IGNORED_BY_BATTLE_RESULTS:
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
                        personalDataOutput['achievementsRight'].append(achieveData)
                    else:
                        personalDataOutput['achievementsLeft'].append(achieveData)

            markOfMastery = data.get('markOfMastery', 0)
            factory = getAchievementFactory(('achievements', 'markOfMastery'))
            if markOfMastery > 0 and factory is not None:
                from gui.shared import g_itemsCache
                achieve = factory.create(value=markOfMastery)
                achieve.setPrevMarkOfMastery(data.get('prevMarkOfMastery', 0))
                achieve.setCompDescr(data.get('typeCompDescr'))
                personalDataOutput['achievementsLeft'].append(self._packAchievement(achieve))
            personalDataOutput['achievementsRight'].sort(key=lambda k: k['isEpic'], reverse=True)

        return

    def __populateEfficiency(self, pData, pCommonData, playersData, commonData, personalDataOutput):
        valsStr = makeHtmlString('html_templates:lobby/battle_results', 'tooltip_params_style', {'text': i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_PARAMS_VAL)})
        details = []
        for techniquesGroup, enemiesGroup, basesGroup in self.__buildEfficiencyDataSource(pData, pCommonData, playersData, commonData):
            enemies = []
            for (vId, vIntCD), iInfo in enemiesGroup:
                result = {}
                accountDBID = self.dataProvider.getAccountDBID(vId)
                vehsData = self.dataProvider.getVehiclesData(accountDBID)
                deathReason = iInfo.get('deathReason', -1)
                if vehsData:
                    vInfo = vehsData[0]
                    deathReason = vInfo.get('deathReason', -1)
                _, result['vehicleName'], _, result['tankIcon'], result['balanceWeight'], _ = self.__getVehicleData(vIntCD)
                result['deathReason'] = deathReason
                result['spotted'] = iInfo.get('spotted', 0)
                result['piercings'] = iInfo.get('piercings', 0)
                result['damageDealt'] = iInfo.get('damageDealt', 0)
                playerNameData = self.__getPlayerName(accountDBID)
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

    @classmethod
    def __populateResultStrings(cls, commonData, pData, commonDataOutput):
        bonusType = commonData.get('bonusType', 0)
        winnerTeam = commonData.get('winnerTeam', 0)
        finishReason = commonData.get('finishReason', 0)
        if not winnerTeam:
            status = 'tie'
        elif winnerTeam == pData.get('team'):
            status = 'win'
        else:
            status = 'lose'

        def _finishReasonFormatter(formatter, **kwargs):
            if finishReason == 1:
                return i18n.makeString(formatter.format(''.join([str(finishReason), str(status)])), **kwargs)
            return i18n.makeString(formatter.format(finishReason))

        if bonusType == ARENA_BONUS_TYPE.FORT_BATTLE:
            fortBuilding = pData.get('fortBuilding', {})
            buildTypeID, buildTeam = fortBuilding.get('buildTypeID'), fortBuilding.get('buildTeam')
            if status == 'tie':
                status = 'win' if buildTeam == pData.get('team') else 'lose'
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
        if commonData.get('guiType', 0) != ARENA_GUI_TYPE.EVENT_BATTLES:
            commonDataOutput['finishReasonStr'] = _frFormatter()
        else:
            resultTemplate = '#battle_results:fallout/%s' % status
            if status != 'tie':
                finishReasonStr = 'points'
                if finishReason == FR.WIN_POINTS_CAP:
                    finishReasonStr = 'cap'
                resultTemplate += '/' + finishReasonStr
            commonDataOutput['finishReasonStr'] = i18n.makeString(resultTemplate)
        commonDataOutput['resultStr'] = RESULT_.format(status)
        return

    def __populateTankSlot(self, commonDataOutput, pData, pCommonData):
        vehsData = []
        playerNameData = self.__getPlayerName(pCommonData.get('accountDBID', None))
        commonDataOutput['playerNameStr'], commonDataOutput['clanNameStr'], commonDataOutput['regionNameStr'], _ = playerNameData[1]
        commonDataOutput['playerFullNameStr'] = playerNameData[0]
        if len(pData) > 1:
            vehsData.append({'vehicleName': i18n.makeString(BATTLE_RESULTS.ALLVEHICLES),
             'tankIcon': RES_ICONS.MAPS_ICONS_LIBRARY_FALLOUTVEHICLESALL})
        for vehTypeCompDescr, data in pData:
            curVeh = {}
            curVeh['vehicleName'], _, curVeh['tankIcon'], _, _, nation = self.__getVehicleData(vehTypeCompDescr)
            killerID = data.get('killerID', 0)
            curVeh['killerID'] = killerID
            deathReason = data.get('deathReason', -1)
            curVeh['deathReason'] = deathReason
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
                    playerNameData = self.__getPlayerName(killerPlayerId)
                    curVeh['killerFullNameStr'] = playerNameData[0]
                    curVeh['killerNameStr'], curVeh['killerClanNameStr'], curVeh['killerRegionNameStr'], _ = playerNameData[1]
                else:
                    curVeh['vehicleStateStr'] = ''
                    curVeh['vehicleStatePrefixStr'], curVeh['vehicleStateSuffixStr'] = ('', '')
                    curVeh['killerFullNameStr'], curVeh['killerNameStr'] = ('', '')
                    curVeh['killerClanNameStr'], curVeh['killerRegionNameStr'] = ('', '')
            else:
                curVeh['vehicleStateStr'] = BATTLE_RESULTS.COMMON_VEHICLESTATE_ALIVE
            vehsData.append(curVeh)

        commonDataOutput['playerVehicles'] = vehsData
        return

    def __populateArenaData(self, commonData, pData, commonDataOutput):
        isFallout = commonData.get('guiType', 0) == ARENA_GUI_TYPE.EVENT_BATTLES
        arenaTypeID = commonData.get('arenaTypeID', 0)
        arenaType = ArenaType.g_cache[arenaTypeID]
        commonDataOutput['arenaStr'] = BATTLE_RESULTS.COMMON_PROGRESSTITLE
        createTime = commonData.get('arenaCreateTime')
        createTime = time_utils.makeLocalServerTime(createTime)
        commonDataOutput['arenaCreateTimeStr'] = BigWorld.wg_getShortDateFormat(createTime) + ' ' + BigWorld.wg_getShortTimeFormat(createTime)
        commonDataOutput['arenaCreateTimeOnlyStr'] = BigWorld.wg_getShortTimeFormat(createTime)
        arenaIcon = arenaType.geometryName
        if isFallout and arenaType.gameplayName in ('fallout', 'fallout2'):
            arenaIcon += '_fallout'
        commonDataOutput['arenaIcon'] = ARENA_SCREEN_FILE.format(arenaIcon)
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
            if isFallout and key in FALLOUT_EXCLUDE_ACCOUNT_STATS:
                continue
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

    def __populateTeamsData(self, pCommonData, playersData, commonData, commonDataOutput):
        squads = {1: {},
         2: {}}
        stat = {1: [],
         2: []}
        lastSquadId = 0
        squadManCount = 0
        playerSquadId = 0
        playerDBID = pCommonData.get('accountDBID')
        playerTeam = pCommonData.get('team')
        enemyTeam = playerTeam % 2 + 1
        bonusType = commonData.get('bonusType', 0)
        winnerTeam = commonData.get('winnerTeam', 0)
        playerNamePosition = bonusType in (ARENA_BONUS_TYPE.FORT_BATTLE, ARENA_BONUS_TYPE.CYBERSPORT, ARENA_BONUS_TYPE.RATED_CYBERSPORT)
        isPlayerObserver = isVehicleObserver(pCommonData.get('typeCompDescr', 0))
        fairPlayViolationName = self.__getFairPlayViolationName(pCommonData)
        isFallout = commonData.get('guiType', 0) == ARENA_GUI_TYPE.EVENT_BATTLES
        if isFallout:
            arenaTypeID = commonData.get('arenaTypeID', None)
            arenaType = ArenaType.g_cache[arenaTypeID]
            pointsKill, pointsFlags = getCosts(arenaType)
            formatter = BigWorld.wg_getNiceNumberFormat
            scorePatterns = []
            if pointsKill > 0:
                costKillText = i18n.makeString(TOOLTIPS.BATTLERESULTS_VICTORYSCOREDESCRIPTION_COST, cost=formatter(pointsKill))
                scorePatterns.append(i18n.makeString(TOOLTIPS.BATTLERESULTS_VICTORYSCOREDESCRIPTION_KILLSPATTERN, pointsKill=costKillText))
            if pointsFlags:
                costFlagTextPatterns = []
                for c in pointsFlags:
                    costFlagTextPatterns.append(i18n.makeString(TOOLTIPS.BATTLERESULTS_VICTORYSCOREDESCRIPTION_COST, cost=formatter(c)))

                scorePatterns.append(i18n.makeString(TOOLTIPS.BATTLERESULTS_VICTORYSCOREDESCRIPTION_POINTSPATTERN, pointsFlag=', '.join(costFlagTextPatterns)))
            tooltipText = i18n.makeString(TOOLTIPS.BATTLERESULTS_VICTORYSCOREDESCRIPTION_BODY, scorePattern=';\n'.join(scorePatterns))
            commonDataOutput['victoryScore'] = [{'score': 0,
              'victory': playerTeam == winnerTeam,
              'tooltip': tooltipText}, {'score': 0,
              'victory': enemyTeam == winnerTeam,
              'tooltip': tooltipText}]

        def comparator(x, y):
            xIntCD = x.get('typeCompDescr', None)
            yIntCD = y.get('typeCompDescr', None)
            xVeh = g_itemsCache.items.getItemByCD(xIntCD)
            yVeh = g_itemsCache.items.getItemByCD(yIntCD)
            return cmp(xVeh, yVeh)

        for pId, pInfo in playersData.iteritems():
            vehsData = sorted(self.dataProvider.getVehiclesData(pId), comparator)
            vId = self.dataProvider.getVehicleID(pId)
            row = {'csNumber': '',
             'isCommander': False,
             'vehicleId': vId}
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
                xp += data.get('xp', 0)
                damageDealt += data.get('damageDealt', 0)
                statValues.append(self.__populateStatValues(data, isFallout, True))
                achievementsData += data.get('achievements', [])
                for k, (d, func) in CUMULATIVE_STATS_DATA.iteritems():
                    if isFallout and k in FALLOUT_EXCLUDE_VEHICLE_STATS:
                        continue
                    if not isFallout and k in FALLOUT_ONLY_STATS:
                        continue
                    v = data.get(k, d)
                    totalStatValues.setdefault(k, d)
                    totalStatValues[k] = func(totalStatValues[k], v)

            damageAssisted.insert(0, totalDamageAssisted)
            row['damageAssisted'] = damageAssisted
            totalStatValues['damageAssisted'] = totalDamageAssisted
            row['kills'] = kills = totalStatValues['kills']
            teamKills = 0
            if not isFallout:
                row['tkills'] = teamKills = totalStatValues['tkills']
            row['realKills'] = kills - teamKills
            row['xp'] = xp
            row['damageDealt'] = damageDealt
            statValues.insert(0, self.__populateStatValues(totalStatValues, isFallout, True))
            row['statValues'] = statValues
            vehs = []
            vInfo = vehsData[0]
            if len(vehsData) > 1:
                vehs.append({'label': i18n.makeString(BATTLE_RESULTS.ALLVEHICLES),
                 'icon': RES_ICONS.MAPS_ICONS_LIBRARY_FALLOUTVEHICLESALL})
                for vInfo in vehsData:
                    _, vehicleName, tankIcon, _, _, nation = self.__getVehicleData(vInfo.get('typeCompDescr', None))
                    vehs.append({'label': vehicleName,
                     'icon': tankIcon,
                     'flag': nations.NAMES[nation]})

            else:
                row['vehicleFullName'], row['vehicleName'], tankIcon, row['tankIcon'], _, _ = self.__getVehicleData(vInfo.get('typeCompDescr', None))
                vehs.append({'icon': tankIcon})
            row['vehicles'] = vehs
            if bonusType == ARENA_BONUS_TYPE.SORTIE:
                row['showResources'] = True
                row['resourceCount'] = vInfo.get('fortResource', 0) if pInfo.get('clanDBID') else None
                row['influencePoints'] = vInfo.get('influencePoints')
            else:
                row['showResources'] = False
            achievementsList = []
            if not (pId == playerDBID and fairPlayViolationName is not None):
                for achievementId in achievementsData:
                    factory = getAchievementFactory(DB_ID_TO_RECORD[achievementId])
                    if factory is not None:
                        achive = factory.create(value=0)
                        if not achive.isApproachable():
                            achievementsList.append(self._packAchievement(achive, isUnique=True))

                achievementsList.sort(key=lambda k: k['isEpic'], reverse=True)
            row['achievements'] = achievementsList
            row['medalsCount'] = len(achievementsList)
            isVehObserver = isVehicleObserver(vInfo.get('typeCompDescr', 0))
            if len(vehsData) == 1:
                killerID = vInfo.get('killerID', 0)
                deathReason = vInfo.get('deathReason', -1)
                isPrematureLeave = vInfo.get('isPrematureLeave', False)
                row['deathReason'] = deathReason
                if not isVehObserver:
                    if isPrematureLeave:
                        row['vehicleStateStr'] = i18n.makeString(BATTLE_RESULTS.COMMON_VEHICLESTATE_PREMATURELEAVE)
                    elif deathReason > -1:
                        row['vehicleStateStr'] = ''
                        if killerID:
                            row['vehicleStateStr'] = i18n.makeString('#battle_results:common/vehicleState/dead{0}'.format(deathReason))
                            killerPlayerId = self.dataProvider.getAccountDBID(pId)
                            row['vehicleStatePrefixStr'] = '{0} ('.format(row['vehicleStateStr'])
                            row['vehicleStateSuffixStr'] = ')'
                            playerNameData = self.__getPlayerName(killerPlayerId)
                            row['killerFullNameStr'] = playerNameData[0]
                            row['killerNameStr'], row['killerClanNameStr'], row['killerRegionNameStr'], _ = playerNameData[1]
                    else:
                        row['vehicleStateStr'] = BATTLE_RESULTS.COMMON_VEHICLESTATE_ALIVE
                else:
                    row['vehicleStateStr'] = ''
                    row['vehicleStatePrefixStr'], row['vehicleStateSuffixStr'] = ('', '')
                    row['killerFullNameStr'], row['killerNameStr'] = ('', '')
                    row['killerClanNameStr'], row['killerRegionNameStr'] = ('', '')
            row['playerId'] = pId
            row['userName'] = pInfo.get('name')
            playerNameData = self.__getPlayerName(pId)
            row['playerFullName'] = playerNameData[0]
            row['playerName'], row['playerClan'], row['playerRegion'], row['playerIgrType'] = playerNameData[1]
            row['playerNamePosition'] = playerNamePosition
            team = pInfo['team']
            if isFallout:
                flagActions = totalStatValues['flagActions']
                row['flags'] = flagActions[FLAG_ACTION.CAPTURED]
                row['deaths'] = totalStatValues['deathCount']
                playerScore = totalStatValues['winPoints']
                row['victoryScore'] = playerScore
                teamIdx = 0 if team == playerTeam else 1
                commonDataOutput['victoryScore'][teamIdx]['score'] += playerScore
            row['playerInfo'] = {}
            row['isSelf'] = playerDBID == pId
            prebattleID = pInfo.get('prebattleID', 0)
            row['prebattleID'] = prebattleID
            if playerDBID == pId:
                playerSquadId = prebattleID
            if bonusType == ARENA_BONUS_TYPE.REGULAR and prebattleID:
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

        if bonusType == ARENA_BONUS_TYPE.REGULAR and not (IS_DEVELOPMENT and squadManCount == len(playersData)):
            squadsSorted = dict()
            squadsSorted[1] = sorted(squads[1].iteritems(), cmp=lambda x, y: cmp(x[0], y[0]))
            squadsSorted[2] = sorted(squads[2].iteritems(), cmp=lambda x, y: cmp(x[0], y[0]))
            squads[1] = [ id for id, num in squadsSorted[1] if 1 < num < 4 ]
            squads[2] = [ id for id, num in squadsSorted[2] if 1 < num < 4 ]
        isInfluencePointsAvailable = True
        for team in (1, 2):
            data = sorted(stat[team], cmp=self.__vehiclesComparator)
            sortIdx = len(data)
            teamResourceTotal = teamInfluencePointsTotal = 0
            for item in data:
                item['vehicleSort'] = sortIdx
                item['xpSort'] = item.get('xp', 0) - item.get('achievementXP', 0)
                sortIdx -= 1
                if bonusType == ARENA_BONUS_TYPE.REGULAR and not (IS_DEVELOPMENT and squadManCount == len(playersData)):
                    item['isOwnSquad'] = playerSquadId == item.get('prebattleID') if playerSquadId != 0 else False
                    item['squadID'] = squads[team].index(item.get('prebattleID')) + 1 if item.get('prebattleID') in squads[team] else 0
                else:
                    item['squadID'] = 0
                    item['isOwnSquad'] = False
                if bonusType == ARENA_BONUS_TYPE.SORTIE:
                    itemResourceCount = item.get('resourceCount')
                    teamResourceTotal += itemResourceCount if itemResourceCount != None else 0
                influencePoints = item.get('influencePoints')
                if influencePoints is not None:
                    teamInfluencePointsTotal += influencePoints
                else:
                    isInfluencePointsAvailable = False

            if team == playerTeam:
                commonDataOutput['totalFortResourceStr'] = makeHtmlString('html_templates:lobby/battle_results', 'teamResourceTotal', {'resourceValue': teamResourceTotal})
                if isInfluencePointsAvailable:
                    commonDataOutput['totalInfluenceStr'] = makeHtmlString('html_templates:lobby/battle_results', 'teamInfluenceTotal', {'resourceValue': teamInfluencePointsTotal})

        return (stat[playerTeam], stat[enemyTeam])

    def __calculateBaseXpPenalty(self, pData, aogasFactor, dailyXpFactor, premXpFactor, igrXpFactor, isPremium):
        if not aogasFactor:
            return 0
        xpPenalty = pData.get('xpPenalty', 0)
        xpPenalty = math.ceil(int(xpPenalty / aogasFactor) / dailyXpFactor)
        if isPremium:
            xpPenalty = math.ceil(xpPenalty / premXpFactor)
        if igrXpFactor:
            xpPenalty = math.ceil(xpPenalty / igrXpFactor)
        return xpPenalty

    def __calculateTotalCredits(self, pData, eventCredits, premCreditsFactor, isPremium, aogasFactor, baseCredits, baseOrderCredits, baseBoosterCredits, creditsToDraw, hasViolation, usePremFactor = False):
        premFactor = premCreditsFactor if usePremFactor else 1.0
        givenCredits = pData['credits']
        credits = int(givenCredits - round(creditsToDraw * premFactor))
        if isPremium != usePremFactor:
            givenCredits = 0
            if not hasViolation:
                givenCredits = (int(baseCredits * premFactor) + round(baseOrderCredits * premFactor) + round(baseBoosterCredits * premFactor) + eventCredits) * aogasFactor
            credits = int(givenCredits - round(creditsToDraw * premFactor * aogasFactor))
        return credits

    def __calculateTotalFreeXp(self, pData, aogasFactor, dailyXpFactor, premXpFactor, igrXpFactor, refSystemFactor, isPremium, baseFreeXp, baseOrderFreeXp, baseBoosterFreeXP, eventFreeXP, hasViolation, usePremFactor = False):
        if not baseFreeXp:
            return 0
        if hasViolation:
            return 0
        freeXP = float(pData['freeXP'])
        if isPremium != usePremFactor:
            premXpFactor = premXpFactor if usePremFactor else 1.0
            subtotalXp = int(int(baseFreeXp * igrXpFactor) * premXpFactor)
            resultXp = int(subtotalXp * dailyXpFactor)
            if abs(refSystemFactor - 1.0) > 0.001:
                resultXp += int(subtotalXp * refSystemFactor)
            freeXP = int((resultXp + int(baseOrderFreeXp * premXpFactor) + int(baseBoosterFreeXP * premXpFactor) + eventFreeXP) * aogasFactor)
        return freeXP

    def __calculateTotalXp(self, pData, aogasFactor, dailyXpFactor, premXpFactor, igrXpFactor, refSystemFactor, isPremium, baseXp, baseOrderXp, baseBoosterXP, eventXP, hasViolation, usePremFactor = False):
        if hasViolation:
            return 0
        xp = pData['xp']
        if isPremium != usePremFactor:
            premFactor = premXpFactor if usePremFactor else 1.0
            if isPremium:
                premiumVehicleXP = pData['premiumVehicleXP'] / premXpFactor
            else:
                premiumVehicleXP = pData['premiumVehicleXP'] * premXpFactor
            subtotalXp = int(int(baseXp * igrXpFactor) * premFactor)
            resultXp = int(subtotalXp * dailyXpFactor)
            if abs(refSystemFactor - 1.0) > 0.001:
                resultXp += int(subtotalXp * refSystemFactor)
            xp = int((resultXp + int(baseOrderXp * premFactor) + int(baseBoosterXP * premFactor) + eventXP + premiumVehicleXP) * aogasFactor)
        return xp

    def __calculateBaseCreditsPenalty(self, pData, isPremium):
        creditsPenalty = pData.get('creditsPenalty', 0) + pData.get('creditsContributionOut', 0)
        if isPremium:
            premFactor = pData.get('premiumCreditsFactor10', 10) / 10.0
            creditsPenalty = math.ceil(creditsPenalty / premFactor)
        return creditsPenalty

    def __calculateBaseParam(self, paramKey, pData, premFactor, isPremium):
        paramValue = pData.get(paramKey, 0)
        if isPremium:
            paramValue = round(paramValue / premFactor)
        return paramValue

    def __calculateParamWithPrem(self, paramKey, pData, premFactor, isPremium):
        paramValue = pData.get(paramKey, 0)
        if not isPremium:
            paramValue = int(paramValue * premFactor)
        return paramValue

    def selectVehicle(self, inventoryId):
        g_currentVehicle.selectVehicle(inventoryId)
        return g_currentVehicle.invID == inventoryId

    @classmethod
    def __parseQuestsProgress(cls, personalData):
        questsProgress = {}
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
                elif potapov_quests.g_cache.isPotapovQuest(qID):
                    pqID = potapov_quests.g_cache.getPotapovQuestIDByUniqueID(qID)
                    quest = g_eventsCache.potapov.getQuests()[pqID]
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
            personalData = results.get('personal', {}).copy()
            personalCommonData = personalData.values()[0]

            def comparator(x, y):
                xIntCD, _ = x
                yIntCD, _ = y
                xVeh = g_itemsCache.items.getItemByCD(xIntCD)
                yVeh = g_itemsCache.items.getItemByCD(yIntCD)
                return cmp(xVeh, yVeh)

            personalData = sorted(personalData.iteritems(), comparator)
            playersData = results.get('players', {}).copy()
            commonData = results.get('common', {}).copy()
            bonusType = commonData.get('bonusType', 0)
            personalDataOutput = {}
            commonDataOutput = {}
            commonDataOutput['bonusType'] = bonusType
            if bonusType == ARENA_BONUS_TYPE.SORTIE or bonusType == ARENA_BONUS_TYPE.FORT_BATTLE:
                commonDataOutput['clans'] = self.__processClanData(personalCommonData, playersData)
            else:
                commonDataOutput['clans'] = {'allies': {'clanDBID': -1,
                            'clanAbbrev': ''},
                 'enemies': {'clanDBID': -1,
                             'clanAbbrev': ''}}
            commonDataOutput['battleResultsSharingIsAvailable'] = self._isSharingBtnEnabled()
            statsSorting = AccountSettings.getSettings('statsSorting' if bonusType != ARENA_BONUS_TYPE.SORTIE else 'statsSortingSortie')
            commonDataOutput['iconType'] = statsSorting.get('iconType')
            commonDataOutput['sortDirection'] = statsSorting.get('sortDirection')
            isFallout = commonData.get('guiType', 0) == ARENA_GUI_TYPE.EVENT_BATTLES
            self.__populateResultStrings(commonData, personalCommonData, commonDataOutput)
            self.__populatePersonalMedals(personalData, personalDataOutput)
            self.__populateArenaData(commonData, personalCommonData, commonDataOutput)
            damageAssisted = []
            totalDamageAssisted = 0
            statValues = []
            totalStatValues = defaultdict(int)
            for _, data in personalData:
                assisted = data.get('damageAssistedTrack', 0) + data.get('damageAssistedRadio', 0)
                damageAssisted.append(assisted)
                totalDamageAssisted += assisted
                statValues.append(self.__populateStatValues(data, isFallout, True))
                for k, (d, func) in CUMULATIVE_STATS_DATA.iteritems():
                    if isFallout and k in FALLOUT_EXCLUDE_VEHICLE_STATS:
                        continue
                    if not isFallout and k in FALLOUT_ONLY_STATS:
                        continue
                    v = data.get(k, d)
                    totalStatValues.setdefault(k, d)
                    totalStatValues[k] = func(totalStatValues[k], v)

            damageAssisted.insert(0, totalDamageAssisted)
            personalDataOutput['damageAssisted'] = damageAssisted
            totalStatValues['damageAssisted'] = totalDamageAssisted
            statValues.insert(0, self.__populateStatValues(totalStatValues, isFallout, True))
            personalDataOutput['statValues'] = statValues
            self.__populateAccounting(commonData, personalCommonData, personalData, playersData, personalDataOutput)
            self.__populateTankSlot(commonDataOutput, personalData, personalCommonData)
            self.__populateEfficiency(personalData, personalCommonData, playersData, commonData, personalDataOutput)
            team1, team2 = self.__populateTeamsData(personalCommonData, playersData, commonData, commonDataOutput)
            resultingVehicles = []
            dailyXpFactor = personalCommonData.get('dailyXPFactor10', 10) / 10.0
            commonDataOutput['isFalloutMode'] = isFallout
            results = {'personal': personalDataOutput,
             'common': commonDataOutput,
             'team1': team1,
             'team2': team2,
             'vehicles': resultingVehicles,
             'dailyXPFactor': dailyXpFactor,
             'quests': self.__parseQuestsProgress(personalData),
             'unlocks': self.__getVehicleProgress(self.dataProvider.getArenaUniqueID(), personalData)}
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
        try:
            results = self.dataProvider.getResults()
            arenaUniqueID = self.dataProvider.getArenaUniqueID()
            common = results['common']
            personal = results['personal'].values()[0]
            svrPackedData = results['uniqueSubUrl']
            clientPackedData = packPostBattleUniqueSubUrl(arenaUniqueID, common['arenaTypeID'], personal['typeCompDescr'], personal['xp'])
            copyToClipboard(functions.getPostBattleUniqueSubUrl(svrPackedData, clientPackedData))
            if hasattr(BigWorld.player(), 'cmdPublishBattleResults'):
                BigWorld.player().cmdPublishBattleResults(svrPackedData, arenaUniqueID)
            SystemMessages.pushI18nMessage('#system_messages:battleResults/sharing/success')
        except:
            LOG_ERROR('There is error while getting post battle sub url')
            LOG_CURRENT_EXCEPTION()

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

    def __getFairPlayViolationName(self, pData):
        fairPlayViolationData = pData.get('fairplayViolations')
        if fairPlayViolationData is not None:
            return getFairPlayViolationName(fairPlayViolationData[1])
        else:
            return

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

    def startCSAnimationSound(self, soundEffectID = 'cs_animation_league_up'):
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
        if unlockType in (PROGRESS_ACTION.RESEARCH_UNLOCK_TYPE, PROGRESS_ACTION.PURCHASE_UNLOCK_TYPE):
            showResearchView(itemId)
            self.onWindowClose()
        elif unlockType == PROGRESS_ACTION.NEW_SKILL_UNLOCK_TYPE:
            showPersonalCase(itemId, 2)
