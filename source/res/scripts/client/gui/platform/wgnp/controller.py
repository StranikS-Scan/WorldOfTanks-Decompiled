# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/wgnp/controller.py
import httplib
import time
import urlparse
import typing
import logging
import Event
from async import async
from AccountCommands import RES_FAILURE
from BWUtil import AsyncReturn
from client_request_lib import exceptions
from constants import EMAIL_CONFIRMATION_TOKEN_NAME, WG_GAMES
from enumerations import Enumeration
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.platform.base.controller import PlatformRequestsController
from gui.platform.base.request import PlatformResponse
from gui.platform.base.settings import REQUEST_TIMEOUT
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.wgnp_controller import IWGNPRequestController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from async import _Future
WAITING_ID = 'loadContent'
_logger = logging.getLogger(__name__)
STATUS_TYPES = Enumeration('WGNP status types', ['email'])

class WGNPRequestController(IWGNPRequestController):
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        super(WGNPRequestController, self).__init__()
        self._requester = None
        self._em = Event.EventManager()
        self.onEmailConfirmed = Event.SafeEvent(self._em)
        self.onEmailAdded = Event.SafeEvent(self._em)
        self.onEmailAddNeeded = Event.SafeEvent(self._em)
        self._emailAddedTime = 0
        self._statuses = {}
        return

    def init(self):
        self.connectionMgr.onConnected += self._start
        self.connectionMgr.onDisconnected += self._stop

    def fini(self):
        self.connectionMgr.onConnected -= self._start
        self.connectionMgr.onDisconnected -= self._stop
        self._em.clear()

    def getSettings(self):
        return self.lobbyContext.getServerSettings().wgnp

    @async
    def getEmailStatus(self, showWaiting=False):
        url = './personal/api/v2/account/email/state/'
        response = self._statuses.get(STATUS_TYPES.email.name())
        _logger.debug('Getting email status from cache=%s, showWaiting=%s', response, showWaiting)
        if response is None:
            response = yield self._request(url, method='POST', auth=True, showWaiting=showWaiting)
            if response.isSuccess():
                if isEmailAddingNeeded(response):
                    self._onEmailAddNeeded()
                elif isEmailConfirmationNeeded(response):
                    self._onEmailAdded(getEmail(response))
                elif isSpaGenericConflict(response):
                    response = PlatformResponse(RES_FAILURE, '', {'errors': {'__all__': 'spa_generic_conflict'}}, httplib.BAD_REQUEST)
                else:
                    self._onEmailConfirmed()
        raise AsyncReturn(response)
        return

    @async
    def addEmail(self, email, showWaiting=False):
        url = './personal/api/v2/account/email/create/'
        _logger.debug('Add email email=%s, showWaiting=%s', email, showWaiting)
        response = yield self._request(url, method='POST', queryParams={'type': 'pow'}, postData={'game': WG_GAMES.TANKS,
         'email': email}, auth=True, proofOfWorkURL='./personal/api/v2/account/email/create/challenge/?type=pow', showWaiting=showWaiting)
        if response.isSuccess():
            self._emailAddedTime = int(time.time())
            self._onEmailAdded(email)
        elif isAccountAlreadyHasEmail(response):
            self._onEmailConfirmed()
        raise AsyncReturn(response)

    @async
    def confirmEmail(self, code, showWaiting=False):
        url = './personal/api/v2/account/email/activate/'
        _logger.debug('Confirm email code=%s, showWaiting=%s', code, showWaiting)
        response = yield self._request(url, method='POST', postData={'code': code}, auth=True, showWaiting=showWaiting)
        if response.isSuccess() or isAccountAlreadyHasEmail(response):
            self._onEmailConfirmed()
        elif isConfirmationCodeDeactivated(response) or isConfirmationCodeExpired(response) or isEmailAlreadyTaken(response):
            self._onEmailAddNeeded()
        raise AsyncReturn(response)

    @property
    def emailAddedTime(self):
        return self._emailAddedTime

    def _start(self):
        self._statuses.clear()
        self._requester = PlatformRequestsController()
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)
        self.itemsCache.onSyncCompleted += self._checkEmailConfirmed
        _logger.debug('WGNPRequestController has started.')

    def _stop(self):
        self._requester.clear()
        self._requester = None
        self._statuses.clear()
        g_clientUpdateManager.removeCallback('tokens', self.__onTokensUpdate)
        self.itemsCache.onSyncCompleted -= self._checkEmailConfirmed
        _logger.debug('WGNPRequestController has stopped.')
        return

    @async
    def _request(self, url, headers=None, timeout=REQUEST_TIMEOUT, method='GET', queryParams=None, postData=None, auth=False, proofOfWorkURL=None, showWaiting=True):
        if not self.getSettings().isEnabled() or self._requester is None:
            raise AsyncReturn(PlatformResponse(RES_FAILURE, '', None, httplib.SERVICE_UNAVAILABLE, None))
        waitingID = showWaiting and WAITING_ID or None
        proofOfWorkURL = self._getUrl(proofOfWorkURL) if proofOfWorkURL else proofOfWorkURL
        response = yield self._requester.request(self._getUrl(url), headers, timeout, method, queryParams, postData, auth, proofOfWorkURL, waitingID=waitingID)
        raise AsyncReturn(response)
        return

    def _getUrl(self, url):
        return urlparse.urljoin(self.getSettings().getUrl(), url)

    def _checkEmailConfirmed(self, *args, **kwargs):
        if self.itemsCache.items.tokens.isTokenAvailable(EMAIL_CONFIRMATION_TOKEN_NAME):
            self._onEmailConfirmed()
        self.itemsCache.onSyncCompleted -= self._checkEmailConfirmed

    def __onTokensUpdate(self, diff):
        if EMAIL_CONFIRMATION_TOKEN_NAME in diff:
            self._onEmailConfirmed()

    def _updateStatus(self, key, status):
        _logger.debug('Update status cache key=%s status=%s.', key, status)
        self._statuses[key] = PlatformResponse(exceptions.ResponseCodes.NO_ERRORS, '', status, httplib.OK, {})

    def _onEmailConfirmed(self):
        self._updateStatus(STATUS_TYPES.email.name(), {'state': 'complete'})
        _logger.debug('Send event on email confirmed.')
        self.onEmailConfirmed()

    def _onEmailAddNeeded(self):
        self._updateStatus(STATUS_TYPES.email.name(), {'state': 'no_active_request'})
        _logger.debug('Send event on email adding needed.')
        self.onEmailAddNeeded()

    def _onEmailAdded(self, email):
        self._updateStatus(STATUS_TYPES.email.name(), {'email': email,
         'state': 'email_sent'})
        _logger.debug('Send event on email added.')
        self.onEmailAdded(email)


