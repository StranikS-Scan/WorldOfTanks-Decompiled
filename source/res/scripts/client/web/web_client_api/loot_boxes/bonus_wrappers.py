# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/loot_boxes/bonus_wrappers.py
from gui.impl.gen import R
from gui.collection.collections_helpers import getCollectionRes
from gui.impl import backport
from gui.server_events.awards_formatters import AWARDS_SIZES
from web.web_client_api.common import ItemPackType, sanitizeResPath

class BonusAggregateWrapper(object):

    @classmethod
    def getWrappedBonus(cls, bonuses):
        return {}


class RandomCrewBooksWrapper(BonusAggregateWrapper):
    _R_IMAGE = R.images.gui.maps.icons.crewBooks.books

    @classmethod
    def getWrappedBonus(cls, bonuses):
        bonus = bonuses[0]
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
    def getWrappedBonus(cls, bonuses):
        bonus = bonuses[0]
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
    def getWrappedBonus(cls, bonuses):
        bonus = bonuses[0]
        return {'id': 0,
         'type': ItemPackType.BLUEPRINT_NATIONAL_ANY,
         'value': bonus.get('value', 0),
         'icon': {AWARDS_SIZES.SMALL: sanitizeResPath(backport.image(cls._R_IMAGE.small.randomNational())),
                  AWARDS_SIZES.BIG: sanitizeResPath(backport.image(cls._R_IMAGE.big.randomNational()))},
         'name': '',
         'description': ''}


class CollectionItemWrapper(BonusAggregateWrapper):

    @classmethod
    def getWrappedBonus(cls, bonuses):
        bonus = bonuses[0]
        collectionID = int(bonus['id'].split('_')[2])
        return {'id': collectionID,
         'type': ItemPackType.CUSTOM_ANY_COLLECTION_ITEM,
         'value': 1,
         'icon': {AWARDS_SIZES.SMALL: sanitizeResPath(backport.image(R.images.gui.maps.icons.collectionItems.c_48x48.dyn('any_{}'.format(collectionID))())),
                  AWARDS_SIZES.BIG: sanitizeResPath(backport.image(R.images.gui.maps.icons.collectionItems.c_80x80.dyn('any_{}'.format(collectionID))()))},
         'name': backport.text(getCollectionRes(collectionID).anyCollectionItem.tooltip.header()),
         'description': backport.text(getCollectionRes(collectionID).anyCollectionItem.tooltip.body())}
