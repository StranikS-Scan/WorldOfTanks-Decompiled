# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/halloween_event/event_battle_results.py
import GUI
import SoundGroups
import constants
from adisp import process
from gui.prb_control import prbDispatcherProperty, prbEntityProperty
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.sounds.sound_constants import HW20SoundConsts
from helpers import dependency
from gui.Scaleform.daapi.view.meta.EventBattleResultScreenMeta import EventBattleResultScreenMeta
from gui.shared import event_bus_handlers, events, EVENT_BUS_SCOPE, event_dispatcher
from CurrentVehicle import g_currentVehicle
from gui.sounds.ambients import BattleResultsEnv
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.server_events import IEventsCache
from messenger.m_constants import PROTO_TYPE
from messenger.storage import storage_getter
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from messenger.proto import proto_getter
from helpers.CallbackDelayer import CallbackDelayer
_SNDID_ACHIEVEMENT = 'result_screen_achievements'
_SNDID_BONUS = 'result_screen_bonus'
_CHECK_FRIEND_TIMEOUT = 5.0

class EventBattleResult(EventBattleResultScreenMeta, CallbackDelayer):
    battleResults = dependency.descriptor(IBattleResultsService)
    appLoader = dependency.descriptor(IAppLoader)
    hangarSpace = dependency.descriptor(IHangarSpace)
    eventsCache = dependency.descriptor(IEventsCache)
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
        self.__blur = GUI.WGUIBackgroundBlur()

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
        if self.prbDispatcher and self.prbDispatcher.getEntity().isInQueue():
            if self.isInEventMode:
                g_eventDispatcher.loadEventBattleQueue()
            else:
                g_eventDispatcher.loadBattleQueue()
        else:
            event_dispatcher.showHangar()
        self.destroy()

    def playSliderSound(self):
        SoundGroups.g_instance.playSound2D(HW20SoundConsts.HANGAR_PBS_SLIDER)

    def playPointsSound(self):
        SoundGroups.g_instance.playSound2D(HW20SoundConsts.HANGAR_PBS_MAIN_POINTS)

    def playQuestSound(self):
        SoundGroups.g_instance.playSound2D(HW20SoundConsts.HANGAR_PBS_QUEST)

    def playRewardSound(self):
        SoundGroups.g_instance.playSound2D(HW20SoundConsts.HANGAR_PBS_REWARD)

    def playProgressBarSound(self):
        SoundGroups.g_instance.playSound2D(HW20SoundConsts.HANGAR_PBS_PROGRESSBAR)

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW, EVENT_BUS_SCOPE.LOBBY)
    def selectVehicle(self, inventoryId):
        g_currentVehicle.selectVehicle(inventoryId)
        return g_currentVehicle.invID == inventoryId

    @process
    def addToSquad(self, databaseID):
        result = False
        if self.eventsCache.isEventEnabled():
            result = yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.EVENT_SQUAD, accountsToInvite=(databaseID,), keepCurrentView=True))
        self.as_addToSquadResultS(result, databaseID)

    def addToFriend(self, databaseID, userName):
        self.proto.contacts.addFriend(databaseID, userName)
        self.delayCallback(_CHECK_FRIEND_TIMEOUT, self.__checkFriendAdded, databaseID)

    def _populate(self):
        super(EventBattleResult, self)._populate()
        self.battleResults.onResultPosted += self.__handleBattleResultsPosted
        self.hangarSpace.onSpaceCreate += self.__onHangarSpaceCreated
        if self.battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__setBattleResults()
        self._updateComponentVisibility(False)
        self.__blur.enable = True
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.battleResults.onResultPosted -= self.__handleBattleResultsPosted
        self.hangarSpace.onSpaceCreate -= self.__onHangarSpaceCreated
        self._updateComponentVisibility(True)
        self.__blur.enable = False
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        self.clearCallbacks()
        super(EventBattleResult, self)._dispose()

    def __setBattleResults(self):
        if self.__isResultsSet:
            return
        self.__isResultsSet = True
        canCreateSquad = self.prbEntity.getPermissions().canCreateSquad()
        canInvite = self.prbEntity.getPermissions().canSendInvite()
        isEventEnable = self.eventsCache.isEventEnabled()
        vo = self.battleResults.getResultsVO(self.__arenaUniqueID)
        friends = self.__getFriendsFromStats(vo)
        self.as_setVictoryDataS(vo, (canCreateSquad or canInvite) and isEventEnable, friends)
        if self.hangarSpace.spaceInited:
            self.as_playAnimationS()

    def __handleBattleResultsPosted(self, reusableInfo, composer, window):
        if self.__arenaUniqueID == reusableInfo.arenaUniqueID:
            self.__setBattleResults()

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
