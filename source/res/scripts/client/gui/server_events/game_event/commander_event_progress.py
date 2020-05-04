# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/commander_event_progress.py
import logging
import re
from typing import TYPE_CHECKING, Dict, Tuple, Generator, Set
import BigWorld
from account_helpers.settings_core.ServerSettingsManager import UIGameEventKeys
from constants import GENERAL_ENERGY_MULTIPLIER_PATTERN, MULTIPLIER_GROUP
from game_event_progress import GameEventProgress
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import mergeBonuses, FloatBonus
from gui.server_events.conditions import getTokenNeededCountInCondition
from gui.server_events.game_event.energy import GameEventPremiumEnergy
from helpers import dependency, int2roman
from items import vehicles as vehiclesDB
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.server_events.game_event.game_event_progress import GameEventProgressItem
from helpers.i18n import makeString
if TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
DEFAULT_BONUSES = [ FloatBonus(name, 0) for name in ('xpFactor', 'creditsFactor', 'freeXPFactor') ]
GENERAL_PROGRESS_TOKEN = 'se20_general_{}_progress_{}'
_COMMANDER_OFFSET = 2
_logger = logging.getLogger(__name__)
_ENERGY_DAILY_QUESTS_GROUP_ID = 'se20_energy_general'

class CommanderEventProgress(GameEventProgress):
    BUY_ENERGY_TOKEN = 'img:se20_energy_general_{}_x10_premium:webId'
    QUEST_ENERGY_TOKEN = 'img:se20_energy_general_{}_x15:webId'
    REFILL_ENERGY_TOKEN = 'img:se20_energy_general_{}_x5:webId'
    BASE_ENERGY_TOKEN = 'img:se20_energy_general_{}_x1:webId'
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, generalId):
        super(CommanderEventProgress, self).__init__('se20_general_{}'.format(generalId), 'progress', 'final_reward', 'bonuses', 'se20_bought_general_{}_last_level'.format(generalId))
        self._id = generalId
        self._energies = {}
        self._uniqueEnergies = []
        self.buildEnergies()

    def fini(self):
        super(CommanderEventProgress, self).fini()
        for energy in self._energies.itervalues():
            energy.stop()

    def buildEnergies(self):
        energyOrder = self.energyOrder()
        energies = {}
        for order, energyID in enumerate(energyOrder):
            modifier = self._getEnergyModifier(energyID)
            energy = energies.get(modifier)
            if energy:
                energy.addID(energyID)
            else:
                energy = GameEventPremiumEnergy(self._id, _ENERGY_DAILY_QUESTS_GROUP_ID, energyID, order, modifier)
                energies[modifier] = energy
                self._uniqueEnergies.append(energy)
            energy.start()
            self._energies[energyID] = energy

    def getCurrentEnergy(self):
        return first(sorted((energy for energy in self._energies.itervalues() if energy.getCurrentCount() > 0 and energy.isDrawActive()), key=lambda x: x.order))

    def getEnergy(self, energyID):
        return self._energies.get(energyID)

    def energyOrder(self):
        return self._getGeneralData().get('energiesOrder', [])

    def getQuestEnergyID(self):
        return self.QUEST_ENERGY_TOKEN.format(self._id)

    def getBuyEnergyID(self):
        return self.BUY_ENERGY_TOKEN.format(self._id)

    def getRefillEnergyID(self):
        return self.REFILL_ENERGY_TOKEN.format(self._id)

    def getEnergiesCount(self):
        return sum((energy.getCurrentCount() for energy in self._uniqueEnergies))

    @property
    def energies(self):
        return self._energies

    @property
    def activeEnergies(self):
        return [ energy for energy in self._uniqueEnergies if energy.isDrawActive() ]

    def isBlockedByEnergy(self):
        energyID = self.BASE_ENERGY_TOKEN.format(self._id)
        energy = self.getEnergy(energyID)
        return False if not energy.isDrawActive() else self.getEnergiesCount() <= 0

    def getID(self):
        return self._id

    def getFrontID(self):
        return self._getGeneralData().get('frontID', None)

    def getVehiclesByLevel(self, level):
        return self._getGeneralDataByLevel('vehicles', level, default=[])

    def getAbilitiesByLevel(self, level):
        return sorted(self._getRawAbilitiesByLevel(level), key=lambda abilityID: (-self._getAbilityWeightCoef(self.getAbilityBaseName(abilityID), level), abilityID))

    def getWeaknessesByLevel(self, level):
        return self._getGeneralDataByLevel('weakness', level)

    def getStrengthByLevel(self, level):
        return self._getGeneralDataByLevel('strength', level)

    def getAbilityBaseName(self, abilityID):
        descr = vehiclesDB.g_cache.equipments()[abilityID]
        return '_'.join(descr.name.split('_')[:-1])

    def getCurrentCostForLevel(self, level):
        buyInfo = self._getGeneralDataByLevel('buyInfo', level, default=None)
        return (None, None) if buyInfo is None else (buyInfo['currency'], buyInfo['amount'])

    def getOldCostForLevel(self, level):
        buyInfo = self._getGeneralDataByLevel('buyInfo', level, default=None)
        return (None, None) if buyInfo is None else (buyInfo['currency'], buyInfo['oldAmount'])

    def canBuy(self, generalLevel):
        currency, amount = self.getCurrentCostForLevel(generalLevel)
        return currency is not None and amount is not None

    def isLocked(self):
        return self.getID() in BigWorld.player().generalsLock.values()

    def getProgressTokenName(self):
        return 'se20_general_{}_event_points'.format(self.getID())

    def getVehicle(self, typeCompDescr):
        return self.itemsCache.items.getStockVehicle(typeCompDescr, useInventory=False)

    def getVehicleByLevel(self, level):
        vehicles = self.getVehiclesByLevel(level)
        vehicle = self.getVehicle(vehicles[0])
        return vehicle

    def isLevelAwardShown(self, level):
        offset = _COMMANDER_OFFSET * self.getID() + (level - 1)
        return self._getGameEventServerSetting(UIGameEventKeys.COMMANDER_LEVEL_AWARD_SHOWN, 0) & 1 << offset

    def setLevelAwardIsShown(self, *levels):
        if not levels:
            return
        oldValue = self._getGameEventServerSetting(UIGameEventKeys.COMMANDER_LEVEL_AWARD_SHOWN, 0)
        for level in levels:
            offset = _COMMANDER_OFFSET * self.getID() + (level - 1)
            newValue = oldValue | 1 << offset
            oldValue = newValue

        self.settingsCore.serverSettings.saveInGameEventStorage({UIGameEventKeys.COMMANDER_LEVEL_AWARD_SHOWN: newValue})

    def getRealMaxLevel(self):
        return len(self._items)

    def _getEnergyModifier(self, energyID):
        match = re.search(GENERAL_ENERGY_MULTIPLIER_PATTERN, energyID)
        if match is None:
            _logger.warning('Wrong format for energy %s', energyID)
            return
        else:
            return int(match.group(MULTIPLIER_GROUP))

    def _getGeneralDataByLevel(self, key, level, default=None):
        generalData = self._getGeneralData()
        if not generalData:
            return default
        levels = generalData.get('levels', {})
        if level in levels:
            levelInfo = levels[level]
            if key in levelInfo:
                return levelInfo[key]
        return default

    def _getGeneralData(self):
        return self.eventsCache.getGameEventData().get('generals', {}).get(self.getID(), None)

    def _getRawAbilitiesByLevel(self, level):
        abilities = []
        for key in ('abilities', 'dummyAbilities'):
            abilities.extend(self._getGeneralDataByLevel(key, level, default=[]))

        return abilities

    def _getAbilityWeightCoef(self, abilityName, level):
        exist = int(abilityName in (self.getAbilityBaseName(abilityID) for abilityID in self._getRawAbilitiesByLevel(level)))
        if level > 0:
            exist += self._getAbilityWeightCoef(abilityName, level - 1)
        return exist

    def _createProgressItem(self, quest):
        return CommanderEventItem(self, quest)


