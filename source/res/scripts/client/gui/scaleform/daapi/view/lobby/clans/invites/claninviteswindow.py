# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/invites/ClanInvitesWindow.py
import weakref
from functools import partial
import BigWorld
import gui
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.meta.ClanInvitesWindowMeta import ClanInvitesWindowMeta
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.WAITING import WAITING
from gui.clans import formatters
from gui.clans.clan_helpers import ClanInvitesPaginator
from gui.clans.clan_helpers import ClanListener
from gui.clans.items import formatField
from gui.clans.settings import CLAN_INVITE_STATES
from gui.shared.event_dispatcher import showClanSendInviteWindow
from gui.shared.events import CoolDownEvent
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from gui.shared.view_helpers import CooldownHelper
from gui.shared.view_helpers.emblems import ClanEmblemsHelper
from gui.wgcg.clan.contexts import ClanApplicationsCtx, ClanInvitesCtx
from gui.wgcg.settings import WebRequestDataType
from helpers import dependency
from helpers import i18n
from helpers.i18n import makeString as _ms
from skeletons.gui.web import IWebController

class ClanInvitesWindow(ClanInvitesWindowMeta, ClanListener, ClanEmblemsHelper):
    __coolDownRequests = [WebRequestDataType.CLAN_APPLICATIONS, WebRequestDataType.CLAN_INVITES]

    def __init__(self, *args):
        super(ClanInvitesWindow, self).__init__()
        self.__actualRequestsCount = '0'
        self.__processedInvitesCount = '0'
        self._cooldown = CooldownHelper(self.__coolDownRequests, self._onCooldownHandle, CoolDownEvent.WGCG)
        self.__clanDbID = self.clanProfile.getClanDbID()
        self.__clanDossier = weakref.proxy(self.webCtrl.getClanDossier(self.__clanDbID))
        self.__pagiatorsController = _PaginatorsController(self.__clanDbID)

    def onClanEnableChanged(self, enabled):
        if not enabled:
            self.onWindowClose()

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
        return self.webCtrl.getAccountProfile()

    @property
    def paginatorsController(self):
        return self.__pagiatorsController

    @property
    def clanInfo(self):
        return self.__clanDossier.getClanInfo()

    def resyncClanInfo(self, force=False):
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
        self.__updateTabsState()
        self._updateHeaderState()
        self._updateClanInfo()
        self._updateClanEmblem()
        self._cooldown.start()
        self.startClanListening()
        self.__pagiatorsController.setCallback(self._onPaginatorListChanged)
        self.resyncClanInfo()
        self.__pagiatorsController.getPanginator(CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL).reset()
        self.__pagiatorsController.getPanginator(CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED).reset()

    def _dispose(self):
        if self.paginatorsController.isInProgress():
            self.as_hideWaitingS()
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

    def _onPaginatorListChanged(self, alias, f, selectedID, isFullUpdate, isReqInCoolDown, result):
        paginator = self.__pagiatorsController.getPanginator(alias, f)
        if alias == CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS:
            if f == CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL:
                self.__actualRequestsCount = self.formatInvitesCount(paginator)
                self.__updateTabsState()
            elif f == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED:
                pass
            elif f == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
                pass
            else:
                LOG_DEBUG('Unexpected behaviour: unknown filter {} for alias {}'.format(f, alias))
        elif alias == CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS:
            if f == CLANS_ALIASES.INVITE_WINDOW_FILTER_ALL:
                pass
            elif f == CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL:
                pass
            elif f == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED:
                pass
            elif f == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
                self.__processedInvitesCount = self.formatInvitesCount(paginator)
                self.__updateTabsState()
            else:
                LOG_DEBUG('Unexpected behaviour: unknown filter {} for alias {}'.format(f, alias))
        else:
            LOG_DEBUG('Unexpected behaviour: unknown view alias ', alias)
        self.showWaiting(False)

    def _updateClanEmblem(self):
        self.requestClanEmblem128x128(self.clanProfile.getClanDbID())

    def _updateClanInfo(self):
        self.as_setClanInfoS({'name': self.clanProfile.getClanFullName(),
         'bgIcon': RES_ICONS.MAPS_ICONS_CLANS_INVITESWINDOW_CC_HEADER_BACK,
         'creationDate': i18n.makeString(CLANS.CLAN_HEADER_CREATIONDATE, creationDate=BigWorld.wg_getLongDateFormat(self.clanInfo.getCreatedAt()))})

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

    def __updateTabsState(self):
        self.as_setDataS({'tabDataProvider': [{'label': i18n.makeString(CLANS.CLANINVITESWINDOW_TABREQUESTS, value=self.__actualRequestsCount),
                              'linkage': CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_LINKAGE}, {'label': i18n.makeString(CLANS.CLANINVITESWINDOW_TABINVITES, value=self.__processedInvitesCount),
                              'linkage': CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_LINKAGE}]})


class _PaginatorsController(object):
    clanCtrl = dependency.descriptor(IWebController)

    def __init__(self, clanDbID):
        super(_PaginatorsController, self).__init__()
        self.__clanDbID = clanDbID
        self.__paginators = {}
        self.__setUpPaginators()

    def getPanginator(self, viewAlias, f):
        return self.__paginators[viewAlias, f]

    def setCallback(self, callback):
        for k, v in self.__paginators.iteritems():
            v.onListUpdated += partial(callback, k[0], k[1])

    def removeCallbacks(self):
        for v in self.__paginators.itervalues():
            v.onListUpdated.clear()

    def resetAllPanginators(self):
        for v in self.__paginators.itervalues():
            v.reset()

    def markPanginatorsAsUnSynced(self, viewAlias):
        for (alias, _), paginator in self.__paginators.iteritems():
            if alias == viewAlias:
                paginator.markAsUnSynced()

    def isInProgress(self):
        inProgress = False
        for v in self.__paginators.itervalues():
            if v.isInProgress():
                inProgress = True
                break

        return inProgress

    def __setUpPaginators(self):
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL, ClanInvitesPaginator(self.clanCtrl, ClanApplicationsCtx, self.__clanDbID, [CLAN_INVITE_STATES.ACTIVE]))
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED, ClanInvitesPaginator(self.clanCtrl, ClanApplicationsCtx, self.__clanDbID, [CLAN_INVITE_STATES.EXPIRED]))
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED, ClanInvitesPaginator(self.clanCtrl, ClanApplicationsCtx, self.__clanDbID, list(CLAN_INVITE_STATES.PROCESSED)))
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL, ClanInvitesPaginator(self.clanCtrl, ClanInvitesCtx, self.__clanDbID, [CLAN_INVITE_STATES.ACTIVE]))
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED, ClanInvitesPaginator(self.clanCtrl, ClanInvitesCtx, self.__clanDbID, [CLAN_INVITE_STATES.EXPIRED]))
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED, ClanInvitesPaginator(self.clanCtrl, ClanInvitesCtx, self.__clanDbID, list(CLAN_INVITE_STATES.PROCESSED)))
        self.__addPaginator(CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS, CLANS_ALIASES.INVITE_WINDOW_FILTER_ALL, ClanInvitesPaginator(self.clanCtrl, ClanInvitesCtx, self.__clanDbID, list(CLAN_INVITE_STATES.ALL)))

    def __addPaginator(self, viewAlias, f, panginator):
        self.__paginators[viewAlias, f] = panginator
