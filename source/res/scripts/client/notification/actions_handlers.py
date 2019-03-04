# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/actions_handlers.py
from collections import defaultdict
import BigWorld
from adisp import process
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import DialogsInterface, makeHtmlString, SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.BARRACKS_CONSTANTS import BARRACKS_CONSTANTS
from gui.battle_results import RequestResultsContext
from gui.clans.clan_helpers import showAcceptClanInviteDialog
from gui.prb_control import prbInvitesProperty, prbDispatcherProperty
from gui.ranked_battles import ranked_helpers
from gui.server_events.events_dispatcher import showPersonalMission
from gui.shared import g_eventBus, events, actions, EVENT_BUS_SCOPE, event_dispatcher as shared_events
from gui.shared.event_dispatcher import showProgressiveRewardWindow
from gui.shared.utils import decorators
from gui.wgcg.clan import contexts as clan_ctxs
from gui.wgnc import g_wgncProvider
from helpers import dependency
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from notification.settings import NOTIFICATION_TYPE, NOTIFICATION_BUTTON_STATE
from notification.tutorial_helper import TutorialGlobalStorage, TUTORIAL_GLOBAL_VAR
from predefined_hosts import g_preDefinedHosts
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IBrowserController, IRankedBattlesController
from skeletons.gui.web import IWebController
from soft_exception import SoftException
from skeletons.gui.customization import ICustomizationService

class _ActionHandler(object):

    @classmethod
    def getNotType(cls):
        return NotImplementedError

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        if action not in self.getActions():
            raise SoftException('Handler does not handle action {0}'.format(action))


class _NavigationDisabledActionHandler(_ActionHandler):

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    def handleAction(self, model, entityID, action):
        super(_NavigationDisabledActionHandler, self).handleAction(model, entityID, action)
        if not self._canNavigate():
            return
        self.doAction(model, entityID, action)

    def doAction(self, model, entityID, action):
        raise NotImplementedError

    def _canNavigate(self):
        prbDispatcher = self.prbDispatcher
        if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled():
            BigWorld.callback(0.0, self.__showMessage)
            return False
        else:
            return True

    @staticmethod
    def __showMessage():
        SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error, priority='high')


class _OpenEventBoardsHandler(_ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_OpenEventBoardsHandler, self).handleAction(model, entityID, action)
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MISSIONS, ctx={'tab': QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS}), scope=EVENT_BUS_SCOPE.LOBBY)


class _ShowArenaResultHandler(_ActionHandler):

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    def handleAction(self, model, entityID, action):
        super(_ShowArenaResultHandler, self).handleAction(model, entityID, action)
        notification = model.collection.getItem(NOTIFICATION_TYPE.MESSAGE, entityID)
        if not notification:
            LOG_ERROR('Notification not found', NOTIFICATION_TYPE.MESSAGE, entityID)
            return
        savedData = notification.getSavedData()
        if not savedData:
            self._updateNotification(notification)
            LOG_ERROR('arenaUniqueID not found', notification)
            return
        self._showWindow(notification, savedData)

    def _updateNotification(self, notification):
        _, formatted, settings = self.proto.serviceChannel.getMessage(notification.getID())
        if formatted and settings:
            formatted['buttonsStates'].update({'submit': NOTIFICATION_BUTTON_STATE.HIDDEN})
            formatted['message'] += makeHtmlString('html_templates:lobby/system_messages', 'infoNoAvailable')
            notification.update(formatted)

    def _showWindow(self, notification, arenaUniqueID):
        pass

    def _showI18nMessage(self, key, msgType):

        def showMessage():
            SystemMessages.pushI18nMessage(key, type=msgType)

        BigWorld.callback(0.0, showMessage)


class _ShowClanSettingsHandler(_ActionHandler):

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_ShowClanSettingsHandler, self).handleAction(model, entityID, action)
        LOG_DEBUG('_ShowClanSettingsHandler handleAction:')
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.SETTINGS_WINDOW, ctx={'redefinedKeyMode': False}), EVENT_BUS_SCOPE.LOBBY)


