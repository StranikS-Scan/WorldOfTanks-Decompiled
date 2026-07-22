# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/shared/event_dispatcher.py
import logging
from gui.impl.pub.notification_commands import WindowNotificationCommand, Priority
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.gui_items.Vehicle import getNationLessName
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import INotificationWindowController
from tank_academy.gui.impl.lobby.tank_academy.tank_academy_welcome_view import TankAcademyWelcomeViewWindow
from th_async import th_async, th_await
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showTankAcademyReward(ctx=None, notificationMgr=None):
    from tank_academy.gui.impl.lobby.tank_academy.tank_academy_rewards_view import TankAcademyRewardsViewWindow
    if ctx is not None:
        window = TankAcademyRewardsViewWindow(ctx=ctx)
        notificationMgr.append(WindowNotificationCommand(window, Priority.HIGH))
    else:
        _logger.error('No context for Tank academy rewards View')
    return


@dependency.replace_none_kwargs(settingsCore=ISettingsCore, notificationMgr=INotificationWindowController)
def showTankAcademy(settingsCore=None, notificationMgr=None):
    if not settingsCore.serverSettings.isTankAcademyWelcomeScreenShown():
        window = TankAcademyWelcomeViewWindow()
        notificationMgr.append(WindowNotificationCommand(window, Priority.HIGH))
    else:
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MISSIONS), ctx={'tab': QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS,
         'openMainView': True}), scope=EVENT_BUS_SCOPE.LOBBY)


def showTankAcademyVehicleSelection(offerToken=None, forceCreate=False):
    kwargs = {'tab': QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS,
     'openVehicleSelection': True,
     'tokenID': offerToken,
     'forceCreate': forceCreate}
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MISSIONS), ctx=kwargs), scope=EVENT_BUS_SCOPE.LOBBY)


@th_async
def showTankAcademyDelayedConfirmationDialog(vehicle, vehiclesLevel, callback=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from tank_academy.gui.impl.lobby.tank_academy.tank_academy_exchange_rewards import TankAcademyExchangeRewards
    vehicleUserName = vehicle.userName
    vehicleName = getNationLessName(vehicle.name)
    result = yield th_await(dialogs.showSimple(FullScreenDialogWindowWrapper(TankAcademyExchangeRewards(vehicleName, vehicleUserName, vehiclesLevel))))
    callback(result)
