# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/collection_presenters.py
import logging
import typing
from helpers import dependency
from items import collectibles
from items.components.ny_constants import YEARS_INFO
from items.new_year import g_cache
from new_year.ny_constants import Collections
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import CustomizationsBonus
_logger = logging.getLogger(__name__)

def getCollectionCost(yearName, settingName):
    pass


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getAdditionalBonusByCollectionID(collectionIntID, eventsCache=None):
    collectionStrID = g_cache.collectionStrIDs[collectionIntID]
    quest = eventsCache.getQuestByID(g_cache.collectionRewardsByCollectionID[collectionStrID])
    if quest is None:
        _logger.error('There is no quest by questID: %s', g_cache.collectionRewardsByCollectionID[collectionStrID])
        return []
    else:
        return quest.getBonuses('customizations')


class CollectionPresenter(object):

    def __init__(self, yearName):
        self.__yearName = yearName

    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def getCount(self, itemsCache=None):
        result = 0
        collectionDistributions = itemsCache.items.festivity.getCollectionDistributions()
        if collectionDistributions:
            for toySettingID in self.getCollectionSettingsIDs(useMega=True):
                result += sum(collectionDistributions[toySettingID])

        return result

    def getName(self):
        return self.__yearName

    def getCollectionTypes(self):
        return YEARS_INFO.getCollectionTypesByYear(self.__yearName)

    def getCollectionSettingsIDs(self, useMega=False):
        result = []
        for settingName in YEARS_INFO.getCollectionTypesByYear(self.__yearName):
            result.append(YEARS_INFO.getCollectionIntID(YEARS_INFO.getCollectionSettingID(settingName, self.__yearName)))

        return result

    def getTotalCount(self):
        return len(collectibles.g_cache[self.__yearName].toys)


def getCurrentNYCollectionPresenter():
    return CollectionPresenter(max(Collections.ALL()))
