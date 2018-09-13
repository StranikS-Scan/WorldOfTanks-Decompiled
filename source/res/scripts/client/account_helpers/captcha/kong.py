# Embedded file name: scripts/client/account_helpers/captcha/Kong.py
from account_helpers.captcha import _BASE_CAPTCHA_API
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG
import time
import urllib

class Kong(_BASE_CAPTCHA_API):
    _SERVER_API_URL = 'http://katpcha.worldoftanks.cn:8081'
    _SERVER_ERROR_CODES = {'unknown': '#kong_captcha:error-codes/unknown',
     'empty response': '#kong_captcha:error-codes/empty-response',
     'wrong response': '#kong_captcha:error-codes/wrong-response',
     'invalid challenge code': '#kong_captcha:error-codes/invalid-challenge-code'}
    _RESPONSE_IS_INCORRECT_CODE = 'wrong response'
    _IMAGE_SIZE = (300, 60)

    def getImageSource(self, publicKey, *args):
        start = time.time()
        pic = None
        challenge = ''
        resp = None
        try:
            resp = urllib.urlopen('%s/captcha.jsp' % self._SERVER_API_URL)
            challenge = resp.read()
            params = urllib.urlencode({'s': challenge})
            resp = urllib.urlopen('%s/verifyCodeServlet?%s' % (self._SERVER_API_URL, params))
            contentType = resp.headers.get('content-type')
            if contentType == 'image/jpeg':
                pic = resp.read()
            else:
                LOG_ERROR('client can not load KONG CAPTCHA image', contentType)
        except:
            LOG_ERROR('client can not load KONG CAPTCHA image')
            LOG_CURRENT_EXCEPTION()
        finally:
            if resp is not None:
                resp.close()

        LOG_DEBUG('get image from web for %.02f seconds' % (time.time() - start))
        return (pic, challenge)
