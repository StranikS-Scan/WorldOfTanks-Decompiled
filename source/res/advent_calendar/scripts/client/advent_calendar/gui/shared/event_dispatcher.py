# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/shared/event_dispatcher.py
import logging
from BWUtil import AsyncReturn
from advent_calendar.skeletons.game_controller import IAdventCalendarController
from frameworks.wulf import WindowLayer
from gui.impl.pub.notification_commands import EventNotificationCommand, NotificationEvent
from helpers import dependency
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.system_messages import ISystemMessages
from wg_async import wg_await, wg_async
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(controller=IAdventCalendarController)
def showAdventCalendarMainWindow(controller=None):
    from advent_calendar.gui.impl.lobby.feature.main_view import AdventCalendarMainWindow
    if AdventCalendarMainWindow.getInstances() or not controller.isAvailable():
        _logger.warning('Can not open the AdventMainView. Feature is not active or view is already opened.')
        return
    AdventCalendarMainWindow().load()


def showAdventCalendarIntroWindow(**kwargs):
    from advent_calendar.gui.impl.lobby.feature.intro_view import AdventCalendarIntroWindow
    if not AdventCalendarIntroWindow.getInstances():
        AdventCalendarIntroWindow(**kwargs).load()


def showRewardWindow(**kwargs):
    from advent_calendar.gui.impl.lobby.feature.reward_view import AdventCalendarRewardWindow
    if AdventCalendarRewardWindow.getInstances():
        _logger.warning('Can not open the AdventCalendarRewardWindow. View is already opened.')
        return
    AdventCalendarRewardWindow(**kwargs).load()


@wg_async
def showPurchaseDialogWindow(dayId=1, price=0, parent=None):
    from gui.impl.pub.dialog_window import DialogButtons
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from gui.impl.dialogs import dialogs
    from advent_calendar.gui.impl.lobby.feature.purchase_dialog_view import PurchaseDialogView
    wrapper = FullScreenDialogWindowWrapper(PurchaseDialogView(dayId, price), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW, doBlur=False)
    result = yield wg_await(dialogs.show(wrapper))
    result = None if result.result == DialogButtons.CANCEL else result.data
    raise AsyncReturn(result)
    return


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def pushAvailableDoorsMessage(data, notificationMgr=None):
    notificationMgr.append(EventNotificationCommand(NotificationEvent(method=showAvailableDoorsNotification, data=data)))


@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def showAvailableDoorsNotification(data, systemMessages=None):
    systemMessages.proto.serviceChannel.pushClientMessage({'data': data,
     'template': data.pop('template'),
     'notificationGuiSettings': {'onlyPopUp': False,
                                 'isNotify': False}}, msgType=SCH_CLIENT_MSG_TYPE.NY_GF_SM_TYPE)
