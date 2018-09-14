# Embedded file name: scripts/client/gui/Scaleform/managers/ContextMenuManager.py
import BigWorld
from adisp import process
import constants
from debug_utils import LOG_ERROR, LOG_DEBUG
from account_helpers import isMoneyTransfer
from gui import DialogsInterface, game_control
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.prb_control.context import unit_ctx, prb_ctx, SendInvitesCtx
from gui.prb_control.prb_helpers import prbDispatcherProperty, unitFunctionalProperty
from helpers import i18n
from gui import SystemMessages
from gui.shared import g_itemsCache
from gui.Scaleform.framework.entities.abstract.ContextMenuManagerMeta import ContextMenuManagerMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.daapi.view.lobby.fortifications.ConfirmOrderDialogMeta import BuyOrderDialogMeta
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.storage import storage_getter
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.gui_items.processors.vehicle import VehicleFavoriteProcessor

class ContextMenuManager(ContextMenuManagerMeta):
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
            self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_PROFILE_WINDOW, {'userName': userName,
             'databaseID': int(uid)}), EVENT_BUS_SCOPE.LOBBY)
        return

    def getContextMenuVehicleData(self, vehInvID):
        vehicle = g_itemsCache.items.getVehicle(int(vehInvID))
        if vehicle is not None:
            canBuyOrRent = False
            if vehicle.isRented:
                money = g_itemsCache.items.stats.money
                canRentResult, rentErrorStr = vehicle.mayRent(money)
                canBuyResult, buyErrorStr = vehicle.mayPurchase(money)
                canBuyOrRent = canRentResult or canBuyResult
            vehicleWasInBattle = False
            accDossier = g_itemsCache.items.getAccountDossier(None)
            if accDossier:
                wasInBattleSet = set(accDossier.getTotalStats().getVehicles().keys())
                if vehicle.intCD in wasInBattleSet:
                    vehicleWasInBattle = True
            return {'inventoryId': vehicle.invID,
             'compactDescr': vehicle.intCD,
             'favorite': vehicle.isFavorite,
             'canSell': vehicle.canSell,
             'wasInBattle': vehicleWasInBattle,
             'isRented': vehicle.isRented,
             'rentalIsOver': vehicle.rentalIsOver,
             'canBuyOrRent': canBuyOrRent}
        else:
            return

    def vehicleBuy(self, vehInvID):
        item = g_itemsCache.items.getVehicle(int(vehInvID))
        if item is not None:
            self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_VEHICLE_BUY_WINDOW, {'nationID': item.nationID,
             'itemID': item.innationID}))
        return

    def showVehicleInfo(self, vehInvID):
        vehicle = g_itemsCache.items.getVehicle(int(vehInvID))
        if vehicle is not None:
            self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_VEHICLE_INFO_WINDOW, {'vehicleCompactDescr': vehicle.intCD}))
        return

    def toResearch(self, intCD):
        if intCD is not None:
            Event = events.LoadEvent
            exitEvent = Event(Event.LOAD_HANGAR)
            loadEvent = Event(Event.LOAD_RESEARCH, ctx={'rootCD': intCD,
             'exit': exitEvent})
            self.fireEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            LOG_ERROR("Can't go to Research because id for current vehicle is None")
        return

    def vehicleSell(self, vehInvID):
        self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_VEHICLE_SELL_DIALOG, {'vehInvID': int(vehInvID)}))

    def showVehicleStats(self, intCD):
        self.fireEvent(events.LoadEvent(events.LoadEvent.LOAD_PROFILE, {'itemCD': intCD}), scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def favoriteVehicle(self, vehInvID, isFavorite):
        vehicle = g_itemsCache.items.getVehicle(int(vehInvID))
        if vehicle is not None:
            result = yield VehicleFavoriteProcessor(vehicle, bool(isFavorite)).request()
            if not result.success:
                LOG_ERROR('Cannot set selected vehicle as favorite due to following error: ', result.userMsg)
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
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_CREATE_DIRECTION_WINDOW_EVENT), EVENT_BUS_SCOPE.LOBBY)

    def fortAssignPlayers(self, value):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_FIXED_PLAYERS_WINDOW_EVENT, ctx={'data': value}), scope=EVENT_BUS_SCOPE.LOBBY)

    def fortModernization(self, value):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_MODERNIZATION_WINDOW_EVENT, ctx={'data': value}), scope=EVENT_BUS_SCOPE.LOBBY)

    def fortDestroy(self, value):
        self.fireEvent(events.ShowWindowEvent(FORTIFICATION_ALIASES.FORT_DEMOUNT_BUILDING_WINDOW_EVENT, ctx={'data': value}), scope=EVENT_BUS_SCOPE.LOBBY)

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
