# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/hangar_cm_handlers.py
from logging import getLogger
from CurrentVehicle import g_currentVehicle
from adisp import process
from constants import GameSeasonType, RentType
from crew2 import settings_globals
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getTradeInVehiclesUrl, getPersonalTradeInVehiclesUrl
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler, CM_BUY_COLOR, SEPARATOR_ID
from gui.Scaleform.locale.MENU import MENU
from gui.impl.auxiliary.detachmnet_convert_helper import isBarracksNotEmpty
from gui.impl.auxiliary.vehicle_helper import validateBestCrewForVehicle, isReturnCrewOptionAvailable
from gui.impl.lobby.buy_vehicle_view import VehicleBuyActionTypes
from gui.prb_control import prbDispatcherProperty
from gui.shared import event_dispatcher as shared_events
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showVehicleRentRenewDialog, showShop
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.processors.vehicle import VehicleFavoriteProcessor
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IVehicleComparisonBasket, IEpicBattleMetaGameController, ITradeInController, IPersonalTradeInController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED
from gui.shared.utils.requesters import REQ_CRITERIA
from uilogging.detachment.loggers import DynamicGroupLogger, g_detachmentFlowLogger
from uilogging.detachment.constants import GROUP, ACTION
_logger = getLogger(__name__)
CM_HIGHLIGHT_COLOR = 13347959

class RECRUITS(CONST_CONTAINER):
    UNLOAD = 'unloadRecruit'
    UNLOAD_ALL = 'unloadRecruits'
    CONVERT_RECRUITS = 'convertRecruitsIntoDetachment'
    RETRAIN_WINDOW = 'retrainWindow'
    CHANGE_ROLE_WINDOW = 'changeRoleWindow'
    RETURN = 'returnRecruits'
    SET_BEST = 'setBestRecruits'
    SET_NATIVE_CREW = 'setNativeCrew'


class MODULE(CONST_CONTAINER):
    INFO = 'moduleInfo'
    CANCEL_BUY = 'cancelBuy'
    UNLOAD = 'unload'
    UNLOCK = 'unlock'
    EQUIP = 'equip'
    SELL = 'sell'
    BUY_AND_EQUIP = 'buyAndEquip'


class VEHICLE(CONST_CONTAINER):
    EXCHANGE = 'exchange'
    PERSONAL_EXCHANGE = 'personalTradeExchange'
    INFO = 'vehicleInfo'
    PREVIEW = 'preview'
    STATS = 'showVehicleStatistics'
    UNLOCK = 'unlock'
    SELECT = 'selectVehicle'
    SELL = 'sell'
    BUY = 'buy'
    RESEARCH = 'vehicleResearch'
    RENEW = 'vehicleRentRenew'
    REMOVE = 'vehicleRemove'
    CHECK = 'vehicleCheck'
    UNCHECK = 'vehicleUncheck'
    COMPARE = 'compare'
    BLUEPRINT = 'blueprint'
    NATION_CHANGE = 'nationChange'
    GO_TO_COLLECTION = 'goToCollection'


def _dismissContextMenuItems(options, exceptions=()):
    return [ item for item in options if item['id'] not in exceptions ]


def _replaceLabelMenuItem(options, itemID, label):
    for item in options:
        if item['id'] != itemID:
            continue
        item.update({'label': label})


