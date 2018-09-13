# Embedded file name: scripts/client/gui/Scaleform/managers/ContextMenuManager.py
import BigWorld
from adisp import process
import constants
from debug_utils import LOG_DEBUG
from account_helpers import isMoneyTransfer
from gui import DialogsInterface, game_control
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.prb_control.context import unit_ctx, prb_ctx
from gui.prb_control.prb_helpers import prbDispatcherProperty
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

    def copyToClipboard(self, name):
        name = unicode(name, 'utf-8', errors='ignore')
        BigWorld.wg_copyToClipboard(name)

    def _getUserInfo(self, uid, userName):
        user = self.usersStorage.getUser(uid)
        roamingCtrl = game_control.g_instance.roaming
        result = {'canAddToFriend': roamingCtrl.isSameRealm(uid),
         'canAddToIgnore': True,
         'canDoDenunciations': True,
         'canCreateChannel': not roamingCtrl.isInRoaming() and not roamingCtrl.isPlayerInRoaming(uid)}
        if user is not None:
            result.update({'isFriend': user.isFriend(),
             'isIgnored': user.isIgnored(),
             'isMuted': user.isMuted(),
             'displayName': user.getFullName()})
        else:
            result.update({'isFriend': False,
             'isIgnored': False,
             'isMuted': False,
             'displayName': userName})
        return result

    def _getDenunciations(self):
        return g_itemsCache.items.stats.denunciationsLeft

    def _isMoneyTransfer(self):
        return isMoneyTransfer(g_itemsCache.items.stats.attributes)

    def isVehicleWasInBattle(self, intCD):
        accDossier = g_itemsCache.items.getAccountDossier(None)
        if accDossier:
            wasInBattleSet = set(accDossier.getTotalStats().getVehicles().keys())
            if intCD in wasInBattleSet:
                return True
        return False

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
