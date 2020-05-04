# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/events_dispatcher.py
import weakref
from collections import namedtuple
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes, ScopeTemplates
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.locale.CHAT import CHAT
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.app_loader import sf_lobby
from gui.prb_control.settings import CTRL_ENTITY_TYPE, FUNCTIONAL_FLAG
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.events import ChannelManagementEvent, PreBattleChannelEvent, checkLoadedView
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from messenger.ext import channel_num_gen
from messenger.ext.channel_num_gen import SPECIAL_CLIENT_WINDOWS
from messenger.m_constants import LAZY_CHANNEL
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.app_loader import IAppLoader
TOOLTIP_PRB_DATA = namedtuple('TOOLTIP_PRB_DATA', ('tooltipId', 'label'))
_SQUAD_TYPE_TO_ALIAS = {PREBATTLE_TYPE.EVENT: PREBATTLE_ALIASES.EVENT_SQUAD_WINDOW_PY,
 PREBATTLE_TYPE.SQUAD: PREBATTLE_ALIASES.SQUAD_WINDOW_PY,
 PREBATTLE_TYPE.EPIC: PREBATTLE_ALIASES.EPIC_SQUAD_WINDOW_PY,
 PREBATTLE_TYPE.BOB: PREBATTLE_ALIASES.BOB_SQUAD_WINDOW_PY}
_CarouselItemCtx = namedtuple('_CarouselItemCtx', ['label',
 'canClose',
 'isNotified',
 'icon',
 'order',
 'criteria',
 'viewType',
 'openHandler',
 'readyData',
 'tooltipData'])
_defCarouselItemCtx = _CarouselItemCtx(label=None, canClose=False, isNotified=False, icon=None, order=channel_num_gen.getOrder4Prebattle(), criteria=None, viewType=ViewTypes.WINDOW, openHandler=None, readyData=None, tooltipData=None)
_LOCKED_SCREENS = (PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY, PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY)
_EPIC_SCREENS = (PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY, PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY)