class _BaseRecruitContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    uiLogger = DynamicGroupLogger()

    def __init__(self, cmProxy, ctx=None, handlers=None, eventNameSuffix=''):
        super(_BaseRecruitContextMenuHandler, self).__init__(cmProxy, ctx, handlers)
        self.__eventNameSuffix = eventNameSuffix

    def _initFlashValues(self, ctx):
        self._recruitID = int(ctx.tankmanID)
        self._vehicle = None
        self._crew = None
        self._recruitIDs = None
        return

    def _clearFlashValues(self):
        self.uiLogger.reset()
        self._recruitID = None
        self._vehicle = None
        self._crew = None
        self._recruitIDs = None
        return

    def _fireEvent(self, eventName, ctx=None):
        self.fireEvent(events.CrewPanelEvent(eventName + self.__eventNameSuffix, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

    def showRetrainWindow(self):
        g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.RETRAIN_CREW_DIALOG)
        self._fireEvent(events.CrewPanelEvent.RETRAIN_RECRUITS, {'recruitID': self._recruitID})

    def openChangeRoleWindow(self):
        g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.RETRAIN_TANKMAN_DIALOG)
        self._fireEvent(events.CrewPanelEvent.OPEN_CHANGE_ROLE, {'recruitID': self._recruitID})

    def unloadRecruit(self):
        self.uiLogger.log(ACTION.UNLOAD_RECRUIT)
        self._fireEvent(events.CrewPanelEvent.UNLOAD_RECRUIT, {'recruitID': self._recruitID})

    def unloadRecruits(self):
        self.uiLogger.log(ACTION.UNLOAD_ALL_RECRUITS)
        self._fireEvent(events.CrewPanelEvent.UNLOAD_RECRUITS)

    def returnRecruits(self):
        self.uiLogger.log(ACTION.RETURN_PREVIOUS_RECRUIT_CONFIGURATION)
        self._fireEvent(events.CrewPanelEvent.RETURN_RECRUITS)

    def setBestRecruits(self):
        self.uiLogger.log(ACTION.SELECT_BEST_RECRUITS)
        self._fireEvent(events.CrewPanelEvent.SET_BEST_RECRUITS, {'isNative': False})

    def setNativeCrew(self):
        self.uiLogger.log(ACTION.SET_NATIVE_CREW)
        self._fireEvent(events.CrewPanelEvent.SET_BEST_RECRUITS, {'isNative': True})

    def convertRecruitsIntoDetachment(self):
        g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.MOBILIZE_CREW_CONFIRMATION)
        self._fireEvent(events.CrewPanelEvent.CONVERT_RECRUITS)

    def _generateOptions(self, ctx=None):
        vehicle = self._vehicle
        recruitIDs = self._recruitIDs
        processStrict = vehicle.isLocked or vehicle.isCrewLocked
        recruitRetrainEnabled = not processStrict and self._isRecruitReadyForRetrain()
        crewRetrainEnabled = not processStrict and self._isRetrainCrewOptionAvailable()
        crewConvertEnabled = not vehicle.isLocked and self._isConvertAvailable()
        return [self._makeItem(RECRUITS.CONVERT_RECRUITS, MENU.contextmenu('convertRecruitsIntoDetachment'), {'enabled': crewConvertEnabled,
          'textColor': CM_HIGHLIGHT_COLOR,
          'disabledTextColor': CM_HIGHLIGHT_COLOR,
          'textAlpha': 1.0 if crewConvertEnabled else 0.5}),
         self._makeSeparator(),
         self._makeItem(RECRUITS.SET_BEST, MENU.contextmenu('setBestCrew'), {'enabled': not processStrict and not validateBestCrewForVehicle(vehicle, recruitIDs, native=False)}),
         self._makeItem(RECRUITS.SET_NATIVE_CREW, MENU.contextmenu('setNativeCrew'), {'enabled': not processStrict and not validateBestCrewForVehicle(vehicle, recruitIDs, native=True)}),
         self._makeItem(RECRUITS.RETURN, MENU.contextmenu('returnCrew'), {'enabled': not processStrict and isReturnCrewOptionAvailable(vehicle, recruitIDs)}),
         self._makeItem(RECRUITS.CHANGE_ROLE_WINDOW, MENU.contextmenu('changeRoleWindow'), {'enabled': recruitRetrainEnabled,
          'textColor': CM_HIGHLIGHT_COLOR,
          'disabledTextColor': CM_HIGHLIGHT_COLOR,
          'textAlpha': 1.0 if recruitRetrainEnabled else 0.5}),
         self._makeItem(RECRUITS.RETRAIN_WINDOW, MENU.contextmenu('retrainWindow'), {'enabled': crewRetrainEnabled,
          'textColor': CM_HIGHLIGHT_COLOR,
          'disabledTextColor': CM_HIGHLIGHT_COLOR,
          'textAlpha': 1.0 if crewRetrainEnabled else 0.5}),
         self._makeItem(RECRUITS.UNLOAD, MENU.contextmenu('tankmanUnload'), {'enabled': not processStrict and self._recruitID}),
         self._makeItem(RECRUITS.UNLOAD_ALL, MENU.contextmenu('unloadCrew'), {'enabled': not processStrict and any(self._crew)})]

    def _isRecruitReadyForRetrain(self):
        vehicle = self._vehicle
        recruit = self.itemsCache.items.getTankman(self._recruitID)
        if not recruit:
            return False
        recruitVehicle = self.itemsCache.items.getVehicle(recruit.vehicleInvID)
        isLocked = recruitVehicle and recruitVehicle.isLocked
        return not isLocked and recruit.vehicleNativeDescr.type.compactDescr != vehicle.intCD

    def _isRetrainCrewOptionAvailable(self):
        vehicle = self._vehicle
        crew = self._crew
        actualRecruits = [ recruit for recruit in crew if recruit is not None ]
        recruitVehs = [ self.itemsCache.items.getVehicle(recruit.vehicleInvID) for recruit in actualRecruits ]
        return any((recruit.vehicleNativeDescr.type.compactDescr != vehicle.intCD for recruit in actualRecruits)) and all((not recruitVehicle.isLocked for recruitVehicle in recruitVehs if recruitVehicle))

    def _isConvertAvailable(self):
        if not self.lobbyContext.getServerSettings().isDetachmentManualConversionEnabled():
            return False
        else:
            conversion = settings_globals.g_conversion
            vehicle = self._vehicle
            crew = self._crew
            recruitDescrs = [ (recruit.descriptor if recruit else None) for recruit in crew ]
            barracksNotEmpty = self._isBarracksNotEmpty()
            validation, _, _ = conversion.validateCrewToConvertIntoDetachment(recruitDescrs, vehicle.compactDescr, barracksNotEmpty)
            return validation

    def _isBarracksNotEmpty(self):
        return False


