# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/FightButton.py
from CurrentVehicle import g_currentVehicle
from account_helpers import isDemonstrator
from adisp import process
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings import VIEW_ALIAS
from gui.Scaleform.framework import AppRef, ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.formatters.tooltips import getActionDisabledTooltip
from gui.prb_control.context import PrebattleAction
from gui.prb_control.prb_helpers import GlobalListener
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared import EVENT_BUS_SCOPE, events, g_eventsCache
from gui.shared.events import ShowWindowEvent
from gui.shared.utils.requesters import StatsRequester
from gui.Scaleform.daapi.view.meta.FightButtonMeta import FightButtonMeta
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FightButton(FightButtonMeta, DAAPIModule, GlobalListener, AppRef):

    def __init__(self):
        super(FightButton, self).__init__()
        self.__menuPrbLabels = {PREBATTLE_TYPE.SQUAD: MENU.HEADERBUTTONS_BATTLE_MENU_SQUAD,
         PREBATTLE_TYPE.TRAINING: MENU.HEADERBUTTONS_BATTLE_MENU_TRAINING,
         PREBATTLE_TYPE.COMPANY: MENU.HEADERBUTTONS_BATTLE_MENU_TEAM,
         PREBATTLE_TYPE.CLAN: MENU.HEADERBUTTONS_BATTLE_MENU_BATTLE_SESSION,
         PREBATTLE_TYPE.TOURNAMENT: MENU.HEADERBUTTONS_BATTLE_MENU_BATTLE_SESSION,
         PREBATTLE_TYPE.UNIT: MENU.HEADERBUTTONS_BATTLE_MENU_UNIT}
        self.__menuQueueLabels = {QUEUE_TYPE.RANDOMS: MENU.HEADERBUTTONS_BATTLE_MENU_STANDART,
         QUEUE_TYPE.HISTORICAL: MENU.HEADERBUTTONS_BATTLE_MENU_HISTORICAL,
         QUEUE_TYPE.EVENT_BATTLES: MENU.HEADERBUTTONS_BATTLE_MENU_STANDART}
        self.__actionsLockedInViews = {VIEW_ALIAS.BATTLE_QUEUE, VIEW_ALIAS.LOBBY_TRAININGS, VIEW_ALIAS.LOBBY_TRAINING_ROOM}
        self.__currentLockedView = None
        self.__isActionsLocked = False
        return

    @process
    def _populate(self):
        self.__currentLockedView = None
        super(FightButton, self)._populate()
        g_currentVehicle.onChanged += self.update
        g_eventsCache.onSyncCompleted += self.update
        self.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdate, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.startGlobalListening()
        g_clientUpdateManager.addCallbacks({'account.attrs': self.updateDemonstratorButton})
        accountAttrs = yield StatsRequester().getAccountAttrs()
        self.updateDemonstratorButton(accountAttrs)
        return

    def _dispose(self):
        self.__currentLockedView = None
        super(FightButton, self)._dispose()
        g_currentVehicle.onChanged -= self.update
        g_eventsCache.onSyncCompleted -= self.update
        self.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdate, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def update(self):
        prbDispatcher = g_prbLoader.getDispatcher()
        if not prbDispatcher:
            return
        else:
            playerInfo = prbDispatcher.getPlayerInfo()
            isCreator = playerInfo.isCreator
            funcState = prbDispatcher.getFunctionalState()
            inPrebattle = funcState.isInPrebattle()
            inUnit = funcState.isInUnit(PREBATTLE_TYPE.UNIT)
            inSortie = funcState.isInUnit(PREBATTLE_TYPE.SORTIE)
            inPreQueue = funcState.isInPreQueue()
            isTraining = funcState.isInPrebattle(PREBATTLE_TYPE.TRAINING)
            disableHint = None
            disabled = False
            if self.__isActionsLocked:
                disabled = True
            else:
                canDo, restriction = prbDispatcher.canPlayerDoAction()
                if not canDo:
                    disabled = True
                    disableHint = getActionDisabledTooltip(restriction, functional=prbDispatcher.getPrbFunctional())
            self.__disableFightButton(disabled, disableHint)
            label = MENU.HEADERBUTTONS_BATTLE
            if not isTraining and not isCreator and (inPrebattle or inUnit or inSortie):
                if playerInfo.isReady:
                    label = MENU.HEADERBUTTONS_NOTREADY
                else:
                    label = MENU.HEADERBUTTONS_READY
            if inUnit:
                menu = MENU.HEADERBUTTONS_BATTLE_MENU_UNIT
            elif inSortie:
                menu = MENU.HEADERBUTTONS_BATTLE_TYPES_FORT
            elif inPrebattle:
                menu = self.__menuPrbLabels.get(funcState.entityTypeID, MENU.HEADERBUTTONS_BATTLE_MENU_STANDART)
            elif inPreQueue:
                menu = self.__menuQueueLabels.get(funcState.entityTypeID)
            else:
                menu = MENU.HEADERBUTTONS_BATTLE_MENU_STANDART
            if self.__currentLockedView == VIEW_ALIAS.LOBBY_TRAININGS:
                menu = MENU.HEADERBUTTONS_BATTLE_MENU_TRAINING
            self.as_setFightButtonS(label, menu, [], self.__currentLockedView != VIEW_ALIAS.BATTLE_QUEUE)
            self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.UPDATE_TANK_PARAMS), scope=EVENT_BUS_SCOPE.LOBBY)
            return

    def __onViewAddedToContainer(self, _, pyEntity):
        settings = pyEntity.settings
        if settings.type is ViewTypes.LOBBY_SUB:
            alias = settings.alias
            if alias == VIEW_ALIAS.BATTLE_LOADING:
                return
            if alias in self.__actionsLockedInViews:
                self.__isActionsLocked = True
                self.__currentLockedView = alias
            else:
                self.__isActionsLocked = False
                self.__currentLockedView = None
            self.update()
        return

    def __handleFightButtonUpdate(self, _):
        self.update()

    def fightClick(self, mapID = None, actionName = ''):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            dispatcher.doAction(PrebattleAction(actionName, mapID=mapID))
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')
        return

    def __disableFightButton(self, isDisabled, toolTip):
        self.as_disableFightButtonS(isDisabled, toolTip)

    def updateDemonstratorButton(self, accountAttrs):
        self.as_setDemonstratorButtonS(isDemonstrator(accountAttrs))

    def demoClick(self):
        demonstratorWindow = self.app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.DEMONSTRATOR_WINDOW})
        if demonstratorWindow is not None:
            demonstratorWindow.onWindowClose()
        else:
            self.fireEvent(ShowWindowEvent(ShowWindowEvent.SHOW_DEMONSTRATOR_WINDOW))
        return

    def onPreQueueSettingsChanged(self, diff):
        self.update()

    def __handleSetPrebattleCoolDown(self, event):
        prbDispatcher = g_prbLoader.getDispatcher()
        if not prbDispatcher:
            return
        playerInfo = prbDispatcher.getPlayerInfo()
        isCreator = playerInfo.isCreator
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE and not isCreator:
            self.as_setCoolDownForReadyS(event.coolDown)
