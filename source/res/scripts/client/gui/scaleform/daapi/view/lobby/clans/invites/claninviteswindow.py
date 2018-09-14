# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/invites/ClanInvitesWindow.py
import weakref
from functools import partial
import BigWorld
import gui
from gui.Scaleform.locale.WAITING import WAITING
from gui.clans.clan_controller import g_clanCtrl
from gui.clans.clan_helpers import ClanListener
from gui.clans import formatters
from gui.clans.settings import CLAN_REQUESTED_DATA_TYPE, CLAN_INVITE_STATES, CLAN_CONTROLLER_STATES
from gui.clans.contexts import ClanApplicationsCtx, ClanInvitesCtx
from gui.clans.items import formatField
from gui.Scaleform.daapi.view.meta.ClanInvitesWindowMeta import ClanInvitesWindowMeta
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.clans.clan_helpers import ClanInvitesPaginator
from gui.shared.view_helpers.emblems import ClanEmblemsHelper
from gui.shared.utils.functions import makeTooltip
from gui.shared.event_dispatcher import showClanSendInviteWindow
from gui.shared.formatters import text_styles
from gui.shared.events import CoolDownEvent
from gui.shared.view_helpers import CooldownHelper
from helpers import i18n
from helpers.i18n import makeString as _ms
from debug_utils import LOG_DEBUG

class ClanInvitesWindow(ClanInvitesWindowMeta, ClanListener, ClanEmblemsHelper):
    __coolDownRequests = [CLAN_REQUESTED_DATA_TYPE.CLAN_APPLICATIONS, CLAN_REQUESTED_DATA_TYPE.CLAN_INVITES]

    def __init__(self, *args):
        super(ClanInvitesWindow, self).__init__()
        self.__actualRequestsCount = '0'
        self.__processedInvitesCount = '0'
        self._cooldown = CooldownHelper(self.__coolDownRequests, self._onCooldownHandle, CoolDownEvent.CLAN)
        self.__clanDbID = self.clanProfile.getClanDbID()
        self.__clanDossier = weakref.proxy(self.clansCtrl.getClanDossier(self.__clanDbID))
        self.__pagiatorsController = _PaginatorsController(self.__clanDbID)

    def onClanStateChanged(self, oldStateID, newStateID):
        if not self.clansCtrl.isEnabled():
            self.onWindowClose()
        if not self.clansCtrl.isAvailable():
            pass

    def onAccountClanProfileChanged(self, profile):
        if not profile.isInClan() or not profile.getMyClanPermissions().canHandleClanInvites():
            self.destroy()

    def onClanInfoReceived(self, clanDbID, clanInfo):
        if clanDbID == self.__clanDbID:
            self._updateClanInfo()
            self._updateHeaderState()

    def onInvitesButtonClick(self):
        showClanSendInviteWindow(self.clanProfile.getClanDbID())

    def onWindowClose(self):
        self.destroy()

    def onClanEmblem128x128Received(self, clanDbID, emblem):
        self.as_setClanEmblemS(self.getMemoryTexturePath(emblem))

    @property
    def clanProfile(self):
        return self.clansCtrl.getAccountProfile()

    @property
    def paginatorsController(self):
        return self.__pagiatorsController

    @property
    def clanInfo(self):
        return self.__clanDossier.getClanInfo()

    def resyncClanInfo(self, force = False):
        self.__clanDossier.resyncClanInfo(force=force)

    def showWaiting(self, show):
        if show:
            self.as_showWaitingS(WAITING.LOADINGDATA, {})
        elif not self.paginatorsController.isInProgress():
            self.as_hideWaitingS()

    def formatInvitesCount(self, paginator):
        return formatters.formatInvitesCount(paginator.getTotalCount())

    def _populate(self):
        self.showWaiting(True)
        super(ClanInvitesWindow, self)._populate()
        self.__initControls()
        self._cooldown.start()
        self.startClanListening()
        self.__pagiatorsController.setCallback(self._onPaginatorListChanged)
        self.resyncClanInfo()
        self.__pagiatorsController.getPanginator(CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL).reset()
        self.__pagiatorsController.getPanginator(CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED).reset()

    def _dispose(self):
        self.stopClanListening()
        self.__pagiatorsController.removeCallbacks()
        self._cooldown.stop()
        self._cooldown = None
        super(ClanInvitesWindow, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(ClanInvitesWindow, self)._onRegisterFlashComponent(viewPy, alias)
        viewPy.setParentWindow(self)

    def _onCooldownHandle(self, isInCooldown):
        self.showWaiting(isInCooldown)

    def _onPaginatorListChanged(self, alias, filter, selectedID, isFullUpdate, isReqInCoolDown, result):
        paginator = self.__pagiatorsController.getPanginator(alias, filter)
        if alias == CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS:
            if filter == CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL:
                self.__actualRequestsCount = self.formatInvitesCount(paginator)
                self._updateTabsState()
            elif filter == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED:
                pass
            elif filter == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
                pass
            else:
                LOG_DEBUG('Unexpected behaviour: unknown filter {} for alias {}'.format(filter, alias))
        elif alias == CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS:
            if filter == CLANS_ALIASES.INVITE_WINDOW_FILTER_ALL:
                pass
            elif filter == CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL:
                pass
            elif filter == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED:
                pass
            elif filter == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
                self.__processedInvitesCount = self.formatInvitesCount(paginator)
                self._updateTabsState()
            else:
                LOG_DEBUG('Unexpected behaviour: unknown filter {} for alias {}'.format(filter, alias))
        else:
            LOG_DEBUG('Unexpected behaviour: unknown view alias ', alias)
        self.showWaiting(False)

    def _updateClanEmblem(self):
        self.requestClanEmblem128x128(self.clanProfile.getClanDbID())

    def _updateClanInfo(self):
        self.as_setClanInfoS({'name': self.clanProfile.getClanFullName(),
         'bgIcon': RES_ICONS.MAPS_ICONS_CLANS_INVITESWINDOW_CC_HEADER_BACK,
         'creationDate': i18n.makeString(CLANS.CLAN_HEADER_CREATIONDATE, creationDate=BigWorld.wg_getLongDateFormat(self.clanProfile.getJoinedAt()))})

    def _updateHeaderState(self):
        freePlaces = self.clanInfo.getFreePlaces()
        freePlacesInClanText = text_styles.concatStylesToSingleLine(text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_HEADER_FREEPLACESINCLAN, count=text_styles.main(formatField(getter=self.clanInfo.getFreePlaces)))))
        if freePlaces == 0:
            inviteButtonEnabled = False
            inviteButtonTooltip = _ms(CLANS.CLANINVITESWINDOW_HEADER_TOOLTIPS_NOPLACES)
            freePlacesInClanText = gui.makeHtmlString('html_templates:lobby/research', 'warningMessage', {'text': freePlacesInClanText})
        else:
            inviteButtonEnabled = True
            inviteButtonTooltip = _ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_HEADER_INVITEBUTTON)
        self.as_setHeaderStateS({'inviteButtonEnabled': inviteButtonEnabled,
         'inviteButtonText': CLANS.CLANINVITESWINDOW_HEADER_INVITEINCLAN,
         'inviteButtonTooltip': makeTooltip(body=inviteButtonTooltip),
         'freePlacesInClanText': freePlacesInClanText})

    def _updateTabsState(self):
        self.as_setDataS({'tabDataProvider': [{'label': i18n.makeString(CLANS.CLANINVITESWINDOW_TABREQUESTS, value=self.__actualRequestsCount),
                              'linkage': CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_LINKAGE}, {'label': i18n.makeString(CLANS.CLANINVITESWINDOW_TABINVITES, value=self.__processedInvitesCount),
                              'linkage': CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_LINKAGE}]})

    def __initControls(self):
        self._updateTabsState()
        self._updateHeaderState()
        self._updateClanInfo()
        self._updateClanEmblem()