class RecruitContextMenuHandler(_BaseRecruitContextMenuHandler):

    def __init__(self, cmProxy, ctx=None):
        super(RecruitContextMenuHandler, self).__init__(cmProxy, ctx, {RECRUITS.CONVERT_RECRUITS: 'convertRecruitsIntoDetachment',
         RECRUITS.UNLOAD: 'unloadRecruit',
         RECRUITS.RETRAIN_WINDOW: 'showRetrainWindow',
         RECRUITS.CHANGE_ROLE_WINDOW: 'openChangeRoleWindow',
         RECRUITS.UNLOAD_ALL: 'unloadRecruits',
         RECRUITS.RETURN: 'returnRecruits',
         RECRUITS.SET_BEST: 'setBestRecruits',
         RECRUITS.SET_NATIVE_CREW: 'setNativeCrew'})
        self.uiLogger.setGroup(GROUP.RECRUIT_PANEL_CONTEXT_MENU)

    def _initFlashValues(self, ctx):
        super(RecruitContextMenuHandler, self)._initFlashValues(ctx)
        self._vehicle = g_currentVehicle.item
        self._crew = [ recruit for _, recruit in self._vehicle.crew ]
        self._recruitIDs = [ (recruit.invID if recruit is not None else None) for recruit in self._crew ]
        return

    def _isBarracksNotEmpty(self):
        itemsCache = self.itemsCache
        criteria = REQ_CRITERIA.EMPTY | ~REQ_CRITERIA.TANKMAN.IN_TANK | REQ_CRITERIA.NATIONS([self._vehicle.nationID]) | ~REQ_CRITERIA.TANKMAN.DISMISSED
        allTankmen = itemsCache.items.getTankmen(criteria)
        return any(itemsCache.items.removeUnsuitableTankmen(allTankmen.values(), ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE))


