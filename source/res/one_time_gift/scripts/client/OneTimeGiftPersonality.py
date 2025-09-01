# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/OneTimeGiftPersonality.py
from debug_utils import LOG_DEBUG
from one_time_gift.gui import gui_constants
from one_time_gift.gui.game_control import registerOneTimeGiftController
from one_time_gift.gui.gui_constants import ONE_TIME_GIFT_TOOLTIP_SET
from gui.shared.system_factory import registerScaleformLobbyPackages, registerMessengerClientFormatter, registerLobbyTooltipsBuilders
from one_time_gift.notification import registerOTGNotificationsListeners
from one_time_gift.messenger.formatters.service_channel import OneTimeGiftVehiclesReceiveFormatter, OneTimeGiftAdditionalRewardsReceiveFormatter, OneTimeGiftCollectorRewardsReceiveFormatter

def registerMessengerClientFormatters():
    registerMessengerClientFormatter(gui_constants.SCH_CLIENT_MSG_TYPE.OTG_VEHICLES_RECEIVED, OneTimeGiftVehiclesReceiveFormatter())
    registerMessengerClientFormatter(gui_constants.SCH_CLIENT_MSG_TYPE.OTG_ADDITIONAL_REWARDS_RECEIVED, OneTimeGiftAdditionalRewardsReceiveFormatter())
    registerMessengerClientFormatter(gui_constants.SCH_CLIENT_MSG_TYPE.OTG_COLLECTOR_REWARDS_RECEIVED, OneTimeGiftCollectorRewardsReceiveFormatter())


def preInit():
    LOG_DEBUG('preInit personality:', __name__)
    registerOneTimeGiftController()
    registerScaleformLobbyPackages(('one_time_gift.gui.impl.lobby',))
    registerOTGNotificationsListeners()
    registerMessengerClientFormatters()
    registerLobbyTooltipsBuilders((('one_time_gift.gui.scaleform.daapi.view.tooltips.tooltip_builders', ONE_TIME_GIFT_TOOLTIP_SET),))


def init():
    pass


def start():
    pass


def fini():
    pass
