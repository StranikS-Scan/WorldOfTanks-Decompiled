# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/crew_skin.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CREW_SKINS_VIEWED
from helpers import i18n
from items.components.crewSkins_constants import NO_CREW_SKIN_ID, TANKMAN_SEX, CREW_SKIN_RARITY
from items import tankmen, parseIntCompactDescr
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.fitting_item import FittingItem

def localizedFullName(crewSkin):
    if crewSkin.getFirstName():
        fullName = '%s %s' % (i18n.makeString(crewSkin.getFirstName()), i18n.makeString(crewSkin.getLastName()))
    else:
        fullName = i18n.makeString(crewSkin.getLastName())
    return fullName


class GenderRestrictionsLocals(object):
    LOCALES = {TANKMAN_SEX.MALE: '#item_types:tankman/gender/man',
     TANKMAN_SEX.FEMALE: '#item_types:tankman/gender/woman'}


class RarityLocals(object):
    LOCALES = {CREW_SKIN_RARITY.COMMON: '#item_types:crewSkins/itemType/common',
     CREW_SKIN_RARITY.RARE: '#item_types:crewSkins/itemType/rare',
     CREW_SKIN_RARITY.EPIC: '#item_types:crewSkins/itemType/epic'}


class CrewSkin(FittingItem):
    __slots__ = ('__id', '__freeCount', '__tankmenIDs')

    def __init__(self, intCompactDescr, proxy=None):
        super(CrewSkin, self).__init__(intCompactDescr, proxy)
        self.__freeCount = 0
        self.__tankmenIDs = set()
        _, _, self.__id = parseIntCompactDescr(intCompactDescr)
        if proxy is not None and proxy.inventory.isSynced():
            self.__freeCount = proxy.inventory.getItems(GUI_ITEM_TYPE.CREW_SKINS, self.__id)
            allTankmen = proxy.getTankmen()
            self.__tankmenIDs = {invID for invID, tankman in allTankmen.iteritems() if tankman.skinID != NO_CREW_SKIN_ID and tankman.skinID == self.__id}
        return

    def getID(self):
        return self.__id

    def getFreeCount(self):
        return self.__freeCount

    def getFirstName(self):
        return self._skinData().firstNameID

    def getLastName(self):
        return self._skinData().lastNameID

    def getIconID(self):
        return self._skinData().iconID

    def getDescription(self):
        return self._skinData().description

    def getRoleID(self):
        return self._skinData().roleID

    def getSex(self):
        return self._skinData().sex

    def getNation(self):
        return self._skinData().nation

    def getRarity(self):
        return self._skinData().rarity

    def getMaxCount(self):
        return self._skinData().maxCount

    def getHistorical(self):
        return self._skinData().historical

    def getSoundSetID(self):
        return self._skinData().soundSetID

    def inAccount(self):
        return self.__freeCount > 0 or self.__tankmenIDs

    def getTankmenIDs(self):
        return self.__tankmenIDs

    def isNew(self):
        return int(self.__id) not in AccountSettings.getSettings(CREW_SKINS_VIEWED)

    def isStorageAvailable(self):
        return self.__freeCount < self.getMaxCount()

    def _getDescriptor(self):
        return tankmen.getItemByCompactDescr(self.intCD)

    def _skinData(self):
        return self._crewSkinsConfig()[self.__id]

    @staticmethod
    def _crewSkinsConfig():
        return tankmen.g_cache.crewSkins().skins
