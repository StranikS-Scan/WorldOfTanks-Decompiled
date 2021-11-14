# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/wgnp/demo_account/response.py
from httplib import REQUEST_TIMEOUT
from gui.platform.base.response import PlatformResponse

class WGNPDemoAccCredentialsActionResponse(PlatformResponse):

    @property
    def isAccountAlreadyHasLogin(self):
        return self._isError('__all__', 'spa_already_has_login')

    @property
    def isLoginAlreadyTaken(self):
        return self._isError('__all__', 'spa_login_already_taken')


class WGNPDemoAccCredentialsAddResponse(WGNPDemoAccCredentialsActionResponse):

    @property
    def requestRestrictedUntilTime(self):
        return self.getData().get('extras', {}).get('restricted_until', 0)

    @property
    def isCredentialsNotFound(self):
        return self._isError('__all__', 'not_found')

    @property
    def isRequestLimitExceeded(self):
        return self._isError('__all__', 'request_limit_exceeded')

    @property
    def isPasswordWeak(self):
        return self._isError('password', 'weak_password') or self._isError('__all__', 'weak_password')

    @property
    def isRestrictedByCountryPolicy(self):
        return self._isError('login', 'restricted_by_country_policy')

    @property
    def isLoginInvalid(self):
        return self._isError('login', 'invalid')

    @property
    def isLoginEmpty(self):
        return self._isError('login', 'required')

    @property
    def isLoginMinLength(self):
        return self._isError('login', 'min_length')

    @property
    def isLoginMaxLength(self):
        return self._isError('login', 'max_length')

    @property
    def isPasswordInvalid(self):
        return self._isError('password', 'invalid')

    @property
    def isPasswordEmpty(self):
        return self._isError('password', 'required')

    @property
    def isPasswordMinLength(self):
        return self._isError('password', 'min_length')

    @property
    def isPasswordMaxLength(self):
        return self._isError('password', 'max_length')


class WGNPDemoAccCredentialsConfirmResponse(WGNPDemoAccCredentialsActionResponse):

    @property
    def isConfirmationCodeIncorrect(self):
        return self._isError('__all__', 'incorrect_confirmation_code')

    @property
    def isConfirmationCodeDeactivated(self):
        return self._isError('__all__', 'incorrect_confirmation_code_request_deactivated')

    @property
    def isConfirmationCodeExpired(self):
        return self._isError('__all__', 'no_active_request')

    @property
    def isFormInvalid(self):
        return self._isError('__all__', 'invalid_form')

    @property
    def isCodeEmpty(self):
        return self._isError('code', 'required')

    @property
    def isSpaWeakPassword(self):
        return self._isError('__all__', 'spa_weak_password')

    @property
    def isSpaGenericConflict(self):
        return self._isError('__all__', 'spa_generic_conflict')

    @property
    def isInvalidChoice(self):
        return self._isError('game', 'invalid_choice')


class WGNPDemoAccChangeNicknameResponse(PlatformResponse):

    @property
    def isNameEmpty(self):
        return self._isError('name', 'required')

    @property
    def isNameInvalid(self):
        return self._isError('name', 'invalid')

    @property
    def isNameMaxLength(self):
        return self._isError('name', 'max_length')

    @property
    def isNameMinLength(self):
        return self._isError('name', 'min_length')

    @property
    def isNameForbidden(self):
        return self._isError('name', 'forbidden')

    @property
    def isNameExists(self):
        return self._isError('name', 'exists')

    @property
    def isGameEmpty(self):
        return self._isError('game', 'required')

    @property
    def isGameInvalid(self):
        return self._isError('game', 'invalid')

    @property
    def isCostEmpty(self):
        return self._isError('cost', 'required')

    @property
    def isCostInvalid(self):
        return self._isError('cost', 'invalid')

    @property
    def isViaMaxLength(self):
        return self._isError('via', 'max_length')

    @property
    def isTimeout(self):
        return self._isError('__all__', 'timeout') or self.getExtraCode() == REQUEST_TIMEOUT

    @property
    def isRequestTimeout(self):
        return self._isError('__all__', 'rename_request_timeout')

    @property
    def isAuthTokenExpired(self):
        return self._isError('__all__', 'oauth_token_expired')

    @property
    def isAuthTokenDenied(self):
        return self._isError('__all__', 'oauth_permission_denied')

    @property
    def isNEGold(self):
        return self._isError('__all__', 'ne_gold')

    @property
    def isFreeCostUnavailable(self):
        return self._isError('__all__', 'does_not_have_demo_free_first_renaming')

    @property
    def isCurrencyBanned(self):
        return self._isError('__all__', 'unknown_ban_type')

    @property
    def isNeedNicknameStatusCheck(self):
        return self._isError('__all__', 'rename_request_timeout', 'does_not_have_demo_free_first_renaming')


class WGNPDemoAccValidateNicknameResponse(PlatformResponse):

    @property
    def spaId(self):
        return self.getData().get('spa_id')

    @property
    def suggestions(self):
        return self.getData().get('suggestions', [])

    @property
    def isBanned(self):
        return self.getData().get('banned', False)

    @property
    def isOccupied(self):
        return self.spaId is not None

    @property
    def isInvalid(self):
        return 'invalid' in self.getData().get('__all__', [])

    @property
    def isMinLength(self):
        return 'min_length' in self.getData().get('__all__', [])

    @property
    def isMaxLength(self):
        return 'max_length' in self.getData().get('__all__', [])