def getRequestRestrictedUntilTime(response):
    return response.data.get('extras', {}).get('restricted_until', 0)


def isEmailConfirmationNeeded(response):
    return response.data and response.data.get('state') == 'email_sent'


def isSpaGenericConflict(response):
    return response.data and response.data.get('state') == 'spa_generic_conflict'


def isEmailAddingNeeded(response):
    return response.data and response.data.get('state') in ('no_active_request', 'spa_email_already_taken', 'confirmation_code_expired')


def getEmail(response):
    data = response.data or {}
    return data.get('email', '')


def isEmailInvalid(response):
    return _isError(response, 'email', 'invalid')


def isEmailForbidden(response):
    return _isError(response, 'email', 'forbidden')


def isEmailMinLength(response):
    return _isError(response, 'email', 'min_length')


def isEmailMaxLength(response):
    return _isError(response, 'email', 'max_length')


def isEmailBannedInCountry(response):
    return _isError(response, 'email', 'restricted_by_country_policy')


def isEmailRestrictedByCountry(response):
    return _isError(response, '__all__', 'restricted_by_country_policy')


def isEmailAlreadyTaken(response):
    return _isError(response, '__all__', 'spa_email_already_taken')


def isAccountAlreadyHasEmail(response):
    return _isError(response, '__all__', 'email_already_exists')


def isRequestLimitExceeded(response):
    return _isError(response, '__all__', 'request_limit_exceeded')


def isConfirmationCodeIncorrect(response):
    return _isError(response, '__all__', 'incorrect_confirmation_code')


def isConfirmationCodeDeactivated(response):
    return _isError(response, '__all__', 'incorrect_confirmation_code_request_deactivated')


def isConfirmationCodeExpired(response):
    return _isError(response, '__all__', 'no_active_request', 'confirmation_code_expired')


def _isError(response, errorType, *errorNames):
    return response.data and set(errorNames) & set(response.data.get('errors', {}).get(errorType, []))
