# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/messenger/formatters/collections_by_type.py
from chat_shared import SYS_MESSAGE_TYPE as _SM_TYPE
from gui.shared.system_factory import registerMessengerClientFormatter, registerMessengerServerFormatter
from gui_lootboxes.gui.lb_gui_constants import SCH_CLIENT_MSG_TYPE
from gui_lootboxes.messenger.formatters import auto_boxes_subformatters
from gui_lootboxes.messenger.formatters.service_channel import LootBoxOpenedFormatter, LootBoxAutoOpenFormatter
from debug_utils import LOG_DEBUG
_AUTO_BOXES_SUB_FORMATTERS = [auto_boxes_subformatters.EventBoxesFormatter(), auto_boxes_subformatters.EventLootBoxesFormatter()]

def registerLootBoxClientFormatters():
    registerMessengerClientFormatter(SCH_CLIENT_MSG_TYPE.LB_OPENED, LootBoxOpenedFormatter())


def registerLootBoxServerFormatters():
    registerMessengerServerFormatter(_SM_TYPE.lootBoxesAutoOpenReward.index(), LootBoxAutoOpenFormatter(subFormatters=_AUTO_BOXES_SUB_FORMATTERS))


def registerAutoBoxesSubFormatter(formatter):
    LOG_DEBUG('formatter {} added to AUTO_BOXES_SUB_FORMATTERS'.format(formatter.__class__.__name__))
    _AUTO_BOXES_SUB_FORMATTERS.append(formatter)
