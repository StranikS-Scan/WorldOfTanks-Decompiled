# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/crew_books_constants.py
CREW_BOOKS_XML_FILE = 'crewBooks.xml'
CREW_BOOKS_PRICE_GROUPS_XML_FILE = 'priceGroups.xml'
CREW_BOOK_TYPES_XML_FILE = 'crewBookTypes.xml'
CREW_BOOK_DISPLAYED_AWARDS_COUNT = 11

class CREW_BOOK_PROPERTIES_MASKS:
    FULL_CREW = 1
    SPECIALIZATION = 2
    EMPTY_MASK = 0
    ALL = (FULL_CREW, SPECIALIZATION)


class CrewBookCacheType:
    CREW_BOOK = 1
    ITEM_GROUP = 2
    RANGE = {CREW_BOOK, ITEM_GROUP}


class CREW_BOOK_RARITY:
    CREW_COMMON = 'brochure'
    CREW_RARE = 'guide'
    CREW_EPIC = 'crewBook'
    PERSONAL = 'personalBook'
    UNIVERSAL = 'universalBook'
    UNIVERSAL_GUIDE = 'universalGuide'
    UNIVERSAL_BROCHURE = 'universalBrochure'
    ALL_TYPES = (CREW_COMMON,
     CREW_RARE,
     CREW_EPIC,
     PERSONAL,
     UNIVERSAL_BROCHURE,
     UNIVERSAL_GUIDE,
     UNIVERSAL)
    NO_NATION_TYPES = (PERSONAL,
     UNIVERSAL,
     UNIVERSAL_GUIDE,
     UNIVERSAL_BROCHURE)
    ORDER = dict(zip(ALL_TYPES, range(len(ALL_TYPES))))


class CREW_BOOK_SPREAD:
    CREW_BOOK = 'crewBook'
    PERSONAL_BOOK = 'personalBook'
    CREW_BOOK_NO_NATION = 'universalBook'
    ALL_SPREADS = (CREW_BOOK, PERSONAL_BOOK, CREW_BOOK_NO_NATION)
