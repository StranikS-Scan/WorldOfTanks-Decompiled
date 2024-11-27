# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/collection_presenters.py
import logging
import typing
from helpers import dependency
from new_year_common.items import collectibles
from new_year_common.items.components.ny_constants import YEARS_INFO
from new_year_common.items.new_year import g_cache
from new_year.ny_constants import Collections
from new_year.gui.shared.ny_toy_info import TOYS_INFO_REGISTRY, NewYearCurrentToyInfo, registerInDict
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import CustomizationsBonus
_logger = logging.getLogger(__name__)
COLLECTION_PRESENTER_REGESTRY = {}

def _getCollectionsCount(settingsIDs, collectionDistributions):
    result = 0
    if collectionDistributions:
        for toySettingID in settingsIDs:
            result += sum(collectionDistributions[toySettingID])

    return result


def getCollectionCost(yearName, settingName):
    if yearName == NewYearCurrentToyInfo.COLLECTION_NAME:
        return 0
    result = 0
    for toyID in collectibles.g_cache[yearName].toys:
        toyInfo = TOYS_INFO_REGISTRY[yearName](toyID)
        if toyInfo.getSetting() == settingName and not toyInfo.isInCollection():
            result += toyInfo.getShards()

    return result


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getAdditionalBonusByCollectionID(collectionIntID, eventsCache=None):
    collectionStrID = g_cache.collectionStrIDs[collectionIntID]
    quest = eventsCache.getQuestByID(g_cache.collectionRewardsByCollectionID[collectionStrID])
    if quest is None:
        _logger.error('There is no quest by questID: %s', g_cache.collectionRewardsByCollectionID[collectionStrID])
        return []
    else:
        return quest.getBonuses('customizations')


class _BaseCollectionPresenter(object):
    _YEAR = None

    @classmethod
    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def getCount(cls, itemsCache=None):
        return _getCollectionsCount(cls.getCollectionSettingsIDs(useMega=True, usePet=True), itemsCache.items.festivity.getCollectionDistributions())

    @classmethod
    def getName(cls):
        return cls._YEAR

    @classmethod
    def getCollectionTypes(cls):
        return YEARS_INFO.getCollectionTypesByYear(cls._YEAR, useMega=False, usePet=False)

    @classmethod
    def getCollectionSettingsIDs(cls, useMega=False, usePet=False):
        result = []
        for settingName in YEARS_INFO.getCollectionTypesByYear(cls._YEAR, useMega=useMega, usePet=usePet):
            result.append(YEARS_INFO.getCollectionIntID(YEARS_INFO.getCollectionSettingID(settingName, cls._YEAR)))

        return result

    @classmethod
    def getTotalCount(cls):
        return len(collectibles.g_cache[cls._YEAR].toys)


@registerInDict(COLLECTION_PRESENTER_REGESTRY, Collections.NewYear18)
class NY18CollectionPresenter(_BaseCollectionPresenter):
    _YEAR = Collections.NewYear18


@registerInDict(COLLECTION_PRESENTER_REGESTRY, Collections.NewYear19)
class NY19CollectionPresenter(_BaseCollectionPresenter):
    _YEAR = Collections.NewYear19


@registerInDict(COLLECTION_PRESENTER_REGESTRY, Collections.NewYear20)
class NY20CollectionPresenter(_BaseCollectionPresenter):
    _YEAR = Collections.NewYear20


@registerInDict(COLLECTION_PRESENTER_REGESTRY, Collections.NewYear21)
class NY21CollectionPresenter(_BaseCollectionPresenter):
    _YEAR = Collections.NewYear21


@registerInDict(COLLECTION_PRESENTER_REGESTRY, Collections.CURRENT)
class CurrentNYCollectionPresenter(_BaseCollectionPresenter):
    _YEAR = Collections.CURRENT