class _ShowClanSettingsFromAppsHandler(_ShowClanSettingsHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_APPS


class _ShowClanSettingsFromInvitesHandler(_ShowClanSettingsHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_INVITES


class _ShowClanAppsHandler(_ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_APPS

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_ShowClanAppsHandler, self).handleAction(model, entityID, action)
        return shared_events.showClanInvitesWindow()


class _ShowClanInvitesHandler(_ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_INVITES

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_ShowClanInvitesHandler, self).handleAction(model, entityID, action)
        g_eventBus.handleEvent(events.LoadViewEvent(CLANS_ALIASES.CLAN_PERSONAL_INVITES_WINDOW_PY), scope=EVENT_BUS_SCOPE.LOBBY)


class _ClanAppHandler(_ActionHandler):
    clanCtrl = dependency.descriptor(IWebController)

    def _getAccountID(self, model, entityID):
        return model.getNotification(self.getNotType(), entityID).getAccountID()

    def _getApplicationID(self, model, entityID):
        return model.getNotification(self.getNotType(), entityID).getApplicationID()


class _AcceptClanAppHandler(_ClanAppHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_APP

    @classmethod
    def getActions(cls):
        pass

    @process
    def handleAction(self, model, entityID, action):
        super(_AcceptClanAppHandler, self).handleAction(model, entityID, action)
        yield self.clanCtrl.sendRequest(clan_ctxs.AcceptApplicationCtx(self._getApplicationID(model, entityID)), allowDelay=True)


class _DeclineClanAppHandler(_ClanAppHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_APP

    @classmethod
    def getActions(cls):
        pass

    @process
    def handleAction(self, model, entityID, action):
        super(_DeclineClanAppHandler, self).handleAction(model, entityID, action)
        yield self.clanCtrl.sendRequest(clan_ctxs.DeclineApplicationCtx(self._getApplicationID(model, entityID)), allowDelay=True)


class _ShowClanAppUserInfoHandler(_ClanAppHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_APP

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_ShowClanAppUserInfoHandler, self).handleAction(model, entityID, action)
        accID = self._getAccountID(model, entityID)

        def onDossierReceived(databaseID, userName):
            shared_events.showProfileWindow(databaseID, userName)

        shared_events.requestProfile(accID, model.getNotification(self.getNotType(), entityID).getUserName(), successCallback=onDossierReceived)
        return None


class _ClanInviteHandler(_ActionHandler):
    clanCtrl = dependency.descriptor(IWebController)

    def _getInviteID(self, model, entityID):
        return model.getNotification(self.getNotType(), entityID).getInviteID()


class _AcceptClanInviteHandler(_ClanInviteHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_INVITE

    @classmethod
    def getActions(cls):
        pass

    @process
    def handleAction(self, model, entityID, action):
        super(_AcceptClanInviteHandler, self).handleAction(model, entityID, action)
        entity = model.getNotification(self.getNotType(), entityID).getEntity()
        clanName = entity.getClanName()
        clanTag = entity.getClanTag()
        result = yield showAcceptClanInviteDialog(clanName, clanTag)
        if result:
            yield self.clanCtrl.sendRequest(clan_ctxs.AcceptInviteCtx(self._getInviteID(model, entityID)), allowDelay=True)


class _DeclineClanInviteHandler(_ClanInviteHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_INVITE

    @classmethod
    def getActions(cls):
        pass

    @process
    def handleAction(self, model, entityID, action):
        super(_DeclineClanInviteHandler, self).handleAction(model, entityID, action)
        yield self.clanCtrl.sendRequest(clan_ctxs.DeclineInviteCtx(self._getInviteID(model, entityID)), allowDelay=True)


class _ShowClanProfileHandler(_ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.CLAN_INVITE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(_ShowClanProfileHandler, self).handleAction(model, entityID, action)
        clan = model.getNotification(self.getNotType(), entityID)
        shared_events.showClanProfileWindow(clan.getClanID(), clan.getClanAbbrev())


class ShowRankedSeasonCompleteHandler(_ActionHandler):
    rankedController = dependency.descriptor(IRankedBattlesController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None:
            self.__showSeasonAward(savedData['quest'], savedData['awards'])
        return

    def __showSeasonAward(self, quest, data):
        seasonID, _, _ = ranked_helpers.getRankedDataFromTokenQuestID(quest.getID())
        season = self.rankedController.getSeason(seasonID)
        if season is not None:
            g_eventBus.handleEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE, ctx={'quest': quest,
             'awards': data,
             'season': season}), scope=EVENT_BUS_SCOPE.LOBBY)
        return


class ShowBattleResultsHandler(_ShowArenaResultHandler):
    battleResults = dependency.descriptor(IBattleResultsService)

    def _updateNotification(self, notification):
        super(ShowBattleResultsHandler, self)._updateNotification(notification)
        self._showI18nMessage('#battle_results:noData', SystemMessages.SM_TYPE.Warning)

    @classmethod
    def getActions(cls):
        pass

    @decorators.process('loadStats')
    def _showWindow(self, notification, arenaUniqueID):
        uniqueID = long(arenaUniqueID)
        result = yield self.battleResults.requestResults(RequestResultsContext(uniqueID, showImmediately=False, showIfPosted=True, resetCache=False))
        if not result:
            self._updateNotification(notification)


class ShowFortBattleResultsHandler(_ShowArenaResultHandler):

    @classmethod
    def getActions(cls):
        pass

    def _updateNotification(self, notification):
        super(ShowFortBattleResultsHandler, self)._updateNotification(notification)
        self._showI18nMessage('#battle_results:noData', SystemMessages.SM_TYPE.Warning)

    def _showWindow(self, notification, data):
        if data:
            battleResultData = data.get('battleResult', None)
            g_eventBus.handleEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, ctx={'data': battleResultData}), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self._updateNotification(notification)
        return


class ShowTutorialBattleHistoryHandler(_ShowArenaResultHandler):
    _lastHistoryID = TutorialGlobalStorage(TUTORIAL_GLOBAL_VAR.LAST_HISTORY_ID, 0)

    @classmethod
    def getActions(cls):
        pass

    def _triggerEvent(self, _, arenaUniqueID):
        g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.SHOW_TUTORIAL_BATTLE_HISTORY, targetID=arenaUniqueID))

    def _updateNotification(self, notification):
        super(ShowTutorialBattleHistoryHandler, self)._updateNotification(notification)
        self._showI18nMessage('#battle_tutorial:labels/results-are-not-available', SystemMessages.SM_TYPE.Warning)

    def _showWindow(self, notification, arenaUniqueID):
        if arenaUniqueID == self._lastHistoryID:
            self._triggerEvent(notification, arenaUniqueID)
        else:
            self._updateNotification(notification)


class OpenPollHandler(_ActionHandler):
    browserCtrl = dependency.descriptor(IBrowserController)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(OpenPollHandler, self).handleAction(model, entityID, action)
        notification = model.collection.getItem(NOTIFICATION_TYPE.MESSAGE, entityID)
        if not notification:
            LOG_ERROR('Notification is not found', NOTIFICATION_TYPE.MESSAGE, entityID)
            return
        link, title = notification.getSettings().auxData
        if not link:
            LOG_ERROR('Poll link is not found', notification)
            return
        self.__doOpen(link, title)

    @process
    def __doOpen(self, link, title):
        yield self.browserCtrl.load(link, title, showActionBtn=False)


class AcceptPrbInviteHandler(_ActionHandler):

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    @prbInvitesProperty
    def prbInvites(self):
        pass

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.INVITE

    @classmethod
    def getActions(cls):
        pass

    @process
    def handleAction(self, model, entityID, action):
        super(AcceptPrbInviteHandler, self).handleAction(model, entityID, action)
        yield lambda callback: callback(None)
        postActions = []
        invite = self.prbInvites.getInvite(entityID)
        state = self.prbDispatcher.getFunctionalState()
        if state.doLeaveToAcceptInvite(invite.type):
            postActions.append(actions.LeavePrbModalEntity())
        if invite and invite.anotherPeriphery:
            success = True
            if g_preDefinedHosts.isRoamingPeriphery(invite.peripheryID):
                success = yield DialogsInterface.showI18nConfirmDialog('changeRoamingPeriphery')
            if not success:
                return
            postActions.append(actions.DisconnectFromPeriphery())
            postActions.append(actions.ConnectToPeriphery(invite.peripheryID))
            postActions.append(actions.PrbInvitesInit())
        self.prbInvites.acceptInvite(entityID, postActions=postActions)


class DeclinePrbInviteHandler(_ActionHandler):

    @prbInvitesProperty
    def prbInvites(self):
        pass

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.INVITE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(DeclinePrbInviteHandler, self).handleAction(model, entityID, action)
        if entityID:
            self.prbInvites.declineInvite(entityID)
        else:
            LOG_ERROR('Invite is invalid', entityID)


class ApproveFriendshipHandler(_ActionHandler):

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.FRIENDSHIP_RQ

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(ApproveFriendshipHandler, self).handleAction(model, entityID, action)
        self.proto.contacts.approveFriendship(entityID)


class CancelFriendshipHandler(_ActionHandler):

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.FRIENDSHIP_RQ

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(CancelFriendshipHandler, self).handleAction(model, entityID, action)
        self.proto.contacts.cancelFriendship(entityID)


class WGNCActionsHandler(_ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.WGNC_POP_UP

    def handleAction(self, model, entityID, action):
        notification = model.collection.getItem(NOTIFICATION_TYPE.WGNC_POP_UP, entityID)
        if notification:
            actorName = notification.getSavedData()
        else:
            actorName = ''
        g_wgncProvider.doAction(entityID, action, actorName)


class SecurityLinkHandler(_ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.SECURITY_SETTINGS))


class OpenCustomizationHandler(_ActionHandler):
    service = dependency.descriptor(ICustomizationService)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(OpenCustomizationHandler, self).handleAction(model, entityID, action)
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        vehicleIntCD = savedData.get('vehicleIntCD')
        vehicle = self.service.getItemByCD(vehicleIntCD)
        if vehicle.invID != -1:
            self.service.showCustomization(vehicle.invID, callback=self.service.getCtx().switchToStyle)


class ProlongStyleRent(_ActionHandler):
    service = dependency.descriptor(ICustomizationService)

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        super(ProlongStyleRent, self).handleAction(model, entityID, action)
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        vehicleIntCD = savedData.get('vehicleIntCD')
        styleIntCD = savedData.get('styleIntCD')
        vehicle = self.service.getItemByCD(vehicleIntCD)
        style = self.service.getItemByCD(styleIntCD)
        if vehicle.invID != -1:
            callback = lambda : self.service.getCtx().prolongStyleRent(style)
            self.service.showCustomization(vehicle.invID, callback)


class _OpenNotrecruitedHandler(_NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_BARRACKS, ctx={'location': BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED}), scope=EVENT_BUS_SCOPE.LOBBY)


class OpenPersonalMissionHandler(_ActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def handleAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None:
            showPersonalMission(missionID=savedData['questID'])
        return


class _OpenLootBoxesHandler(_NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None:
            pass
        return


class _LootBoxesAutoOpenHandler(_NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData is not None and 'rewards' in savedData:
            pass
        return


class _OpenProgressiveRewardView(_NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.PROGRESSIVE_REWARD

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        showProgressiveRewardWindow()


_AVAILABLE_HANDLERS = (ShowBattleResultsHandler,
 ShowTutorialBattleHistoryHandler,
 ShowFortBattleResultsHandler,
 OpenPollHandler,
 AcceptPrbInviteHandler,
 DeclinePrbInviteHandler,
 ApproveFriendshipHandler,
 CancelFriendshipHandler,
 WGNCActionsHandler,
 SecurityLinkHandler,
 ShowRankedSeasonCompleteHandler,
 _ShowClanAppsHandler,
 _ShowClanInvitesHandler,
 _AcceptClanAppHandler,
 _DeclineClanAppHandler,
 _ShowClanAppUserInfoHandler,
 _ShowClanProfileHandler,
 _ShowClanSettingsFromAppsHandler,
 _ShowClanSettingsFromInvitesHandler,
 _AcceptClanInviteHandler,
 _DeclineClanInviteHandler,
 _OpenEventBoardsHandler,
 OpenCustomizationHandler,
 _OpenNotrecruitedHandler,
 OpenPersonalMissionHandler,
 _OpenLootBoxesHandler,
 _LootBoxesAutoOpenHandler,
 _OpenProgressiveRewardView,
 ProlongStyleRent)

class NotificationsActionsHandlers(object):
    __slots__ = ('__single', '__multi')

    def __init__(self, handlers=None):
        super(NotificationsActionsHandlers, self).__init__()
        self.__single = {}
        self.__multi = defaultdict(set)
        if not handlers:
            handlers = _AVAILABLE_HANDLERS
        for clazz in handlers:
            actionsList = clazz.getActions()
            if actionsList:
                if len(actionsList) == 1:
                    self.__single[clazz.getNotType(), actionsList[0]] = clazz
                else:
                    LOG_ERROR('Handler is not added to collection', clazz)
            self.__multi[clazz.getNotType()].add(clazz)

    def handleAction(self, model, typeID, entityID, actionName):
        key = (typeID, actionName)
        if key in self.__single:
            clazz = self.__single[key]
            clazz().handleAction(model, entityID, actionName)
        elif typeID in self.__multi:
            for clazz in self.__multi[typeID]:
                clazz().handleAction(model, entityID, actionName)

        else:
            LOG_ERROR('Action handler not found', typeID, entityID, actionName)

    def cleanUp(self):
        self.__single.clear()
        self.__multi.clear()
