# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/wgnp/steam_account/response.py
from gui.platform.base.response import PlatformResponse

class WGNPSteamEmailActionResponse(PlatformResponse):

    @property
    def isAccountAlreadyHasEmail(self):
        return self._isError('__all__', 'email_already_exists')

    @property
    def isEmailAlreadyTaken(self):
        return self._isError('__all__', 'spa_email_already_taken')


class WGNPSteamAccEmailAddResponse(WGNPSteamEmailActionResponse):

    @property
    def requestRestrictedUntilTime(self):
        return self.getData().get('extras', {}).get('restricted_until', 0)

    @property
    def isEmailInvalid(self):
        return self._isError('email', 'invalid')

    @property
    def isEmailForbidden(self):
        return self._isError('email', 'forbidden')

    @property
    def isEmailMinLength(self):
        return self._isError('email', 'min_length')

    @property
    def isEmailMaxLength(self):
        return self._isError('email', 'max_length')

    @property
    def isEmailBannedInCountry(self):
        return self._isError('email', 'restricted_by_country_policy')

    @property
    def isEmailRestrictedByCountry(self):
        return self._isError('__all__', 'restricted_by_country_policy')

    @property
    def isRequestLimitExceeded(self):
        return self._isError('__all__', 'request_limit_exceeded')


class WGNPSteamAccEmailConfirmResponse(WGNPSteamEmailActionResponse):

    @property
    def isConfirmationCodeIncorrect(self):
        return self._isError('__all__', 'incorrect_confirmation_code')

    @property
    def isConfirmationCodeDeactivated(self):
        return self._isError('__all__', 'incorrect_confirmation_code_request_deactivated')

    @property
    def isConfirmationCodeExpired(self):
        return self._isError('__all__', 'no_active_request', 'confirmation_code_expired')
