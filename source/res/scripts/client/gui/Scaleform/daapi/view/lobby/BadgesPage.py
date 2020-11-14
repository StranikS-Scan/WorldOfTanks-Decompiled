# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/BadgesPage.py
import BigWorld
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from helpers import dependency
from account_helpers.AccountSettings import AccountSettings, LAST_BADGES_VISIT, LAST_SELECTED_SUFFIX_BADGE_ID
from helpers.time_utils import getServerUTCTime
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBadgesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.meta.BadgesPageMeta import BadgesPageMeta
from gui.Scaleform.settings import ICONS_SIZES
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.BADGE import BADGE
from tutorial.control.context import GLOBAL_FLAG
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.badges.BadgesCollector import BadgesCollector
from gui.badges.badges_vos import makeBadgeVO, makeSuffixBadgeVO

class BadgesPage(BadgesPageMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.instance(ILobbyContext)
    settingsCore = dependency.descriptor(ISettingsCore)
    badgesController = dependency.descriptor(IBadgesController)

    def __init__(self, ctx=None, *args, **kwargs):
        super(BadgesPage, self).__init__(*args, **kwargs)
        self.__prefixBadgeID = None
        self.__suffixBadgeID = None
        self.__selectedItemIdx = 0
        self.__badgesCollector = BadgesCollector()
        self.__backViewName = ctx.get('backViewName', '') if ctx is not None else ''
        self.__tutorStorage = getTutorialGlobalStorage()
        return

    def onBackClick(self):
        self.destroy()

    def onSelectBadge(self, badgeID):
        self.__prefixBadgeID = badgeID
        self.__selectBadges()

    def onDeselectBadge(self):
        self.__prefixBadgeID = None
        self.__selectBadges()
        return

    def onSelectSuffixBadge(self, badgeID):
        self.__suffixBadgeID = badgeID
        self.__selectBadges()

    def onDeselectSuffixBadge(self):
        self.__suffixBadgeID = None
        self.__selectBadges()
        return

    def _populate(self):
        super(BadgesPage, self)._populate()
        userName = BigWorld.player().name
        self.as_setStaticDataS({'header': {'backBtnLabel': backport.text(R.strings.badge.badgesPage.header.backBtn.label()),
                    'backBtnDescrLabel': self.__backViewName,
                    'descrTf': text_styles.main(BADGE.BADGESPAGE_HEADER_DESCR),
                    'playerText': text_styles.grandTitle(self.lobbyContext.getPlayerFullName(userName))}})
        self.__updateBadges()
        if self.__tutorStorage is not None:
            hasNewBadges = self.__checkNewSuffixBadges()
            if hasNewBadges:
                self.__tutorStorage.setValue(GLOBAL_FLAG.BADGE_PAGE_HAS_NEW_SUFFIX_BADGE, True)
        self.badgesController.onUpdated += self.__updateBadges
        return

    def _dispose(self):
        if self.__tutorStorage is not None:
            for flag in (GLOBAL_FLAG.BADGE_PAGE_HAS_NEW_SUFFIX_BADGE, GLOBAL_FLAG.HAVE_NEW_SUFFIX_BADGE, GLOBAL_FLAG.HAVE_NEW_BADGE):
                self.__tutorStorage.setValue(flag, False)

        self.badgesController.onUpdated -= self.__updateBadges
        AccountSettings.setSettings(LAST_BADGES_VISIT, getServerUTCTime())
        super(BadgesPage, self)._dispose()
        return

    def __sentSuffixBadgesVO(self):
        suffixBadgesVO = []
        lastSelectedSuffixBadgeID = AccountSettings.getSettings(LAST_SELECTED_SUFFIX_BADGE_ID)
        selectedItemIdx = None
        lastSelectedItemIdx = None
        if self.__badgesCollector.getSuffixAchievedBadges():
            for i, badge in enumerate(self.__badgesCollector.getSuffixAchievedBadges()):
                self.__deselectNotSelectedBadge(badge)
                suffixBadgesVO.append(makeSuffixBadgeVO(badge))
                if badge.isSelected:
                    selectedItemIdx = i
                if lastSelectedSuffixBadgeID is not None and lastSelectedSuffixBadgeID == badge.badgeID:
                    lastSelectedItemIdx = i

            if selectedItemIdx is not None:
                self.__selectedItemIdx = selectedItemIdx
                AccountSettings.setSettings(LAST_SELECTED_SUFFIX_BADGE_ID, self.badgesController.getSuffix().badgeID)
            elif lastSelectedItemIdx is not None:
                self.__selectedItemIdx = lastSelectedItemIdx
            self.as_setBadgeSuffixS({'checkboxLabel': backport.text(R.strings.badge.badgesPage.header.suffixSetting.label()),
             'checkboxTooltip': makeTooltip(TOOLTIPS.BADGEINFO_TITLE, TOOLTIPS.BADGEINFO_TEXT),
             'checkboxSelected': self.badgesController.getSuffix() is not None,
             'selectedItemIdx': self.__selectedItemIdx,
             'items': suffixBadgesVO})
        return

    def __deselectNotSelectedBadge(self, badge):
        prefixSelected = self.badgesController.getPrefix()
        suffixSelected = self.badgesController.getSuffix()
        badge.isSelected = False
        if badge.isSuffixLayout():
            if suffixSelected is not None and badge.badgeID == suffixSelected.badgeID:
                badge.isSelected = True
        elif badge.isPrefixLayout():
            if prefixSelected is not None and badge.badgeID == prefixSelected.badgeID:
                badge.isSelected = True
        return

    def __updateBadges(self):
        receivedBadgesVO = []
        notReceivedBadgesVO = []
        self.__badgesCollector.updateCollector(self.itemsCache.items.getBadges().values())
        for badge in self.__badgesCollector.getReceivedPrefixBadges():
            self.__deselectNotSelectedBadge(badge)
            receivedBadgesVO.append(makeBadgeVO(badge))

        for badge in self.__badgesCollector.getNotReceivedPrefixBadges():
            self.__deselectNotSelectedBadge(badge)
            notReceivedBadgesVO.append(makeBadgeVO(badge))

        self.__prefixBadgeID = None
        self.__suffixBadgeID = None
        if self.badgesController.getPrefix() is not None:
            self.__prefixBadgeID = self.badgesController.getPrefix().badgeID
            self.as_setSelectedBadgeS(self.badgesController.getPrefix().getBadgeVO(ICONS_SIZES.X48), selected=True)
        else:
            self.as_setSelectedBadgeS({'icon': backport.image(R.images.gui.maps.icons.library.badges.c_48x48.badge_empty()),
             'isDynamic': False}, selected=False)
        if self.badgesController.getSuffix() is not None:
            self.__suffixBadgeID = self.badgesController.getSuffix().badgeID
        self.__sentSuffixBadgesVO()
        self.as_setReceivedBadgesS({'badgesData': receivedBadgesVO})
        self.as_setNotReceivedBadgesS({'title': text_styles.highTitle(BADGE.BADGESPAGE_BODY_UNCOLLECTED_TITLE),
         'badgesData': notReceivedBadgesVO})
        return

    def __selectBadges(self):
        badges = []
        if self.__prefixBadgeID:
            badges.append(self.__prefixBadgeID)
        if self.__suffixBadgeID:
            badges.append(self.__suffixBadgeID)
        self.badgesController.select(badges)

    def __checkNewSuffixBadges(self):
        return any((suffix.isNew() for suffix in self.__badgesCollector.getSuffixAchievedBadges()))
