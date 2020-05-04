# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/front_progress.py
import logging
from typing import Dict, Tuple, Generator, Set
from account_helpers.settings_core.ServerSettingsManager import UIGameEventKeys
from game_event_progress import GameEventProgress, GameEventProgressItem, GameEventProgressItemEmpty
from gui.server_events.bonuses import mergeBonuses, VehiclesBonus
from gui.server_events.conditions import getTokenNeededCountInCondition
from gui.impl.gen import R
from gui.impl import backport
from helpers import int2roman
from gui.server_events.awards_formatters import QuestsBonusComposer
from shared_utils import first
from dossiers2.custom.records import DB_ID_TO_RECORD
_logger = logging.getLogger(__name__)
_SPECIAL_ACHIEVMENTS = set(['se2020Medal'])
_ACHIEVMENTS_DELETE_FROM_POPUPS = set((aID for aID, (_, name) in DB_ID_TO_RECORD.iteritems() if name in _SPECIAL_ACHIEVMENTS))

class FrontProgress(GameEventProgress):

    def __init__(self, frontID):
        super(FrontProgress, self).__init__('se20_front_{}'.format(frontID), 'progress', 'final_reward', 'bonuses', 'se20_front_{}_bought_last_level'.format(frontID))
        self._id = frontID

    def getID(self):
        return self._id

    def getProgressTokenName(self):
        return 'se20_front_{}_event_points'.format(self.getID())

    def getFrontMarkTokenName(self):
        return 'img:front_mark_{}:webId'.format(self.getID())

    def getFrontMarksCount(self):
        return self.getFrontMarksTotalCount() if self.isCompleted() else self.eventsCache.questsProgress.getTokenCount(self.getFrontMarkTokenName())

    def getFrontMarksTotalCountForLevel(self, level):
        return sum((self.getItems()[itemID].getMaxFrontMarksCount() for itemID in xrange(level + 1)))

    def getFrontMarksTotalCount(self):
        return self.getFrontMarksTotalCountForLevel(self.getMaxLevel())

    def getBonuses(self):
        if not self.getItems():
            return []
        bonuses = [ bonus for item in self.getItems() for bonus in item.getBonuses() ]
        return mergeBonuses(bonuses)

    def _createProgressItem(self, quest):
        return FrontProgressItem(self, quest)

    def _createProgressItemEmpty(self):
        return FrontProgressItemEmpty(self)

    def isAwardShown(self, index):
        offset = index - 1
        return self._getGameEventServerSetting(UIGameEventKeys.FRONT_AWARD_SHOWN, 0) & 1 << offset

    def setAwardIsShown(self, index):
        offset = index - 1
        oldValue = self._getGameEventServerSetting(UIGameEventKeys.FRONT_AWARD_SHOWN, 0)
        newValue = oldValue | 1 << offset
        self.settingsCore.serverSettings.saveInGameEventStorage({UIGameEventKeys.FRONT_AWARD_SHOWN: newValue})


class FrontProgressItem(GameEventProgressItem):
    _LEVEL_COMPLETE_TEMPLATE = 'SE20FrontLevelCompleted'
    _LEVEL_COMPLETE_TEMPLATE_VEHICLE = 'SE20FrontLevelVehicleCompleted'
    _SE20_TANK_DISCOUNT_PREFIX = 'se20_tank_discount'
    BONUS_REWARDS = {'se20_front_1_progress_4': (lambda inst: not inst.gameEventController.getHeroTank().wasBought(), 'se20_front_1_progress_4_bonus')}

    def getMaxFrontMarksCount(self):
        return getTokenNeededCountInCondition(self._quest, self._progressController.getFrontMarkTokenName(), default=0)

    def getBonuses(self, *kv, **kw):
        reward = super(FrontProgressItem, self).getBonuses(*kv, **kw)
        bonusQuest = self.__getBonusQuest()

        def _isDiscount(rewardData):
            return False if not isinstance(rewardData, dict) else any((isinstance(key, str) and self._SE20_TANK_DISCOUNT_PREFIX in key for key, _ in rewardData.iteritems()))

        if bonusQuest:
            reward += bonusQuest.getBonuses(*kv, **kw)
        return sorted(reward, key=self._getBonusPriority)

    def getCompletedMessages(self, popUps):
        questComposer = QuestsBonusComposer()
        awards = []
        data = {'header': backport.text(R.strings.system_messages.se20.front_level_complete.title()),
         'text': backport.text(R.strings.system_messages.se20.front_level_complete.body(), level=int2roman(self.getLevel()))}
        bonusQuest = self.__getBonusQuest()
        template = self._LEVEL_COMPLETE_TEMPLATE
        if bonusQuest:
            template = self._LEVEL_COMPLETE_TEMPLATE_VEHICLE
            slots = first(bonusQuest.getBonuses('slots'))
            if slots:
                slotsCount = slots.getCount()
            else:
                slotsCount = 0
            data['slotsCount'] = slotsCount
            for vehBonus in bonusQuest.getBonuses('vehicles'):
                for vehData in vehBonus.getValue().itervalues():
                    crewLevel = backport.text(R.strings.messenger.serviceChannelMessages.invoiceReceived.crewOnVehicle(), VehiclesBonus.getTmanRoleLevel(vehData))
                    vehicle = first(questComposer.getPreformattedBonuses([vehBonus])).userName + ' ({})'.format(crewLevel)
                    awards.append(vehicle)

        for record in list(popUps):
            recordID, _ = record
            if recordID in _ACHIEVMENTS_DELETE_FROM_POPUPS:
                popUps.remove(record)

        for bonus in self._quest.getBonuses():
            preformattedBonuses = questComposer.getPreformattedBonuses([bonus])
            for item in preformattedBonuses:
                award = item.userName
                if item.bonusName == 'premium_plus':
                    award += ': {}'.format(bonus.getValue())
                elif item.label:
                    award += ' ({})'.format(item.label)
                awards.append(award)

        data['awards'] = ', '.join(awards)
        yield (template, data)

    def __getBonusQuest(self):
        bonusData = self.BONUS_REWARDS.get(self._quest.getID())
        return self.eventsCache.getAllQuests().get(bonusData[1]) if bonusData and callable(bonusData[0]) and bonusData[0](self) else None


class FrontProgressItemEmpty(GameEventProgressItemEmpty):

    def getMaxFrontMarksCount(self):
        pass