class _PaginatorsController(object):

    def __init__(self, clanDbID):
        super(_PaginatorsController, self).__init__()
        self.__clanDbID = clanDbID
        self.__paginators = {}
        self.__setUpPaginators()

    def getPanginator(self, viewAlias, filter):
        return self.__paginators[viewAlias, filter]

    def setCallback(self, callback):
        for k, v in self.__paginators.iteritems():
            v.onListUpdated += partial(callback, k[0], k[1])

    def removeCallbacks(self):
        for v in self.__paginators.itervalues():
            v.onListUpdated.clear()

    def resetAllPanginators(self):
        for v in self.__paginators.itervalues():
            v.reset()

    def markPanginatorsAsUnSynced(self):
        for v in self.__paginators.itervalues():
            v.markAsUnSynced()

    def isInProgress(self):
        inProgress = False
        for v in self.__paginators.itervalues():
            if v.isInProgress():
                inProgress = True
                break

        return inProgress

    def __setUpPaginators(self):
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL, ClanInvitesPaginator(g_clanCtrl, ClanApplicationsCtx, self.__clanDbID, [CLAN_INVITE_STATES.ACTIVE]))
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED, ClanInvitesPaginator(g_clanCtrl, ClanApplicationsCtx, self.__clanDbID, [CLAN_INVITE_STATES.EXPIRED]))
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED, ClanInvitesPaginator(g_clanCtrl, ClanApplicationsCtx, self.__clanDbID, list(CLAN_INVITE_STATES.PROCESSED)))
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL, ClanInvitesPaginator(g_clanCtrl, ClanInvitesCtx, self.__clanDbID, [CLAN_INVITE_STATES.ACTIVE]))
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED, ClanInvitesPaginator(g_clanCtrl, ClanInvitesCtx, self.__clanDbID, [CLAN_INVITE_STATES.EXPIRED]))
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED, ClanInvitesPaginator(g_clanCtrl, ClanInvitesCtx, self.__clanDbID, list(CLAN_INVITE_STATES.PROCESSED)))
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_ALL, ClanInvitesPaginator(g_clanCtrl, ClanInvitesCtx, self.__clanDbID, list(CLAN_INVITE_STATES.ALL)))

    def __addPaginator(self, viewAlias, filter, panginator):
        self.__paginators[viewAlias, filter] = panginator
