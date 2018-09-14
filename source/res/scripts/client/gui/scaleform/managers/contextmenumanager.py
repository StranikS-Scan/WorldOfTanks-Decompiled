# Embedded file name: scripts/client/gui/Scaleform/managers/ContextMenuManager.py
import weakref
import BigWorld
import constants
from adisp import process
from abc import ABCMeta, abstractmethod
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_ERROR
from account_helpers import isMoneyTransfer
from gui import DialogsInterface, game_control, SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.prb_control.context import unit_ctx, prb_ctx, SendInvitesCtx
from gui.prb_control.prb_helpers import prbDispatcherProperty, unitFunctionalProperty
from gui.shared.events import ChannelCarouselEvent
from gui.shared.gui_items.processors.tankman import TankmanUnload
from gui.shared.gui_items.processors.vehicle import VehicleFavoriteProcessor
from gui.shared.utils import CONST_CONTAINER, functions, decorators
from gui.shared.utils.functions import getViewName
from helpers import i18n
from gui.shared import g_itemsCache, events, EVENT_BUS_SCOPE
from gui.shared import event_dispatcher as shared_events
from gui.Scaleform.framework.entities.abstract.ContextMenuManagerMeta import ContextMenuManagerMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.daapi.view.lobby.fortifications.ConfirmOrderDialogMeta import BuyOrderDialogMeta
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.storage import storage_getter
_SEPARATOR_ID = 'separate'

class AbstractContextMenuHandler(object):
    __metaclass__ = ABCMeta

    def __init__(self, cmProxy, itemId, ctx, handlers = None):
        super(AbstractContextMenuHandler, self).__init__()
        self._itemId = itemId
        self._ctx = ctx
        self.__cmProxy = weakref.proxy(cmProxy)
        self.__handlers = handlers or {}

    def fini(self):
        self.__handlers = None
        self.__cmProxy = None
        return

    @abstractmethod
    def getOptions(self):
        raise NotImplementedError

    def onOptionSelect(self, optionId):
        if optionId in self.__handlers:
            return getattr(self, self.__handlers[optionId])()
        LOG_WARNING('Unknown context menu option', self, self.__cmProxy, optionId)

    def _dispatchChanges(self, options):
        if self.__cmProxy is not None:
            self.__cmProxy._onOptionsChanged(options)
        return

    @classmethod
    def _constructOptionVO(cls, optId, optLabel = None, optInitData = None, optSubMenu = None):
        return {'id': optId,
         'label': optLabel,
         'initData': optInitData,
         'submenu': optSubMenu}


class CrewContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):

    class OPTIONS(CONST_CONTAINER):
        PERSONAL_CASE = 'personalCase'
        UNLOAD = 'tankmanUnload'

    def __init__(self, cmProxy, itemId, ctx):
        super(CrewContextMenuHandler, self).__init__(cmProxy, int(itemId), ctx, {self.OPTIONS.PERSONAL_CASE: 'showPersonalCase',
         self.OPTIONS.UNLOAD: 'unloadTankman'})

    def getOptions(self):
        return self.generateOptions()

    def generateOptions(self):
        options = [self._constructOptionVO(self.OPTIONS.PERSONAL_CASE, MENU.contextmenu('personalCase')), self._constructOptionVO(_SEPARATOR_ID), self._constructOptionVO(self.OPTIONS.UNLOAD, MENU.contextmenu('tankmanUnload'))]
        return options

    def showPersonalCase(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.PERSONAL_CASE, functions.getViewName(VIEW_ALIAS.PERSONAL_CASE, self._itemId), {'tankmanID': int(self._itemId),
         'page': 0}))

    @decorators.process('unloading')
    def unloadTankman(self):
        tankman = g_itemsCache.items.getTankman(self._itemId)
        result = yield TankmanUnload(g_currentVehicle.item, tankman.vehicleSlotIdx).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)


class ChannelListContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):

    class OPTIONS(CONST_CONTAINER):
        CLOSE_CURRENT = 'clC'
        MINIMIZE_ALL = 'mA'
        CLOSE_ALL_EXCEPT_CURRENT = 'clAdE'

    def __init__(self, cmProxy, itemId, ctx):
        super(ChannelListContextMenuHandler, self).__init__(cmProxy, int(itemId), ctx, {self.OPTIONS.MINIMIZE_ALL: 'minimizeAll',
         self.OPTIONS.CLOSE_CURRENT: 'closeCurrent',
         self.OPTIONS.CLOSE_ALL_EXCEPT_CURRENT: 'closeAllExceptCurrent'})

    def closeCurrent(self):
        self.fireEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.CLOSE_BUTTON_CLICK, self._itemId), scope=EVENT_BUS_SCOPE.LOBBY)

    def minimizeAll(self):
        self.fireEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.MINIMIZE_ALL_CHANNELS, None), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def closeAllExceptCurrent(self):
        self.fireEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.CLOSE_ALL_EXCEPT_CURRENT, self._itemId), scope=EVENT_BUS_SCOPE.LOBBY)

    def getOptions(self):
        self.currentOptions = self.generateOptions()
        return self.currentOptions

    def generateOptions(self):
        options = [self._constructOptionVO(self.OPTIONS.MINIMIZE_ALL, MENU.contextmenu('messenger/minimizeAll')),
         self._constructOptionVO(_SEPARATOR_ID),
         self._constructOptionVO(self.OPTIONS.CLOSE_CURRENT, MENU.contextmenu('messenger/closeCurrent'), {'enabled': self._ctx.canCloseCurrent}),
         self._constructOptionVO(_SEPARATOR_ID),
         self._constructOptionVO(self.OPTIONS.CLOSE_ALL_EXCEPT_CURRENT, MENU.contextmenu('messenger/closeAllExceptCurrent'))]
        return options


class VehicleContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):

    class VEHICLE(CONST_CONTAINER):
        INFO = 'vehicleInfo'
        SELL = 'vehicleSell'
        RESEARCH = 'vehicleResearch'
        CHECK = 'vehicleCheck'
        UNCHECK = 'vehicleUncheck'
        STATISTIC = 'showVehicleStatistics'
        BUY = 'vehicleBuy'
        REMOVE = 'vehicleRemove'

    def __init__(self, cmProxy, invID, ctx):
        super(VehicleContextMenuHandler, self).__init__(cmProxy, int(invID), ctx, {self.VEHICLE.INFO: 'showVehicleInfo',
         self.VEHICLE.SELL: 'vehicleSell',
         self.VEHICLE.RESEARCH: 'toResearch',
         self.VEHICLE.CHECK: 'checkFavoriteVehicle',
         self.VEHICLE.UNCHECK: 'uncheckFavoriteVehicle',
         self.VEHICLE.STATISTIC: 'showVehicleStats',
         self.VEHICLE.BUY: 'vehicleBuy',
         self.VEHICLE.REMOVE: 'vehicleSell'})

    def showVehicleInfo(self):
        vehicle = g_itemsCache.items.getVehicle(self._itemId)
        if vehicle is not None:
            shared_events.showVehicleInfo(vehicle.intCD)
        else:
            LOG_WARNING('Truing to show unknown vehicle info window', self._itemId)
        return

    def vehicleSell(self):
        if self._itemId is not None:
            shared_events.showVehicleSellDialog(self._itemId)
        return

    def vehicleBuy(self):
        item = g_itemsCache.items.getVehicle(self._itemId)
        if item is not None:
            shared_events.showVehicleBuyDialog(item)
        return

    def showVehicleStats(self):
        vehicle = g_itemsCache.items.getVehicle(self._itemId)
        if vehicle is not None:
            shared_events.showVehicleStats(vehicle.intCD)
        return

    def toResearch(self):
        vehicle = g_itemsCache.items.getVehicle(self._itemId)
        if vehicle is not None:
            shared_events.showResearchView(vehicle.intCD)
        else:
            LOG_ERROR("Can't go to Research because id for current vehicle is None")
        return

    def checkFavoriteVehicle(self):
        self.__favoriteVehicle(True)

    def uncheckFavoriteVehicle(self):
        self.__favoriteVehicle(False)

    @process
    def __favoriteVehicle(self, isFavorite):
        vehicle = g_itemsCache.items.getVehicle(self._itemId)
        if vehicle is not None:
            result = yield VehicleFavoriteProcessor(vehicle, bool(isFavorite)).request()
            if not result.success:
                LOG_ERROR('Cannot set selected vehicle as favorite due to following error: ', result.userMsg)
        return

    def getOptions(self):
        self.currentOptions = self.generateOptions()
        return self.currentOptions

    def generateOptions(self):
        options = []
        vehicle = g_itemsCache.items.getVehicle(self._itemId)
        vehicleWasInBattle = False
        accDossier = g_itemsCache.items.getAccountDossier(None)
        if accDossier:
            wasInBattleSet = set(accDossier.getTotalStats().getVehicles().keys())
            if vehicle.intCD in wasInBattleSet:
                vehicleWasInBattle = True
        if vehicle is not None:
            options.append(self._constructOptionVO(self.VEHICLE.INFO, MENU.contextmenu(self.VEHICLE.INFO)))
            options.append(self._constructOptionVO(self.VEHICLE.STATISTIC, MENU.contextmenu(self.VEHICLE.STATISTIC), {'enabled': vehicleWasInBattle}))
            options.append(self._constructOptionVO(_SEPARATOR_ID))
            if vehicle.isRented:
                if not vehicle.isPremiumIGR:
                    money = g_itemsCache.items.stats.money
                    canBuyOrRent, _ = vehicle.mayRentOrBuy(money)
                    options.append(self._constructOptionVO(self.VEHICLE.BUY, MENU.contextmenu(self.VEHICLE.BUY), {'enabled': canBuyOrRent}))
                options.append(self._constructOptionVO(self.VEHICLE.REMOVE, MENU.contextmenu(self.VEHICLE.REMOVE), {'enabled': vehicle.canSell and vehicle.rentalIsOver}))
            else:
                options.append(self._constructOptionVO(self.VEHICLE.SELL, MENU.contextmenu(self.VEHICLE.SELL), {'enabled': vehicle.canSell}))
            options.append(self._constructOptionVO(_SEPARATOR_ID))
            options.append(self._constructOptionVO(self.VEHICLE.RESEARCH, MENU.contextmenu(self.VEHICLE.RESEARCH)))
            if vehicle.isFavorite:
                options.append(self._constructOptionVO(self.VEHICLE.UNCHECK, MENU.contextmenu(self.VEHICLE.UNCHECK)))
            else:
                options.append(self._constructOptionVO(self.VEHICLE.CHECK, MENU.contextmenu(self.VEHICLE.CHECK)))
        return options


class CONTEXT_MENU_HANDLER_TYPE(object):
    CREW = 'crew'
    CHANNEL_LIST = 'channelList'
    VEHICLE = 'vehicle'


