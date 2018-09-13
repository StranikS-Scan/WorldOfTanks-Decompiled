# Embedded file name: scripts/client/account_helpers/captcha/__init__.py
from constants import CAPTCHA_API, CURRENT_CAPTCHA_API
from helpers import i18n
SUPPORTED_CAPTCHA_APIS = {CAPTCHA_API.RE_CAPTCHA: ('account_helpers.captcha.reCAPTCHA', 'reCAPTCHA'),
 CAPTCHA_API.KONG: ('account_helpers.captcha.Kong', 'Kong')}

class _BASE_CAPTCHA_API(object):
    _SERVER_API_URL = None
    _SERVER_ERROR_CODES = {}
    _RESPONSE_IS_INCORRECT_CODE = None
    _IMAGE_SIZE = (0, 0)

    def getI18nServerErrorText(self, errorCode, defaultErrorCode = 'unknown'):
        key = self._SERVER_ERROR_CODES.get(errorCode)
        if key is None:
            key = self._SERVER_ERROR_CODES.get(defaultErrorCode)
        if key is None:
            raise Exception, "It is impossible to determine error text for code = '%s', default code = '%s'" % (errorCode, defaultErrorCode)
        return i18n.makeString(key)

    def getImageSource(self, publicKey, *args):
        raise NotImplemented, 'method getImageSource must be implement'


def _CAPTCHA_API_FACTORY():
    module, clazz = SUPPORTED_CAPTCHA_APIS.get(CURRENT_CAPTCHA_API, (None, None))
    if module is not None:
        imported = __import__(module, globals(), locals(), [clazz])
        return getattr(imported, clazz)
    else:
        return _BASE_CAPTCHA_API


CAPTCHA_API_CLASS = _CAPTCHA_API_FACTORY()
