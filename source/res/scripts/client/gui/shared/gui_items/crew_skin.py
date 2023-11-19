# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/crew_skin.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CREW_SKINS_VIEWED
from helpers import i18n
from items.components.crew_skins_constants import NO_CREW_SKIN_ID, TANKMAN_SEX, CREW_SKIN_RARITY
from items import tankmen, parseIntCompactDescr
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.fitting_item import FittingItem

def localizedFullName(crewSkin):
    if crewSkin.getFirstName():
        fullName = '%s %s' % (i18n.makeString(crewSkin.getFirstName()), i18n.makeString(crewSkin.getLastName()))
    else:
        fullName = i18n.makeString(crewSkin.getLastName())
    return fullName


class GenderRestrictionsLocales(object):
    KEYS = {TANKMAN_SEX.MALE: 'man',
     TANKMAN_SEX.FEMALE: 'woman'}


class Rarity(object):
    STRINGS = {CREW_SKIN_RARITY.COMMON: 'common',
     CREW_SKIN_RARITY.RARE: 'rare',
     CREW_SKIN_RARITY.EPIC: 'epic'}


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

    def getLocalizedFullName(self):
        if self.getFirstName():
            fullName = '%s %s' % (i18n.makeString(self.getFirstName()), i18n.makeString(self.getLastName()))
        else:
            fullName = i18n.makeString(self.getLastName())
        return fullName

    def getIconID(self):
        return self._skinData().iconID

    def getIconName(self):
        return self._skinData().iconID.split('.')[0]

    def getDescription(self):
        return self._skinData().description

    def getSex(self):
        return self._skinData().sex

    def getNation(self):
        return self._skinData().nation

    def getRarity(self):
        return self._skinData().rarity

    def getHistorical(self):
        return self._skinData().historical

    def getSoundSetID(self):
        return self._skinData().soundSetID

    def inAccount(self):
        return self.__freeCount > 0 or self.__tankmenIDs

    def getTankmenIDs(self):
        return self.__tankmenIDs

    def isNew(self):
        return self.getNewCount() > 0

    def getTotalCount(self):
        return self.__freeCount + len(self.__tankmenIDs)

    def getNewCount(self):
        totalCount = self.getTotalCount()
        crewSkinViewed = AccountSettings.getSettings(CREW_SKINS_VIEWED)
        viewedCount = 0
        if isinstance(crewSkinViewed, dict):
            viewedCount = AccountSettings.getSettings(CREW_SKINS_VIEWED).get(self.__id, 0)
        return totalCount - viewedCount if viewedCount < totalCount else 0

    def _getDescriptor(self):
        return tankmen.getItemByCompactDescr(self.intCD)

    def _skinData(self):
        return self._crewSkinsConfig()[self.__id]

    @staticmethod
    def _crewSkinsConfig():
        return tankmen.g_cache.crewSkins().skins
