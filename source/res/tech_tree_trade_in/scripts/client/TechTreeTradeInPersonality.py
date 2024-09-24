# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/TechTreeTradeInPersonality.py
from debug_utils import LOG_DEBUG
from gui.shared.system_factory import registerMessengerClientFormatter
from tech_tree_trade_in.gui import gui_constants
from tech_tree_trade_in.messenger.formatters.service_channel import TechTreeTradeInCompletedFormatter, TechTreeTradeInDetailsFormatter
from tech_tree_trade_in import account_settings
from tech_tree_trade_in.gui.game_control import registerTradeInController
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig

def registerMessengerClientFormatters():
    registerMessengerClientFormatter(gui_constants.SCH_CLIENT_MSG_TYPE.TECH_TREE_TRADE_IN_COMPLETED_NOTIFICATION, TechTreeTradeInCompletedFormatter())
    registerMessengerClientFormatter(gui_constants.SCH_CLIENT_MSG_TYPE.TECH_TREE_TRADE_IN_DETAILS_NOTIFICATION, TechTreeTradeInDetailsFormatter())


def preInit():
    LOG_DEBUG('preInit personality:', __name__)
    registerTradeInController()
    registerMessengerClientFormatters()


def init():
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, ['tech_tree_trade_in.gui.scaleform.daapi.view.lobby'])
    account_settings.init()


def start():
    pass


def fini():
    pass