class CommanderEventItem(GameEventProgressItem):
    _LEVEL_COMPLETE_TEMPLATE = 'SE20CommanderLevelCompleted'

    def getCompletedMessages(self, popUps):
        progressController = self._progressController
        currentVehicle = ''
        currentLevel = self.getLevel()
        typeCompDescr = first(progressController.getVehiclesByLevel(currentLevel))
        if typeCompDescr is not None:
            vehicle = progressController.getVehicle(typeCompDescr)
            currentVehicle = vehicle.userName
        romanLevel = int2roman(currentLevel + 1)
        gCacheEquipments = vehiclesDB.g_cache.equipments()
        abilities = (abID for abID in progressController.getAbilitiesByLevel(currentLevel) if abID in gCacheEquipments)
        abilities = ', '.join((makeString(gCacheEquipments[abID].userString) + ' ' + romanLevel for abID in abilities))
        yield (self._LEVEL_COMPLETE_TEMPLATE, {'header': backport.text(R.strings.event.unit.name.num(self._progressController.getID())()),
          'text': backport.text(R.strings.system_messages.se20.commander_level_complete.body(), level=romanLevel),
          'currentVehicle': currentVehicle,
          'abilities': abilities})
        return


class GeneralBonusQuest(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, questID, progressTokenName):
        self._questID = questID
        self._progressTokenName = progressTokenName

    def isActive(self):
        return False if self._quest is None else any((item.isAvailable() for item in self._quest.accountReqs.getConditions().items))

    def getBonuses(self):
        if self._quest is None:
            return list(DEFAULT_BONUSES)
        else:
            bonuses = self._quest.getBonuses()
            bonuses.extend(DEFAULT_BONUSES)
            return mergeBonuses(bonuses)

    def getQuestID(self):
        return self._questID

    def getMedalsNeeded(self):
        return 0 if self._quest is None else getTokenNeededCountInCondition(self._quest, self._progressTokenName, default=0)

    @property
    def _quest(self):
        hiddenQuests = self.eventsCache.getHiddenQuests()
        return hiddenQuests[self.getQuestID()] if self.getQuestID() in hiddenQuests else None
