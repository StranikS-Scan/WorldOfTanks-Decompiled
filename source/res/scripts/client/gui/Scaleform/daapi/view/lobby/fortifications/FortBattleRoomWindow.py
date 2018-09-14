# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBattleRoomWindow.py
import BigWorld
from UnitBase import UNIT_BROWSER_ERROR
from UnitBase import UNIT_OP
from adisp import process
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui import DialogsInterface, SystemMessages
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.dialogs.rally_dialog_meta import UnitConfirmDialogMeta
from gui.Scaleform.daapi.view.meta.FortBattleRoomWindowMeta import FortBattleRoomWindowMeta
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES as I18N_SYSTEM_MESSAGES
from gui.Scaleform.managers.windows_stored_data import stored_window, DATA_TYPE, TARGET_ID
from gui.prb_control import settings, prbPeripheriesHandlerProperty
from gui.prb_control.entities.fort.unit.fort_battle.ctx import CreateOrJoinFortBattleCtx
from gui.prb_control.entities.fort.unit.sortie.ctx import CreateSortieCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.formatters import messages
from gui.prb_control.formatters.windows import SwitchPeripheryFortCtx
from gui.prb_control.entities.base.unit.ctx import JoinUnitCtx, AutoSearchUnitCtx, DeclineSearchUnitCtx, BattleQueueUnitCtx
from gui.prb_control.items.sortie_items import getDivisionNameByUnit
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES, PREBATTLE_ACTION_NAME
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import FortEvent
from gui.shared.fortifications.fort_listener import FortListener
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from gui.shared.utils import getPlayerDatabaseID
from helpers import i18n
from messenger.storage import storage_getter

