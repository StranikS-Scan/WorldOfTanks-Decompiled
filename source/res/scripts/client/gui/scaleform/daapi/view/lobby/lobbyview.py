# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/LobbyView.py
import BigWorld
import VOIP
import constants
import CommandMapping
from PlayerEvents import g_playerEvents
from gui import game_control, SystemMessages
import gui
from gui.LobbyContext import g_lobbyContext
from gui.battle_control import g_sessionProvider
from gui.Scaleform.daapi.view.meta.LobbyPageMeta import LobbyPageMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared import EVENT_BUS_SCOPE, events, event_dispatcher as shared_events
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.utils.functions import getViewName
from helpers import i18n

class LobbyView(LobbyPageMeta):
    VIEW_WAITING = (VIEW_ALIAS.LOBBY_HANGAR,
     VIEW_ALIAS.LOBBY_INVENTORY,
     VIEW_ALIAS.LOBBY_SHOP,
     VIEW_ALIAS.LOBBY_PROFILE,
     VIEW_ALIAS.LOBBY_BARRACKS,
     PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY,
     PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY,
     VIEW_ALIAS.LOBBY_CUSTOMIZATION,
     VIEW_ALIAS.LOBBY_RESEARCH,
     VIEW_ALIAS.LOBBY_TECHTREE,
     FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_ALIAS,
     VIEW_ALIAS.BATTLE_QUEUE,
     VIEW_ALIAS.BATTLE_LOADING)

    class COMPONENTS:
        HEADER = 'lobbyHeader'

    def __init__(self, ctx = None):
        super(LobbyView, self).__init__(ctx)
        self.__currIgrType = constants.IGR_TYPE.NONE

    def getSubContainerType(self):
        return ViewTypes.LOBBY_SUB

    def _populate(self):
        View._populate(self)
        self.__currIgrType = gui.game_control.g_instance.igr.getRoomType()
        g_prbLoader.setEnabled(True)
        self.addListener(events.LobbySimpleEvent.SHOW_HELPLAYOUT, self.__showHelpLayout, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.LobbySimpleEvent.CLOSE_HELPLAYOUT, self.__closeHelpLayout, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.GameEvent.SCREEN_SHOT_MADE, self.__handleScreenShotMade, EVENT_BUS_SCOPE.GLOBAL)
        g_playerEvents.onVehicleBecomeElite += self.__onVehicleBecomeElite
        self.app.loaderManager.onViewLoadInit += self.__onViewLoadInit
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.app.loaderManager.onViewLoadError += self.__onViewLoadError
        game_control.g_instance.igr.onIgrTypeChanged += self.__onIgrTypeChanged
        self.__showBattleResults()
        battlesCount = g_itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()
        g_lobbyContext.updateBattlesCount(battlesCount)
        self.fireEvent(events.GUICommonEvent(events.GUICommonEvent.LOBBY_VIEW_LOADED))
        keyCode = CommandMapping.g_instance.get('CMD_VOICECHAT_MUTE')
        if not BigWorld.isKeyDown(keyCode):
            VOIP.getVOIPManager().setMicMute(True)

    def _dispose(self):
        game_control.g_instance.igr.onIgrTypeChanged -= self.__onIgrTypeChanged
        self.app.loaderManager.onViewLoadError -= self.__onViewLoadError
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        self.app.loaderManager.onViewLoadInit -= self.__onViewLoadInit
        g_playerEvents.onVehicleBecomeElite -= self.__onVehicleBecomeElite
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
        if alias != VIEW_ALIAS.BATTLE_LOADING and alias in self.VIEW_WAITING:
            Waiting.hide('loadPage')

    def __showBattleResults(self):
        battleCtx = g_sessionProvider.getCtx()
        if battleCtx.lastArenaUniqueID:
            shared_events.showMyBattleResults(battleCtx.lastArenaUniqueID)
            battleCtx.lastArenaUniqueID = None
        return
