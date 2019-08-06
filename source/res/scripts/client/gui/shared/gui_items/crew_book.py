# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/crew_book.py
import nations
from gui.impl import backport
from gui.impl.gen import R
from items import tankmen, parseIntCompactDescr
from gui.shared.gui_items.Vehicle import getIconResourceName
from gui.shared.utils.functions import stripExpAmountTags
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.fitting_item import FittingItem
from helpers import func_utils, dependency
from items.components.crew_books_constants import CREW_BOOK_RARITY, CREW_BOOK_SPREAD
from skeletons.gui.lobby_context import ILobbyContext

def orderCmp(item1, item2, rarityReverse=False):
    itemOrder1 = item1.getBookTypeOrder()
    itemOrder2 = item2.getBookTypeOrder()
    if itemOrder1 == itemOrder2:
        return cmp(item1.getNationID(), item2.getNationID())
    rarityCmp = 1 if itemOrder1 > itemOrder2 else -1
    reverse = -1 if rarityReverse else 1
    return rarityCmp * reverse


def sortItems(items):
    return sorted(items, orderCmp)


class CrewBook(FittingItem):
    __slots__ = ('__id', '__count')
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, intCompactDescr, proxy=None):
        super(CrewBook, self).__init__(intCompactDescr, proxy)
        self.__count = 0
        _, _, self.__id = parseIntCompactDescr(intCompactDescr)
        self.nationID = nations.INDICES.get(self.getNation(), nations.NONE_INDEX)
        if proxy is not None and proxy.inventory.isSynced():
            self.__count = proxy.inventory.getItems(GUI_ITEM_TYPE.CREW_BOOKS, intCompactDescr)
        return

    @property
    def isForSale(self):
        return self.__lobbyContext.getServerSettings().isCrewBooksSaleEnabled()

    def getID(self):
        return self.__id

    def getBookType(self):
        return self._bookData().type

    def isCommon(self):
        return self.getBookType() is CREW_BOOK_RARITY.CREW_COMMON

    def getBookTypeOrder(self):
        return CREW_BOOK_RARITY.ORDER[self.getBookType()]

    def getBookSpread(self):
        return CREW_BOOK_SPREAD.PERSONAL_BOOK if self.isPersonal() else CREW_BOOK_SPREAD.CREW_BOOK

    def isPersonal(self):
        return self.getBookType() == CREW_BOOK_RARITY.PERSONAL

    def getFreeCount(self):
        return 0 if not self.__count else self.__count

    def getNation(self):
        return self._bookData().nation

    def getNationID(self):
        return nations.INDICES.get(self.getNation(), nations.NONE_INDEX)

    def getXP(self):
        bookType = self.getBookType()
        return self._crewBookTypesConfig()[bookType]

    def inAccount(self):
        return self.__count > 0

    def getName(self):
        return self.userName

    def getBonusIconName(self):
        iconName = self.getBookType()
        if not self.isPersonal():
            iconName += '_' + self.getNation()
        return iconName

    def getGUIEmblemID(self):
        return '{}_{}'.format(self.itemTypeName, self.getBookType())

    def getOldStyleIcon(self, size='large'):
        resId = R.images.gui.maps.icons.crewBooks.books.dyn(size).dyn(getIconResourceName(self.icon))()
        return func_utils.makeFlashPath(backport.image(resId)[6:])

    def formattedShortDescription(self, formatter):
        description = self.shortDescription
        return description.format(**formatter)

    @property
    def level(self):
        pass

    @property
    def inventoryCount(self):
        return self.__count

    @property
    def userName(self):
        params = {}
        if not self.isPersonal():
            params['nation'] = backport.text(R.strings.nations.dyn(self.getNation())())
        return backport.text(R.strings.crew_books.items.dyn(self.getBookType()).Name(), **params)

    @property
    def fullDescription(self):
        return stripExpAmountTags(self.shortDescription)

    @property
    def shortDescription(self):
        return backport.text(R.strings.crew_books.items.dyn(self.getBookSpread()).Descr(), exp=backport.getIntegralFormat(self.getXP()))

    @property
    def icon(self):
        return self._bookData().getExtensionLessIcon()

    def _bookData(self):
        return self._crewBooksConfig()[self.__id]

    def _getDescriptor(self):
        return tankmen.getItemByCompactDescr(self.intCD)

    def _getShortInfoKey(self):
        return backport.text(R.strings.menu.descriptions.dyn(self.getBookSpread())())

    def _getShortInfo(self, vehicle=None, expanded=False):
        return self.fullDescription

    @staticmethod
    def _crewBooksConfig():
        return tankmen.g_cache.crewBooks().books

    @staticmethod
    def _crewBookTypesConfig():
        return tankmen.g_cache.crewBooks().rarityGroups