class MobilizationRecruitContextMenuHandler(_BaseRecruitContextMenuHandler):
    itemsCache = dependency.descriptor(IItemsCache)
    _INVALID_TANKMAN_ID = -1
    _EXCLUDE = (RECRUITS.CONVERT_RECRUITS, SEPARATOR_ID)

    def __init__(self, cmProxy, ctx=None):
        super(MobilizationRecruitContextMenuHandler, self).__init__(cmProxy, ctx, {RECRUITS.CONVERT_RECRUITS: 'convertRecruitsIntoDetachment',
         RECRUITS.SET_BEST: 'setBestRecruits',
         RECRUITS.SET_NATIVE_CREW: 'setNativeCrew',
         RECRUITS.RETURN: 'returnRecruits',
         RECRUITS.CHANGE_ROLE_WINDOW: 'openChangeRoleWindow',
         RECRUITS.RETRAIN_WINDOW: 'showRetrainWindow',
         RECRUITS.UNLOAD: 'unloadRecruit',
         RECRUITS.UNLOAD_ALL: 'unloadRecruits'}, eventNameSuffix='_mobilization')
        self.uiLogger.setGroup(GROUP.RECRUIT_MOBILIZATION_CONTEXT_MENU)

    def _generateOptions(self, ctx=None):
        options = super(MobilizationRecruitContextMenuHandler, self)._generateOptions(ctx)
        options = _dismissContextMenuItems(options, self._EXCLUDE)
        _replaceLabelMenuItem(options, RECRUITS.UNLOAD, MENU.contextmenu('tankmanUnloadFromSlot'))
        return options

    def _initFlashValues(self, ctx):
        super(MobilizationRecruitContextMenuHandler, self)._initFlashValues(ctx)
        self._recruitIDs = [ (int(recruitID) if int(recruitID) != self._INVALID_TANKMAN_ID else None) for recruitID in ctx.tankmanList ]
        self._vehicle = self.itemsCache.items.getItemByCD(int(ctx.vehicleID))
        self._crew = [ self.itemsCache.items.getTankman(recruitID) for recruitID in self._recruitIDs ]
        return

    def _isBarracksNotEmpty(self):
        return isBarracksNotEmpty(self._vehicle.nationID, [ recruit.invID for recruit in self._crew if recruit ], itemsCache=self.itemsCache)


