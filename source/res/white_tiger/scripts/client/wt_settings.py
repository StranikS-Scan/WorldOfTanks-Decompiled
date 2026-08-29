# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/wt_settings.py
import Event
from collections import namedtuple
from PlayerEvents import g_playerEvents
from shared_utils import makeTupleByDict
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from items import tankmen
from items.vehicles import getItemByCompactDescr
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.gui_items import Tankman
from gui.ClientUpdateManager import g_clientUpdateManager
from white_tiger_common.wt_helpers import isHunterVehicle, isBossVehicle, isSpecialBossVehicle, isAnyTypeBoss
from white_tiger_common.wt_constants import WHITE_TIGER_GAME_PARAMS_KEY

class _WhiteTigerConfig(namedtuple('WhiteTigerConfig', ('isEnabled',
 'peripheryIDs',
 'primeTimes',
 'seasons',
 'cycleTimes',
 'progression',
 'stampsPerProgressionStage',
 'stamp',
 'mainPrizeDiscountToken',
 'mainPrizeDiscountPerToken',
 'mainPrizeMaxDiscountTokenCount',
 'mainPrizeBoughtToken',
 'hunterPortalPrice',
 'bossPortalPrice',
 'tankPortalPrice',
 'ticketToken',
 'vipTicketToken',
 'quickBossTicketToken',
 'quickHunterTicketToken',
 'ticketsToDraw',
 'maxPlayerInactiveTime',
 'eventVehicles'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs={}, primeTimes={}, seasons={}, cycleTimes={}, progression=[], stampsPerProgressionStage=0, stamp='', mainPrizeDiscountToken='', mainPrizeDiscountPerToken=0, mainPrizeMaxDiscountTokenCount=0, mainPrizeBoughtToken='', hunterPortalPrice=0, bossPortalPrice=0, tankPortalPrice=0, ticketToken='', vipTicketToken='', quickBossTicketToken='', quickHunterTicketToken='', ticketsToDraw=0, maxPlayerInactiveTime=60, eventVehicles={})
        defaults.update(kwargs)
        return super(_WhiteTigerConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    @classmethod
    def defaults(cls):
        return cls()


_VehicleData = namedtuple('VehicleData', ('vehicle',
 'equipments',
 'type',
 'subType',
 'crew',
 'tokenForPlay',
 'isBoss',
 'isSpecialBoss',
 'isHunter',
 'canShowInHangar'))

class WTConfig(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __itemsCache = dependency.descriptor(IItemsCache)
    PROGRESSION_TOKEN_PREFIX = 'wtevent:progression'
    PROGRESSION_STAMP_TOKEN_PREFIX = 'wtevent:stamp'
    MAIN_PRIZE_DISCOUNT_TOKEN_PREFIX = 'wtevent:main_prize_discount'
    MAIN_PRIZE_BOUGHT_TOKEN_PREFIX = 'wtevent:main_prize_bought'
    QUICK_TOKEN_PREFIX = 'wtevent:quick_ticket'
    PASS_TOKEN_PREFIX = 'wtevent:pass_ticket'
    BOSS_TOKEN_PREFIX = 'wtevent:boss'

    def __init__(self):
        self.__config = _WhiteTigerConfig.defaults()
        self.__vehiclesCachedData = {}
        self.__vehiclesCachedDataByType = {}
        self.__eventTokens = {}
        self.onConfigWasUpdated = Event.Event()
        self.onProgressionTokenUpdate = Event.Event()
        self.onProgressionStampTokenUpdate = Event.Event()
        self.onMainPrizeDiscountTokenUpdate = Event.Event()
        self.onMainPrizeBoughtTokenUpdate = Event.Event()
        self.onQuickTokenUpdate = Event.Event()
        self.onPassTokenUpdate = Event.Event()
        self.onBossTokenUpdate = Event.Event()
        self.onEventTokenUpdate = Event.Event()
        self.__tokenUpdater = [[False, self.onProgressionTokenUpdate],
         [False, self.onProgressionStampTokenUpdate],
         [False, self.onMainPrizeDiscountTokenUpdate],
         [False, self.onMainPrizeBoughtTokenUpdate],
         [False, self.onQuickTokenUpdate],
         [False, self.onPassTokenUpdate],
         [False, self.onBossTokenUpdate],
         [False, self.onEventTokenUpdate]]

    def init(self):
        self.__connectionMgr.onConnected += self.__onConnected

    def __onConnected(self):
        self.__connectionMgr.onConnected -= self.__onConnected
        self.__connectionMgr.onDisconnected += self.__onDisconnected
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.onBossTokenUpdate += self.__cacheData

    def __onDisconnected(self):
        self.__connectionMgr.onConnected += self.__onConnected
        self.__connectionMgr.onDisconnected -= self.__onDisconnected
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.onBossTokenUpdate -= self.__cacheData
        self.onConfigWasUpdated.clear()
        self.onProgressionTokenUpdate.clear()
        self.onProgressionStampTokenUpdate.clear()
        self.onMainPrizeDiscountTokenUpdate.clear()
        self.onMainPrizeBoughtTokenUpdate.clear()
        self.onQuickTokenUpdate.clear()
        self.onPassTokenUpdate.clear()
        self.onBossTokenUpdate.clear()
        self.onEventTokenUpdate.clear()

    def __onClientUpdated(self, diff, _):
        self.__updateConfig(diff.get('serverSettings', {}))

    def __onTokensUpdate(self, diff):
        keys = set()
        for upd in self.__tokenUpdater:
            upd[0] = False

        for key in diff.keys():
            if key.startswith(self.PROGRESSION_TOKEN_PREFIX):
                self.__tokenUpdater[0][0] = True
                keys.add(key)
            elif key.startswith(self.PROGRESSION_STAMP_TOKEN_PREFIX):
                self.__tokenUpdater[1][0] = True
                keys.add(key)
            elif key.startswith(self.MAIN_PRIZE_DISCOUNT_TOKEN_PREFIX):
                self.__tokenUpdater[2][0] = True
                keys.add(key)
            elif key.startswith(self.MAIN_PRIZE_BOUGHT_TOKEN_PREFIX):
                self.__tokenUpdater[3][0] = True
                keys.add(key)
            elif key.startswith(self.QUICK_TOKEN_PREFIX):
                self.__tokenUpdater[4][0] = True
                keys.add(key)
            elif key.startswith(self.PASS_TOKEN_PREFIX):
                self.__tokenUpdater[5][0] = True
                keys.add(key)
            elif key.startswith(self.BOSS_TOKEN_PREFIX):
                self.__tokenUpdater[6][0] = True
                keys.add(key)
            if key.startswith('wtevent:'):
                self.__tokenUpdater[7][0] = True
                keys.add(key)

        for upd in self.__tokenUpdater:
            if upd[0]:
                upd[1](keys, diff)

    def __onServerSettingsChanged(self, serverSettings):
        settings = serverSettings.getSettings()
        self.__updateConfig(settings)

    def __updateConfig(self, diff):
        if WHITE_TIGER_GAME_PARAMS_KEY in diff:
            self.__config = makeTupleByDict(_WhiteTigerConfig, diff[WHITE_TIGER_GAME_PARAMS_KEY])
            self.__cacheData(None, None)
            self.onConfigWasUpdated()
        return

    def __onSyncCompleted(self, reason, __):
        if reason == CACHE_SYNC_REASON.SHOW_GUI:
            self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def getConfig(self):
        return self.__config

    def getAllVehiclesData(self):
        return self.__vehiclesCachedData

    def getVehicleTokens(self):
        return self.__eventTokens

    def getTokenDataByName(self, tokenName):
        tokenDraw = 0
        if tokenName in self.__eventTokens:
            tokenDraw = self.__eventTokens[tokenName]
        return {'tokenDraw': tokenDraw,
         'currentCount': self.__itemsCache.items.tokens.getTokenCount(tokenName)}

    def hasTokensByName(self, tokenName):
        countTokens = self.__itemsCache.items.tokens.getTokenCount(tokenName)
        return countTokens > 0 and countTokens >= self.getTokenDrawCountByName(tokenName)

    def getTokenDrawCountByName(self, tokenName):
        return self.__eventTokens[tokenName] if tokenName in self.__eventTokens else -1

    def hasTokensForBattle(self, vehicleCD):
        if vehicleCD not in self.__vehiclesCachedData:
            return False
        tokenForPlay = self.__vehiclesCachedData[vehicleCD].tokenForPlay
        if tokenForPlay:
            countTokens = self.__itemsCache.items.tokens.getTokenCount(tokenForPlay['name'])
            drawTokens = self.__itemsCache.items.tokens.getTokenCount(tokenForPlay['drawForBattle'])
            return countTokens > 0 and countTokens >= drawTokens
        return True

    def getTokensForBattle(self, vehicleCD):
        tokenForPlay = self.__vehiclesCachedData[vehicleCD].tokenForPlay
        return self.__itemsCache.items.tokens.getTokenCount(tokenForPlay['name']) if tokenForPlay else -1

    def getTokenExpiryTime(self, tokenID):
        return self.__itemsCache.items.tokens.getTokenExpiryTime(tokenID)

    def getVehicleData(self, vehicleCD):
        return self.__vehiclesCachedData[vehicleCD]

    def getBossVehiclesData(self):
        return self.__vehiclesCachedDataByType['bosses']

    def getAvailableBossesForBattle(self):
        return [ vehData.vehicle for vehData in self.getBossVehiclesData().itervalues() if self.hasTokensForBattle(vehData.vehicle.intCD) ]

    def isBossVehicle(self, vehicleCD):
        return isBossVehicle(vehicleCD, self.__vehiclesCachedDataByType)

    def getSpecialBossVehiclesData(self):
        return self.__vehiclesCachedDataByType['specialBosses']

    def getAvailableSpecialBossesForBattle(self):
        return [ vehData.vehicle for vehData in self.getSpecialBossVehiclesData().itervalues() if self.hasTokensForBattle(vehData.vehicle.intCD) ]

    def isSpecialBossVehicle(self, vehicleCD):
        return isSpecialBossVehicle(vehicleCD, self.__vehiclesCachedDataByType)

    def getHunterVehiclesData(self):
        return self.__vehiclesCachedDataByType['hunters']

    def getAvailableHuntersForBattle(self):
        return [ vehData.vehicle for vehData in self.getHunterVehiclesData().itervalues() if self.hasTokensForBattle(vehData.vehicle.intCD) ]

    def isHunterVehicle(self, vehicleCD):
        return isHunterVehicle(vehicleCD, self.__vehiclesCachedDataByType)

    def isAnyTypeBoss(self, vehicleCD):
        return isAnyTypeBoss(vehicleCD, self.__vehiclesCachedDataByType)

    def hasAbility(self, vehicleCD, abilityName):
        st = False
        eventVehicles = self.__config.eventVehicles
        if vehicleCD not in eventVehicles.get('hunters', {}):
            return st
        equipments = eventVehicles['hunters'][vehicleCD]['equipments']
        for equipmentCD in equipments:
            eq = getItemByCompactDescr(equipmentCD)
            if eq.name == abilityName:
                st = True
                break

        return st

    def __cacheData(self, _, __):
        self.__vehiclesCachedData = {}
        self.__vehiclesCachedDataByType = {}
        self.__eventTokens = {}
        eventVehicles = self.__config.eventVehicles
        self.__vehiclesCachedDataByType['bosses'] = {}
        for vehicleCD, data in eventVehicles['bosses'].iteritems():
            vehData = self.__getVehicleData(vehicleCD, data, isBoss=True)
            if vehData:
                self.__vehiclesCachedData[vehicleCD] = vehData
                self.__vehiclesCachedDataByType['bosses'][vehicleCD] = vehData
                if vehData.tokenForPlay:
                    self.__eventTokens.update({vehData.tokenForPlay['name']: vehData.tokenForPlay['drawForBattle']})

        self.__vehiclesCachedDataByType['specialBosses'] = {}
        for vehicleCD, data in eventVehicles['specialBosses'].iteritems():
            vehData = self.__getVehicleData(vehicleCD, data, isSpecialBoss=True)
            if vehData:
                self.__vehiclesCachedData[vehicleCD] = vehData
                self.__vehiclesCachedDataByType['specialBosses'][vehicleCD] = vehData
                if vehData.tokenForPlay:
                    self.__eventTokens.update({vehData.tokenForPlay['name']: vehData.tokenForPlay['drawForBattle']})

        self.__vehiclesCachedDataByType['hunters'] = {}
        for vehicleCD, data in eventVehicles['hunters'].iteritems():
            vehData = self.__getVehicleData(vehicleCD, data, isHunter=True)
            if vehData:
                self.__vehiclesCachedData[vehicleCD] = vehData
                self.__vehiclesCachedDataByType['hunters'][vehicleCD] = vehData
                if vehData.tokenForPlay:
                    self.__eventTokens.update({vehData.tokenForPlay['name']: vehData.tokenForPlay['drawForBattle']})

    def __getVehicleData(self, vehicleCD, data, isBoss=False, isSpecialBoss=False, isHunter=False):
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        if not data['tankManData']:
            return None
        else:
            tankmanCompDescr = tankmen.makeTmanDescrByTmanData(data['tankManData'])
            hasSpecialToken = data.get('tokenForShow', {})
            hasEnoughSpecialTokens = self.__itemsCache.items.tokens.getTokenCount(hasSpecialToken.get('name')) > 0
            canShowInHangar = not hasSpecialToken or hasEnoughSpecialTokens
            return _VehicleData(vehicle, data['equipments'], data['type'], data['subType'], Tankman.Tankman(tankmanCompDescr, vehicle=vehicle), data.get('tokenForPlay', {'name': '',
             'drawForBattle': 0}), isBoss, isSpecialBoss, isHunter, canShowInHangar)


g_wt_config = WTConfig()