class ContextMenuManager(ContextMenuManagerMeta):
    _HANDLERS_MAP = {CONTEXT_MENU_HANDLER_TYPE.CREW: CrewContextMenuHandler,
     CONTEXT_MENU_HANDLER_TYPE.CHANNEL_LIST: ChannelListContextMenuHandler,
     CONTEXT_MENU_HANDLER_TYPE.VEHICLE: VehicleContextMenuHandler}

    def __init__(self):
        super(ContextMenuManager, self).__init__()
        self.__currentHandler = None
        return

    def getCurrentHandler(self):
        return self.__currentHandler

    def requestOptions(self, itemId, handlerType, ctx):
        self.__currentHandler = self._getHandler(itemId, handlerType, ctx)
        if self.__currentHandler is not None:
            self._sendOptionsToFlash(self.__currentHandler.getOptions())
        return

    def onOptionSelect(self, optionId):
        if self.__currentHandler is not None:
            self.__currentHandler.onOptionSelect(optionId)
        return

    def onHide(self):
        self.__disposeHandler()

    def _dispose(self):
        self.__disposeHandler()
        super(ContextMenuManager, self)._dispose()

    def _getHandler(self, itemId, handlerType, ctx):
        if handlerType in self._HANDLERS_MAP:
            return self._HANDLERS_MAP[handlerType](self, itemId, ctx)
        else:
            LOG_WARNING('Unknown context menu handler type', itemId, handlerType, ctx)
            return None

    def _sendOptionsToFlash(self, options):
        self.as_setOptionsS({'options': options})

    def _onOptionsChanged(self, options):
        self._sendOptionsToFlash(options)

    def __disposeHandler(self):
        if self.__currentHandler is not None:
            self.__currentHandler.fini()
            self.__currentHandler = None
        return

    DENUNCIATIONS = {'bot': constants.DENUNCIATION.BOT,
     'flood': constants.DENUNCIATION.FLOOD,
     'offend': constants.DENUNCIATION.OFFEND,
     'notFairPlay': constants.DENUNCIATION.NOT_FAIR_PLAY,
     'forbiddenNick': constants.DENUNCIATION.FORBIDDEN_NICK,
     'swindle': constants.DENUNCIATION.SWINDLE,
     'blackmail': constants.DENUNCIATION.BLACKMAIL}

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @unitFunctionalProperty
    def unitFunctional(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    @process
    def showUserInfo(self, uid, userName):
        userDossier, _, isHidden = yield g_itemsCache.items.requestUserDossier(int(uid))
        if userDossier is None:
            if isHidden:
                key = 'messenger/userInfoHidden'
            else:
                key = 'messenger/userInfoNotAvailable'
            DialogsInterface.showI18nInfoDialog(key, lambda result: None, I18nInfoDialogMeta(key, messageCtx={'userName': userName}))
        else:
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.PROFILE_WINDOW, getViewName(VIEW_ALIAS.PROFILE_WINDOW, uid), {'userName': userName,
             'databaseID': int(uid)}), EVENT_BUS_SCOPE.LOBBY)
        return

    def showMoneyTransfer(self, uid, userName):
        LOG_DEBUG('Money transfer window is not implemented yet', uid, userName)

    def createPrivateChannel(self, uid, userName):
        self.proto.users.createPrivateChannel(uid, userName)

    def addFriend(self, uid, userName):
        self.proto.users.addFriend(uid, userName)

    def removeFriend(self, uid):
        self.proto.users.removeFriend(uid)

    def setMuted(self, uid, userName):
        self.proto.users.setMuted(uid, userName)

    def unsetMuted(self, uid):
        self.proto.users.unsetMuted(uid)

    def setIgnored(self, uid, userName):
        self.proto.users.addIgnored(uid, userName)

    def unsetIgnored(self, uid):
        self.proto.users.removeIgnored(uid)

    def appeal(self, uid, userName, topic):
        topicID = self.DENUNCIATIONS.get(topic)
        if topicID is not None:
            BigWorld.player().makeDenunciation(uid, topicID, constants.VIOLATOR_KIND.UNKNOWN)
            topicStr = i18n.makeString(MENU.denunciation(topicID))
            sysMsg = i18n.makeString(SYSTEM_MESSAGES.DENUNCIATION_SUCCESS) % {'name': userName,
             'topic': topicStr}
            SystemMessages.pushMessage(sysMsg, type=SystemMessages.SM_TYPE.Information)
        return

    def kickPlayerFromPrebattle(self, accID):
        self._kickPlayerFromPrebattle(accID)

    @process
    def _kickPlayerFromPrebattle(self, databaseID):
        yield self.prbDispatcher.sendPrbRequest(prb_ctx.KickPlayerCtx(databaseID, 'prebattle/kick'))

    def kickPlayerFromUnit(self, databaseID):
        self._kickPlayerFromUnit(databaseID)

    @process
    def _kickPlayerFromUnit(self, databaseID):
        yield self.prbDispatcher.sendUnitRequest(unit_ctx.KickPlayerCtx(databaseID, 'prebattle/kick'))

    def giveLeadership(self, databaseID):
        self._giveLeadership(databaseID)

    @process
    def _giveLeadership(self, databaseID):
        yield self.prbDispatcher.sendUnitRequest(unit_ctx.GiveLeadershipCtx(databaseID, 'prebattle/giveLeadership'))

    def canGiveLeadership(self, databaseID):
        return not self.unitFunctional.getPlayerInfo(dbID=databaseID).isLegionary()

    @process
    def createSquad(self, databaseID):
        user = self.proto.users.usersStorage.getUser(databaseID)
        result = yield self.prbDispatcher.create(prb_ctx.SquadSettingsCtx(waitingID='prebattle/create', accountsToInvite=[databaseID], isForced=True))
        if result:
            self.__showInviteMessage(user)

    def canInvite(self, databaseID):
        return self.prbDispatcher.getFunctionalCollection().canSendInvite(databaseID)

    def invite(self, databaseID, data):
        user = self.proto.users.usersStorage.getUser(databaseID)
        for func in self.prbDispatcher.getFunctionalCollection().getIterator():
            if func.getPermissions().canSendInvite():
                func.request(SendInvitesCtx([databaseID], ''))
                self.__showInviteMessage(user)
                break

    def copyToClipboard(self, name):
        BigWorld.wg_copyToClipboard(unicode(name, 'utf-8', errors='ignore'))

    def _getUserInfo(self, uid, userName):
        user = self.usersStorage.getUser(uid)
        roamingCtrl = game_control.g_instance.roaming
        result = {'canAddToFriend': roamingCtrl.isSameRealm(uid),
         'canAddToIgnore': True,
         'canDoDenunciations': True,
         'canCreateChannel': not roamingCtrl.isInRoaming() and not roamingCtrl.isPlayerInRoaming(uid)}
        if user is not None:
            result.update({'dbID': uid,
             'isFriend': user.isFriend(),
             'isIgnored': user.isIgnored(),
             'isMuted': user.isMuted(),
             'displayName': user.getFullName()})
        else:
            result.update({'dbID': uid,
             'isFriend': False,
             'isIgnored': False,
             'isMuted': False,
             'displayName': userName})
        return result

    def _getDenunciations(self):
        return g_itemsCache.items.stats.denunciationsLeft

    def _isMoneyTransfer(self):
        return isMoneyTransfer(g_itemsCache.items.stats.attributes)

    def fortDirection(self):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_ALIAS), EVENT_BUS_SCOPE.LOBBY)

    def fortAssignPlayers(self, value):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_ALIAS, ctx={'data': value}), scope=EVENT_BUS_SCOPE.LOBBY)

    def fortModernization(self, value):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_ALIAS, ctx={'data': value}), scope=EVENT_BUS_SCOPE.LOBBY)

    def fortDestroy(self, value):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW, ctx={'data': value}), scope=EVENT_BUS_SCOPE.LOBBY)

    def fortPrepareOrder(self, value):
        from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
        currentOrderID = FortViewHelper.fortCtrl.getFort().getBuildingOrder(FortViewHelper.UI_BUILDINGS_BIND.index(value))
        DialogsInterface.showDialog(BuyOrderDialogMeta(FortViewHelper.UI_ORDERS_BIND[currentOrderID]), None)
        return

    @classmethod
    def __showInviteMessage(cls, user):
        if user:
            SystemMessages.pushI18nMessage('#system_messages:prebattle/invites/sendInvite/name', type=SystemMessages.SM_TYPE.Information, name=user.getFullName())
        else:
            SystemMessages.pushI18nMessage('#system_messages:prebattle/invites/sendInvite', type=SystemMessages.SM_TYPE.Information)
