# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_helper.py
import BigWorld
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.requesters.tokens_requester import TOTAL_KEY
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

def showRestrictedSysMessage():

    def _showRestrictedSysMessage():
        SystemMessages.pushMessage(text=backport.text(R.strings.lootboxes.restrictedMessage.body()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.lootboxes.restrictedMessage.header())})

    BigWorld.callback(0.0, _showRestrictedSysMessage)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def getLootboxCount(itemsCache=None, lobbyContext=None):
    itemsByType = itemsCache.items.tokens.getLootBoxesCountByType()
    totalCount = 0
    for boxType in EventLootBoxes.ALL():
        categories = itemsByType.get(boxType, {})
        totalCount += categories.get(TOTAL_KEY, 0)

    return totalCount
