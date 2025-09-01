# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/providers/quest_providers.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from config_schemas.umg import WeightsModel
from config_schemas.umg_config import umgConfigSchema
from constants import PREMIUM_TYPE
from gui.impl.lobby.user_missions.hangar_widget.providers import ConfigKeys
from gui.impl.lobby.user_missions.hangar_widget.providers.user_mission_item import DailyQuestMissionItem, PremiumDailyQuestMissionItem, MissionItem, WeeklyQuestMissionItem
from gui.server_events.event_items import Quest
from gui.server_events.events_helpers import isDailyQuestsEnable, isPremiumQuestsEnable, premMissionsSortFunc, isWeeklyQuestsEnable
from skeletons.gui.game_control import IHangarGuiController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from helpers import dependency
import typing
import logging
_logger = logging.getLogger(__name__)

class QuestProviderBase(object):
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)

    def getQuests(self):
        raise NotImplementedError

    def updateConfig(self, config):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def _setRawData(self, item, raw):
        item.rawData = raw

    def _checkEnabled(self):
        raise NotImplementedError

    def _checkBonusCaps(self, bonusCaps):
        return self.__hangarGuiCtrl.checkCurrentBonusCaps(bonusCaps)

    def _setCompletedState(self, item, raw):
        item.isCompleted = raw.isCompleted()

    def _setPacker(self, item, packer):
        item.uiPacker = packer


class DailyQuestProvider(QuestProviderBase):
    _KEY = ConfigKeys.REGULAR_DAILY
    _ITEM = DailyQuestMissionItem

    def __init__(self, storage, config):
        self.storage = storage
        self.config = config

    def getQuests(self):
        if not self._checkEnabled():
            return []
        else:
            rawQuests = self.storage.getDailyQuests().values()
            quests = []
            for raw in rawQuests:
                levelKey = '{}_{}'.format(self._KEY, raw.getLevel())
                weightConfig = self.config.getWeightByName(levelKey)
                if weightConfig is None:
                    _logger.error('Invalid weightConfig %s', self._KEY)
                    return []
                dailyQuest = self._ITEM(raw.getID(), weightConfig.weight, raw.getLevel())
                self._setRawData(dailyQuest, raw)
                self._setCompletedState(dailyQuest, raw)
                if raw.isBonus():
                    dailyQuest.setItemType('bonus')
                quests.append(dailyQuest)

            return quests

    def updateConfig(self, config):
        self.config = config

    def destroy(self):
        self.storage = None
        self.config = None
        return

    def _checkEnabled(self):
        return isDailyQuestsEnable() and umgConfigSchema.getModel().enableAllDaily and self._checkBonusCaps(ARENA_BONUS_TYPE_CAPS.DAILY_QUESTS)


class PremiumQuestProvider(QuestProviderBase):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, storage, config):
        self.storage = storage
        self.config = config

    def getQuests(self):
        if not self._checkEnabled():
            return []
        else:
            weightConfig = self.config.getWeightByName(ConfigKeys.PREMIUM_DAILY)
            if weightConfig is None:
                _logger.error('Invalid weightConfig %s', ConfigKeys.PREMIUM_DAILY)
                return []
            rawQuests = sorted(self.storage.getPremiumQuests().values(), cmp=premMissionsSortFunc)
            hasPremium = self._itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
            quests = []
            if not hasPremium:
                return quests
            for raw in rawQuests:
                if raw.isCompleted() or raw.isAvailable().isValid:
                    premiumQuest = PremiumDailyQuestMissionItem(raw.getID(), weightConfig.weight)
                    self._setRawData(premiumQuest, raw)
                    self._setCompletedState(premiumQuest, raw)
                    quests.append(premiumQuest)

            return quests

    def updateConfig(self, config):
        self.config = config

    def destroy(self):
        self.storage = None
        self.config = None
        return

    def _checkEnabled(self):
        return isPremiumQuestsEnable() and umgConfigSchema.getModel().enableAllDaily and self._checkBonusCaps(ARENA_BONUS_TYPE_CAPS.PREM_QUESTS)


class WeeklyQuestProvider(QuestProviderBase):
    _KEY = ConfigKeys.WEEKLY
    _ITEM = WeeklyQuestMissionItem

    def __init__(self, storage, config):
        self.storage = storage
        self.weightsModel = config

    def getQuests(self):
        if not self._checkEnabled():
            return []
        else:
            weightConfig = self.weightsModel.getWeightByName(self._KEY)
            if weightConfig is None:
                _logger.error('Invalid weightConfig %s', self._KEY)
                return []
            weeklyQuests = self.storage.getWeeklyQuests()
            questData = {wq.getInfo().id:wq for wq in weeklyQuests.values()}
            questIds = sorted(questData.keys())
            quests = []
            for questId in questIds:
                rawQuest = questData[questId]
                weeklyQuestItem = self._ITEM(rawQuest.getID(), weightConfig.weight, questId)
                self._setRawData(weeklyQuestItem, rawQuest)
                self._setCompletedState(weeklyQuestItem, rawQuest)
                self._setConditions(weeklyQuestItem, rawQuest)
                quests.append(weeklyQuestItem)

            return quests

    def updateConfig(self, config):
        self.weightsModel = config

    def destroy(self):
        self.storage = None
        self.weightsModel = None
        return

    def _setConditions(self, item, raw):
        questInfo = raw.getInfo()
        item.commonConditionId = questInfo.getMainConditionId()
        item.specialConditionIds = questInfo.getSpecialConditionIds()

    def _checkEnabled(self):
        return isWeeklyQuestsEnable() and umgConfigSchema.getModel().enableAllWeekly
