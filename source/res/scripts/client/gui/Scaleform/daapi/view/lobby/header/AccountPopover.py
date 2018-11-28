# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/AccountPopover.py
import BigWorld
from adisp import process
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, BOOSTERS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.daapi.view.meta.AccountPopoverMeta import AccountPopoverMeta
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.clans import formatters as clans_fmts
from gui.clans.clan_helpers import ClanListener
from gui.clans.restrictions import ClanMemberPermissions
from gui.clans.settings import getNoClanEmblem32x32
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import event_dispatcher as shared_events
from gui.shared import events
from gui.shared.ClanCache import g_clanCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showStorage
from gui.shared.formatters import text_styles, icons
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.view_helpers.emblems import ClanEmblemsHelper
from helpers import dependency
from helpers import isPlayerAccount
from helpers.i18n import makeString
from skeletons.gui.game_control import IRefSystemController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from tutorial.control.context import GLOBAL_FLAG
from tutorial.hints_manager import HINT_SHOWN_STATUS
_PREFIX_BADGE_HINT_ID = 'HaveNewBadgeHint'
_SUFFIX_BADGE_HINT_ID = 'HaveNewSuffixBadgeHint'

class AccountPopover(AccountPopoverMeta, IGlobalListener, ClanListener, ClanEmblemsHelper):
    itemsCache = dependency.descriptor(IItemsCache)
    refSystem = dependency.descriptor(IRefSystemController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, _):
        super(AccountPopover, self).__init__()
        self.__clanData = None
        self.__infoBtnEnabled = True
        self.__achieves = []
        self.__tutorStorage = getTutorialGlobalStorage()
        self.__processHints()
        return

    @process
    def openBoostersWindow(self, idx):
        slotID = self.components.get(VIEW_ALIAS.BOOSTERS_PANEL).getBoosterSlotID(idx)
        settings = self.lobbyContext.getServerSettings()
        shouldOpenStorage = isIngameShopEnabled() and settings.isIngameStorageEnabled()
        if shouldOpenStorage:
            navigationPossible = yield self.lobbyContext.isHeaderNavigationPossible()
            if navigationPossible:
                showStorage(defaultSection=STORAGE_CONSTANTS.PERSONAL_RESERVES)
        else:
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.BOOSTERS_WINDOW, ctx={'slotID': slotID}), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def openClanStatistic(self):
        isClanFeaturesEnabled = self.lobbyContext.getServerSettings().clanProfile.isEnabled()
        if isClanFeaturesEnabled:
            clan = self.webCtrl.getAccountProfile()
            shared_events.showClanProfileWindow(clan.getClanDbID(), clan.getClanAbbrev())
        else:
            self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def openRequestWindow(self):
        self.fireEvent(events.LoadViewEvent(CLANS_ALIASES.CLAN_PROFILE_INVITES_WINDOW_PY), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def openClanResearch(self):
        shared_events.showClanSearchWindow()
        self.destroy()

    def openInviteWindow(self):
        self.fireEvent(events.LoadViewEvent(CLANS_ALIASES.CLAN_PERSONAL_INVITES_WINDOW_PY), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def openReferralManagement(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.REFERRAL_MANAGEMENT_WINDOW), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    @process
    def openBadgesWindow(self):
        navigationPossible = yield self.lobbyContext.isHeaderNavigationPossible()
        if not navigationPossible:
            return
        shared_events.showBadges()
        self.destroy()

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.__updateButtonsStates()

    def onTeamStatesReceived(self, entity, team1State, team2State):
        self.__updateButtonsStates()

    def onEnqueued(self, queueType, *args):
        self.__updateButtonsStates()

    def onClanEnableChanged(self, enabled):
        self.__syncUserInfo()
        self.__setClanData()

    def onAccountClanProfileChanged(self, profile):
        self.__setUserData()
        self.__setClanData()
        self.__syncUserInfo()

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        if emblem:
            self.as_setClanEmblemS(self.getMemoryTexturePath(emblem))

    def onClanInfoReceived(self, clanDbID, clanInfo):
        self.__syncUserInfo()
        self.__setClanData()

    def onClanAppsCountReceived(self, clanDbID, appsCount):
        self.__setClanData()

    def onAccountClanInfoReceived(self, info):
        self.__setUserData()
        self.__setClanData()
        self.__syncUserInfo()

    def onAccountInvitesReceived(self, invitesCount):
        self.__syncUserInfo()

    def _populate(self):
        super(AccountPopover, self)._populate()
        self.__populateUserInfo()
        self.startGlobalListening()
        self.startClanListening()
        AccountSettings.setFilter(BOOSTERS, {'wasShown': True})
        g_playerEvents.onCenterIsLongDisconnected += self.__onCenterIsLongDisconnected

    def _getMyInvitesBtnParams(self):
        if self.webCtrl.isAvailable():
            inviteBtnEnabled = True
            inviteBtnTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_INVITEBTN
        else:
            inviteBtnEnabled = False
            inviteBtnTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_INVITEBTN_UNAVAILABLE
        return {'inviteBtnEnabled': inviteBtnEnabled,
         'inviteBtnTooltip': inviteBtnTooltip}

    def _getClanBtnsParams(self, appsCount):
        if self.webCtrl.isAvailable():
            isAvailable = True
            searchClanTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_SEARCHCLAN
            requestInviteBtnTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_INVITEREQUESTBTN
            btnTooltip = str()
        else:
            isAvailable = False
            searchClanTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_SEARCHCLAN_UNAVAILABLE
            requestInviteBtnTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_INVITEREQUESTBTN_UNAVAILABLE
            btnTooltip = str()
        btnEnabled = not BigWorld.player().isLongDisconnectedFromCenter and self.__infoBtnEnabled
        if self.webCtrl.isEnabled():
            btnEnabled = self.webCtrl.isAvailable()
            if not btnEnabled:
                btnTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_CLANPROFILE_UNAVAILABLE
        elif not self.lobbyContext.getServerSettings().isStrongholdsEnabled():
            btnEnabled = False
            btnTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_CLANPROFILE_UNAVAILABLE
        return {'searchClanTooltip': searchClanTooltip,
         'btnEnabled': btnEnabled,
         'btnTooltip': btnTooltip,
         'requestInviteBtnTooltip': requestInviteBtnTooltip,
         'requestInviteBtnEnabled': isAvailable,
         'isSearchClanBtnEnabled': isAvailable}

    def _dispose(self):
        if self.__tutorStorage is not None:
            self.__tutorStorage.setValue(GLOBAL_FLAG.HAVE_NEW_SUFFIX_BADGE, False)
            self.__tutorStorage.setValue(GLOBAL_FLAG.HAVE_NEW_BADGE, False)
        g_playerEvents.onCenterIsLongDisconnected -= self.__onCenterIsLongDisconnected
        self.stopGlobalListening()
        self.stopClanListening()
        super(AccountPopover, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(AccountPopover, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BOOSTERS_PANEL:
            self.components.get(alias).setSettings(isPanelInactive=not self.__infoBtnEnabled)

    def __updateButtonsStates(self):
        self.__setInfoButtonState()
        self.__setClanData()
        self.__setReferralData()
        self.__updateBoostersPanelState()
        self.__syncUserInfo()

    def __updateBoostersPanelState(self):
        boostersPanel = self.components.get(VIEW_ALIAS.BOOSTERS_PANEL)
        if boostersPanel is not None:
            boostersPanel.setSettings(isPanelInactive=not self.__infoBtnEnabled)
        return

    def __populateUserInfo(self):
        if isPlayerAccount():
            self.__setUserInfo()
            self.__syncUserInfo()
            self.__setReferralData()

    def __setUserInfo(self):
        self.__setInfoButtonState()
        self.__setUserData()
        self.__setAchieves()
        self.__setClanData()
        self.__updateBoostersPanelState()

    def __setUserData(self):
        userName = BigWorld.player().name
        clanAbbrev = self.webCtrl.getAccountProfile().getClanAbbrev()
        self.__userData = {'fullName': self.lobbyContext.getPlayerFullName(userName, clanAbbrev=clanAbbrev),
         'userName': userName,
         'clanAbbrev': clanAbbrev}

    def __setAchieves(self):
        items = self.itemsCache.items
        randomStats = items.getAccountDossier().getRandomStats()
        winsEfficiency = randomStats.getWinsEfficiency()
        if winsEfficiency is None:
            winsEffLabel = '--'
        else:
            winsEffLabel = '%s %%' % BigWorld.wg_getNiceNumberFormat(winsEfficiency * 100)

        def _packStats(label, value, iconPath):
            return {'name': makeString('#menu:header/account/popover/achieves/%s' % label),
             'value': value,
             'icon': iconPath}

        self.__achieves = [_packStats('rating', BigWorld.wg_getIntegralFormat(items.stats.globalRating), RES_ICONS.MAPS_ICONS_STATISTIC_RATING), _packStats('battles', BigWorld.wg_getIntegralFormat(randomStats.getBattlesCount()), RES_ICONS.MAPS_ICONS_STATISTIC_RATIO), _packStats('wins', winsEffLabel, RES_ICONS.MAPS_ICONS_STATISTIC_FIGHTS)]
        return

    def __setClanData(self):
        profile = self.webCtrl.getAccountProfile()
        isInClan = profile.isInClan()
        clanDossier = profile.getClanDossier()
        isClanFeaturesEnabled = self.lobbyContext.getServerSettings().clanProfile.isEnabled()
        if isClanFeaturesEnabled:
            btnLabel = makeString(MENU.HEADER_ACCOUNT_POPOVER_CLAN_ENABLED_BTNLABEL)
        else:
            btnLabel = makeString(MENU.HEADER_ACCOUNT_POPOVER_CLAN_NOT_ENABLED_BTNLABEL)
        if isInClan:
            permissions = ClanMemberPermissions(g_clanCache.clanRole)
            requestInviteBtnVisible = isClanFeaturesEnabled and permissions.canHandleClanInvites()
            appsCount = clanDossier.getAppsCount() or 0
            clanBtnsParams = self._getClanBtnsParams(appsCount)
            self.requestClanEmblem32x32(profile.getClanDbID())
            if appsCount == 0:
                envelopeIcon = RES_ICONS.MAPS_ICONS_BUTTONS_ENVELOPEOPENED
            else:
                envelopeIcon = RES_ICONS.MAPS_ICONS_BUTTONS_ENVELOPE
            self.__clanData = {'formation': makeString(MENU.HEADER_ACCOUNT_POPOVER_CLAN_HEADER),
             'formationName': profile.getClanFullName(),
             'position': profile.getRoleUserString(),
             'btnLabel': btnLabel,
             'requestInviteBtnIcon': envelopeIcon,
             'clanResearchIcon': RES_ICONS.MAPS_ICONS_BUTTONS_SEARCH,
             'clanResearchTFText': MENU.HEADER_ACCOUNT_POPOVER_CLAN_SEARCHCLAN2}
            self.__clanData.update(clanBtnsParams)
        else:
            requestInviteBtnVisible = False
            clanBtnsParams = self._getClanBtnsParams(clans_fmts.formatDataToString(None))
            clanProfile = self.webCtrl.getAccountProfile()
            invitesCount = 0
            if not clanProfile.isInClan():
                invitesCount = clanProfile.getInvitesCount() or 0
            if invitesCount == 0:
                envelopeIcon = RES_ICONS.MAPS_ICONS_BUTTONS_ENVELOPEOPENED
            else:
                envelopeIcon = RES_ICONS.MAPS_ICONS_BUTTONS_ENVELOPE
            self.__clanData = {'formation': makeString(MENU.HEADER_ACCOUNT_POPOVER_CLAN_HEADER),
             'clanResearchIcon': RES_ICONS.MAPS_ICONS_BUTTONS_SEARCH,
             'clanResearchTFText': MENU.HEADER_ACCOUNT_POPOVER_CLAN_SEARCHCLAN1,
             'searchClanTooltip': clanBtnsParams['searchClanTooltip'],
             'isSearchClanBtnEnabled': clanBtnsParams['isSearchClanBtnEnabled'],
             'inviteBtnIcon': envelopeIcon}
            self.__clanData.update(self._getMyInvitesBtnParams())
            self.as_setClanEmblemS(getNoClanEmblem32x32())
        self.__clanData.update({'isInClan': isInClan,
         'isClanFeaturesEnabled': isClanFeaturesEnabled,
         'isDoActionBtnVisible': isInClan,
         'requestInviteBtnVisible': requestInviteBtnVisible,
         'isSearchClanBtnVisible': isClanFeaturesEnabled,
         'isTextFieldNameVisible': isInClan,
         'clansResearchBtnYposition': 119 if isInClan else 72})
        self.as_setClanDataS(self.__clanData)
        return

    def __syncUserInfo(self):
        selectedBages = self.itemsCache.items.getBadges(REQ_CRITERIA.BADGE.SELECTED | REQ_CRITERIA.BADGE.PREFIX_LAYOUT).values()
        if selectedBages:
            badgeIcon = selectedBages[0].getSmallIcon()
        else:
            badgeIcon = RES_ICONS.MAPS_ICONS_LIBRARY_BADGES_48X48_BADGE_DEFAULT
        title = text_styles.middleTitle(MENU.HEADER_ACCOUNT_POPOVER_BOOSTERS_BLOCKTITLE) + ' ' + icons.info()
        userVO = {'userData': self.__userData,
         'isTeamKiller': self.itemsCache.items.stats.isTeamKiller,
         'boostersBlockTitle': title,
         'boostersBlockTitleTooltip': TOOLTIPS.HEADER_ACCOUNTPOPOVER_BOOSTERSTITLE,
         'badgeIcon': badgeIcon}
        self.as_setDataS(userVO)

    def __setInfoButtonState(self):
        self.__infoBtnEnabled = True
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher:
            state = prbDispatcher.getFunctionalState()
            self.__infoBtnEnabled = not state.isNavigationDisabled()

    def __onCenterIsLongDisconnected(self, *args):
        self.__setClanData()
        self.__syncUserInfo()

    def __setReferralData(self):
        if self.refSystem.isReferrer():
            self.as_setReferralDataS({'invitedText': makeString(MENU.HEADER_ACCOUNT_POPOVER_REFERRAL_INVITED, referrersNum=len(self.refSystem.getReferrals())),
             'moreInfoText': makeString(MENU.HEADER_ACCOUNT_POPOVER_REFERRAL_MOREINFO),
             'isLinkBtnEnabled': self.__infoBtnEnabled})

    def __checkNewBadges(self):
        prefixNew = False
        suffixNew = False
        for badge in self.itemsCache.items.getBadges().itervalues():
            if badge.isNew():
                if badge.isSuffixLayout():
                    suffixNew = True
                elif badge.isPrefixLayout():
                    prefixNew = True
                if suffixNew and prefixNew:
                    break

        return (prefixNew, suffixNew)

    def __processHints(self):
        if self.__tutorStorage is None:
            return
        else:
            hasNewPrefixBadges, hasNewSuffixBadges = self.__checkNewBadges()
            serverSettings = self.settingsCore.serverSettings
            hintShown = serverSettings.getOnceOnlyHintsSetting(_SUFFIX_BADGE_HINT_ID)
            if not hintShown and hasNewSuffixBadges:
                self.__tutorStorage.setValue(GLOBAL_FLAG.HAVE_NEW_SUFFIX_BADGE, True)
                if hasNewPrefixBadges:
                    serverSettings.setOnceOnlyHintsSettings({_PREFIX_BADGE_HINT_ID: HINT_SHOWN_STATUS})
                return
            hintShown = serverSettings.getOnceOnlyHintsSetting(_PREFIX_BADGE_HINT_ID)
            if not hintShown and hasNewPrefixBadges:
                self.__tutorStorage.setValue(GLOBAL_FLAG.HAVE_NEW_BADGE, True)
            return
