# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/wot_anniversary_helpers.py
from account_helpers.AccountSettings import GUI_START_BEHAVIOR, AccountSettings, WotAnniversary15
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from shared_utils import first
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.wot_anniversary import IWotAnniversaryController

def setWelcomeScreenShown(isShown):
    settings = AccountSettings.getFilter(GUI_START_BEHAVIOR)
    settings[GuiSettingsBehavior.WOT_ANNIVERSARY_15_WELCOME_SHOWN] = isShown
    AccountSettings.setFilter(GUI_START_BEHAVIOR, settings)


def isWelcomeScreenShown():
    return AccountSettings.getFilter(GUI_START_BEHAVIOR).get(GuiSettingsBehavior.WOT_ANNIVERSARY_15_WELCOME_SHOWN, False)


def getWotAnniversarySetting(settingName):
    return AccountSettings.getSettings(WotAnniversary15.SETTINGS).get(settingName)


def setWotAnniversarySetting(settingName, settingValue):
    settings = AccountSettings.getSettings(WotAnniversary15.SETTINGS)
    settings.update({settingName: settingValue})
    AccountSettings.setSettings(WotAnniversary15.SETTINGS, settings)


@dependency.replace_none_kwargs(wotAnniversaryController=IWotAnniversaryController, notificationMgr=INotificationWindowController)
def showWelcomeScreen(wotAnniversaryController=None, notificationMgr=None):
    from gui.impl.lobby.wot_anniversary.welcome_view import WelcomeWindow
    if wotAnniversaryController.isEnabled() and not isWelcomeScreenShown():
        notificationMgr.append(WindowNotificationCommand(WelcomeWindow()))
        setWelcomeScreenShown(True)


def showWotAnniversaryMainView():
    from gui.impl.lobby.wot_anniversary.main_view import MainWindow
    windows = MainWindow.getInstances()
    if not windows:
        window = MainWindow()
        window.load()


def showImageView(parent=None, **kwargs):
    from gui.impl.lobby.wot_anniversary.image_view import ImageWindow
    windows = ImageWindow.getInstances()
    if not windows:
        window = ImageWindow(parent=parent, **kwargs)
        window.load()
    else:
        first(windows).tryFocus()


def pushErrorSysMessage():
    SystemMessages.pushMessage(backport.text(R.strings.wot_anniversary.notifications.serverError.description()), type=SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)


def showRegularRewardView(bonuses, parent=None, closeCallback=None):
    from gui.impl.lobby.wot_anniversary.regular_reward_view import RegularRewardWindow
    window = RegularRewardWindow(parent=parent, closeCallback=closeCallback, bonuses=bonuses)
    window.load()


def showProgressionRewardView(parent=None, *args, **kwargs):
    from gui.impl.lobby.wot_anniversary.progression_reward_view import ProgressionRewardWindow
    window = ProgressionRewardWindow(parent=parent, *args, **kwargs)
    window.load()
