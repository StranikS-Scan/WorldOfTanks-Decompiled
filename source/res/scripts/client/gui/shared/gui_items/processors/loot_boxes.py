# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/loot_boxes.py
import logging
from copy import copy
import BigWorld
from gui import SystemMessages
from gui.gift_system.wrappers import OpenedGiftData
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared import g_eventBus
from gui.shared.events import GiftSystemOperationEvent
from gui.shared.gui_items.processors import Processor, makeI18nError
from helpers import dependency
from messenger.formatters.service_channel import QuestAchievesFormatter
from skeletons.gui.system_messages import ISystemMessages
from skeletons.new_year import INewYearController
from items.components.ny_constants import CurrentNYConstants
_logger = logging.getLogger(__name__)

class LootBoxOpenProcessor(Processor):
    __systemMessages = dependency.descriptor(ISystemMessages)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, lootBoxItem, count=1):
        super(LootBoxOpenProcessor, self).__init__()
        self.__lootBox = lootBoxItem
        self.__count = count
        self.__prevCollectedToys = self.__nyController.getAllCollectedToysId()

    def _errorHandler(self, code, errStr='', ctx=None):
        defaultKey = 'lootboxes/open/server_error'
        return makeI18nError('/'.join((defaultKey, errStr)), defaultKey)

    def _successHandler(self, code, ctx=None):
        bonuses = getMergedBonusesFromDicts(ctx['bonus'])
        ctx['giftsInfo'] = [ OpenedGiftData(*item) for item in ctx.get('giftsInfo', []) ]
        fmt = QuestAchievesFormatter.formatQuestAchieves(bonuses, False)
        if fmt is not None:
            if ctx['giftsInfo']:
                eventCtx = {'lootbox': self.__lootBox,
                 'giftsInfo': copy(ctx['giftsInfo']),
                 'fmtBonuses': fmt}
                g_eventBus.handleEvent(GiftSystemOperationEvent(GiftSystemOperationEvent.GIFT_OPENED, ctx=eventCtx))
            else:
                SystemMessages.pushMessage(fmt, SystemMessages.SM_TYPE.LootBoxRewards)
        for bonuses in ctx['bonus']:
            nyToys = bonuses.get(CurrentNYConstants.TOYS)
            if nyToys is None:
                continue
            for toyId, toyData in nyToys.iteritems():
                toyData['newCount'] = 0 if toyId in self.__prevCollectedToys else 1
                self.__prevCollectedToys.add(toyId)

        return super(LootBoxOpenProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to open loot box by id: %r, count: %d', self.__lootBox, self.__count)
        BigWorld.player().tokens.openLootBox(self.__lootBox.getID(), self.__count, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
