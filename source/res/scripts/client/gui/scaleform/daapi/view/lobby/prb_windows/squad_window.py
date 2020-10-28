# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/squad_window.py
from constants import PREBATTLE_TYPE
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import getDifficultyStars
from gui.Scaleform.daapi.view.meta.SquadWindowMeta import SquadWindowMeta
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from gui.prb_control import settings
from gui.prb_control.formatters import messages
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import i18n

@stored_window(DATA_TYPE.UNIQUE_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)
class SquadWindow(SquadWindowMeta):

    def __init__(self, ctx=None):
        super(SquadWindow, self).__init__()
        self._isInvitesOpen = ctx.get('isInvitesOpen', False)

    def getPrbType(self):
        return PREBATTLE_TYPE.SQUAD

    def onWindowMinimize(self):
        self.destroy()

    @property
    def squadViewComponent(self):
        return self.components.get(self._getSquadViewAlias())

    def onUnitRejoin(self):
        self.as_enableWndCloseBtnS(not self.prbEntity.hasLockedState())

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.as_enableWndCloseBtnS(not self.prbEntity.hasLockedState())

    def onUnitPlayerOnlineStatusChanged(self, pInfo):
        if pInfo.isOffline():
            key = settings.UNIT_NOTIFICATION_KEY.PLAYER_OFFLINE
        else:
            key = settings.UNIT_NOTIFICATION_KEY.PLAYER_ONLINE
        self.__addPlayerNotification(key, pInfo)

    def onUnitPlayerAdded(self, pInfo):
        if not pInfo.isInvite():
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_ADDED, pInfo)

    def onUnitPlayerRemoved(self, pInfo):
        if not pInfo.isInvite():
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_REMOVED, pInfo)

    def onUnitPlayerBecomeCreator(self, pInfo):
        if pInfo.isCurrentPlayer():
            self._showLeadershipNotification()
        chat = self.chat
        if chat:
            chat.as_addMessageS(messages.getUnitPlayerNotification(settings.UNIT_NOTIFICATION_KEY.GIVE_LEADERSHIP, pInfo))

    def _populate(self):
        self.as_setComponentIdS(self._getSquadViewAlias())
        super(SquadWindow, self)._populate()
        self.as_setWindowTitleS(self._getTitle())
        self.addListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__handleSquadWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)

    def _getTitle(self):
        return ''.join((i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_SQUAD), i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_SQUAD_RANDOMBATTLE)))

    def _dispose(self):
        self.removeListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__handleSquadWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        super(SquadWindow, self)._dispose()

    def _showLeadershipNotification(self):
        pass

    def _getSquadViewAlias(self):
        return PREBATTLE_ALIASES.SQUAD_VIEW_PY

    def __handleSquadWindowHide(self, _):
        self.destroy()

    def __addPlayerNotification(self, key, pInfo):
        chat = self.chat
        if chat and not pInfo.isCurrentPlayer():
            chat.as_addMessageS(messages.getUnitPlayerNotification(key, pInfo))


class EventSquadWindow(SquadWindow):

    def getPrbType(self):
        return PREBATTLE_TYPE.EVENT

    def _getTitle(self):
        return ''.join((i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_SQUAD), i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_SQUAD_EVENT)))

    def _addPlayerDifficultyLevelNotification(self, key, username, level):
        chat = self.chat
        if chat:
            chat.as_addMessageS(i18n.makeString(SYSTEM_MESSAGES.unit_notification(key), userName=username, level=level))

    def onUnitPlayerStateChanged(self, pInfo):
        if not pInfo.isReady and not pInfo.isCommander():
            self._addPlayerDifficultyLevelNotification(settings.UNIT_NOTIFICATION_KEY.NOT_READY_DIFFICULTY_LEVEL, pInfo.getFullName(), getDifficultyStars(pInfo.maxDifficultyLevel))

    def onUnitPlayerInfoChanged(self, pInfo):
        if pInfo.isCommander():
            self._addPlayerDifficultyLevelNotification(settings.UNIT_NOTIFICATION_KEY.SELECTED_DIFFICULTY_LEVEL, pInfo.getFullName(), getDifficultyStars(pInfo.difficultyLevel))

    def onUnitPlayerAdded(self, pInfo):
        if not pInfo.isInvite():
            chat = self.chat
            if chat and not pInfo.isCurrentPlayer():
                chat.as_addMessageS(messages.getUnitPlayerNotification(settings.UNIT_NOTIFICATION_KEY.EVENT_PLAYER_ADDED, pInfo))

    def onUnitPlayerRemoved(self, pInfo):
        if not pInfo.isInvite():
            chat = self.chat
            if chat and not pInfo.isCurrentPlayer():
                chat.as_addMessageS(messages.getUnitPlayerNotification(settings.UNIT_NOTIFICATION_KEY.EVENT_PLAYER_REMOVED, pInfo))

    def _getSquadViewAlias(self):
        return PREBATTLE_ALIASES.EVENT_SQUAD_VIEW_PY


class EpicSquadWindow(SquadWindow):

    def getPrbType(self):
        return PREBATTLE_TYPE.EPIC

    def _getTitle(self):
        return ''.join((i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_SQUAD), i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_SQUAD_EPIC)))

    def _getSquadViewAlias(self):
        return PREBATTLE_ALIASES.EPIC_SQUAD_VIEW_PY


class BattleRoyaleSquadWindow(SquadWindow):

    def _getTitle(self):
        return ''.join((i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_SQUAD), i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_SQUAD_BATTLEROYALE)))

    def getPrbType(self):
        return PREBATTLE_TYPE.BATTLE_ROYALE

    def _getSquadViewAlias(self):
        return PREBATTLE_ALIASES.BATTLE_ROYALE_SQUAD_VIEW_PY
