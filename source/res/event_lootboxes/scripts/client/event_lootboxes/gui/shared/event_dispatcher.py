# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/shared/event_dispatcher.py
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from skeletons.gui.game_control import IEventLootBoxesController
from skeletons.gui.impl import IGuiLoader

def showEventLootBoxesWelcomeScreen():
    from event_lootboxes.gui.impl.lobby.event_lootboxes.welcome_screen import EventLootBoxesWelcomeScreenWindow
    uiLoader = dependency.instance(IGuiLoader)
    existingView = uiLoader.windowsManager.getViewByLayoutID(R.views.event_lootboxes.lobby.event_lootboxes.WelcomeScreen())
    if existingView:
        return
    eventLootBoxesCtrl = dependency.instance(IEventLootBoxesController)
    if eventLootBoxesCtrl.isActive() and eventLootBoxesCtrl.isLootBoxesAvailable():
        window = EventLootBoxesWelcomeScreenWindow()
        window.load()


def showEventLootBoxOpenWindow(boxType, rewards):
    from event_lootboxes.gui.impl.lobby.event_lootboxes.open_box_screen import EventLootBoxesOpenBoxScreenWindow
    uiLoader = dependency.instance(IGuiLoader)
    existingView = uiLoader.windowsManager.getViewByLayoutID(R.views.event_lootboxes.lobby.event_lootboxes.OpenBoxScreen())
    if existingView:
        existingView.update(boxType=boxType, rewards=rewards)
    else:
        window = EventLootBoxesOpenBoxScreenWindow(boxType=boxType, rewards=rewards)
        window.load()


def showEventLootBoxOpenErrorWindow():
    from event_lootboxes.gui.impl.lobby.event_lootboxes.open_box_error import EventLootBoxesOpenBoxErrorWindow
    window = EventLootBoxesOpenBoxErrorWindow()
    window.load()
    SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.lootboxes.open.server_error.DISABLED()), priority=NotificationPriorityLevel.MEDIUM, type=SystemMessages.SM_TYPE.Error)