class TechnicalMaintenanceCMHandler(AbstractContextMenuHandler, EventSystemEntity):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, cmProxy, ctx=None):
        super(TechnicalMaintenanceCMHandler, self).__init__(cmProxy, ctx, {MODULE.INFO: 'showModuleInfo',
         MODULE.CANCEL_BUY: 'resetSlot',
         MODULE.UNLOAD: 'resetSlot'})

    def showModuleInfo(self):
        if self._equipmentCD is not None and g_currentVehicle.isPresent():
            shared_events.showModuleInfo(self._equipmentCD, g_currentVehicle.item.descriptor)
        return

    def resetSlot(self):
        self.fireEvent(events.TechnicalMaintenanceEvent(events.TechnicalMaintenanceEvent.RESET_EQUIPMENT, ctx={'eqCD': self._equipmentCD}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _initFlashValues(self, ctx):
        self._equipmentCD = ctx.equipmentCD
        self._isCanceled = bool(ctx.isCanceled)

    def _clearFlashValues(self):
        self._equipmentCD = None
        self._isCanceled = None
        return

    def _generateOptions(self, ctx=None):
        options = [self._makeItem(MODULE.INFO, MENU.contextmenu(MODULE.INFO))]
        equipment = self.itemsCache.items.getItemByCD(int(self._equipmentCD))
        if equipment is not None and equipment.isBuiltIn:
            return options
        else:
            if self._isCanceled:
                options.append(self._makeItem(MODULE.CANCEL_BUY, MENU.contextmenu(MODULE.CANCEL_BUY)))
            else:
                options.append(self._makeItem(MODULE.UNLOAD, MENU.contextmenu(MODULE.UNLOAD)))
            return options


class SimpleVehicleCMHandler(AbstractContextMenuHandler, EventSystemEntity):
    itemsCache = dependency.descriptor(IItemsCache)

    def getVehCD(self):
        raise NotImplementedError

    def getVehInvID(self):
        raise NotImplementedError

    def showVehicleInfo(self):
        shared_events.showVehicleInfo(self.getVehCD())

    def showVehicleStats(self):
        shared_events.showVehicleStats(self.getVehCD())

    def sellVehicle(self):
        vehicle = self.itemsCache.items.getVehicle(self.getVehInvID())
        if vehicle:
            shared_events.showVehicleSellDialog(self.getVehInvID())

    def buyVehicle(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, self.getVehCD(), False, VehicleBuyActionTypes.BUY)

    def _generateOptions(self, ctx=None):
        return []


class VehicleContextMenuHandler(SimpleVehicleCMHandler):
    _comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    _epicController = dependency.descriptor(IEpicBattleMetaGameController)
    _tradeInController = dependency.descriptor(ITradeInController)
    _personalTradeInController = dependency.descriptor(IPersonalTradeInController)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, cmProxy, ctx=None):
        super(VehicleContextMenuHandler, self).__init__(cmProxy, ctx, {VEHICLE.EXCHANGE: 'showVehicleExchange',
         VEHICLE.PERSONAL_EXCHANGE: 'showVehiclePersonalExchange',
         VEHICLE.INFO: 'showVehicleInfo',
         VEHICLE.SELL: 'sellVehicle',
         VEHICLE.RESEARCH: 'toResearch',
         VEHICLE.CHECK: 'checkFavoriteVehicle',
         VEHICLE.UNCHECK: 'uncheckFavoriteVehicle',
         VEHICLE.STATS: 'showVehicleStats',
         VEHICLE.BUY: 'buyVehicle',
         VEHICLE.COMPARE: 'compareVehicle',
         VEHICLE.RENEW: 'renewRentVehicle',
         VEHICLE.NATION_CHANGE: 'changeVehicleNation',
         VEHICLE.GO_TO_COLLECTION: 'goToCollection'})

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def getVehCD(self):
        return self.vehCD

    def getVehInvID(self):
        return self.vehInvID

    def toResearch(self):
        vehicle = self.itemsCache.items.getVehicle(self.getVehInvID())
        if vehicle is not None:
            shared_events.showResearchView(vehicle.intCD)
        else:
            _logger.error('Can not go to Research because id for current vehicle is None')
        return

    def showVehicleExchange(self):
        self._tradeInController.setActiveTradeOffVehicleCD(self.vehCD)
        showShop(getTradeInVehiclesUrl(), isClientCloseControl=True)

    def showVehiclePersonalExchange(self):
        self._personalTradeInController.setActiveTradeInSaleVehicleCD(self.vehCD)
        showShop(getPersonalTradeInVehiclesUrl(), isClientCloseControl=True)

    def checkFavoriteVehicle(self):
        self.__favoriteVehicle(True)

    def uncheckFavoriteVehicle(self):
        self.__favoriteVehicle(False)

    def compareVehicle(self):
        self._comparisonBasket.addVehicle(self.vehCD)

    def renewRentVehicle(self):
        vehicle = self.itemsCache.items.getVehicle(self.vehInvID)
        rentRenewCycle = vehicle.rentInfo.getAvailableRentRenewCycleInfoForSeason(GameSeasonType.EPIC)
        showVehicleRentRenewDialog(self.vehCD, RentType.SEASON_CYCLE_RENT, rentRenewCycle.ID, GameSeasonType.EPIC)

    def changeVehicleNation(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.CHANGE_NATION, self.vehCD)

    def goToCollection(self):
        vehicle = self.itemsCache.items.getVehicle(self.vehInvID)
        shared_events.showCollectibleVehicles(vehicle.nationID)

    def _initFlashValues(self, ctx):
        self.vehInvID = int(ctx.inventoryId)
        vehicle = self.itemsCache.items.getVehicle(self.vehInvID)
        self.vehCD = vehicle.intCD if vehicle is not None else None
        return

    def _clearFlashValues(self):
        self.vehInvID = None
        self.vehCD = None
        return

    def _generateOptions(self, ctx=None):
        options = []
        vehicle = self.itemsCache.items.getVehicle(self.getVehInvID())
        vehicleWasInBattle = False
        accDossier = self.itemsCache.items.getAccountDossier(None)
        buyVehicleCDs = self._personalTradeInController.getBuyVehicleCDs()
        if vehicle is None:
            return options
        else:
            isEventVehicle = vehicle.isOnlyForEventBattles
            if accDossier:
                wasInBattleSet = set(accDossier.getTotalStats().getVehicles().keys())
                wasInBattleSet.update(accDossier.getGlobalMapStats().getVehicles().keys())
                if vehicle.intCD in wasInBattleSet:
                    vehicleWasInBattle = True
            if vehicle is not None:
                if vehicle.canTradeOff:
                    options.append(self._makeItem(VEHICLE.EXCHANGE, MENU.contextmenu(VEHICLE.EXCHANGE), {'enabled': vehicle.isReadyToTradeOff,
                     'textColor': CM_BUY_COLOR}))
                if vehicle.canPersonalTradeInSale and buyVehicleCDs:
                    options.append(self._makeItem(VEHICLE.PERSONAL_EXCHANGE, MENU.contextmenu(VEHICLE.PERSONAL_EXCHANGE), {'enabled': vehicle.isReadyPersonalTradeInSale,
                     'textColor': CM_BUY_COLOR}))
                options.extend([self._makeItem(VEHICLE.INFO, MENU.contextmenu(VEHICLE.INFO)), self._makeItem(VEHICLE.STATS, MENU.contextmenu(VEHICLE.STATS), {'enabled': vehicleWasInBattle})])
                if not vehicleWasInBattle:
                    options.append(self._makeSeparator())
                self._manageVehCompareOptions(options, vehicle)
                if self.prbDispatcher is not None:
                    isNavigationEnabled = not self.prbDispatcher.getFunctionalState().isNavigationDisabled()
                else:
                    isNavigationEnabled = True
                if not vehicle.isOnlyForEpicBattles:
                    options.append(self._makeItem(VEHICLE.RESEARCH, MENU.contextmenu(VEHICLE.RESEARCH), {'enabled': isNavigationEnabled}))
                if vehicle.isCollectible:
                    options.append(self._makeItem(VEHICLE.GO_TO_COLLECTION, MENU.contextmenu(VEHICLE.GO_TO_COLLECTION), {'enabled': self._lobbyContext.getServerSettings().isCollectorVehicleEnabled()}))
                if vehicle.hasNationGroup:
                    isNew = not AccountSettings.getSettings(NATION_CHANGE_VIEWED)
                    options.append(self._makeItem(VEHICLE.NATION_CHANGE, MENU.CONTEXTMENU_NATIONCHANGE, {'enabled': vehicle.isNationChangeAvailable,
                     'isNew': isNew}))
                if vehicle.isRented:
                    if not vehicle.isPremiumIGR:
                        items = self.itemsCache.items
                        enabled = vehicle.mayObtainWithMoneyExchange(items.stats.money, items.shop.exchangeRate)
                        label = MENU.CONTEXTMENU_RESTORE if vehicle.isRestoreAvailable() else MENU.CONTEXTMENU_BUY
                        options.append(self._makeItem(VEHICLE.BUY, label, {'enabled': enabled}))
                    options.append(self._makeItem(VEHICLE.SELL, MENU.contextmenu(VEHICLE.REMOVE), {'enabled': vehicle.canSell and vehicle.rentalIsOver}))
                    options.append(self._makeItem(VEHICLE.RENEW, MENU.contextmenu(VEHICLE.RENEW), {'enabled': vehicle.isOnlyForEpicBattles and vehicle.rentInfo.canCycleRentRenewForSeason(GameSeasonType.EPIC)}))
                else:
                    options.append(self._makeItem(VEHICLE.SELL, MENU.contextmenu(VEHICLE.SELL), {'enabled': vehicle.canSell and not isEventVehicle}))
                if vehicle.isFavorite:
                    options.append(self._makeItem(VEHICLE.UNCHECK, MENU.contextmenu(VEHICLE.UNCHECK)))
                else:
                    options.append(self._makeItem(VEHICLE.CHECK, MENU.contextmenu(VEHICLE.CHECK), {'enabled': not isEventVehicle}))
            return options

    def _manageVehCompareOptions(self, options, vehicle):
        if self._comparisonBasket.isEnabled():
            options.append(self._makeItem(VEHICLE.COMPARE, MENU.contextmenu(VEHICLE.COMPARE), {'enabled': self._comparisonBasket.isReadyToAdd(vehicle)}))

    @process
    def __favoriteVehicle(self, isFavorite):
        vehicle = self.itemsCache.items.getVehicle(self.getVehInvID())
        if vehicle is not None:
            result = yield VehicleFavoriteProcessor(vehicle, bool(isFavorite)).request()
            if not result.success:
                _logger.error('Cannot set selected vehicle as favorite due to following error: %s', result.userMsg)
        return
