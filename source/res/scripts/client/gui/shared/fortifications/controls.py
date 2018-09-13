# Embedded file name: scripts/client/gui/shared/fortifications/controls.py
import BigWorld
from constants import REQUEST_COOLDOWN
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.shared.fortifications import getClientFort, getClientFortMgr
from gui.shared.fortifications.context import FortRequestCtx
from gui.shared.fortifications.fort_ext import FortCooldownManager
from gui.shared.fortifications.fort_ext import PlayerFortRequester
from gui.shared.fortifications.fort_seqs import SortiesCache
from gui.shared.fortifications.interfaces import IFortController
from gui.shared.fortifications.restrictions import FortPermissions, NoFortLimits, IntroFortLimits
from gui.shared.fortifications.restrictions import FortLimits
from gui.shared.fortifications.settings import FORT_REQUEST_TYPE, CLIENT_FORT_STATE

class _FortController(IFortController):

    def __init__(self, handlers):
        super(_FortController, self).__init__()
        self._requester = None
        self._limits = None
        self._sortiesCache = None
        self._handlers = handlers
        self._cooldown = FortCooldownManager()
        self.clear()
        return

    def clear(self):
        self._clan = None
        self._listeners = None
        return

    def init(self, clan, listeners):
        self._requester = PlayerFortRequester()
        self._requester.init()
        self._setLimits()
        self._clan = clan
        self._listeners = listeners
        self._addFortListeners()

    def fini(self):
        self._removeFortListeners()
        if self._requester:
            self._requester.fini()
            self._requester = None
        if self._limits:
            self._limits = None
        self.clear()
        self._handlers.clear()
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

    def getSortiesCache(self):
        return self._sortiesCache

    def removeSortiesCache(self):
        SortiesCache._removeStoredData()

    def request(self, ctx, callback = None):
        if self._clan is None:
            return self._failChecking('Clan is not defined', ctx, callback)
        else:
            requestType = ctx.getRequestType()
            if requestType in self._handlers:
                if self._cooldown.validate(requestType):
                    if callback:
                        callback(False)
                else:
                    LOG_DEBUG('Fort request', ctx)
                    if self._handlers[requestType](ctx, callback=callback):
                        if requestType == FORT_REQUEST_TYPE.REQUEST_SORTIE_UNIT:
                            coolDown = REQUEST_COOLDOWN.GET_FORT_SORTIE_DATA
                        else:
                            coolDown = REQUEST_COOLDOWN.CALL_FORT_METHOD
                        self._cooldown.process(requestType, coolDown)
            else:
                self._failChecking('Handler not found', ctx, callback)
            return

    def subscribe(self, callback = None):
        if self._cooldown.validate(FORT_REQUEST_TYPE.SUBSCRIBE):
            if callback:
                callback(False)
        LOG_DEBUG('Fort request to subscribe')
        result = self._requester.doRequestEx(FortRequestCtx('fort/subscribe'), callback, 'subscribe')
        if result:
            self._cooldown.process(FORT_REQUEST_TYPE.SUBSCRIBE)

    def unsubscribe(self, callback = None):
        LOG_DEBUG('Fort request to unsubscribe')
        self._requester.doRequestEx(FortRequestCtx('fort/unsubscribe'), callback, 'unsubscribe')
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