class EventDispatcher(object):
    gameSession = dependency.descriptor(IGameSessionController)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(EventDispatcher, self).__init__()
        self.__loadingEvent = None
        return

    @sf_lobby
    def app(self):
        return None

    def init(self, dispatcher):
        self.__setPrebattleDispatcher(dispatcher)
        app = self.app
        if app and app.containerManager:
            app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
            app.containerManager.onViewLoadCanceled += self.__onViewLoadCanceled

    def fini(self):
        self.__setPrebattleDispatcher(None)
        self.__loadingEvent = None
        app = self.app
        if app and app.containerManager:
            app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
            app.containerManager.onViewLoadCanceled -= self.__onViewLoadCanceled
        return

    def isTrainingLoaded(self):
        return self.__getLoadedEvent() in _LOCKED_SCREENS or self.__loadingEvent in _LOCKED_SCREENS

    def isEpicTrainingLoaded(self):
        return self.__getLoadedEvent() in _EPIC_SCREENS or self.__loadingEvent in _EPIC_SCREENS

    def updateUI(self, loadedAlias=None):
        self.__fireEvent(events.FightButtonEvent(events.FightButtonEvent.FIGHT_BUTTON_UPDATE))
        self.__invalidatePrbEntity(loadedAlias)

    def loadHangar(self):
        self.__fireLoadEvent(VIEW_ALIAS.LOBBY_HANGAR)

    @checkLoadedView(R.views.lobby.secretEvent.ActionHangarWindow())
    def loadEventHangar(self):
        from gui.impl.lobby.secret_event.action_hangar_view import ActionHangarView
        g_eventBus.handleEvent(events.LoadUnboundViewEvent(R.views.lobby.secretEvent.ActionHangarWindow(), ActionHangarView, ScopeTemplates.DEFAULT_SCOPE), scope=EVENT_BUS_SCOPE.LOBBY)

    def loadBattleQueue(self):
        self.__fireLoadEvent(VIEW_ALIAS.BATTLE_QUEUE)

    def loadEventBattleQueue(self):
        self.__fireLoadEvent(VIEW_ALIAS.EVENT_BATTLE_QUEUE)

    def loadTrainingList(self):
        self.addTrainingToCarousel()
        self.__showTrainingList()

    def loadTrainingRoom(self):
        self.addTrainingToCarousel(False)
        self.__showTrainingRoom()

    def loadEpicTrainingList(self):
        self.addEpicTrainingToCarousel()
        self._showEpicTrainingList()

    def loadEpicTrainingRoom(self):
        self.addEpicTrainingToCarousel(False)
        self.__showEpicTrainingRoom()

    def loadBattleSessionWindow(self, prbType):
        self.addSpecBattleToCarousel(prbType)
        self.showBattleSessionWindow()

    def loadBattleSessionList(self):
        self.__fireShowEvent(PREBATTLE_ALIASES.BATTLE_SESSION_LIST_WINDOW_PY)

    def loadUnit(self, prbType):
        self.__addUnitToCarousel(prbType)
        self.showUnitWindow(prbType)

    def loadStrongholds(self):
        self.__addStrongholdsToCarousel()
        self.showStrongholdsWindow()

    def loadTournaments(self):
        pass

    def loadSquad(self, prbType, ctx=None, isTeamReady=False):
        self.__addSquadToCarousel(prbType, isTeamReady)
        self.__showSquadWindow(prbType, ctx and ctx.get('showInvitesWindow', False))

    def loadSandboxQueue(self):
        self.__fireShowEvent(VIEW_ALIAS.SANDBOX_QUEUE_DIALOG)

    def loadRanked(self):
        self.__fireShowEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_INTRO_ALIAS)

    def loadEpicWelcome(self):
        self.__fireShowEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_WELCOME_BACK_ALIAS)

    def loadRankedUnreachable(self):
        self.__fireShowEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_UNREACHABLE_VIEW_ALIAS)

    def startOffbattleTutorial(self):
        self.__fireEvent(events.TutorialEvent(events.TutorialEvent.START_TRAINING, settingsID='OFFBATTLE', reloadIfRun=True, restoreIfRun=True, isStopForced=True), scope=EVENT_BUS_SCOPE.GLOBAL)

    def unloadSandboxQueue(self):
        self.__fireHideEvent(events.HideWindowEvent.HIDE_SANDBOX_QUEUE_DIALOG)

    def loadBootcampQueue(self):
        self.__fireEvent(events.BootcampEvent(events.BootcampEvent.QUEUE_DIALOG_SHOW))

    def unloadBootcampQueue(self):
        self.__fireEvent(events.BootcampEvent(events.BootcampEvent.QUEUE_DIALOG_CLOSE))

    def removeTrainingFromCarousel(self, isList=True, closeWindow=True):
        clientType = SPECIAL_CLIENT_WINDOWS.TRAINING_LIST if isList else SPECIAL_CLIENT_WINDOWS.TRAINING_ROOM
        clientID = channel_num_gen.getClientID4SpecialWindow(clientType)
        if not clientID:
            LOG_ERROR('Client ID not found', 'removeTrainingToCarousel')
            return
        self.__handleRemoveRequest(clientID, closeWindow=closeWindow)

    def removeEpicTrainingFromCarousel(self, isList=True, closeWindow=True):
        clientType = SPECIAL_CLIENT_WINDOWS.EPIC_TRAINING_LIST if isList else SPECIAL_CLIENT_WINDOWS.EPIC_TRAINING_ROOM
        clientID = channel_num_gen.getClientID4SpecialWindow(clientType)
        if not clientID:
            LOG_ERROR('Client ID not found', 'removeEpicTrainingFromCarousel')
            return
        self.__handleRemoveRequest(clientID, closeWindow=closeWindow)

    def addTrainingToCarousel(self, isList=True):
        self.removeTrainingFromCarousel(not isList, closeWindow=False)
        if isList:
            clientType = SPECIAL_CLIENT_WINDOWS.TRAINING_LIST
            alias = PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY
            handler = self.__showTrainingList
        else:
            clientType = SPECIAL_CLIENT_WINDOWS.TRAINING_ROOM
            alias = PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY
            handler = self.__returnToTrainingRoom
        clientID = channel_num_gen.getClientID4SpecialWindow(clientType)
        if not clientID:
            LOG_ERROR('Client ID not found', 'addTrainingToCarousel')
            return
        currCarouselItemCtx = _defCarouselItemCtx._replace(label=MENU.HEADERBUTTONS_BATTLE_TYPES_TRAINING, criteria={POP_UP_CRITERIA.VIEW_ALIAS: alias}, viewType=ViewTypes.LOBBY_SUB, openHandler=handler)
        self.__handleAddPreBattleRequest(clientID, currCarouselItemCtx._asdict())

    def addEpicTrainingToCarousel(self, isList=True):
        self.removeEpicTrainingFromCarousel(not isList, closeWindow=False)
        if isList:
            clientType = SPECIAL_CLIENT_WINDOWS.EPIC_TRAINING_LIST
            alias = PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY
            handler = self._showEpicTrainingList
        else:
            clientType = SPECIAL_CLIENT_WINDOWS.EPIC_TRAINING_ROOM
            alias = PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY
            handler = self.__returnToTrainingRoom
        clientID = channel_num_gen.getClientID4SpecialWindow(clientType)
        if not clientID:
            LOG_ERROR('Client ID not found', 'addEpicTrainingToCarousel')
            return
        label = '{} - {}'.format(backport.text(R.strings.menu.headerButtons.battle.types.epicTraining()), backport.text(R.strings.menu.headerButtons.battle.types.epicTraining.descr()))
        currCarouselItemCtx = _defCarouselItemCtx._replace(label=label, criteria={POP_UP_CRITERIA.VIEW_ALIAS: alias}, viewType=ViewTypes.LOBBY_SUB, openHandler=handler)
        self.__handleAddPreBattleRequest(clientID, currCarouselItemCtx._asdict())

    def addSpecBattleToCarousel(self, prbType):
        clientID = channel_num_gen.getClientID4Prebattle(prbType)
        if not clientID:
            LOG_ERROR('Client ID not found', 'addSpecBattleToCarousel')
            return
        if prbType is PREBATTLE_TYPE.CLAN:
            label = CHAT.CHANNELS_CLAN
        elif prbType is PREBATTLE_TYPE.TOURNAMENT:
            label = CHAT.CHANNELS_TOURNAMENT
        else:
            LOG_ERROR('Prebattle type is not valid', prbType)
            return
        currCarouselItemCtx = _defCarouselItemCtx._replace(label=label, criteria={POP_UP_CRITERIA.VIEW_ALIAS: PREBATTLE_ALIASES.BATTLE_SESSION_ROOM_WINDOW_PY}, openHandler=self.showBattleSessionWindow)
        self.__handleAddPreBattleRequest(clientID, currCarouselItemCtx._asdict())

    def addSpecBattlesToCarousel(self):
        clientID = channel_num_gen.getClientID4LazyChannel(LAZY_CHANNEL.SPECIAL_BATTLES)
        if not clientID:
            LOG_ERROR('Client ID not found', 'addSpecBattlesToCarousel')
            return
        currCarouselItemCtx = _defCarouselItemCtx._replace(label=LAZY_CHANNEL.SPECIAL_BATTLES, order=channel_num_gen.getOrder4LazyChannel(LAZY_CHANNEL.SPECIAL_BATTLES), isNotified=True, criteria={POP_UP_CRITERIA.VIEW_ALIAS: PREBATTLE_ALIASES.BATTLE_SESSION_LIST_WINDOW_PY}, openHandler=self.loadBattleSessionList)
        self.__fireEvent(ChannelManagementEvent(clientID, PreBattleChannelEvent.REQUEST_TO_ADD, currCarouselItemCtx._asdict()))

    def removeSpecBattleFromCarousel(self, prbType, closeWindow=True):
        clientID = channel_num_gen.getClientID4Prebattle(prbType)
        if not clientID:
            LOG_ERROR('Client ID not found', '_removeSpecBattleFromCarousel')
            return
        self.__handleRemoveRequest(clientID, closeWindow=closeWindow)

    def removeSpecBattlesFromCarousel(self):
        clientID = channel_num_gen.getClientID4LazyChannel(LAZY_CHANNEL.SPECIAL_BATTLES)
        if not clientID:
            LOG_ERROR('Client ID not found', 'removeSpecBattlesFromCarousel')
            return
        self.__fireEvent(ChannelManagementEvent(clientID, PreBattleChannelEvent.REQUEST_TO_REMOVE))

    def showUnitWindow(self, prbType):
        if prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            self.__showSquadWindow(prbType)
        else:
            self.__fireShowEvent(CYBER_SPORT_ALIASES.CYBER_SPORT_WINDOW_PY)

    def showStrongholdsWindow(self):
        from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
        self.__fireShowEvent(FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS)

    def showTournamentWindow(self):
        pass

    def showStrongholdsBattleQueue(self):
        self.removeUnitFromCarousel(PREBATTLE_TYPE.STRONGHOLD)
        self.__fireShowEvent(VIEW_ALIAS.BATTLE_STRONGHOLDS_QUEUE)

    def showTournamentQueue(self):
        pass

    def strongholdsOnTimer(self, data):
        self.__fireEvent(events.StrongholdEvent(events.StrongholdEvent.STRONGHOLD_ON_TIMER, ctx=data), scope=EVENT_BUS_SCOPE.STRONGHOLD)

    def showSwitchPeripheryWindow(self, ctx, isModal=True):
        if isModal:
            alias = VIEW_ALIAS.SWITCH_PERIPHERY_WINDOW_MODAL
        else:
            alias = VIEW_ALIAS.SWITCH_PERIPHERY_WINDOW
        g_eventBus.handleEvent(events.LoadViewEvent(alias, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

    def removeUnitFromCarousel(self, prbType, closeWindow=True):
        clientID = channel_num_gen.getClientID4Prebattle(prbType)
        if not clientID:
            LOG_ERROR('Client ID not found', 'removeUnitFromCarousel', prbType)
            return
        self.__handleRemoveRequest(clientID, closeWindow=closeWindow)

    def setUnitProgressInCarousel(self, prbType, isInProgress):
        if prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            LOG_DEBUG('No unit progress for squad.')
            return
        clientID = channel_num_gen.getClientID4Prebattle(prbType)
        if not clientID:
            LOG_ERROR('Client ID not found', 'setUnitProgressInCarousel', prbType)
            return
        self.__fireEvent(events.ChannelManagementEvent(clientID, events.ChannelManagementEvent.REQUEST_TO_CHANGE, {'key': 'isInProgress',
         'value': isInProgress,
         'isShowByReq': isInProgress,
         'showIfClosed': True}))

    def showUnitProgressInCarousel(self, prbType):
        self._showUnitProgress(prbType, True)

    def hideUnitProgressInCarousel(self, prbType):
        self._showUnitProgress(prbType, False)

    def fireAutoInviteReceived(self, invite):
        self.__fireEvent(events.AutoInviteEvent(invite, events.AutoInviteEvent.INVITE_RECEIVED))

    def showParentControlNotification(self):
        from gui import DialogsInterface
        DialogsInterface.showDialog(self.gameSession.getParentControlNotificationMeta(), lambda *args: None)

    def showBattleSessionWindow(self):
        self.__fireShowEvent(PREBATTLE_ALIASES.BATTLE_SESSION_ROOM_WINDOW_PY)

    def setSquadTeamReadyInCarousel(self, prbType, isTeamReady):
        clientID = channel_num_gen.getClientID4Prebattle(prbType)
        if not clientID:
            LOG_ERROR('Client ID not found', 'setSquadTeamReadyInCarousel', prbType)
            return
        readyData = self.__getReadyPrbData(isTeamReady)
        g_eventBus.handleEvent(events.ChannelManagementEvent(clientID, events.ChannelManagementEvent.REQUEST_TO_CHANGE, {'key': 'readyData',
         'value': readyData,
         'isShowByReq': False,
         'showIfClosed': True}), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(events.ChannelManagementEvent(clientID, events.ChannelManagementEvent.REQUEST_TO_CHANGE, {'key': 'tooltipData',
         'value': self.__getTooltipPrbData(CHAT.CHANNELS_SQUADREADY_TOOLTIP if isTeamReady else CHAT.CHANNELS_SQUADNOTREADY_TOOLTIP),
         'isShowByReq': False,
         'showIfClosed': True}), scope=EVENT_BUS_SCOPE.LOBBY)

    def needToLoadHangar(self, ctx, modeFlags, aliasToLoad):
        if ctx is not None:
            switchMask = FUNCTIONAL_FLAG.TRAINING | FUNCTIONAL_FLAG.EPIC_TRAINING
            canSwitch = (ctx.getFlags() | modeFlags) & switchMask == switchMask
            if canSwitch:
                return False
        res = False
        inView = None
        if self.__appLoader is not None and self.__appLoader.getApp() is not None and self.__appLoader.getApp().containerManager is not None:
            inView = self.__appLoader.getApp().containerManager.getView(ViewTypes.LOBBY_SUB)
        if inView is not None:
            if inView.alias in aliasToLoad:
                res = True
        return res

    def showEpicBattlesPrimeTimeWindow(self):
        g_eventBus.handleEvent(events.LoadViewEvent(alias=EPICBATTLES_ALIASES.EPIC_BATTLES_PRIME_TIME_ALIAS, ctx={}), EVENT_BUS_SCOPE.LOBBY)

    def showRankedPrimeTimeWindow(self):
        g_eventBus.handleEvent(events.LoadViewEvent(alias=RANKEDBATTLES_ALIASES.RANKED_BATTLE_PRIME_TIME, ctx={}), EVENT_BUS_SCOPE.LOBBY)

    def _showUnitProgress(self, prbType, show):
        clientID = channel_num_gen.getClientID4Prebattle(prbType)
        if not clientID:
            LOG_ERROR('Client ID not found', '_showUnitStatus', prbType)
            return
        self.__fireEvent(events.ChannelManagementEvent(clientID, events.ChannelManagementEvent.REQUEST_TO_SHOW, {'show': show}))

    def __showSquadWindow(self, prbType, showInvitesWindow=False):
        self.__fireShowEvent(_SQUAD_TYPE_TO_ALIAS[prbType])
        if showInvitesWindow:
            self.__fireShowEvent(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, {'prbName': 'squad',
             'ctrlType': CTRL_ENTITY_TYPE.UNIT})

    def __showTrainingRoom(self):
        self.__fireLoadEvent(PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY)

    def __returnToTrainingRoom(self):
        if self.__prbDispatcher is not None:
            self.__prbDispatcher.doAction()
        return

    def __showEpicTrainingRoom(self):
        self.__fireLoadEvent(PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY)

    def __fireEvent(self, event, scope=EVENT_BUS_SCOPE.LOBBY):
        g_eventBus.handleEvent(event, scope)

    def __fireHideEvent(self, event):
        self.__fireEvent(events.HideWindowEvent(event))

    def __fireShowEvent(self, eventName, arg=None):
        if arg is None:
            self.__fireEvent(events.LoadViewEvent(eventName))
        else:
            self.__fireEvent(events.LoadViewEvent(eventName, ctx=arg))
        return

    def __fireLoadEvent(self, eventName, arg=None):
        if self.__getLoadedEvent() == eventName:
            LOG_DEBUG('View already is loaded', eventName)
            return
        else:
            if self.__loadingEvent:
                LOG_DEBUG('View is still loading. It is ignored', self.__loadingEvent, eventName)
            else:
                self.__loadingEvent = eventName
                if arg is None:
                    self.__fireEvent(events.LoadViewEvent(eventName))
                else:
                    self.__fireEvent(events.LoadViewEvent(eventName, ctx=arg))
            return

    def __handleRemoveRequest(self, clientID, closeWindow=True):
        self.__fireEvent(ChannelManagementEvent(clientID, PreBattleChannelEvent.REQUEST_TO_REMOVE_PRE_BATTLE_CHANNEL, ctx={'closeWindow': closeWindow}))

    def __handleAddPreBattleRequest(self, clientID, carouselItemCtx):
        self.__fireEvent(ChannelManagementEvent(clientID, PreBattleChannelEvent.REQUEST_TO_ADD_PRE_BATTLE_CHANNEL, carouselItemCtx))

    def __closeBattleSessionWindow(self):
        self.__fireHideEvent(events.HideWindowEvent.HIDE_BATTLE_SESSION_WINDOW)

    def __closeUnitWindow(self):
        self.__fireHideEvent(events.HideWindowEvent.HIDE_UNIT_WINDOW)

    def __setPrebattleDispatcher(self, prbDispatcher):
        if prbDispatcher is not None:
            self.__prbDispatcher = weakref.proxy(prbDispatcher)
        else:
            self.__prbDispatcher = None
        return

    def __showTrainingList(self):
        self.__fireLoadEvent(PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY)

    def _showEpicTrainingList(self):
        self.__fireLoadEvent(PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY)

    def __getReadyPrbData(self, isReady):
        return {'isReady': isReady}

    def __getTooltipPrbData(self, tooltipId, label=''):
        return TOOLTIP_PRB_DATA(tooltipId=tooltipId, label=label)._asdict()

    def __invalidatePrbEntity(self, loadedAlias):
        if loadedAlias == VIEW_ALIAS.LOBBY_HANGAR and self.__prbDispatcher is not None:
            entity = self.__prbDispatcher.getEntity()
            if entity:
                entity.invalidate()
        return

    def __onViewAddedToContainer(self, _, pyEntity):
        settings = pyEntity.settings
        if settings is None or settings.event == self.__loadingEvent:
            self.__loadingEvent = None
        if pyEntity.viewType == ViewTypes.LOBBY_SUB:
            self.updateUI(pyEntity.alias)
        return

    def __onViewLoadCanceled(self, _, pyEntity):
        settings = pyEntity.settings
        if settings is None or settings.event == self.__loadingEvent:
            self.__loadingEvent = None
        return

    def __getLoadedEvent(self):
        app = self.app
        if app and app.containerManager:
            container = app.containerManager.getContainer(ViewTypes.LOBBY_SUB)
            if container:
                view = container.getView()
                if view and view.settings is not None:
                    return view.settings.event
        return

    def __addUnitToCarousel(self, prbType):
        from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
        self.__addUnitToCarouselCommon(prbType, CYBERSPORT.WINDOW_TITLE, CYBER_SPORT_ALIASES.CYBER_SPORT_WINDOW_PY, lambda : self.showUnitWindow(prbType))

    def __addStrongholdsToCarousel(self):
        from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
        from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
        self.__addUnitToCarouselCommon(PREBATTLE_TYPE.STRONGHOLD, FORTIFICATIONS.SORTIE_INTROVIEW_TITLE, FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS, self.showStrongholdsWindow)

    def __addTournamentToCarousel(self):
        pass

    def __addUnitToCarouselCommon(self, prbType, label, viewAlias, openHandler):
        clientID = channel_num_gen.getClientID4Prebattle(prbType)
        if not clientID:
            LOG_ERROR('Client ID not found', 'addUnitToCarousel', clientID)
            return
        criteria = {POP_UP_CRITERIA.VIEW_ALIAS: viewAlias}
        currCarouselItemCtx = _defCarouselItemCtx._replace(label=label, criteria=criteria, viewType=ViewTypes.WINDOW, openHandler=openHandler)
        self.__handleAddPreBattleRequest(clientID, currCarouselItemCtx._asdict())

    def __addSquadToCarousel(self, prbType, isTeamReady=False):
        clientID = channel_num_gen.getClientID4Prebattle(prbType)
        if not clientID:
            LOG_ERROR('Client ID not found', 'addSquadToCarousel')
            return
        currCarouselItemCtx = _defCarouselItemCtx._replace(label=CHAT.CHANNELS_SQUAD, icon=RES_ICONS.MAPS_ICONS_MESSENGER_SQUAD_ICON, criteria={POP_UP_CRITERIA.VIEW_ALIAS: _SQUAD_TYPE_TO_ALIAS[prbType]}, openHandler=lambda : self.__showSquadWindow(prbType), readyData=self.__getReadyPrbData(isTeamReady), tooltipData=self.__getTooltipPrbData(CHAT.CHANNELS_SQUADREADY_TOOLTIP if isTeamReady else CHAT.CHANNELS_SQUADNOTREADY_TOOLTIP))
        self.__handleAddPreBattleRequest(clientID, currCarouselItemCtx._asdict())


g_eventDispatcher = EventDispatcher()
