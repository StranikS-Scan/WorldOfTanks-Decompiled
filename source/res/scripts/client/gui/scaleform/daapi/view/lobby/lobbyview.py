# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/LobbyView.py
from account_helpers.AccountSettings import AccountSettings, CHRISTMAS_STARTED, CHRISTMAS_FINISHED, CHRISTMAS_PAUSED, CHRISTMAS_STARTED_AGAIN
import constants
import gui
from PlayerEvents import g_playerEvents
from gui import SystemMessages
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.LobbyPageMeta import LobbyPageMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.locale.CHRISTMAS import CHRISTMAS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.christmas.christmas_controller import g_christmasCtrl
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared import EVENT_BUS_SCOPE, events, event_dispatcher as shared_events
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.events import OpenLinkEvent
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.utils.functions import getViewName
from helpers import i18n, dependency
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IIGRController
from christmas_shared import EVENT_STATE

class LobbyView(LobbyPageMeta):
    VIEW_WAITING = (VIEW_ALIAS.LOBBY_HANGAR,
     VIEW_ALIAS.LOBBY_INVENTORY,
     VIEW_ALIAS.LOBBY_STORE,
     VIEW_ALIAS.LOBBY_PROFILE,
     VIEW_ALIAS.LOBBY_BARRACKS,
     PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY,
     PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY,
     VIEW_ALIAS.LOBBY_CUSTOMIZATION,
     VIEW_ALIAS.VEHICLE_PREVIEW,
     VIEW_ALIAS.VEHICLE_COMPARE,
     VIEW_ALIAS.LOBBY_RESEARCH,
     VIEW_ALIAS.LOBBY_TECHTREE,
     FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_ALIAS,
     VIEW_ALIAS.BATTLE_QUEUE,
     VIEW_ALIAS.LOBBY_ACADEMY,
     VIEW_ALIAS.LOBBY_CHRISTMAS)

    class COMPONENTS:
        HEADER = 'lobbyHeader'

    igrCtrl = dependency.descriptor(IIGRController)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, ctx=None):
        super(LobbyView, self).__init__(ctx)
        self.__currIgrType = constants.IGR_TYPE.NONE

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def getSubContainerType(self):
        return ViewTypes.LOBBY_SUB

    def _populate(self):
        View._populate(self)
        self.__currIgrType = self.igrCtrl.getRoomType()
        g_prbLoader.setEnabled(True)
        self.addListener(events.LobbySimpleEvent.SHOW_HELPLAYOUT, self.__showHelpLayout, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.LobbySimpleEvent.CLOSE_HELPLAYOUT, self.__closeHelpLayout, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.GameEvent.SCREEN_SHOT_MADE, self.__handleScreenShotMade, EVENT_BUS_SCOPE.GLOBAL)
        g_playerEvents.onVehicleBecomeElite += self.__onVehicleBecomeElite
        self.app.loaderManager.onViewLoadInit += self.__onViewLoadInit
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.app.loaderManager.onViewLoadError += self.__onViewLoadError
        self.igrCtrl.onIgrTypeChanged += self.__onIgrTypeChanged
        self.__showBattleResults()
        battlesCount = g_itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()
        g_lobbyContext.updateBattlesCount(battlesCount)
        g_christmasCtrl.onEventStarted += self.__updateChristmasState
        g_christmasCtrl.onEventStopped += self.__updateChristmasState
        self.fireEvent(events.GUICommonEvent(events.GUICommonEvent.LOBBY_VIEW_LOADED))
        self.bwProto.voipController.invalidateMicrophoneMute()
        self.__checkChristmasState()

    def _dispose(self):
        self.igrCtrl.onIgrTypeChanged -= self.__onIgrTypeChanged
        self.app.loaderManager.onViewLoadError -= self.__onViewLoadError
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        self.app.loaderManager.onViewLoadInit -= self.__onViewLoadInit
        g_playerEvents.onVehicleBecomeElite -= self.__onVehicleBecomeElite
        g_christmasCtrl.onEventStarted -= self.__updateChristmasState
        g_christmasCtrl.onEventStopped -= self.__updateChristmasState
        self.removeListener(events.LobbySimpleEvent.SHOW_HELPLAYOUT, self.__showHelpLayout, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.LobbySimpleEvent.CLOSE_HELPLAYOUT, self.__closeHelpLayout, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.GameEvent.SCREEN_SHOT_MADE, self.__handleScreenShotMade, EVENT_BUS_SCOPE.GLOBAL)
        View._dispose(self)

    def __showHelpLayout(self, _):
        self.as_showHelpLayoutS()

    def __closeHelpLayout(self, _):
        self.as_closeHelpLayoutS()

    def __handleScreenShotMade(self, event):
        if 'path' not in event.ctx:
            return
        SystemMessages.pushMessage(i18n.makeString('#menu:screenshot/save') % {'path': event.ctx['path']}, SystemMessages.SM_TYPE.Information)

    def __onVehicleBecomeElite(self, vehTypeCompDescr):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.ELITE_WINDOW, getViewName(VIEW_ALIAS.ELITE_WINDOW, vehTypeCompDescr), {'vehTypeCompDescr': vehTypeCompDescr}), EVENT_BUS_SCOPE.LOBBY)

    def moveSpace(self, dx, dy, dz):
        if g_hangarSpace.space:
            g_hangarSpace.space.handleMouseEvent(int(dx), int(dy), int(dz))

    def notifyCursorOver3dScene(self, isOver3dScene):
        self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': isOver3dScene}))

    def __onViewLoadInit(self, view):
        if view is not None and view.settings is not None:
            self.__subViewTransferStart(view.settings.alias)
        return

    def __onViewLoaded(self, view):
        if view is not None and view.settings is not None:
            self.__subViewTransferStop(view.settings.alias)
        return

    def __onViewLoadError(self, name, msg, item):
        if item is not None and item.pyEntity is not None:
            self.__subViewTransferStop(item.pyEntity.settings.alias)
        return

    def __onIgrTypeChanged(self, roomType, xpFactor):
        icon = gui.makeHtmlString('html_templates:igr/iconSmall', 'premium')
        if roomType == constants.IGR_TYPE.PREMIUM:
            SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.IGR_CUSTOMIZATION_BEGIN, igrIcon=icon), type=SystemMessages.SM_TYPE.Information)
        elif roomType in [constants.IGR_TYPE.BASE, constants.IGR_TYPE.NONE] and self.__currIgrType == constants.IGR_TYPE.PREMIUM:
            SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.IGR_CUSTOMIZATION_END, igrIcon=icon), type=SystemMessages.SM_TYPE.Information)
        self.__currIgrType = roomType

    def __subViewTransferStart(self, alias):
        if alias in self.VIEW_WAITING:
            Waiting.show('loadPage')

    def __subViewTransferStop(self, alias):
        if alias in self.VIEW_WAITING:
            Waiting.hide('loadPage')

    def __showBattleResults(self):
        battleCtx = self.sessionProvider.getCtx()
        if battleCtx.lastArenaUniqueID:
            shared_events.showMyBattleResults(battleCtx.lastArenaUniqueID)
            battleCtx.lastArenaUniqueID = None
        return

    def __updateChristmasState(self, *args):
        self.__checkChristmasState()

    def __checkChristmasState(self):
        if g_christmasCtrl.getGlobalState() == EVENT_STATE.IN_PROGRESS:
            if not AccountSettings.getSettings(CHRISTMAS_STARTED):
                SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.CHRISTMAS_EVENT_STARTED), type=SystemMessages.SM_TYPE.Information)
                if not constants.IS_CHINA:
                    self.fireEvent(OpenLinkEvent(OpenLinkEvent.NY_RULES, title=i18n.makeString(CHRISTMAS.NYMARATHON_PROMO_TITLE)))
                AccountSettings.setSettings(CHRISTMAS_STARTED, True)
            elif AccountSettings.getSettings(CHRISTMAS_PAUSED) and not AccountSettings.getSettings(CHRISTMAS_STARTED_AGAIN):
                SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.CHRISTMAS_EVENT_INPROGRESSAGAIN), type=SystemMessages.SM_TYPE.Information)
                AccountSettings.setSettings(CHRISTMAS_STARTED_AGAIN, True)
                AccountSettings.setSettings(CHRISTMAS_PAUSED, False)
        elif g_christmasCtrl.getGlobalState() == EVENT_STATE.SUSPENDED:
            if not AccountSettings.getSettings(CHRISTMAS_PAUSED):
                SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.CHRISTMAS_EVENT_SUSPENDED), type=SystemMessages.SM_TYPE.Information)
                AccountSettings.setSettings(CHRISTMAS_PAUSED, True)
                AccountSettings.setSettings(CHRISTMAS_STARTED_AGAIN, False)
        elif g_christmasCtrl.getGlobalState() == EVENT_STATE.FINISHED and not AccountSettings.getSettings(CHRISTMAS_FINISHED):
            SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.CHRISTMAS_EVENT_FINISHED), type=SystemMessages.SM_TYPE.Information)
            AccountSettings.setSettings(CHRISTMAS_FINISHED, True)
