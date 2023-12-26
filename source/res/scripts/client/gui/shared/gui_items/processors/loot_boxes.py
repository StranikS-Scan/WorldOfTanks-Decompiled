# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/loot_boxes.py
import logging
import BigWorld
from gui import SystemMessages
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared.gui_items.processors import Processor, makeI18nError
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from messenger.formatters.service_channel import QuestAchievesFormatter, InvoiceReceivedFormatter
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
        fmt = QuestAchievesFormatter.formatQuestAchieves(bonuses, False, processCompensations=False)
        if fmt is not None:
            SystemMessages.pushMessage(fmt, SystemMessages.SM_TYPE.LootBoxRewards, priority=NotificationPriorityLevel.LOW)
        compensationStr = InvoiceReceivedFormatter.getVehiclesCompensationString(bonuses.get('vehicles', []), htmlTplPostfix='QuestsReceived')
        if compensationStr:
            SystemMessages.pushMessage(compensationStr, SystemMessages.SM_TYPE.LootBoxCompensation, priority=NotificationPriorityLevel.HIGH)
        for bonuses in ctx['bonus']:
            nyToys = bonuses.get(CurrentNYConstants.TOYS)
            if nyToys is None:
                continue
            for toysData in nyToys.itervalues():
                newCount = 0
                for toyId in toysData.iterkeys():
                    if toyId not in self.__prevCollectedToys:
                        newCount += 1
                        self.__prevCollectedToys.add(toyId)

                toysData['newCount'] = newCount

        return super(LootBoxOpenProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to open loot box by id: %r, count: %d', self.__lootBox, self.__count)
        BigWorld.player().tokens.openLootBox(self.__lootBox.getID(), self.__count, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class LootBoxGetInfoProcessor(Processor):

    def __init__(self, lootBoxes):
        super(LootBoxGetInfoProcessor, self).__init__()
        self.__lootBoxes = lootBoxes

    def _request(self, callback):
        lootboxIDs = [ item.getID() for item in self.__lootBoxes ]
        _logger.debug('Make server request to get info about loot boxes by ids %r', lootboxIDs)
        BigWorld.player().tokens.getInfoLootBox(lootboxIDs, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
