# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/AccountPopover.py
import BigWorld
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, BOOSTERS
from helpers.i18n import makeString
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.clans.settings import getNoClanEmblem32x32
from gui import game_control
from gui.prb_control.dispatcher import g_prbLoader
from gui.clans.clan_helpers import ClanListener
from gui.clans.restrictions import ClanMemberPermissions
from gui.clubs import events_dispatcher as club_events
from gui.clans import formatters as clans_fmts
from gui.clubs.club_helpers import MyClubListener
from gui.clubs.settings import CLIENT_CLUB_STATE
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.meta.AccountPopoverMeta import AccountPopoverMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_itemsCache, events
from gui.shared.ClanCache import g_clanCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.view_helpers.emblems import ClubEmblemsHelper, ClanEmblemsHelper
from gui.prb_control.prb_helpers import GlobalListener
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters import text_styles

class AccountPopover(AccountPopoverMeta, GlobalListener, MyClubListener, ClanListener, ClubEmblemsHelper, ClanEmblemsHelper):

    def __init__(self, _):
        super(AccountPopover, self).__init__()
        self.__crewData = None
        self.__clanData = None
        self.__infoBtnEnabled = True
        self.__achieves = []
        return

    def openBoostersWindow(self, idx):
        slotID = self.components.get(VIEW_ALIAS.BOOSTERS_PANEL).getBoosterSlotID(idx)
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.BOOSTERS_WINDOW, ctx={'slotID': slotID}), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def openClanStatistic(self):
        if self.clansCtrl.isEnabled():
            shared_events.showClanProfileWindow(self.clansCtrl.getAccountProfile().getClanDbID())
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

    def openCrewStatistic(self):
        club = self.getClub()
        if club is not None:
            club_events.showClubProfile(club.getClubDbID())
        self.destroy()
        return

    def openReferralManagement(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.REFERRAL_MANAGEMENT_WINDOW), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.__updateButtonsStates()

    def onTeamStatesReceived(self, functional, team1State, team2State):
        self.__updateButtonsStates()

    def onEnqueued(self, queueType, *args):
        self.__updateButtonsStates()

    def onAccountClubStateChanged(self, state):
        self.__setCrewData()
        self.__syncUserInfo()

    def onAccountClubRestrictionsChanged(self):
        self.__setCrewData()
        self.__syncUserInfo()

    def onClubUpdated(self, club):
        self.__setCrewData()
        self.__syncUserInfo()

    def onClubEmblem32x32Received(self, clubDbID, emblem):
        if emblem:
            self.as_setCrewEmblemS(self.getMemoryTexturePath(emblem))

    def onClanStateChanged(self, oldStateID, newStateID):
        self.__syncUserInfo()
        self.__setClanData()

    def onAccountClanProfileChanged(self, profile):
        self.__setUserData()
        self.__setClanData()
        self.__syncUserInfo()

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

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        if emblem:
            self.as_setClanEmblemS(self.getMemoryTexturePath(emblem))

    def _populate(self):
        super(AccountPopover, self)._populate()
        self.__populateUserInfo()
        self.startGlobalListening()
        self.startMyClubListening()
        self.startClanListening()
        AccountSettings.setFilter(BOOSTERS, {'wasShown': True})
        g_playerEvents.onCenterIsLongDisconnected += self.__onCenterIsLongDisconnected

    def _getMyInvitesBtnParams(self):
        if self.clansCtrl.isAvailable():
            inviteBtnEnabled = True
            inviteBtnTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_INVITEBTN
        else:
            inviteBtnEnabled = False
            inviteBtnTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_INVITEBTN_UNAVAILABLE
        return {'inviteBtnEnabled': inviteBtnEnabled,
         'inviteBtnTooltip': inviteBtnTooltip}

    def _getClanBtnsParams(self, appsCount):
        if self.clansCtrl.isAvailable():
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
        if self.clansCtrl.isEnabled():
            btnEnabled = self.clansCtrl.isAvailable()
            if not btnEnabled:
                btnTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_CLANPROFILE_UNAVAILABLE
        return {'searchClanTooltip': searchClanTooltip,
         'btnEnabled': btnEnabled,
         'requestInviteBtnTooltip': requestInviteBtnTooltip,
         'btnTooltip': btnTooltip,
         'isOpenInviteBtnEnabled': isAvailable,
         'isSearchClanBtnEnabled': isAvailable}

    def _dispose(self):
        g_playerEvents.onCenterIsLongDisconnected -= self.__onCenterIsLongDisconnected
        self.stopMyClubListening()
        self.stopGlobalListening()
        self.stopClanListening()
        super(AccountPopover, self)._dispose()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(AccountPopover, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BOOSTERS_PANEL:
            self.components.get(alias).setSettings(isPanelInactive=not self.__infoBtnEnabled)

    def __updateButtonsStates(self):
        self.__setInfoButtonState()
        self.__setCrewData()
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
        self.__setUserInfo()
        self.__syncUserInfo()
        self.__setReferralData()

    def __setUserInfo(self):
        self.__setInfoButtonState()
        self.__setUserData()
        self.__setAchieves()
        self.__setClanData()
        self.__setCrewData()
        self.__updateBoostersPanelState()

    def __setUserData(self):
        userName = BigWorld.player().name
        clanAbbrev = self.clansCtrl.getAccountProfile().getClanAbbrev()
        self.__userData = {'fullName': g_lobbyContext.getPlayerFullName(userName, clanAbbrev=clanAbbrev),
         'userName': userName,
         'clanAbbrev': clanAbbrev}

    def __setAchieves(self):
        items = g_itemsCache.items
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
        profile = self.clansCtrl.getAccountProfile()
        isInClan = profile.isInClan()
        clanDossier = profile.getClanDossier()
        isClanFeaturesEnabled = self.clansCtrl.isEnabled()
        if isClanFeaturesEnabled:
            btnLabel = makeString(MENU.HEADER_ACCOUNT_POPOVER_CLAN_ENABLED_BTNLABEL)
        else:
            btnLabel = makeString(MENU.HEADER_ACCOUNT_POPOVER_CLAN_NOT_ENABLED_BTNLABEL)
        if isInClan:
            permissions = ClanMemberPermissions(g_clanCache.clanRole)
            isOpenInviteBtnVisible = isClanFeaturesEnabled and permissions.canHandleClanInvites()
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
             'inviteBtnIcon': envelopeIcon,
             'clanResearchIcon': RES_ICONS.MAPS_ICONS_BUTTONS_SEARCH,
             'clanResearchTFText': MENU.HEADER_ACCOUNT_POPOVER_CLAN_SEARCHCLAN2}
            self.__clanData.update(clanBtnsParams)
        else:
            isOpenInviteBtnVisible = False
            clanBtnsParams = self._getClanBtnsParams(clans_fmts.formatDataToString(None))
            self.__clanData = {'formation': makeString(MENU.HEADER_ACCOUNT_POPOVER_CLAN_HEADER),
             'position': MENU.HEADER_ACCOUNT_POPOVER_CLAN_NOTINCLAN,
             'clanResearchIcon': RES_ICONS.MAPS_ICONS_BUTTONS_SEARCH,
             'clanResearchTFText': MENU.HEADER_ACCOUNT_POPOVER_CLAN_SEARCHCLAN1,
             'searchClanTooltip': clanBtnsParams['searchClanTooltip'],
             'isSearchClanBtnEnabled': clanBtnsParams['isSearchClanBtnEnabled']}
            self.as_setClanEmblemS(getNoClanEmblem32x32())
        self.__clanData.update({'isInClan': isInClan,
         'isClanFeaturesEnabled': isClanFeaturesEnabled,
         'isDoActionBtnVisible': isInClan,
         'isOpenInviteBtnVisible': isOpenInviteBtnVisible,
         'isSearchClanBtnVisible': isClanFeaturesEnabled,
         'isTextFieldNameVisible': isInClan,
         'clansResearchBtnYposition': 119 if isInClan else 72,
         'textFieldPositionYposition': 57 if isInClan else 42})
        self.as_setClanDataS(self.__clanData)
        return

    def __setCrewData(self):
        club = self.getClub()
        if self.clubsState.getStateID() == CLIENT_CLUB_STATE.HAS_CLUB and club:
            self.requestClubEmblem32x32(self.clubsState.getClubDbID(), club.getEmblem32x32())
            member = club.getMember()
            self.__crewData = {'formation': makeString(MENU.HEADER_ACCOUNT_POPOVER_CREW_HEADER),
             'formationName': club.getUserName(),
             'position': member.getRoleUserName(),
             'btnLabel': makeString(MENU.HEADER_ACCOUNT_POPOVER_CREW_BTNLABEL),
             'btnEnabled': not BigWorld.player().isLongDisconnectedFromCenter and self.__infoBtnEnabled}
        if self.__crewData is not None:
            self.as_setCrewDataS(self.__crewData)
        return

    def __syncUserInfo(self):
        clanProfile = self.clansCtrl.getAccountProfile()
        invitesCount = 0
        if not clanProfile.isInClan():
            invitesCount = clanProfile.getInvitesCount() or 0
        if invitesCount == 0:
            envelopeIcon = RES_ICONS.MAPS_ICONS_BUTTONS_ENVELOPEOPENED
        else:
            envelopeIcon = RES_ICONS.MAPS_ICONS_BUTTONS_ENVELOPE
        userVO = {'userData': self.__userData,
         'isInClan': clanProfile.isInClan() or not self.clansCtrl.isEnabled(),
         'isTeamKiller': g_itemsCache.items.stats.isTeamKiller,
         'openInviteBtnIcon': envelopeIcon,
         'boostersBlockTitle': text_styles.middleTitle(MENU.HEADER_ACCOUNT_POPOVER_BOOSTERS_BLOCKTITLE)}
        userVO.update(self._getMyInvitesBtnParams())
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
        refSysCtrl = game_control.g_instance.refSystem
        if refSysCtrl.isReferrer():
            self.as_setReferralDataS({'invitedText': makeString(MENU.HEADER_ACCOUNT_POPOVER_REFERRAL_INVITED, referrersNum=len(refSysCtrl.getReferrals())),
             'moreInfoText': makeString(MENU.HEADER_ACCOUNT_POPOVER_REFERRAL_MOREINFO),
             'isLinkBtnEnabled': self.__infoBtnEnabled})
