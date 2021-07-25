# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/detachment_customization.py
from items.components.crew_skins_components import CrewSkinsCache
from items.components.crew_books_components import CrewBooksCache
from items import vehicles, ITEM_TYPES, parseIntCompactDescr
from items.tankmen import TankmanDescr, MAX_SKILL_LEVEL
from items.components import crew_books_constants
from items.readers.crewSkins_readers import readCrewSkinsCacheFromXML
from items.readers.crewBooks_readers import readCrewBooksCacheFromXML
from constants import ITEM_DEFS_PATH
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
_CREW_SKINS_XML_PATH = ITEM_DEFS_PATH + 'crewSkins/'
_CREW_BOOKS_XML_PATH = ITEM_DEFS_PATH + 'crewBooks/'
g_cache = None

def init(preloadEverything, pricesToCollect):
    global g_cache
    g_cache = Cache()
    if preloadEverything:
        g_cache.initCrewSkins(pricesToCollect)
        g_cache.initCrewBooks(pricesToCollect)


class Cache(object):
    __slots__ = ('__crewSkins', '__crewBooks')

    def __init__(self):
        self.__crewSkins = None
        self.__crewBooks = None
        return

    def initCrewSkins(self, pricesCache):
        if self.__crewSkins is None:
            self.__crewSkins = CrewSkinsCache()
            readCrewSkinsCacheFromXML(pricesCache, self.__crewSkins, _CREW_SKINS_XML_PATH)
        return

    def initCrewBooks(self, pricesCache):
        if self.__crewBooks is None:
            self.__crewBooks = CrewBooksCache()
            readCrewBooksCacheFromXML(pricesCache, self.__crewBooks, _CREW_BOOKS_XML_PATH)
        return

    def crewSkins(self):
        return self.__crewSkins

    def crewBooks(self):
        return self.__crewBooks


def validateCrewToLearnCrewBook(crew, vehTypeCompDescr):
    resultMask = crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.EMPTY_MASK
    resultMsg = ''
    crewLists = {mask:[] for mask in crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.ALL}
    if None in crew:
        resultMsg += 'Vehicle has not full crew; '
        resultMask = resultMask | crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.FULL_CREW
    _, _, vehicleID = vehicles.parseIntCompactDescr(vehTypeCompDescr)
    for slotID, tmanCompDescr in enumerate(crew):
        if tmanCompDescr is None:
            if not resultMask & crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.FULL_CREW:
                resultMsg += 'Vehicle has not full crew; '
            resultMask = resultMask | crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.FULL_CREW
            continue
        tmanDescr = TankmanDescr(tmanCompDescr)
        if tmanDescr.roleLevel < MAX_SKILL_LEVEL:
            if not resultMask & crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.ROLE_LEVEL:
                resultMsg += 'One of crew members has not enough level of specialization; '
            resultMask = resultMask | crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.ROLE_LEVEL
            crewLists[crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.ROLE_LEVEL].append(slotID)
        if vehicleID != tmanDescr.vehicleTypeID:
            if not resultMask & crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.SPECIALIZATION:
                resultMsg += 'One of crew members has specialization not compatible with current vehicle;'
            resultMask = resultMask | crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.SPECIALIZATION
            crewLists[crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.SPECIALIZATION].append(slotID)

    return (resultMask == 0,
     resultMask,
     resultMsg,
     crewLists)


def getItemByCompactDescr(compactDescr):
    try:
        itemTypeID, nationID, compTypeID = parseIntCompactDescr(compactDescr)
        items = None
        if itemTypeID == ITEM_TYPES.crewSkin:
            items = g_cache.crewSkins().skins
        elif itemTypeID == ITEM_TYPES.crewBook:
            items = g_cache.crewBooks().books
        return items[compTypeID]
    except Exception:
        LOG_CURRENT_EXCEPTION()
        LOG_ERROR('(compact description to XML mismatch?)', compactDescr)

    return


def isItemWithCompactDescrExist(compactDescr):
    try:
        return getItemByCompactDescr(compactDescr) is not None
    except Exception:
        return False

    return None
