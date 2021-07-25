# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/crew_skin.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CREW_SKINS_VIEWED
from helpers import dependency, i18n
from items.components.crew_skins_constants import NO_CREW_SKIN_ID, CREW_SKIN_RARITY
from items import detachment_customization, parseIntCompactDescr
from gui.impl.gen import R
from gui.impl import backport
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.fitting_item import FittingItem
from skeletons.gui.detachment import IDetachmentCache

def localizedFullName(crewSkin):
    if crewSkin.getFirstName():
        fullName = '%s %s' % (i18n.makeString(crewSkin.getFirstName()), i18n.makeString(crewSkin.getLastName()))
    else:
        fullName = i18n.makeString(crewSkin.getLastName())
    return fullName


def getCrewSkinIconBig(iconID):
    return backport.image(R.images.gui.maps.icons.tankmen.icons.big.crewSkins.dyn(iconID)())


def getCrewSkinNationPath(nationID):
    return backport.image(R.images.gui.maps.icons.tankmen.crewSkins.nations.dyn(nationID)()) if nationID else ''


def getCrewSkinIconSmall(iconID):
    return backport.image(R.images.gui.maps.icons.tankmen.icons.small.crewSkins.dyn(iconID)())


def getCrewSkinIconSmallWithoutPath(iconID, withFolder=True):
    fullPath = backport.image(R.images.gui.maps.icons.tankmen.icons.small.crewSkins.dyn(iconID)())
    return '/'.join(fullPath.rsplit('/')[-2 if withFolder else -1:])


class Rarity(object):
    STRINGS = {CREW_SKIN_RARITY.COMMON: 'common',
     CREW_SKIN_RARITY.RARE: 'rare',
     CREW_SKIN_RARITY.EPIC: 'epic'}


class CrewSkin(FittingItem):
    __slots__ = ('__id', '__freeCount', '__detachmentIDs')
    _detachmentCache = dependency.descriptor(IDetachmentCache)

    def __init__(self, intCompactDescr, proxy=None):
        super(CrewSkin, self).__init__(intCompactDescr, proxy)
        self.__freeCount = 0
        self.__detachmentIDs = set()
        _, _, self.__id = parseIntCompactDescr(intCompactDescr)
        if proxy is not None and proxy.inventory.isSynced():
            self.__freeCount = proxy.inventory.getItems(GUI_ITEM_TYPE.CREW_SKINS, self.__id)
            allDetachments = self._detachmentCache.getDetachments()
            self.__detachmentIDs = {invID for invID, det in allDetachments.iteritems() if det.skinID != NO_CREW_SKIN_ID and det.skinID == self.__id}
        return

    def getID(self):
        return self.__id

    def getCount(self):
        return self.__freeCount + len(self.__detachmentIDs)

    def getFreeCount(self):
        return self.__freeCount

    def getFirstName(self):
        return self._skinData().firstNameID

    def getLastName(self):
        return self._skinData().lastNameID

    def getIconID(self):
        return self._skinData().iconID

    def getIconName(self):
        return self._skinData().iconID.split('.')[0]

    def getDescription(self):
        return self._skinData().description

    def getNation(self):
        return self._skinData().nation

    def getRarity(self):
        return self._skinData().rarity

    def getHistorical(self):
        return self._skinData().historical

    def inAccount(self):
        return self.__freeCount > 0 or self.__detachmentIDs

    def getDetachmentIDs(self):
        return self.__detachmentIDs

    def getNewCount(self):
        viewedSkins = AccountSettings.getSettings(CREW_SKINS_VIEWED)
        return self.getCount() - viewedSkins.get(self.__id, 0)

    def isNew(self):
        viewedSkins = AccountSettings.getSettings(CREW_SKINS_VIEWED)
        return self.getCount() > viewedSkins.get(self.__id, 0)

    def _getDescriptor(self):
        return detachment_customization.getItemByCompactDescr(self.intCD)

    def _skinData(self):
        return self._crewSkinsConfig()[self.__id]

    @staticmethod
    def _crewSkinsConfig():
        return detachment_customization.g_cache.crewSkins().skins
