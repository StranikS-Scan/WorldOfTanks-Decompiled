# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/award_window_controller.py
from weakref import proxy
from functools import partial
from gui import makeHtmlString
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers import dependency
from gui.app_loader import sf_lobby
from skeletons.gui.server_events import IEventsCache
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.events import GUICommonEvent
from gui.shared.utils import isPopupsWindowsOpenDisabled
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.EVENT import EVENT
from gui.server_events.awards_formatters import getEventAwardFormatter
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.server_events.awards_formatters import AWARDS_SIZES
_SNDID_ACHIEVEMENT_GENERAL_AWARDS = 'ev_2019_secret_event_1_hangar_event_next_level'
_SNDID_ACHIEVEMENT_FRONT_AWARDS = 'result_screen_achievements'

class GameEventAwardWindowController(CallbackDelayer):
    settingsCore = dependency.descriptor(ISettingsCore)
    eventsCache = dependency.descriptor(IEventsCache)
    _CALLBACK_SHOW_AWARD_WAIT_TIME = 2

    def __init__(self, gameEventController):
        super(GameEventAwardWindowController, self).__init__()
        self._lobbyInited = False
        self._gameEventController = proxy(gameEventController)

    def start(self):
        self._lobbyInited = False
        self._gameEventController.onProgressChanged += self._onProgressChanged
        self.eventsCache.onSyncCompleted += self._onProgressChanged
        g_eventBus.addListener(GUICommonEvent.LOBBY_VIEW_LOADED, self._onLobbyInited)

    def stop(self):
        self._lobbyInited = False
        self._gameEventController.onProgressChanged -= self._onProgressChanged
        self.eventsCache.onSyncCompleted -= self._onProgressChanged
        g_eventBus.removeListener(GUICommonEvent.LOBBY_VIEW_LOADED, self._onLobbyInited)
        self.destroy()

    @sf_lobby
    def app(self):
        return None

    def _onLobbyInited(self, _):
        self._lobbyInited = True
        self._onProgressChanged()

    def _onProgressChanged(self):
        if not self._lobbyInited or isPopupsWindowsOpenDisabled():
            self.delayCallback(self._CALLBACK_SHOW_AWARD_WAIT_TIME, self._onProgressChanged)
            return
        self.stopCallback(self._onProgressChanged)
        messages = self._getMessages()
        self._showAwardWindow(messages)

    def _getMessages(self):
        messages = self._getGeneralAwards()
        messages.extend(self._getFrontAwards())
        return messages

    def _getGeneralAwards(self):
        gameEventController = self._gameEventController
        messages = []
        for general in gameEventController.getGenerals().itervalues():
            generalID = general.getID()
            curLevel = general.getCurrentProgressLevel()
            for level in range(1, curLevel + 1):
                if not general.isLevelAwardShown(level):
                    description = makeHtmlString('html_templates:event', 'rewardFront', {'message': _ms(EVENT.getGeneralRewardLevel(level))})
                    bonuses = general.items[level].getBonuses()
                    buyBonusQuest = general.items[level].getCorrespondBonusQuest()
                    if buyBonusQuest and buyBonusQuest.isCompleted():
                        bonuses.extend(buyBonusQuest.getBonuses())
                    messages.append({'iconPath': RES_ICONS.getGeneralLevelRewardIcon(generalID, level),
                     'title': _ms(EVENT.getGeneralTooltipHeader(generalID)),
                     'description': description,
                     'buttonLabel': _ms(EVENT.FINAL_REWARD_CONTINUE),
                     'bonuses': bonuses,
                     'soundID': _SNDID_ACHIEVEMENT_GENERAL_AWARDS,
                     'callback': self._onClose(partial(general.setLevelAwardIsShown, level))})

        return messages

    def _getFrontAwards(self):
        gameEventController = self._gameEventController
        messages = []
        for front in gameEventController.getFronts().itervalues():
            for ind, item in enumerate(front.items):
                if front.isAwardShown(ind) or not item.isCompleted():
                    continue
                bonuses = item.getBonuses()
                formatedBonuses = getEventAwardFormatter().format(bonuses)
                if not formatedBonuses:
                    continue
                bonus = formatedBonuses[0]
                description = makeHtmlString('html_templates:event', 'rewardFront', {'message': bonus.userName})
                messages.append({'iconPath': bonus.images[AWARDS_SIZES.EVENT_REWARD],
                 'title': _ms(EVENT.GENERALS_REWARDRECEIVED),
                 'description': description,
                 'buttonLabel': _ms(EVENT.FINAL_REWARD_CONTINUE),
                 'bonuses': bonuses if len(bonuses) > 1 else [],
                 'soundID': _SNDID_ACHIEVEMENT_FRONT_AWARDS,
                 'callback': self._onClose(partial(front.setAwardIsShown, ind))})

        return messages

    def _showAwardWindow(self, messages):
        if not messages:
            return
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LINKEDSET_HINTS, ctx={'messages': messages,
         'withBlur': True}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onClose(self, callback):

        def func():
            if callback:
                callback()
            view = self._getChapterView()
            if view:
                messages = self._getMessages()
                view.updateMessages(messages)

        return func

    def _getChapterView(self):
        windowContainer = self.app.containerManager.getContainer(ViewTypes.OVERLAY)
        return windowContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LINKEDSET_HINTS})
