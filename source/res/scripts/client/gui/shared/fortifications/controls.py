# Embedded file name: scripts/client/gui/shared/fortifications/controls.py
import BigWorld
from functools import partial
from operator import attrgetter
from debug_utils import LOG_ERROR, LOG_DEBUG
import fortified_regions
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.fortifications import getClientFort, getClientFortMgr
from gui.shared.fortifications.FortFinder import FortFinder
from gui.shared.fortifications.context import FortRequestCtx
from gui.shared.fortifications.fort_ext import FortCooldownManager
from gui.shared.fortifications.fort_ext import PlayerFortRequester
from gui.game_control.battle_availability import SortiesCurfewController
from gui.shared.fortifications.fort_seqs import SortiesCache, PublicInfoCache, FortBattlesCache
from gui.shared.fortifications.interfaces import IFortController
from gui.shared.fortifications.restrictions import FortPermissions, NoFortLimits, IntroFortLimits, NoFortValidators, FortValidators
from gui.shared.fortifications.restrictions import FortLimits
from gui.shared.fortifications.settings import FORT_REQUEST_TYPE, CLIENT_FORT_STATE
from helpers import time_utils

class _FortController(IFortController):
    _TIME_OUT = 45

    def __init__(self, handlers):
        super(_FortController, self).__init__()
        self._requester = None
        self._limits = None
        self._validators = None
        self._sortiesCache = None
        self._sortiesCurfewCtrl = None
        self._fortBattlesCache = None
        self._publicInfoCache = None
        self._handlers = handlers
        self._cooldown = FortCooldownManager()
        self.clear()
        return

    def clear(self):
        self._clan = None
        self._listeners = None
        self._waiters = None
        return

    def init(self, clan, listeners, prevController = None):
        self._requester = PlayerFortRequester()
        self._requester.init()
        self._setLimits()
        self._setValidators()
        self._clan = clan
        self._listeners = listeners
        self._addFortListeners()
        self._waiters = {}

    def fini(self, clearCache = True):
        self._removeFortListeners()
        self.stopProcessing()
        if self._requester:
            self._requester.fini()
            self._requester = None
        if self._limits:
            self._limits = None
        if self._validators:
            self._validators.fini()
            self._validators = None
        self.clear()
        self._handlers.clear()
        return

    def stopProcessing(self):
        self._clearWaiters()
        if self._requester is not None:
            self._requester.stopProcessing()
        return

    def getFort(self):
        return getClientFort()

    def getPermissions(self):
        if self._clan:
            roles = self._clan.clanRole
        else:
            roles = 0
        return FortPermissions(roles)

    def getLimits(self):
        return self._limits

    def getValidators(self):
        return self._validators

    def getSortiesCache(self):
        return self._sortiesCache

    def getFortBattlesCache(self):
        return self._fortBattlesCache

    def getSortiesCurfewCtrl(self):
        return self._sortiesCurfewCtrl

    def getPublicInfoCache(self):
        return self._publicInfoCache

    def removeSortiesCache(self):
        SortiesCache._removeStoredData()

    def removeFortBattlesCache(self):
        FortBattlesCache._removeStoredData()

    def request(self, ctx, callback = None):
        if self._clan is None:
            return self._failChecking('Clan is not defined', ctx, callback)
        else:
            requestType = ctx.getRequestType()
            if requestType in self._handlers:
                cooldown = ctx.getCooldown()
                if self._cooldown.validate(requestType, cooldown):
                    if callback:
                        callback(False)
                else:
                    LOG_DEBUG('Fort request', ctx)
                    if self._handlers[requestType](ctx, callback=partial(self._callbackWrapper, requestType, callback, cooldown)):
                        self._waiters[requestType] = BigWorld.callback(self._TIME_OUT, self._onTimeout)
                        self._cooldown.process(requestType, cooldown)
            else:
                self._failChecking('Handler not found', ctx, callback)
            return

    def subscribe(self, callback = None):

        def _doRequest():
            LOG_DEBUG('Fort request to subscribe')
            result = self._requester.doRequestEx(FortRequestCtx(), callback, 'subscribe')
            if result:
                self._waiters[FORT_REQUEST_TYPE.SUBSCRIBE] = BigWorld.callback(self._TIME_OUT, self._onTimeout)
                self._cooldown.process(FORT_REQUEST_TYPE.SUBSCRIBE)

        if self._cooldown.validate(FORT_REQUEST_TYPE.SUBSCRIBE):
            BigWorld.callback(self._cooldown.getTime(FORT_REQUEST_TYPE.SUBSCRIBE), _doRequest)
        else:
            _doRequest()

    def unsubscribe(self, callback = None):
        LOG_DEBUG('Fort request to unsubscribe')
        self._requester.doRequestEx(FortRequestCtx(), callback, 'unsubscribe')
        return False

    def _failChecking(self, ctx, msg, callback = None):
        if callback:
            callback(False)
        LOG_ERROR(msg, ctx)
        return False

    def _addFortListeners(self):
        pass

    def _removeFortListeners(self):
        pass

    def _setLimits(self):
        self._limits = NoFortLimits()

    def _setValidators(self):
        self._validators = NoFortValidators()

    def _callbackWrapper(self, requestType, callback, cooldown, *args):
        callbackID = self._waiters.pop(requestType, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        self._cooldown.adjust(requestType, cooldown)
        callback(*args)
        return

    def _clearWaiters(self):
        if self._waiters is not None:
            while len(self._waiters):
                _, callbackID = self._waiters.popitem()
                BigWorld.cancelCallback(callbackID)

        return

    def _onTimeout(self):
        LOG_ERROR('Fort request time out!')
        self.stopProcessing()
        g_eventBus.handleEvent(events.FortEvent(events.FortEvent.REQUEST_TIMEOUT), scope=EVENT_BUS_SCOPE.FORT)


class NoFortController(_FortController):

    def __init__(self):
        super(NoFortController, self).__init__({})

    @classmethod
    def isNext(cls, stateID, isLeader):
        if stateID in [CLIENT_FORT_STATE.NO_CLAN, CLIENT_FORT_STATE.UNSUBSCRIBED]:
            return True
        if not isLeader and stateID == CLIENT_FORT_STATE.NO_FORT:
            return True

    def request(self, ctx, callback = None):
        self._failChecking('Has been invoked NoFortController.request', ctx, callback)

    def init(self, clan, listeners, prevController = None):
        super(NoFortController, self).init(clan, listeners, prevController)
        self._sortiesCurfewCtrl = SortiesCurfewController()
        self._sortiesCurfewCtrl.start()

    def fini(self, clearCache = True):
        if self._sortiesCurfewCtrl:
            self._sortiesCurfewCtrl.stop()
            self._sortiesCurfewCtrl = None
        super(NoFortController, self).fini(clearCache)
        return


class CenterUnavailableController(_FortController):

    def __init__(self):
        super(CenterUnavailableController, self).__init__({})

    @classmethod
    def isNext(cls, stateID, isLeader):
        if stateID in [CLIENT_FORT_STATE.CENTER_UNAVAILABLE]:
            return True
        if not isLeader and stateID == CLIENT_FORT_STATE.NO_FORT:
            return True

    def init(self, clan, listeners, prevController = None):
        super(CenterUnavailableController, self).init(clan, listeners, prevController)
        if prevController is not None:
            self._sortiesCache = prevController.getSortiesCache()
            if self._sortiesCache is not None:
                self._sortiesCache.setController(self)
        return

    def fini(self, clearCache = True):
        if self._sortiesCache and clearCache:
            self._sortiesCache.stop()
            self._sortiesCache = None
        super(CenterUnavailableController, self).fini()
        return

    def request(self, ctx, callback = None):
        self._failChecking('Has been invoked CenterUnavailableController.request', ctx, callback)


class IntroController(_FortController):

    def __init__(self):
        super(IntroController, self).__init__({FORT_REQUEST_TYPE.CREATE_FORT: self.create})

    @classmethod
    def isNext(cls, stateID, isLeader):
        return isLeader and stateID == CLIENT_FORT_STATE.NO_FORT

    def create(self, ctx, callback = None):
        perm = self.getPermissions()
        if not perm.canCreate():
            return self._failChecking('Player can not create fort', ctx, callback)
        fort = self.getFort()
        if not fort.isEmpty():
            return self._failChecking('Fort is already created', ctx, callback)
        limits = self.getLimits()
        valid, reason = limits.isCreationValid()
        if not valid:
            return self._failChecking('Creation is not valid: {0}'.format(reason), ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'create')

    def _setLimits(self):
        self._limits = IntroFortLimits()


class FortController(_FortController):

    def __init__(self):
        super(FortController, self).__init__({FORT_REQUEST_TYPE.OPEN_DIRECTION: self.openDirection,
         FORT_REQUEST_TYPE.CLOSE_DIRECTION: self.closeDirection,
         FORT_REQUEST_TYPE.ADD_BUILDING: self.addBuilding,
         FORT_REQUEST_TYPE.DELETE_BUILDING: self.deleteBuilding,
         FORT_REQUEST_TYPE.TRANSPORTATION: self.transport,
         FORT_REQUEST_TYPE.ADD_ORDER: self.addOrder,
         FORT_REQUEST_TYPE.ACTIVATE_ORDER: self.activateOrder,
         FORT_REQUEST_TYPE.ATTACH: self.attach,
         FORT_REQUEST_TYPE.UPGRADE: self.upgrade,
         FORT_REQUEST_TYPE.CREATE_SORTIE: self.createSortie,
         FORT_REQUEST_TYPE.REQUEST_SORTIE_UNIT: self.requestSortieUnit,
         FORT_REQUEST_TYPE.CHANGE_DEF_HOUR: self.changeDefHour,
         FORT_REQUEST_TYPE.CHANGE_OFF_DAY: self.changeOffDay,
         FORT_REQUEST_TYPE.CHANGE_PERIPHERY: self.changePeriphery,
         FORT_REQUEST_TYPE.CHANGE_VACATION: self.changeVacation,
         FORT_REQUEST_TYPE.CHANGE_SETTINGS: self.changeSettings,
         FORT_REQUEST_TYPE.SHUTDOWN_DEF_HOUR: self.shutDownDefHour,
         FORT_REQUEST_TYPE.CANCEL_SHUTDOWN_DEF_HOUR: self.cancelShutDownDefHour,
         FORT_REQUEST_TYPE.REQUEST_PUBLIC_INFO: self.requestFortPublicInfo,
         FORT_REQUEST_TYPE.REQUEST_CLAN_CARD: self.requestClanCard,
         FORT_REQUEST_TYPE.ADD_FAVORITE: self.addFavorite,
         FORT_REQUEST_TYPE.REMOVE_FAVORITE: self.removeFavorite,
         FORT_REQUEST_TYPE.PLAN_ATTACK: self.planAttack,
         FORT_REQUEST_TYPE.CREATE_OR_JOIN_FORT_BATTLE: self.createOrJoinFortBattle,
         FORT_REQUEST_TYPE.ACTIVATE_CONSUMABLE: self.activateConsumable,
         FORT_REQUEST_TYPE.RETURN_CONSUMABLE: self.returnConsumable})
        self.__cooldownCallback = None
        self.__cooldownBuildings = []
        self.__cooldownPassed = False
        self._upgradeVisitedBuildings = set()
        self._finder = None
        self.__defencePeriodCallback = None
        return

    @classmethod
    def isNext(cls, stateID, _):
        return stateID in [CLIENT_FORT_STATE.WIZARD, CLIENT_FORT_STATE.HAS_FORT]

    def init(self, clan, listeners, prevController = None):
        super(FortController, self).init(clan, listeners, prevController)
        self._sortiesCache = SortiesCache(self)
        self._sortiesCache.start()
        self._sortiesCurfewCtrl = SortiesCurfewController()
        self._sortiesCurfewCtrl.start()
        self._fortBattlesCache = FortBattlesCache(self)
        self._fortBattlesCache.start()
        self._finder = FortFinder()
        self._finder.init()
        self._publicInfoCache = PublicInfoCache(self)
        self._publicInfoCache.start()

    def fini(self, clearCache = True):
        if self._sortiesCache and clearCache:
            self._sortiesCache.stop()
            self._sortiesCache = None
        if self._sortiesCurfewCtrl:
            self._sortiesCurfewCtrl.stop()
            self._sortiesCurfewCtrl = None
        if self._fortBattlesCache:
            self._fortBattlesCache.stop()
            self._fortBattlesCache = None
        if self._publicInfoCache:
            self._publicInfoCache.stop()
            self._publicInfoCache = None
        super(FortController, self).fini()
        return

    def stopProcessing(self):
        if self._finder is not None:
            self._finder.stopProcessing()
        super(FortController, self).stopProcessing()
        return

    def openDirection(self, ctx, callback = None):
        perm = self.getPermissions()
        fort = self.getFort()
        direction = ctx.getDirection()
        if fort.isDirectionOpened(direction):
            return self._failChecking('Direction already is opened', ctx, callback)
        if not perm.canOpenDirection():
            return self._failChecking('Player can not open direction', ctx, callback)
        limits = self.getLimits()
        valid, reason = limits.isDirectionValid(direction)
        if not valid:
            return self._failChecking('Direction is invalid: {0}'.format(reason), ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'openDir', direction)

    def closeDirection(self, ctx, callback = None):
        perm = self.getPermissions()
        fort = self.getFort()
        direction = ctx.getDirection()
        if not fort.isDirectionOpened(direction):
            return self._failChecking('Direction is not opened', ctx, callback)
        if not perm.canCloseDirection():
            return self._failChecking('Player can not open direction', ctx, callback)
        limits = self.getLimits()
        valid, reason = limits.isDirectionValid(direction, open=False)
        if not valid:
            return self._failChecking('Direction is invalid: {0}'.format(reason), ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'closeDir', direction)

    def addBuilding(self, ctx, callback = None):
        perm = self.getPermissions()
        fort = self.getFort()
        buildingTypeID = ctx.getBuildingTypeID()
        direction = ctx.getDirection()
        position = ctx.getPosition()
        if not fort.isPositionAvailable(direction, position):
            return self._failChecking('Positions is not available', ctx, callback)
        if fort.isBuildingBuilt(buildingTypeID):
            return self._failChecking('Building is already built', ctx, callback)
        if not perm.canAddBuilding():
            return self._failChecking('Player can not build buildings', ctx, callback)
        limits = self.getLimits()
        valid, reason = limits.canBuild(buildingTypeID)
        if not valid:
            return self._failChecking('Building is invalid: {0}'.format(reason), ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'addBuilding', buildingTypeID, direction, position)

    def deleteBuilding(self, ctx, callback = None):
        perm = self.getPermissions()
        fort = self.getFort()
        buildingTypeID = ctx.getBuildingTypeID()
        if not fort.isBuildingBuilt(buildingTypeID):
            return self._failChecking('Building is not built', ctx, callback)
        if not perm.canDeleteBuilding():
            return self._failChecking('Player can not build buildings', ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'delBuilding', buildingTypeID)

    def transport(self, ctx, callback = None):
        perm = self.getPermissions()
        fort = self.getFort()
        fromBuildingID = ctx.getFromBuildingTypeID()
        toBuildingID = ctx.getToBuildingTypeID()
        resCount = ctx.getResCount()
        if not fort.isBuildingBuilt(fromBuildingID):
            return self._failChecking('Exporting building is not built', ctx, callback)
        if not fort.isBuildingBuilt(toBuildingID):
            return self._failChecking('Importing building is not built', ctx, callback)
        fromBuilding = fort.getBuilding(fromBuildingID)
        if not fromBuilding.isReady() or not fromBuilding.isExportAvailable(resCount):
            return self._failChecking('Exporting from building is not available', ctx, callback)
        toBuilding = fort.getBuilding(toBuildingID)
        if not toBuilding.isImportAvailable(resCount):
            return self._failChecking('Importing into building is not available', ctx, callback)
        if not perm.canTransport():
            return self._failChecking('Player can not transport', ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'transport', fromBuildingID, toBuildingID, resCount)

    def attach(self, ctx, callback = None):
        perm = self.getPermissions()
        fort = self.getFort()
        buildingTypeID = ctx.getBuildingTypeID()
        if not fort.isBuildingBuilt(buildingTypeID):
            return self._failChecking('Building is not built', ctx, callback)
        if not perm.canAttach():
            return self._failChecking('Player can not attach', ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'attach', buildingTypeID)

    def upgrade(self, ctx, callback = None):
        perm = self.getPermissions()
        fort = self.getFort()
        buildingTypeID = ctx.getBuildingTypeID()
        if not fort.isBuildingBuilt(buildingTypeID):
            return self._failChecking('Building is not built', ctx, callback)
        building = fort.getBuilding(buildingTypeID)
        if not building.isReady():
            return self._failChecking('Building is not available', ctx, callback)
        if not perm.canUpgradeBuilding():
            return self._failChecking('Player can not upgrade building', ctx, callback)
        limits = self.getLimits()
        valid, reason = limits.canUpgrade(buildingTypeID)
        if not valid:
            return self._failChecking('Building is invalid: {0}'.format(reason), ctx, callback)
        self.removeUpgradeVisitedBuilding(buildingTypeID)
        return self._requester.doRequestEx(ctx, callback, 'upgrade', buildingTypeID)

    def addOrder(self, ctx, callback = None):
        perm = self.getPermissions()
        fort = self.getFort()
        orderTypeID = ctx.getOrderTypeID()
        count = ctx.getCount()
        order = fort.getOrder(orderTypeID)
        if not order.hasBuilding:
            return self._failChecking('Order building is not built', ctx, callback)
        orderBuilding = fort.getBuilding(order.buildingID)
        if not orderBuilding.isReady() and not orderBuilding.orderInProduction:
            return self._failChecking('Building is not ready to add order', ctx, callback)
        if not perm.canAddOrder():
            return self._failChecking('Player can not add order', ctx, callback)
        limits = self.getLimits()
        valid, reason = limits.isOrderValid(orderTypeID, add=False)
        if not valid:
            return self._failChecking('Orded is invalid: {0}'.format(reason), ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'addOrder', order.buildingID, count)

    def activateOrder(self, ctx, callback = None):
        perm = self.getPermissions()
        fort = self.getFort()
        orderTypeID = ctx.getOrderTypeID()
        order = fort.getOrder(orderTypeID)
        if not order.hasBuilding:
            return self._failChecking('Order building is not built', ctx, callback)
        orderBuilding = fort.getBuilding(order.buildingID)
        if not orderBuilding.isReady():
            return self._failChecking('Building is not ready to add order', ctx, callback)
        if not perm.canActivateOrder():
            return self._failChecking('Player can not add order', ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'activateOrder', orderTypeID)

    def createSortie(self, ctx, callback = None):
        level = ctx.getDivisionLevel()
        perm = self.getPermissions()
        if not perm.canCreateSortie():
            return self._failChecking('Player can not create sortie, no permission', ctx, callback)
        limits = self.getLimits()
        valid, reason = limits.isSortieCreationValid(level)
        if not valid:
            return self._failChecking('Player can not create sortie: {0}'.format(reason), ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'createSortie', level)

    def requestSortieUnit(self, ctx, callback = None):
        unitMgrID = ctx.getUnitMgrID()
        peripheryID = ctx.getPeripheryID()
        fort = self.getFort()
        if not fort:
            return self._failChecking('Client fort is not found', ctx, callback)
        if (unitMgrID, peripheryID) not in fort.sorties:
            return self._failChecking('Sortie does not exists on client', ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'getSortieData', unitMgrID, peripheryID)

    def getUpgradeVisitedBuildings(self):
        return self._upgradeVisitedBuildings

    def addUpgradeVisitedBuildings(self, buildingID):
        if buildingID not in self._upgradeVisitedBuildings:
            self._upgradeVisitedBuildings.add(buildingID)
            self._listeners.notify('onUpgradeVisitedBuildingChanged', buildingID)

    def removeUpgradeVisitedBuilding(self, buildingID):
        if buildingID in self._upgradeVisitedBuildings:
            self._upgradeVisitedBuildings.remove(buildingID)
            self._listeners.notify('onUpgradeVisitedBuildingChanged', buildingID)

    def changeDefHour(self, ctx, callback = None):
        perm = self.getPermissions()
        defHour = ctx.getDefenceHour()
        if not perm.canChangeDefHour():
            return self._failChecking('Player can not change defence hour', ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'changeDefHour', defHour)

    def changeOffDay(self, ctx, callback = None):
        perm = self.getPermissions()
        offDay = ctx.getOffDay()
        if not perm.canChangeOffDay():
            return self._failChecking('Player can not change off day', ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'changeOffDay', offDay)

    def changePeriphery(self, ctx, callback = None):
        perm = self.getPermissions()
        peripheryID = ctx.getPeripheryID()
        if not perm.canChangePeriphery():
            return self._failChecking('Player can not change periphery', ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'changePeriphery', peripheryID)

    def changeVacation(self, ctx, callback = None):
        perm = self.getPermissions()
        timeVacationStart = ctx.getTimeVacationStart()
        timeVacationDuration = ctx.getTimeVacationDuration()
        if not perm.canChangeVacation():
            return self._failChecking('Player can not change vacation', ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'changeVacation', timeVacationStart, timeVacationDuration)

    def changeSettings(self, ctx, callback = None):
        perm = self.getPermissions()
        fort = self.getFort()
        chain = []
        defHour = ctx.getDefenceHour()
        if defHour != fort.defenceHour:
            if not perm.canChangeDefHour():
                return self._failChecking('Player can not change defence hour', ctx, callback)
            chain.append(('changeDefHour', (defHour,), {}))
        offDay = ctx.getOffDay()
        if offDay != fort.offDay:
            if not perm.canChangeOffDay():
                return self._failChecking('Player can not change off day', ctx, callback)
            chain.append(('changeOffDay', (offDay,), {}))
        peripheryID = ctx.getPeripheryID()
        if peripheryID != fort.peripheryID:
            if not perm.canChangePeriphery():
                return self._failChecking('Player can not change periphery', ctx, callback)
            chain.append(('changePeriphery', (peripheryID,), {}))
        if not chain:
            return self._failChecking('No requests to process', ctx, callback)
        return self._requester.doRequestChainEx(ctx, callback, chain)

    def shutDownDefHour(self, ctx, callback = None):
        perm = self.getPermissions()
        if not perm.canShutDownDefHour():
            return self._failChecking('Player can not shut down def hour', ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'shutdownDefHour')

    def cancelShutDownDefHour(self, ctx, callback = None):
        perm = self.getPermissions()
        if not perm.canCancelShutDownDefHour():
            return self._failChecking('Player can not cancel shut down def hour', ctx, callback)
        return self._requester.doRequestEx(ctx, callback, 'cancelDefHourShutdown')

    def requestFortPublicInfo(self, ctx, callback = None):
        fort = self.getFort()
        perm = self.getPermissions()
        if not perm.canRequestPublicInfo():
            return self._failChecking('Player can not request public info', ctx, callback)
        filterType = ctx.getFilterType()
        abbrevPattern = ctx.getAbbrevPattern()
        homePeripheryID = fort.peripheryID
        limit = ctx.getLimit()
        lvlFrom = ctx.getLvlFrom()
        lvlTo = ctx.getLvlTo()
        ownStartDefHourFrom = fort.defenceHour
        nextOwnStartDefHourFrom, defHourChangeDay = fort.getNextDefenceHourData()
        extStartDefHourFrom = ctx.getStartDefHourFrom()
        extStartDefHourTo = ctx.getStartDefHourTo()
        attackDay = ctx.getAttackDay()
        ownFortLvl = fort.level
        battleStats = fort.getFortDossier().getBattlesStats()
        ownProfitFactor10 = int(battleStats.getProfitFactor() * 10)
        buildingLevels = map(attrgetter('level'), fort.getBuildings().itervalues())
        minLevel = fortified_regions.g_cache.defenceConditions.minRegionLevel
        validBuildingLevels = filter(lambda x: x >= minLevel, buildingLevels)
        avgBuildingLevel10 = 0
        if validBuildingLevels:
            avgBuildingLevel10 = int(float(sum(validBuildingLevels)) / len(validBuildingLevels) * 10)
        ownBattleCountForFort = battleStats.getBattlesCount()
        firstDefaultQuery = ctx.isFirstDefaultQuery()
        electedClanDBIDs = tuple(fort.favorites)
        val = self.getValidators()
        validationResult, validationReason = val.validate(ctx.getRequestType(), filterType, abbrevPattern)
        if not validationResult:
            self._listeners.notify('onFortPublicInfoValidationError', validationReason)
            return self._failChecking('Player input is invalid', ctx, callback)
        return self._finder.request(filterType, abbrevPattern, homePeripheryID, limit, lvlFrom, lvlTo, ownStartDefHourFrom, ownStartDefHourFrom + 1, nextOwnStartDefHourFrom, nextOwnStartDefHourFrom + 1, defHourChangeDay, extStartDefHourFrom, extStartDefHourTo, attackDay, ownFortLvl, ownProfitFactor10, avgBuildingLevel10, ownBattleCountForFort, firstDefaultQuery, electedClanDBIDs, callback)

    def requestClanCard(self, ctx, callback = None):
        perm = self.getPermissions()
        if not perm.canRequestClanCard():
            return self._failChecking('Player can not request clan card', ctx, callback)
        clanDBID = ctx.getClanDBID()
        return self._requester.doRequestEx(ctx, callback, 'getEnemyClanCard', clanDBID)

    def addFavorite(self, ctx, callback = None):
        perm = self.getPermissions()
        if not perm.canAddToFavorite():
            return self._failChecking('Player can not add favorite', ctx, callback)
        clanDBID = ctx.getClanDBID()
        return self._requester.doRequestEx(ctx, callback, 'addFavorite', clanDBID)

    def removeFavorite(self, ctx, callback = None):
        perm = self.getPermissions()
        if not perm.canRemoveFavorite():
            return self._failChecking('Player can not remove favorite', ctx, callback)
        clanDBID = ctx.getClanDBID()
        return self._requester.doRequestEx(ctx, callback, 'removeFavorite', clanDBID)

    def planAttack(self, ctx, callback = None):
        perm = self.getPermissions()
        if not perm.canPlanAttack():
            return self._failChecking('Player can not plan attack', ctx, callback)
        clanDBID = ctx.getClanDBID()
        timeAttack = ctx.getTimeAttack()
        dirFrom = ctx.getDirFrom()
        dirTo = ctx.getDirTo()
        return self._requester.doRequestEx(ctx, callback, 'planAttack', clanDBID, timeAttack, dirFrom, dirTo)

    def createOrJoinFortBattle(self, ctx, callback = None):
        perm = self.getPermissions()
        if not perm.canCreateFortBattle():
            return self._failChecking('Player can not plan attack', ctx, callback)
        battleID = ctx.getBattleID()
        slotIdx = ctx.getSlotIdx()
        return self._requester.doRequestEx(ctx, callback, 'createOrJoinFortBattle', battleID, slotIdx)

    def activateConsumable(self, ctx, callback = None):
        perm = self.getPermissions()
        if not perm.canActivateConsumable():
            return self._failChecking('Player can not activate consumable', ctx, callback)
        orderTypeID = ctx.getConsumableOrderTypeID()
        slotIdx = ctx.getSlotIdx()
        return self._requester.doRequestEx(ctx, callback, 'activateConsumable', orderTypeID, slotIdx)

    def returnConsumable(self, ctx, callback = None):
        perm = self.getPermissions()
        if not perm.canReturnConsumable():
            return self._failChecking('Player can not return consumable', ctx, callback)
        orderTypeID = ctx.getConsumableOrderTypeID()
        return self._requester.doRequestEx(ctx, callback, 'returnConsumable', orderTypeID)

    def _setLimits(self):
        self._limits = FortLimits()

    def _setValidators(self):
        self._validators = FortValidators()

    def _addFortListeners(self):
        super(FortController, self)._addFortListeners()
        fort = self.getFort()
        if not fort:
            LOG_ERROR('No fort to subscribe')
            return
        fort.onBuildingChanged += self.__fort_onBuildingChanged
        fort.onTransport += self.__fort_onTransport
        fort.onDirectionOpened += self.__fort_onDirectionOpened
        fort.onDirectionClosed += self.__fort_onDirectionClosed
        fort.onDirectionLockChanged += self.__fort_onDirectionLockChanged
        fort.onStateChanged += self.__fort_onStateChanged
        fort.onOrderChanged += self.__fort_onOrderChanged
        fort.onDossierChanged += self.__fort_onDossierChanged
        fort.onPlayerAttached += self.__fort_onPlayerAttached
        fort.onSettingCooldown += self.__fort_onSettingCooldown
        fort.onPeripheryChanged += self.__fort_onPeripheryChanged
        fort.onDefenceHourChanged += self.__fort_onDefenceHourChanged
        fort.onOffDayChanged += self.__fort_onOffDayChanged
        fort.onVacationChanged += self.__fort_onVacationChanged
        fort.onFavoritesChanged += self.__fort_onFavoritesChanged
        fort.onEnemyClanCardReceived += self.__fort_onEnemyClanCardReceived
        fort.onShutdownDowngrade += self.__fort_onShutdownDowngrade
        fort.onDefenceHourShutdown += self.__fort_onDefenceHourShutdown
        fort.onEmergencyRestore += self.__fort_onEmergencyRestore
        fort.onConsumablesChanged += self.__fort_onConsumablesChanged
        fort.onDefenceHourActivated += self.__fort_onDefenceHourActivated
        fortMgr = getClientFortMgr()
        if not fortMgr:
            LOG_ERROR('No fort manager to subscribe')
            return
        fortMgr.onFortUpdateReceived += self.__fortMgr_onFortUpdateReceived
        fortMgr.onFortPublicInfoReceived += self.__fortMgr_onFortPublicInfoReceived
        self.__refreshCooldowns(False)
        self.__processDefencePeriodCallback()

    def _removeFortListeners(self):
        self.__cancelCooldownCallback()
        self.__cancelDefencePeriodCallback()
        fort = self.getFort()
        if fort:
            fort.onBuildingChanged -= self.__fort_onBuildingChanged
            fort.onTransport -= self.__fort_onTransport
            fort.onDirectionOpened -= self.__fort_onDirectionOpened
            fort.onDirectionClosed -= self.__fort_onDirectionClosed
            fort.onDirectionLockChanged -= self.__fort_onDirectionLockChanged
            fort.onStateChanged -= self.__fort_onStateChanged
            fort.onOrderChanged -= self.__fort_onOrderChanged
            fort.onDossierChanged -= self.__fort_onDossierChanged
            fort.onPlayerAttached -= self.__fort_onPlayerAttached
            fort.onSettingCooldown -= self.__fort_onSettingCooldown
            fort.onPeripheryChanged -= self.__fort_onPeripheryChanged
            fort.onDefenceHourChanged -= self.__fort_onDefenceHourChanged
            fort.onOffDayChanged -= self.__fort_onOffDayChanged
            fort.onVacationChanged -= self.__fort_onVacationChanged
            fort.onFavoritesChanged -= self.__fort_onFavoritesChanged
            fort.onEnemyClanCardReceived -= self.__fort_onEnemyClanCardReceived
            fort.onShutdownDowngrade -= self.__fort_onShutdownDowngrade
            fort.onDefenceHourShutdown -= self.__fort_onDefenceHourShutdown
            fort.onEmergencyRestore -= self.__fort_onEmergencyRestore
            fort.onConsumablesChanged -= self.__fort_onConsumablesChanged
            fort.onDefenceHourActivated -= self.__fort_onDefenceHourActivated
        fortMgr = getClientFortMgr()
        if fortMgr:
            fortMgr.onFortUpdateReceived -= self.__fortMgr_onFortUpdateReceived
            fortMgr.onFortPublicInfoReceived -= self.__fortMgr_onFortPublicInfoReceived
        super(FortController, self)._removeFortListeners()

    def __refreshCooldowns(self, doNotify = True):
        if self.__cooldownBuildings and doNotify:
            self._listeners.notify('onBuildingsUpdated', self.__cooldownBuildings, self.__cooldownPassed)
        self.__cancelCooldownCallback()
        fort = self.getFort()
        self.__cooldownBuildings = fort.getBuildingsOnCooldown()
        if self.__cooldownBuildings:
            time = 30
            self.__cooldownPassed = False
            for buildingID in self.__cooldownBuildings:
                building = fort.getBuilding(buildingID)
                estimatedCooldown = building.getEstimatedCooldown()
                if 0 < estimatedCooldown <= time:
                    time = estimatedCooldown
                    self.__cooldownPassed = True
                productionCooldown = building.getProductionCooldown()
                if 0 < productionCooldown < time:
                    time = productionCooldown

            self.__cooldownCallback = BigWorld.callback(time, self.__refreshCooldowns)

    def __cancelCooldownCallback(self):
        if self.__cooldownCallback is not None:
            BigWorld.cancelCallback(self.__cooldownCallback)
            self.__cooldownCallback = None
            self.__cooldownBuildings = []
            self.__cooldownPassed = False
        return

    def __processDefencePeriodCallback(self):
        self.__cancelDefencePeriodCallback()
        fort = self.getFort()
        self._listeners.notify('onDefenceHourStateChanged')
        start, finish = fort.getClosestDefencePeriod()
        if fort.isOnDefenceHour():
            timer = time_utils.getTimeDeltaFromNow(finish)
        else:
            timer = time_utils.getTimeDeltaFromNow(start)
        if timer > 0:
            self.__defencePeriodCallback = BigWorld.callback(timer, self.__processDefencePeriodCallback)

    def __cancelDefencePeriodCallback(self):
        if self.__defencePeriodCallback is not None:
            BigWorld.cancelCallback(self.__defencePeriodCallback)
            self.__defencePeriodCallback = None
        return

    def __fort_onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        self._listeners.notify('onBuildingChanged', buildingTypeID, reason, ctx)

    def __fort_onBuildingRemoved(self, buildingTypeID):
        self._listeners.notify('onBuildingRemoved', buildingTypeID)

    def __fort_onTransport(self):
        self._listeners.notify('onTransport')

    def __fort_onDirectionOpened(self, dir):
        self._listeners.notify('onDirectionOpened', dir)

    def __fort_onDirectionClosed(self, dir):
        self._listeners.notify('onDirectionClosed', dir)

    def __fort_onDirectionLockChanged(self):
        self._listeners.notify('onDirectionLockChanged')

    def __fort_onStateChanged(self, state):
        self._listeners.notify('onStateChanged', state)

    def __fort_onOrderChanged(self, orderTypeID, reason):
        self._listeners.notify('onOrderChanged', orderTypeID, reason)

    def __fort_onDossierChanged(self, compDossierDescr):
        self._listeners.notify('onDossierChanged', compDossierDescr)

    def __fort_onPlayerAttached(self, buildingTypeID):
        self._listeners.notify('onPlayerAttached', buildingTypeID)

    def __fort_onSettingCooldown(self, eventTypeID):
        self._listeners.notify('onSettingCooldown', eventTypeID)

    def __fort_onPeripheryChanged(self, peripheryID):
        self._listeners.notify('onPeripheryChanged', peripheryID)

    def __fort_onDefenceHourChanged(self, hour):
        self._listeners.notify('onDefenceHourChanged', hour)
        self.__processDefencePeriodCallback()

    def __fort_onDefenceHourActivated(self, hour, initiatorDBID):
        self._listeners.notify('onDefenceHourActivated', hour, initiatorDBID)
        self.__processDefencePeriodCallback()

    def __fort_onOffDayChanged(self, offDay):
        self._listeners.notify('onOffDayChanged', offDay)
        self.__processDefencePeriodCallback()

    def __fort_onVacationChanged(self, vacationStart, vacationEnd):
        self._listeners.notify('onVacationChanged', vacationStart, vacationEnd)
        self.__processDefencePeriodCallback()

    def __fort_onFavoritesChanged(self, clanDBID):
        self._listeners.notify('onFavoritesChanged', clanDBID)

    def __fort_onEnemyClanCardReceived(self, card):
        if self._publicInfoCache is not None:
            self._publicInfoCache.storeSelectedClanCard(card)
        self._listeners.notify('onEnemyClanCardReceived', card)
        return

    def __fort_onShutdownDowngrade(self):
        self._listeners.notify('onShutdownDowngrade')

    def __fort_onDefenceHourShutdown(self):
        self._listeners.notify('onDefenceHourShutdown')

    def __fortMgr_onFortUpdateReceived(self, isFullUpdate = False):
        self.__refreshCooldowns(isFullUpdate)

    def __fortMgr_onFortPublicInfoReceived(self, requestID, errorID, resultSet):
        self._finder.response(requestID, errorID, resultSet)
        self._listeners.notify('onFortPublicInfoReceived', bool(resultSet))

    def __fort_onEmergencyRestore(self):
        self.stopProcessing()

    def __fort_onConsumablesChanged(self, unitMgrID):
        self._listeners.notify('onConsumablesChanged', unitMgrID)


def createInitial():
    return NoFortController()


def createByState(state, isLeader = False, exclude = None):
    all = [NoFortController,
     IntroController,
     FortController,
     CenterUnavailableController]
    if exclude:
        if exclude in all:
            all.remove(exclude)
        else:
            LOG_ERROR('Fort controller is not found', exclude)
            return None
    stateID = state.getStateID()
    for clazz in all:
        if clazz.isNext(stateID, isLeader):
            return clazz()

    return None
