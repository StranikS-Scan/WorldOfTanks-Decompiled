# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/loot_boxes/__init__.py
from gui.collection.collections_helpers import getCollectionRes
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.awards_formatters import AWARDS_SIZES
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from web.web_client_api import Field, W2CSchema, w2c, w2capi
from web.web_client_api.common import ItemPackType, sanitizeResPath, ItemPackTypeGroup

class _LootBoxSchema(W2CSchema):
    id = Field(required=True, type=int)


class BonusAggregateWrapper(object):

    @classmethod
    def getWrappedBonus(cls, bonus):
        return {}


class RandomCrewBooksWrapper(BonusAggregateWrapper):
    _R_IMAGE = R.images.gui.maps.icons.crewBooks.books

    @classmethod
    def getWrappedBonus(cls, bonus):
        return {'id': bonus.get('id', 0),
         'type': ItemPackType.CREW_BOOK_RANDOM,
         'value': bonus.get('value', 0),
         'icon': {AWARDS_SIZES.SMALL: sanitizeResPath(backport.image(cls._R_IMAGE.small.brochure_universal())),
                  AWARDS_SIZES.BIG: sanitizeResPath(backport.image(cls._R_IMAGE.big.brochure_universal()))},
         'name': '',
         'description': ''}


class RandomGuideWrapper(BonusAggregateWrapper):
    _R_IMAGE = R.images.gui.maps.icons.crewBooks.books

    @classmethod
    def getWrappedBonus(cls, bonus):
        return {'id': bonus.get('id', 0),
         'type': ItemPackType.CREW_BOOK_RANDOM,
         'value': bonus.get('value', 0),
         'icon': {AWARDS_SIZES.SMALL: sanitizeResPath(backport.image(cls._R_IMAGE.small.guide_universal())),
                  AWARDS_SIZES.BIG: sanitizeResPath(backport.image(cls._R_IMAGE.big.guide_universal()))},
         'name': '',
         'description': ''}


class RandomNationalBlueprintWrapper(BonusAggregateWrapper):
    _R_IMAGE = R.images.gui.maps.icons.blueprints.fragment

    @classmethod
    def getWrappedBonus(cls, bonus):
        return {'id': 0,
         'type': ItemPackType.BLUEPRINT_NATIONAL_ANY,
         'value': bonus.get('value', 0),
         'icon': {AWARDS_SIZES.SMALL: sanitizeResPath(backport.image(cls._R_IMAGE.small.randomNational())),
                  AWARDS_SIZES.BIG: sanitizeResPath(backport.image(cls._R_IMAGE.big.randomNational()))},
         'name': '',
         'description': ''}


class CollectionItemWrapper(BonusAggregateWrapper):

    @classmethod
    def getWrappedBonus(cls, bonus):
        collectionID = int(bonus['id'].split('_')[2])
        return {'id': collectionID,
         'type': ItemPackType.CUSTOM_ANY_COLLECTION_ITEM,
         'value': 1,
         'icon': {AWARDS_SIZES.SMALL: sanitizeResPath(backport.image(R.images.gui.maps.icons.collectionItems.c_48x48.dyn('any_{}'.format(collectionID))())),
                  AWARDS_SIZES.BIG: sanitizeResPath(backport.image(R.images.gui.maps.icons.collectionItems.c_80x80.dyn('any_{}'.format(collectionID))()))},
         'name': backport.text(getCollectionRes(collectionID).anyCollectionItem.tooltip.header()),
         'description': backport.text(getCollectionRes(collectionID).anyCollectionItem.tooltip.body())}


_BONUS_WRAPPERS = {ItemPackType.CREW_BOOK_BROCHURE: RandomCrewBooksWrapper,
 ItemPackType.CREW_BOOK_GUIDE: RandomGuideWrapper,
 ItemPackType.BLUEPRINT_NATIONAL: RandomNationalBlueprintWrapper,
 ItemPackType.CUSTOM_COLLECTION_ENTITLEMENT: CollectionItemWrapper}
_BONUS_FOR_AGGREGATE = (ItemPackType.CREW_BOOK_BROCHURE,
 ItemPackType.BLUEPRINT_NATIONAL,
 ItemPackType.CUSTOM_COLLECTION_ENTITLEMENT,
 ItemPackType.CREW_BOOK_GUIDE)

@w2capi(name='loot_box', key='action')
class LootBoxWebApi(object):
    __itemsCache = dependency.descriptor(IItemsCache)

    @w2c(_LootBoxSchema, 'get_loot_box_info')
    def getLootBoxInfo(self, cmd):
        result = dict()
        lootBox = self.__itemsCache.items.tokens.getLootBoxByID(cmd.id)
        if lootBox is not None:
            history = self.__itemsCache.items.tokens.getCacheValue('lootBoxes', {}).get('history', {})
            result = self.__parseBoxInfo(lootBox.getBoxInfo(history))
        return result

    def __parseBoxInfo(self, boxInfo):
        result = dict()
        aggregateBonus = {}
        if 'slots' in boxInfo:
            for idx, slotData in boxInfo['slots'].iteritems():
                result.update({idx: {'probability': round(slotData.get('probability', [[0]])[0][0] * 100, 2),
                       'bonuses': []}})
                aggregateBonus.clear()
                for bonus in slotData.get('bonuses', []):
                    bonusList = bonus.getWrappedLootBoxesBonusList()
                    for bonusEntry in bonusList:
                        bonusType = bonusEntry['type']
                        if bonusType in _BONUS_FOR_AGGREGATE:
                            if aggregateBonus.get(bonusType, None) is None or aggregateBonus[bonusType].get('value', 0) < bonusEntry.get('value', 0):
                                aggregateBonus[bonusType] = bonusEntry
                        if not self.__isExistingVehicle(bonusEntry, result[idx]['bonuses']):
                            bonusEntry['icon'] = {size:sanitizeResPath(path) for size, path in bonusEntry['icon'].iteritems()}
                            result[idx]['bonuses'].append(bonusEntry)
                            if bonusType in ItemPackTypeGroup.VEHICLE:
                                result[idx]['guaranteed_bonus_limit'] = boxInfo.get('limit', 0)

                result[idx]['bonuses'].extend([ _BONUS_WRAPPERS.get(bType, BonusAggregateWrapper).getWrappedBonus(bValue) for bType, bValue in aggregateBonus.iteritems() ])

        return result

    @staticmethod
    def __isExistingVehicle(bonusEntry, bonuses):
        return bonusEntry['type'] in ItemPackTypeGroup.VEHICLE and bonusEntry['id'] in (b['id'] for b in bonuses)

    @w2c(W2CSchema, 'set_loot_box_category_visited')
    def setLootBoxCategoryVisited(self, _):
        pass


class LootBoxesWindowWebApiMixin(object):

    @w2c(W2CSchema, 'lootboxes_storage_window')
    def showLootBoxesStorage(self, _):
        from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
        showStorageView()
