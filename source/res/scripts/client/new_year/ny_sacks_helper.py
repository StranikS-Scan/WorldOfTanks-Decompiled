# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_sacks_helper.py
import logging
from collections import namedtuple
import typing
from Event import Event, EventManager
from adisp import adisp_process
from constants import Configs
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.server_events.bonuses import getNonQuestBonuses, CrewBooksBonus, ItemsBonus
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from helpers import dependency, time_utils
from items.components.component_constants import EMPTY_STRING
from items.components.ny_constants import NySackLootBox, NY_SACK_CATEGORY_TO_LEVEL
from new_year.celebrity.celebrity_quests_helpers import getDogLevel
from new_year.ny_constants import GuestsQuestsTokens, NyGFNotificationTemplates
from ny_common.NYDogConfig import NYDogConfig
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.loot_box import LootBox
    from typing import Generator, Tuple, Optional, List
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)
_SACK_QUEST_NAME = 'ny_battle_quest'
_SACK_QUEST_TOKEN = 'ny_battle_quest_complete'
_DEFAULT_QUEST_COUNT = 3

def sacksQuestsFilter(quests):
    for questName in quests:
        if questName.startswith('ny_dog_sack'):
            yield questName


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getNYDogConfig(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearDogConfig()


SackInfo = namedtuple('SackInfo', ('level', 'count'))

class NYSacksHelper(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self):
        self._eManager = EventManager()
        self.onUpdated = Event(self._eManager)
        self.onSackOpened = Event(self._eManager)
        self.__sacks = tuple()
        self.__boxBonusesInfo = {}
        self.__onOpenProcess = False

    def onLobbyInited(self):
        self.__addEventHandlers()

    def clear(self):
        self._eManager.clear()
        self.__removeEventHandlers()

    def __addEventHandlers(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensChanged})
        self.__eventsCache.onSyncCompleted += self.onUpdated

    def __removeEventHandlers(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__eventsCache.onSyncCompleted -= self.onUpdated

    def getSacks(self):
        self.__buildSacksInfo()
        return tuple(self.__getSackModelVO())

    def getSacksCount(self):
        totalCount = 0
        for item in self.getSacks():
            totalCount += item.count

        return totalCount

    def getMissionsCompleted(self):
        return self.__itemsCache.items.tokens.getTokenCount(_SACK_QUEST_TOKEN)

    @classmethod
    def getBoxPrices(cls, level):
        config = getNYDogConfig()
        price = config.getLevelPrice(level - 1)
        return price.items()[0] if price else ('credits', 0)

    def getMissionsTotal(self):
        quests = self.__eventsCache.getAllQuests(lambda q: q.getID().startswith(_SACK_QUEST_NAME))
        return len(quests) if quests else _DEFAULT_QUEST_COUNT

    @classmethod
    def getMissionsCountDown(cls):
        return time_utils.getDayTimeLeft()

    def getMissionsDescription(self):
        quests = self.__eventsCache.getAllQuests(lambda q: q.getID().startswith(_SACK_QUEST_NAME))
        for quest in quests.values():
            return quest.getDescription()

        return EMPTY_STRING

    def getAllBoxes(self):

        def _sortFunc(item):
            return NySackLootBox.ALL.index(item.getCategory()) if item.getCategory() in NySackLootBox.ALL else len(NySackLootBox.ALL)

        allSacks = []
        for sack in self.__itemsCache.items.tokens.getLootBoxes().values():
            if sack.getType() == NySackLootBox.TYPE and sack.getCategory() in NySackLootBox.ALL:
                allSacks.append(sack)

        allSacks.sort(key=_sortFunc)
        return allSacks

    def getBoxBonusesInfo(self, category):
        if not any(self.__boxBonusesInfo):
            self.__buildLBoxBonusesInfo()
        return self.__boxBonusesInfo.get(category, [])

    def onOpenBox(self):
        sack = self.__getFirstAvailableSack()
        if sack.getInventoryCount() > 0 and self.__isSackSuitable(sack):
            self.__requestLootBoxOpen(sack)

    @classmethod
    def __tokenFilterFn(cls, token):
        return token.startswith(GuestsQuestsTokens.TOKEN_DOG) or token.startswith('lootBox:')

    def __onTokensChanged(self, tokens):
        if any((self.__tokenFilterFn(token) for token in tokens)):
            self.__buildSacksInfo()
            self.onUpdated()

    def __onServerSettingsChanged(self, diff):
        if Configs.NY_DOG_CONFIG.value in diff or 'lootBoxes_config' in diff:
            self.__update()
            self.onUpdated()

    def __update(self):
        self.__buildLBoxBonusesInfo()
        self.__buildSacksInfo()

    def __buildLBoxBonusesInfo(self):
        self.__boxBonusesInfo = {sack.getCategory():self.__parseBonuses(sack) for sack in self.__itemsCache.items.tokens.getLootBoxes().values() if sack.getType() == NySackLootBox.TYPE and sack.getCategory() in NySackLootBox.ALL}

    def __buildSacksInfo(self):
        allSacks = []
        for sack in self.__itemsCache.items.tokens.getLootBoxes().values():
            if sack.getType() == NySackLootBox.TYPE and sack.getCategory() in NySackLootBox.ALL and self.__isSackSuitable(sack):
                allSacks.append(sack)

        self.__sacks = sorted((s for s in allSacks), key=self.__getSackLevel, reverse=True)

    def __getSackModelVO(self):
        return (SackInfo(level=self.__getSackLevel(sack), count=sack.getInventoryCount()) for sack in self.__sacks)

    @classmethod
    def __getSackLevel(cls, box):
        return NY_SACK_CATEGORY_TO_LEVEL.get(box.getCategory(), 1)

    def __getFirstAvailableSack(self):
        for sack in self.__sacks:
            if sack.getInventoryCount() > 0:
                return sack

    def __isSackSuitable(self, sack):
        return self.__getSackLevel(sack) <= getDogLevel() + 1

    @adisp_process
    def __requestLootBoxOpen(self, boxItem):
        if self.__onOpenProcess:
            return
        self.__onOpenProcess = True
        result = yield LootBoxOpenProcessor(boxItem, 1).request()
        if result:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                rewardList = result.auxData.get('bonus')
                if not rewardList:
                    _logger.error('Lootbox is opened, but no rewards has been received.')
                    return
                if self.__hasRareReward(rewardList[0]):
                    self.__systemMessages.proto.serviceChannel.pushClientMessage({'data': rewardList[0].get('customizations')[0],
                     'template': NyGFNotificationTemplates.NY_SACKS_RARE_LOOT}, SCH_CLIENT_MSG_TYPE.NY_GF_SM_TYPE)
                self.onSackOpened(rewardList[0])
        self.__onOpenProcess = False

    def __hasRareReward(self, data):
        return data.get('customizations')[0].get('custType') == 'style' if data.get('customizations') else None

    def __parseBonuses(self, sack):
        return [ bonus for bonus in self.__parseAllSection(sack.getBonuses()) if bonus.isShowInGUI() ]

    def __parseAllSection(self, data):
        bonuses = []
        if data:
            for rawData in data.values():
                bonuses.extend(self.__parseOneOfSection(rawData[0]))

        return bonuses

    def __parseGroupsSection(self, data, isGroup=False):
        groups = data.get('groups', [])
        bonuses = []
        for groupData in groups:
            bonuses.extend(self.__parseOneOfSection(groupData, isGroup))

        return bonuses

    def __parseOneOfSection(self, data, isGroup=False):
        oneOf = data.get('oneof', ())
        bonuses = []
        if oneOf and len(oneOf) == 2:
            _, items = oneOf
            for item in items:
                if item and len(item) == 4:
                    _, _, _, rawData = item
                    if rawData:
                        for k, v in rawData.iteritems():
                            if k == 'groups':
                                bonuses.extend(self.__parseGroupsSection(rawData, isGroup=True))
                            if isGroup:
                                bonus = getNonQuestBonuses(k, v)
                                return self.__wrapToNyRandomResource(bonus[0])
                            bonuses.extend(getNonQuestBonuses(k, v))

        return bonuses

    @classmethod
    def __wrapToNyRandomResource(cls, bonus):
        if isinstance(bonus, CrewBooksBonus):
            for bonusItem in bonus.getItems():
                crewBook, count = bonusItem
                if crewBook.isCommon():
                    return getNonQuestBonuses('randomNyBooklet', count)
                return getNonQuestBonuses('randomNyGuide', count)

        if isinstance(bonus, ItemsBonus):
            for count in bonus.getItems().itervalues():
                return getNonQuestBonuses('randomNyInstruction', count)

        if bonus.getName() == 'ny24Toys':
            for bonusValue in bonus.getValue().itervalues():
                for count in bonusValue.itervalues():
                    return getNonQuestBonuses('randomNy24Toy', count)