class NoFortController(_FortController):

    def __init__(self):
        super(NoFortController, self).__init__({})

    @classmethod
    def isNext(cls, stateID, isLeader):
        if stateID in [CLIENT_FORT_STATE.NO_CLAN, CLIENT_FORT_STATE.UNSUBSCRIBED, CLIENT_FORT_STATE.CENTER_UNAVAILABLE]:
            return True
        if not isLeader and stateID == CLIENT_FORT_STATE.NO_FORT:
            return True

    def request(self, ctx, callback = None):
        self._failChecking('Has been invoked NoFortController.request', ctx, callback)


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
         FORT_REQUEST_TYPE.REQUEST_SORTIE_UNIT: self.requestSortieUnit})
        self.__cooldownCallback = None
        self.__cooldownBuildings = []
        self.__cooldownPassed = False
        self._upgradeVisitedBuildings = set()
        return

    @classmethod
    def isNext(cls, stateID, _):
        return stateID in [CLIENT_FORT_STATE.WIZARD, CLIENT_FORT_STATE.HAS_FORT]

    def init(self, clan, listeners):
        super(FortController, self).init(clan, listeners)
        self._sortiesCache = SortiesCache(self)
        self._sortiesCache.start()

    def fini(self):
        if self._sortiesCache:
            self._sortiesCache.stop()
            self._sortiesCache = None
        self.cancelCooldownCallback()
        super(FortController, self).fini()
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

    def refreshCooldowns(self, doNotify = True):
        self.cancelCooldownCallback()
        if self.__cooldownBuildings and doNotify:
            self._listeners.notify('onBuildingsUpdated', self.__cooldownBuildings, self.__cooldownPassed)
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

            self.__cooldownCallback = BigWorld.callback(time, self.refreshCooldowns)

    def cancelCooldownCallback(self):
        if self.__cooldownCallback is not None:
            BigWorld.cancelCallback(self.__cooldownCallback)
            self.__cooldownCallback = None
            self.__cooldownBuildings = []
            self.__cooldownPassed = False
        return

    def _setLimits(self):
        self._limits = FortLimits()

    def _addFortListeners(self):
        super(FortController, self)._addFortListeners()
        fort = self.getFort()
        if not fort:
            LOG_ERROR('No fort to subscribe')
            return
        fort.onBuildingChanged += self.__fort_onBuildingChanged
        fort.onBuildingRemoved += self.__fort_onBuildingRemoved
        fort.onTransport += self.__fort_onTransport
        fort.onDirectionOpened += self.__fort_onDirectionOpened
        fort.onDirectionClosed += self.__fort_onDirectionClosed
        fort.onStateChanged += self.__fort_onStateChanged
        fort.onOrderReady += self.__fort_onOrderReady
        fort.onDossierChanged += self.__fort_onDossierChanged
        fort.onPlayerAttached += self.__fort_onPlayerAttached
        fortMgr = getClientFortMgr()
        if not fortMgr:
            LOG_ERROR('No fort manager to subscribe')
            return
        fortMgr.onFortUpdateReceived += self.__fortMgr_onFortUpdateReceived
        self.refreshCooldowns(False)

    def _removeFortListeners(self):
        fort = self.getFort()
        if not fort:
            LOG_ERROR('No fort to unsubscribe')
            return
        fort.onBuildingChanged -= self.__fort_onBuildingChanged
        fort.onBuildingRemoved -= self.__fort_onBuildingRemoved
        fort.onTransport -= self.__fort_onTransport
        fort.onDirectionOpened -= self.__fort_onDirectionOpened
        fort.onDirectionClosed -= self.__fort_onDirectionClosed
        fort.onStateChanged -= self.__fort_onStateChanged
        fort.onOrderReady -= self.__fort_onOrderReady
        fort.onDossierChanged -= self.__fort_onDossierChanged
        fort.onPlayerAttached -= self.__fort_onPlayerAttached
        fortMgr = getClientFortMgr()
        if not fort:
            LOG_ERROR('No fort manager to unsubscribe')
            return
        fortMgr.onFortUpdateReceived -= self.__fortMgr_onFortUpdateReceived
        super(FortController, self)._removeFortListeners()

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

    def __fort_onStateChanged(self, state):
        self._listeners.notify('onStateChanged', state)

    def __fort_onOrderReady(self, orderTypeID, count):
        self._listeners.notify('onOrderReady', orderTypeID, count)

    def __fort_onDossierChanged(self, compDossierDescr):
        self._listeners.notify('onDossierChanged', compDossierDescr)

    def __fort_onPlayerAttached(self, buildingTypeID):
        self._listeners.notify('onPlayerAttached', buildingTypeID)

    def __fortMgr_onFortUpdateReceived(self):
        self.refreshCooldowns(False)


def createInitial():
    return NoFortController()


def createByState(state, isLeader = False, exclude = None):
    all = [NoFortController, IntroController, FortController]
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
