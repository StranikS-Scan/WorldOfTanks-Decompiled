# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/football_buffon_lobby_button.py
from gui.shared.events import LoadViewEvent
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.Scaleform.daapi.view.meta.BuffonLobbyButtonMeta import BuffonLobbyButtonMeta
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers import i18n
from skeletons.gui.game_control import IFootballMetaGame
from skeletons.gui.server_events import IEventsCache
from football_hangar_common import getHangarBuffonTooltip
_BUFFON_INVISIBLE, _BUFFON_NOT_AVAILABLE, _BUFFON_AVAILABLE, _BUFFON_RECRUITED = range(4)
_BUTTON_CLICK_MAP = {_BUFFON_INVISIBLE: VIEW_ALIAS.FOOTBALL_CARD_COLLECTION,
 _BUFFON_NOT_AVAILABLE: VIEW_ALIAS.FOOTBALL_CARD_COLLECTION,
 _BUFFON_AVAILABLE: VIEW_ALIAS.FOOTBALL_BUFFON_RECRUITMENT_PANEL,
 _BUFFON_RECRUITED: VIEW_ALIAS.FOOTBALL_CARD_COLLECTION}

class BuffonLobbyButton(BuffonLobbyButtonMeta):
    eventsCache = dependency.descriptor(IEventsCache)
    footballMetaGame = dependency.descriptor(IFootballMetaGame)

    def __init__(self):
        super(BuffonLobbyButton, self).__init__()
        self.__state = _BUFFON_NOT_AVAILABLE
        self.__visible = True

    def _populate(self):
        super(BuffonLobbyButton, self)._populate()
        self.eventsCache.onSyncCompleted += self.__onEventsSyncCompleted
        self.footballMetaGame.onMilestoneReached += self.__onMilestoneReached
        self.__state = self.__getState()
        self.__initButton()
        self.__updateUI()

    def _dispose(self):
        self.eventsCache.onSyncCompleted -= self.__onEventsSyncCompleted
        self.footballMetaGame.onMilestoneReached -= self.__onMilestoneReached
        super(BuffonLobbyButton, self)._dispose()

    def buttonIsClicked(self):
        alias = _BUTTON_CLICK_MAP[self.__state]
        self.fireEvent(LoadViewEvent(alias), EVENT_BUS_SCOPE.LOBBY)

    def __getState(self):
        if self.eventsCache.isEventEnabled():
            if self.footballMetaGame.isBuffonRecruited():
                return _BUFFON_RECRUITED
            if self.footballMetaGame.isBuffonAvailable():
                return _BUFFON_AVAILABLE
            return _BUFFON_NOT_AVAILABLE
        return _BUFFON_AVAILABLE if self.footballMetaGame.isBuffonAvailable() else _BUFFON_INVISIBLE

    def __onEventsSyncCompleted(self, *args):
        self.__updateState()

    def __onMilestoneReached(self, *args):
        self.__updateState()

    def __initButton(self):
        buffonLobbyButtonVO = {'notEarnedStr': text_styles.stats(i18n.makeString(FOOTBALL2018.CARDCOLLECTION_LOBBY_BUTTON_BUFFON_NOT_RECEIVED)),
         'notAssignedYetStr': text_styles.stats(i18n.makeString(FOOTBALL2018.CARDCOLLECTION_LOBBY_BUTTON_EARNED_BUFFON_BUT_NOT_RECRUITED)),
         'hasBuffonCrew': self.__state == _BUFFON_RECRUITED,
         'hasBuffonCard': self.__state == _BUFFON_AVAILABLE,
         'tooltip': getHangarBuffonTooltip(self.footballMetaGame.isBuffonAvailable(), self.footballMetaGame.isBuffonRecruited())}
        self.as_initButtonS(buffonLobbyButtonVO)

    def __updateState(self):
        state = self.__getState()
        if state != self.__state:
            self.__state = state
            self.__updateUI()

    def __updateUI(self):
        if self.__state == _BUFFON_INVISIBLE:
            self.__setVisible(False)
        else:
            if self.__state == _BUFFON_AVAILABLE:
                self.as_haveBuffonCardS()
            elif self.__state == _BUFFON_RECRUITED:
                self.as_crewmanBuffonAssignedS()
            self.__setVisible(True)

    def __setVisible(self, visible):
        if self.__visible != visible:
            self.__visible = visible
            if visible:
                self.as_showBuffonS()
            else:
                self.as_hideBuffonS()