@stored_window(DATA_TYPE.UNIQUE_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)
class FortBattleRoomWindow(FortBattleRoomWindowMeta, FortListener):

    def __init__(self, ctx=None):
        self.__isMinimize = False
        super(FortBattleRoomWindow, self).__init__()

    @prbPeripheriesHandlerProperty
    def prbPeripheriesHandler(self):
        return None

    def onWindowMinimize(self):
        self.__isMinimize = True
        g_eventDispatcher.showUnitProgressInCarousel(self.getPrbType())
        self.destroy()

    def getIntroViewAlias(self):
        return FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_INTRO_VIEW_UI

    def getBrowserViewAlias(self, prbType):
        if prbType == PREBATTLE_TYPE.SORTIE:
            return FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_LIST_VIEW_UI
        return FORTIFICATION_ALIASES.FORT_CLAN_BATTLE_LIST_VIEW_UI if prbType == PREBATTLE_TYPE.FORT_BATTLE else None

    def getRoomViewAlias(self, prbType):
        if prbType == PREBATTLE_TYPE.FORT_BATTLE:
            return FORTIFICATION_ALIASES.FORT_CLAN_BATTLE_ROOM_VIEW_UI
        return FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_VIEW_UI if prbType == PREBATTLE_TYPE.SORTIE else None

    def getFlashAliases(self):
        return FORTIFICATION_ALIASES.FLASH_ALIASES

    def getPythonAliases(self):
        return FORTIFICATION_ALIASES.PYTHON_ALIASES

    def getPrbType(self):
        return PREBATTLE_TYPE.FORT_COMMON

    def onBrowseRallies(self):
        self._doSelect(PREBATTLE_ACTION_NAME.SORTIES_LIST)

    def onBrowseClanBattles(self):
        self._doSelect(PREBATTLE_ACTION_NAME.FORT_BATTLES_LIST)

    def onJoinClanBattle(self, battleID, slotIndex, peripheryID):
        self.__handleCreateOrJoinFortBattle(peripheryID, battleID, slotIndex)

    def onCreatedBattleRoom(self, battleID, peripheryID):
        self.__handleCreateOrJoinFortBattle(peripheryID, battleID)

    def onCreateRally(self):
        if not BigWorld.player().isLongDisconnectedFromCenter:
            sortiesAvailable, severAvailable = self.fortProvider.getController().getSortiesCurfewCtrl().getStatus()
            if not severAvailable:
                g_eventDispatcher.showSwitchPeripheryWindow(ctx=SwitchPeripheryFortCtx())
            elif sortiesAvailable:
                self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)
            else:
                LOG_ERROR('Sorties is not Available at this moment')
        else:
            SystemMessages.pushI18nMessage('#system_messages:fortification/errors/CENTER_NOT_AVAILABLE', type=SystemMessages.SM_TYPE.Error)

    def onJoinRally(self, rallyId, slotIndex, peripheryID):
        ctx = JoinUnitCtx(rallyId, PREBATTLE_TYPE.SORTIE, slotIndex, waitingID='prebattle/join')
        if g_lobbyContext.isAnotherPeriphery(peripheryID):
            if g_lobbyContext.isPeripheryAvailable(peripheryID):
                self.__requestToReloginAndJoinSortie(peripheryID, ctx)
            else:
                SystemMessages.pushI18nMessage('#system_messages:periphery/errors/isNotAvailable', type=SystemMessages.SM_TYPE.Error)
        else:
            self.__requestToJoinSortie(ctx)

    def autoSearchCancel(self, value):
        self.currentState = value
        if value == CYBER_SPORT_ALIASES.AUTO_SEARCH_COMMANDS_STATE or value == CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE or value == CYBER_SPORT_ALIASES.AUTO_SEARCH_WAITING_PLAYERS_STATE:
            self.prbEntity.request(AutoSearchUnitCtx(action=0))
        elif value == CYBER_SPORT_ALIASES.AUTO_SEARCH_CONFIRMATION_STATE:
            self.prbEntity.request(DeclineSearchUnitCtx())
        elif value == CYBER_SPORT_ALIASES.AUTO_SEARCH_ENEMY_STATE:
            self.prbEntity.request(BattleQueueUnitCtx(action=0))

    def onUnitPlayerAdded(self, pInfo):
        if not pInfo.isInvite():
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_ADDED, pInfo)

    def onUnitPlayerRemoved(self, pInfo):
        if not pInfo.isInvite():
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_REMOVED, pInfo)

    def onClientStateChanged(self, state):
        if self.prbEntity.getID() == 0 and state.getStateID() == CLIENT_FORT_STATE.DISABLED:
            self.onWindowClose()

    def __addPlayerNotification(self, key, pInfo):
        chat = self.chat
        if chat and not pInfo.isCurrentPlayer():
            chat.as_addMessageS(messages.getUnitPlayerNotification(key, pInfo))

    def onUnitFlagsChanged(self, flags, timeLeft):
        if self.prbEntity.hasLockedState():
            if flags.isInQueue():
                self.as_enableWndCloseBtnS(False)
                self.currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_ENEMY_STATE
            else:
                LOG_ERROR('View for modal state is not resolved', flags)
            self.__initState(timeLeft=timeLeft)
        else:
            self.__clearState()

    def onUnitErrorReceived(self, errorCode):
        self.as_autoSearchEnableBtnS(True)

    def onUnitAutoSearchFinished(self):
        self.__clearState()

    def onUnitBrowserErrorReceived(self, errorCode):
        if errorCode == UNIT_BROWSER_ERROR.ACCEPT_TIMEOUT:
            self.currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE
            self.__initState()
        else:
            self.as_autoSearchEnableBtnS(True)

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        if pInfo.isCurrentPlayer():
            self.as_changeAutoSearchBtnsStateS(pPermissions.canInvokeAutoSearch(), pPermissions.canStopBattleQueue())

    def onUnitRejoin(self):
        self.__clearState()
        self.__clearCache()

    def onUnitRosterChanged(self):
        super(FortBattleRoomWindow, self).onUnitRosterChanged()
        chat = self.chat
        if chat:
            _, unit = self.prbEntity.getUnit()
            commanderID = unit.getCommanderDBID()
            if commanderID != getPlayerDatabaseID():
                getter = storage_getter('users')
                commander = getter().getUser(commanderID)
                if commander is None:
                    return
                division = getDivisionNameByUnit(unit)
                divisionName = i18n.makeString(I18N_SYSTEM_MESSAGES.unit_notification_divisiontype(division))
                key = I18N_SYSTEM_MESSAGES.UNIT_NOTIFICATION_CHANGEDIVISION
                txt = i18n.makeString(key, name=commander.getName(), division=divisionName)
                chat.addNotification(txt)
        return

    def onUnitSettingChanged(self, opCode, value):
        if opCode == UNIT_OP.CHANGE_DIVISION:
            unitMgrID = self.prbEntity.getID()
            if unitMgrID > 0:
                self._loadRoomView(self.prbEntity.getEntityType())

    def _populate(self):
        super(FortBattleRoomWindow, self)._populate()
        from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.SORTIE)
        self.addListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__handleUnitWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(FortEvent.CHOICE_DIVISION, self.__onDivisionSet, scope=EVENT_BUS_SCOPE.LOBBY)
        self.prbEntity.initEvents(self)
        g_eventDispatcher.hideUnitProgressInCarousel(self.getPrbType())
        self.startFortListening()

    def _dispose(self):
        self.stopFortListening()
        self.removeListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__handleUnitWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(FortEvent.CHOICE_DIVISION, self.__onDivisionSet, scope=EVENT_BUS_SCOPE.LOBBY)
        super(FortBattleRoomWindow, self)._dispose()

    def __clearCache(self):
        if not self.__isMinimize and self.fortCtrl is not None:
            self.fortCtrl.removeSortiesCache()
            self.fortCtrl.removeFortBattlesCache()
        return

    @process
    def __requestToCreateSortie(self, division):
        yield self.prbDispatcher.create(CreateSortieCtx(division, 'fort/sortie/create'))

    @process
    def __requestToReloginAndJoinSortie(self, peripheryID, ctx):
        result = yield DialogsInterface.showDialog(UnitConfirmDialogMeta(PREBATTLE_TYPE.UNIT, 'changePeriphery', messageCtx={'host': g_lobbyContext.getPeripheryName(peripheryID)}))
        if result:
            self.prbPeripheriesHandler.join(peripheryID, ctx)

    @process
    def __requestToJoinSortie(self, ctx):
        yield self.prbDispatcher.join(ctx)

    def __handleCreateOrJoinFortBattle(self, peripheryID, battleID, slotIndex=-1):
        if g_lobbyContext.isAnotherPeriphery(peripheryID):
            if g_lobbyContext.isPeripheryAvailable(peripheryID):
                self.__requestToReloginAndCreateOrJoinFortBattle(peripheryID, battleID, slotIndex)
            else:
                SystemMessages.pushI18nMessage('#system_messages:periphery/errors/isNotAvailable', type=SystemMessages.SM_TYPE.Error)
        else:
            self.__requestToCreateOrJoinFortBattle(battleID, slotIndex)

    @process
    def __requestToCreateOrJoinFortBattle(self, battleID, slotIndex=-1):
        yield self.prbDispatcher.join(CreateOrJoinFortBattleCtx(battleID, slotIndex, 'fort/fortBattle/createOrJoin'))

    @process
    def __requestToReloginAndCreateOrJoinFortBattle(self, peripheryID, battleID, slotIndex=-1):
        result = yield DialogsInterface.showDialog(UnitConfirmDialogMeta(PREBATTLE_TYPE.FORT_BATTLE, 'changePeriphery', messageCtx={'host': g_lobbyContext.getPeripheryName(peripheryID)}))
        if result:
            self.prbPeripheriesHandler.join(peripheryID, CreateOrJoinFortBattleCtx(battleID, slotIndex, 'fort/fortBattle/createOrJoin'))

    def __onDivisionSet(self, event):
        divisionLevel = event.ctx.get('data', None)
        if divisionLevel:
            self.__requestToCreateSortie(divisionLevel)
        return

    def __handleUnitWindowHide(self, _):
        self.destroy()

    def __initState(self, timeLeft=0, acceptDelta=0):
        model = None
        if self.isPlayerInSlot():
            if self.currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_ENEMY_STATE:
                model = self.__createAutoUpdateModel(self.currentState, timeLeft, '', [])
            elif self.currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE:
                model = self.__createAutoUpdateModel(self.currentState, 0, '', [])
        if model is not None:
            self.as_changeAutoSearchStateS(model)
        return

    def __clearState(self):
        self.currentState = ''
        self.as_enableWndCloseBtnS(True)
        self.as_hideAutoSearchS()

    def __createAutoUpdateModel(self, state, countDownSeconds, ctxMessage, playersReadiness):
        permissions = self.prbEntity.getPermissions(unitIdx=self.prbEntity.getUnitIdx())
        model = {'state': state,
         'countDownSeconds': countDownSeconds,
         'contextMessage': ctxMessage,
         'playersReadiness': playersReadiness,
         'canInvokeAutoSearch': permissions.canInvokeAutoSearch(),
         'canInvokeBattleQueue': permissions.canStopBattleQueue()}
        return model
