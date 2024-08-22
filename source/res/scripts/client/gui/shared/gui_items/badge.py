# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/badge.py
import re
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LAST_BADGES_VISIT
from dossiers2.ui.achievements import BADGES_BLOCK
from gui.Scaleform.locale.BADGE import BADGE
from gui.Scaleform.settings import getBadgeIconPath, getAwardBadgeIconPath, getBadgeHighlightIconPath, BADGES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.gui_item import GUIItem
from helpers import i18n, dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IRTSBattlesController
if typing.TYPE_CHECKING:
    from typing import Dict, Optional
    from skeletons.gui.shared import IItemsRequester
CUSTOM_LOGIC_KEY = 'customLogicImpl'

class BadgeTypes(CONST_CONTAINER):
    OBSOLETE = 1
    COLLAPSIBLE = 2


class BadgeLayouts(CONST_CONTAINER):
    PREFIX = 1
    SUFFIX = 2


class Badge(GUIItem):
    __slots__ = ('badgeID', 'data', 'isSelected', 'isAchieved', 'achievedAt', 'group', 'isAchievable', 'isTemporary', 'showCongratsView')

    def __init__(self, data, proxy=None, receivedBadges=None):
        super(Badge, self).__init__(proxy)
        self.badgeID = data['id']
        self.data = data
        self.group = data.get('group')
        self.isAchievable = data.get('achievable', True)
        self.isTemporary = data.get('temporary', False)
        self.showCongratsView = data.get('showCongratsView', False)
        self.isSelected = False
        self.isAchieved = False
        self.achievedAt = None
        if proxy is not None and proxy.dossiers.isSynced() and proxy.badges.isSynced():
            self.isSelected = self.badgeID in proxy.badges.selected
            if receivedBadges is None:
                receivedBadges = proxy.getAccountDossier().getDossierDescr()[BADGES_BLOCK]
            self.isAchieved = self.badgeID in receivedBadges
            if self.isAchieved:
                self.achievedAt = receivedBadges[self.badgeID]
        return

    def __cmp__(self, other):
        if self.achievedAt == other.achievedAt:
            return cmp(self.getWeight(), other.getWeight())
        elif self.achievedAt is None:
            return 1
        else:
            return -1 if other.achievedAt is None else cmp(other.achievedAt, self.achievedAt)

    def hasDynamicContent(self):
        return False

    def getDynamicContent(self):
        return None

    def getBadgeClass(self):
        return self.data.get('class', 0)

    def getName(self):
        return self.data['name']

    def getWeight(self):
        return self.data['weight']

    def isObsolete(self):
        return self.__checkType(BadgeTypes.OBSOLETE)

    def isCollapsible(self):
        return self.__checkType(BadgeTypes.COLLAPSIBLE)

    def isPrefixLayout(self):
        return self.__checkLayout(BadgeLayouts.PREFIX)

    def isSuffixLayout(self):
        return self.__checkLayout(BadgeLayouts.SUFFIX)

    def isVisibleAsAchievable(self):
        return self.isAchievable

    def getHugeIcon(self):
        return self.__getIconPath(BADGES_ICONS.X220)

    def getBigIcon(self):
        return self.__getIconPath(BADGES_ICONS.X80)

    def getIconX110(self):
        return self.__getIconPath(BADGES_ICONS.X110)

    def getIconX320(self):
        return self.__getIconPath(BADGES_ICONS.X320)

    def getSmallIcon(self):
        return self.__getIconPath(BADGES_ICONS.X48)

    def getThumbnailIcon(self):
        return self.__getIconPath(BADGES_ICONS.X24)

    def getSuffixSmallIcon(self):
        return self.getSuffixSmallIconByID(self.badgeID)

    def getAwardBadgeIcon(self, size):
        return getAwardBadgeIconPath(size, self.badgeID)

    @classmethod
    def getSuffixSmallIconByID(cls, badgeID):
        return getBadgeIconPath(BADGES_ICONS.X32, badgeID)

    @classmethod
    def getSmallIconById(cls, badgeID):
        return getBadgeIconPath(BADGES_ICONS.X48, badgeID)

    @classmethod
    def getBigIconById(cls, badgeID):
        return getBadgeIconPath(BADGES_ICONS.X80, badgeID)

    def getUserName(self):
        key = BADGE.badgeName(self.badgeID)
        return i18n.makeString(key)

    def getShortUserName(self):
        key = BADGE.getShortName(self.badgeID)
        return self.getUserName() if key is None else i18n.makeString(key)

    def getUserDescription(self):
        key = BADGE.badgeDescriptor(self.badgeID)
        return i18n.makeString(key)

    def getLongUserDescription(self):
        longDescription = R.strings.badge.dyn('badge_{}_descr_long'.format(self.badgeID))
        return backport.text(longDescription()) if longDescription.exists() else ''

    def getHighlightIcon(self):
        highlight = self.data.get('highlight', '')
        return highlight and getBadgeHighlightIconPath(highlight)

    def isNew(self):
        result = False
        if self.isAchieved:
            lastBadgesVisit = AccountSettings.getSettings(LAST_BADGES_VISIT)
            if lastBadgesVisit is not None:
                result = lastBadgesVisit < self.achievedAt
            else:
                result = True
        return result

    def getBadgeVO(self, size, extraData=None, shortIconName=False):
        iconPath = self.__getIconPath(size, shortIconName)
        result = {'icon': iconPath,
         'content': self.getDynamicContent(),
         'sizeContent': size,
         'isDynamic': self.hasDynamicContent()}
        if extraData:
            result.update(extraData)
        return result

    def getIconPostfix(self):
        return str(self.badgeID)

    @staticmethod
    def getBadgeIDFromIconPath(iconPath):
        m = re.search('badge_([0-9]+)*', iconPath)
        return m.group(1) if m else ''

    def __getIconPath(self, size, shortIconName=False):
        iconPostfix = self.getIconPostfix()
        if shortIconName:
            iconPath = 'badge_%s' % iconPostfix
        else:
            iconPath = getBadgeIconPath(size, iconPostfix)
        return iconPath

    def __checkType(self, badgeType):
        return self.data['type'] & badgeType > 0

    def __checkLayout(self, badgeLayout):
        return self.data['layout'] & badgeLayout > 0


class RTSBadge(Badge):
    _rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self, data, proxy=None, receivedBadges=None, extraData=None):
        super(RTSBadge, self).__init__(data, proxy, receivedBadges=receivedBadges)

    def isVisibleAsAchievable(self):
        return self.isAchievable and self._rtsController.isVisible()
