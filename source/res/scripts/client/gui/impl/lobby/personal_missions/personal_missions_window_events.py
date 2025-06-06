# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/personal_missions_window_events.py
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PersonalMissions
from frameworks.wulf import WindowFlags, WindowLayer, ViewFlags
from gui import GUI_SETTINGS
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_rewards_view_model import CompletedQuestsType
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_main_quests_view_model import PageViewIdEnum
from helpers import dependency
from skeletons.gui.impl import INotificationWindowController
_logger = logging.getLogger(__name__)
PM3_INFO_PAGE = 'pm3InfoPage'
SERVER_SETTINGS_KEYS = ('disabledPMOperations', 'disabledPersonalMissions', 'isPM3QuestEnabled')

def checkIntroSeen():

    def decorator(func):

        def wrapper(*args, **kwargs):
            if not AccountSettings.getPersonalMissions(PersonalMissions.INTRO_SEEN):
                showIntroView()
                showIntroVideoView()
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


@checkIntroSeen()
def showPersonalMissionsOperationWindow(*args):
    from gui.impl.lobby.personal_missions.personal_missions_main_quests_view import PersonalMissionsMainQuestsView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.personal_missions.PersonalMissionsMainQuestsView(), PersonalMissionsMainQuestsView, ScopeTemplates.LOBBY_SUB_SCOPE), *args), scope=EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionsMainQuestsWindow(*args):
    from gui.impl.lobby.personal_missions.personal_missions_main_quests_view import PersonalMissionsMainQuestsView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.personal_missions.PersonalMissionsMainQuestsView(), PersonalMissionsMainQuestsView, ScopeTemplates.LOBBY_SUB_SCOPE), *args), scope=EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionsRewardsSelectionWindow(questId=0, onRewardsReceivedCallback=None, onCloseCallback=None):
    from gui.impl.lobby.personal_missions.personal_missions_rewards_selection_view import PersonalMissionsRewardsSelectionWindow
    window = PersonalMissionsRewardsSelectionWindow(questId, onRewardsReceivedCallback, onCloseCallback)
    window.load()


def showPersonalMissionsVehicleView(operationId):
    from gui.impl.lobby.personal_missions.personal_missions_vehicle_view import PersonalMissionsVehicleView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.personal_missions.PersonalMissionsVehicleView(), PersonalMissionsVehicleView, ScopeTemplates.LOBBY_SUB_SCOPE), operationId=operationId), scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showPersonalMissionsVideoRewardView(operationId, addToQueue=False, notificationMgr=None):
    from gui.impl.lobby.personal_missions.personal_missions_video_rewards_view import PersonalMissionsVideoRewardsViewWindow
    window = PersonalMissionsVideoRewardsViewWindow(operationId)
    if addToQueue:
        notificationMgr.append(WindowNotificationCommand(window))
    else:
        window.load()


def showIntroView():
    from gui.impl.lobby.personal_missions.personal_missions_intro_view import PersonalMissionsIntroViewWindow
    window = PersonalMissionsIntroViewWindow()
    window.load()


def showIntroVideoView():
    from gui.impl.lobby.personal_missions.personal_missions_intro_video_view import PersonalMissionsIntroVideoWindow
    window = PersonalMissionsIntroVideoWindow()
    window.load()


def showQuestViewById(questId, operationId):
    showPersonalMissionsMainQuestsWindow(PageViewIdEnum.QUEST, operationId, questId)


def showPersonalMissionsWebbrg(keyWord, parent=None, returnClb=None):
    settings = GUI_SETTINGS.personalMissions.get(keyWord, {})
    if not settings.get('isEnabled', False):
        return
    else:
        url = settings.get('url')
        if url is None:
            _logger.error('[showPersonalMissionsIntroWebbrg]: %s URL is missed, check gui_settings.xml', keyWord)
            return
        window = LobbyWindow(content=__createPersonalMissionsBrowserView(url=url, viewFlags=ViewFlags.VIEW, returnClb=returnClb), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, parent=parent, layer=WindowLayer.OVERLAY)
        window.load()
        return


def __createPersonalMissionsBrowserView(url, viewFlags, returnClb=None):
    from gui.impl.lobby.common.browser_view import BrowserView, makeSettings
    from web.web_client_api import webApiCollection, ui, sound, request
    webHandlers = webApiCollection(request.RequestWebApi, ui.OpenWindowWebApi, ui.CloseWindowWebApi, ui.OpenTabWebApi, ui.UtilWebApi, sound.SoundWebApi, sound.HangarSoundWebApi)
    settings = makeSettings(url=url, webHandlers=webHandlers, viewFlags=viewFlags, restoreBackground=True, returnClb=returnClb)
    return BrowserView(R.views.lobby.common.BrowserView(), settings)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showPersonalMissionsRewardsView(qID, selectedBonuses=None, viewType=CompletedQuestsType.COMPLETE, addToQueue=False, notificationMgr=None):
    from gui.impl.lobby.personal_missions.personal_missions_rewards_view import PersonalMissionsRewardsWindow
    window = PersonalMissionsRewardsWindow(qID, selectedBonuses, viewType)
    if addToQueue:
        notificationMgr.append(WindowNotificationCommand(window))
    else:
        window.load()


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showOperationAdditionRewardsView(operationID, addToQueue=False, notificationMgr=None):
    from gui.impl.lobby.personal_missions.personal_missions_rewards_view import PersonalMissionsRewardsWindow
    window = PersonalMissionsRewardsWindow(operationID=operationID)
    if addToQueue:
        notificationMgr.append(WindowNotificationCommand(window))
    else:
        window.load()
