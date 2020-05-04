# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_hangar/event_battle_results.py
import constants
from adisp import process
from gui.impl.lobby.secret_event.sound_constants import SOUND
from gui.prb_control import prbDispatcherProperty, prbEntityProperty, prbInvitesProperty
from helpers import dependency
from gui.Scaleform.daapi.view.meta.EventBattleResultScreenMeta import EventBattleResultScreenMeta
from gui.shared import event_bus_handlers, events, EVENT_BUS_SCOPE
from CurrentVehicle import g_currentVehicle
from gui.sounds.ambients import BattleResultsEnv
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.shared.utils import IHangarSpace
from messenger.m_constants import PROTO_TYPE
from messenger.storage import storage_getter
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, PRB_INVITE_STATE
from messenger.proto import proto_getter
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.se20 import ICustomizableObjectsManager
from constants import QUEUE_TYPE
_FEEDBACK_TO_SOUND_EVENT = {'stat_item': SOUND.SECRET_EVENT_POSTBATTLE_EFFICIENCY_SOUND_EVENT,
 'main_points': SOUND.SECRET_EVENT_POSTBATTLE_MAIN_POINTS_SOUND_EVENT,
 'no_bonus_points': SOUND.SECRET_EVENT_POSTBATTLE_MAIN_POINTS_NO_PRIKAZ_SOUND_EVENT,
 'progress_bar': SOUND.SECRET_EVENT_POSTBATTLE_PROGRESS_BAR_SOUND_EVENT,
 'banner': SOUND.SECRET_EVENT_POSTBATTLE_SUBDIVISION_BAR_SOUND_EVENT,
 'bonus': SOUND.SECRET_EVENT_POSTBATTLE_PRIKAZ_SOUND_EVENT,
 'no_bonus': SOUND.SECRET_EVENT_POSTBATTLE_NO_PRIKAZ_SOUND_EVENT}
_CHECK_FRIEND_TIMEOUT = 5.0

class EventBattleResult(EventBattleResultScreenMeta, CallbackDelayer):
    battleResults = dependency.descriptor(IBattleResultsService)
    appLoader = dependency.descriptor(IAppLoader)
    hangarSpace = dependency.descriptor(IHangarSpace)
    customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    __sound_env__ = BattleResultsEnv
    __metaclass__ = event_bus_handlers.EventBusListener

    def __init__(self, ctx=None):
        super(EventBattleResult, self).__init__()
        if 'arenaUniqueID' not in ctx:
            raise UserWarning('Key "arenaUniqueID" is not found in context', ctx)
        if not ctx['arenaUniqueID']:
            raise UserWarning('Value of "arenaUniqueID" must be greater than 0')
        self.__arenaUniqueID = ctx['arenaUniqueID']
        self.__isResultsSet = False
        self.__invitePlayerIDs = []

    @prbInvitesProperty
    def prbInvites(self):
        return None

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @prbEntityProperty
    def prbEntity(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    @property
    def isInEventMode(self):
        if self.prbDispatcher:
            state = self.prbDispatcher.getFunctionalState()
            return state.isInUnit(constants.PREBATTLE_TYPE.EVENT) or state.isInPreQueue(constants.QUEUE_TYPE.EVENT_BATTLES)
        return False

    def closeView(self):
        self.destroy()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW, EVENT_BUS_SCOPE.LOBBY)
    def selectVehicle(self, inventoryId):
        g_currentVehicle.selectVehicle(inventoryId)
        return g_currentVehicle.invID == inventoryId

    @process
    def addToSquad(self, databaseID):
        databaseID = int(databaseID)
        result = yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.EVENT_SQUAD, accountsToInvite=(databaseID,), keepCurrentView=True))
        self.as_addToSquadResultS(result, databaseID)
        self.__invitePlayerIDs.append(databaseID)

    def addToFriend(self, databaseID, userName):
        self.proto.contacts.addFriend(databaseID, userName)
        self.delayCallback(_CHECK_FRIEND_TIMEOUT, self.__checkFriendAdded, databaseID)

    def _populate(self):
        super(EventBattleResult, self)._populate()
        self.battleResults.onResultPosted += self.__handleBattleResultsPosted
        self.hangarSpace.onSpaceCreate += self.__onHangarSpaceCreated
        self.customizableObjectsMgr.onPrbEntityChanged += self._onPrbEntityChanged
        invitesManager = self.prbInvites
        if invitesManager is not None:
            invitesManager.onSentInviteListModified += self.__onSentInviteListModified
        if self.battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__setBattleResults()
        self._updateComponentVisibility(False)
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        return

    def _dispose(self):
        self.battleResults.onResultPosted -= self.__handleBattleResultsPosted
        self.hangarSpace.onSpaceCreate -= self.__onHangarSpaceCreated
        self.customizableObjectsMgr.onPrbEntityChanged -= self._onPrbEntityChanged
        invitesManager = self.prbInvites
        if invitesManager is not None:
            invitesManager.onSentInviteListModified -= self.__onSentInviteListModified
        self._updateComponentVisibility(True)
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        self.clearCallbacks()
        super(EventBattleResult, self)._dispose()
        return

    def _onPrbEntityChanged(self, queueType):
        if queueType != QUEUE_TYPE.EVENT_BATTLES:
            self.closeView()

    def __setBattleResults(self):
        if self.__isResultsSet:
            return
        self.__isResultsSet = True
        canCreateSquad = self.prbEntity.getPermissions().canCreateSquad()
        canInvite = self.prbEntity.getPermissions().canSendInvite()
        vo = self.battleResults.getResultsVO(self.__arenaUniqueID)
        friends = self.__getFriendsFromStats(vo)
        self.as_setVictoryDataS(vo, canCreateSquad or canInvite, friends)
        if self.hangarSpace.spaceInited:
            self.as_playAnimationS()

    def __handleBattleResultsPosted(self, reusableInfo, composer):
        if self.__arenaUniqueID == reusableInfo.arenaUniqueID:
            self.__setBattleResults()

    def playSoundFeedback(self, eventName):
        self.soundManager.playSound(_FEEDBACK_TO_SOUND_EVENT[eventName])

    def _updateComponentVisibility(self, visible):
        if not self.isInEventMode:
            tutorialManager = self.appLoader.getApp().tutorialManager
            componentsToHide = ('MainMenuButtonBar', 'HeaderCenterMenuBg', 'MainMenuGradient')
            for component in componentsToHide:
                tutorialManager.setComponentProps(component, {'visible': visible})

    def __onHangarSpaceCreated(self):
        self.as_playAnimationS()

    def __getFriendsFromStats(self, vo):
        players = vo['players']
        result = []
        for player in players:
            playerId = player['playerId']
            user = self.usersStorage.getUser(playerId)
            if user is not None and user.isFriend():
                result.append(playerId)

        return result

    def __checkFriendAdded(self, databaseID):
        user = self.usersStorage.getUser(databaseID)
        if user is None or not user.isFriend():
            self.as_addToFriendResultS(False, databaseID)
        return

    def __onSentInviteListModified(self, added, changed, deleted):
        prbInvites = self.prbInvites
        invitePlayerIDs = self.__invitePlayerIDs
        for inviteID in changed:
            invite = prbInvites.getInvite(inviteID)
            databaseID = invite.receiverID
            validStates = (PRB_INVITE_STATE.PENDING, PRB_INVITE_STATE.ACCEPTED)
            if databaseID in invitePlayerIDs and invite.getState() not in validStates:
                self.as_addToSquadResultS(False, databaseID)
                invitePlayerIDs.remove(databaseID)
