# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/WinbackPersonality.py
from constants_utils import AbstractBattleMode
from debug_utils import LOG_DEBUG
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from winback.gui import gui_constants
from winback.gui.gui_constants import SM_TYPE_WINBACK_PROGRESSION, SCH_CLIENT_MSG_TYPE
from winback.gui.game_control.awards_controller import registerWinbackProgressionAwardController
from winback.gui.Scaleform import registerWinbackTooltipsBuilders

class ClientWinbackBattleMode(AbstractBattleMode):
    _SM_TYPES = [SM_TYPE_WINBACK_PROGRESSION]

    @property
    def _client_gameControllers(self):
        from skeletons.gui.game_control import IWinbackController
        from winback.gui.game_control.winback_controller import WinbackController
        return ((IWinbackController, WinbackController, False),)

    @property
    def _client_notificationListeners(self):
        from winback.notification import listeners
        return (listeners.WinbackSelectableRewardReminder,)

    @property
    def _client_notificationActionHandlers(self):
        from winback.notification import actions_handlers as handlers
        return (handlers.ShowWinbackProgressionActionHandler, handlers.OpenWinbackSelectableRewardView, handlers.OpenWinbackSelectableRewardViewFromQuest)

    @property
    def _client_messengerClientFormatters(self):
        from winback.messenger.formatters import service_channel as sc
        return {SCH_CLIENT_MSG_TYPE.WINBACK_PROGRESSION_NOTIFICATIONS: sc.WinbackProgressionSystemMessageFormatter(),
         SCH_CLIENT_MSG_TYPE.WINBACK_SELECTABLE_REWARD: sc.WinbackSelectedAward()}


def preInit():
    battleMode = ClientWinbackBattleMode(__name__)
    battleMode.registerGameControllers()
    battleMode.registerSystemMessagesTypes()
    battleMode.registerClientNotificationListeners()
    battleMode.registerClientNotificationHandlers()
    battleMode.registerMessengerClientFormatters(gui_constants)
    battleMode.registerClientTokenQuestsSubFormatters()
    registerWinbackProgressionAwardController()
    registerWinbackTooltipsBuilders()


def init():
    LOG_DEBUG('init', __name__)
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, ['winback.gui.Scaleform.daapi.view.lobby'])


def start():
    pass


def fini():
    pass
