# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/CaptchaView.py
# Compiled at: 2011-07-11 14:58:24
from gui import SystemMessages
from helpers import i18n
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG
from gui.CaptchaUI import CaptchaUI
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.Waiting import Waiting
import time
import threading
CAPTCHA_IMAGE_NAME = 'captcha-cache-%s'
CAPTCHA_IMAGE_URL = 'img://' + CAPTCHA_IMAGE_NAME
CAPTCHA_TRIES_LEFT_NOTIFY_THESHOLD = 1

class CaptchaImageWorker(threading.Thread):

    def __init__(self, sharedObj, callbackName):
        super(CaptchaImageWorker, self).__init__()
        self.sharedObj = sharedObj
        self.callbackName = callbackName

    def __del__(self):
        LOG_DEBUG('CaptchaImageWorker deleted')

    def run(self):
        if self.sharedObj is None:
            return
        else:
            binaryData, challenge = self.sharedObj._api.getImageSource(self.sharedObj.getPublicKey(), self.sharedObj.getCaptchaRegex())
            if binaryData is None or len(binaryData) == 0 or len(challenge) == 0:
                getattr(self.sharedObj, self.callbackName)(None)
                self.sharedObj = None
                return
            try:
                imageID = CAPTCHA_IMAGE_NAME % self.sharedObj.generateImageID()
                BigWorld.wg_addTempScaleformTexture(imageID, binaryData)
            except AttributeError:
                LOG_CURRENT_EXCEPTION()
                challenge = None

            getattr(self.sharedObj, self.callbackName)(challenge)
            self.sharedObj = None
            return


class CaptchaView(CaptchaUI, UIInterface):
    _challenge = None
    __callback = None
    __imageID = 0
    __tryReset = False

    def generateImageID(self):
        self.__imageID = int(time.time())
        return self.__imageID

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.startListening()
        self.uiHolder.addExternalCallbacks({'CAPTCHA.ReloadImage': self.onReloadImage,
         'CAPTCHA.HandleClose': self.onHandleClose,
         'CAPTCHA.VerifyResponse': self.onVerifyResponse})

    def dispossessUI(self):
        self.stopListening()
        self.uiHolder.removeExternalCallbacks('CAPTCHA.ReloadImage', 'CAPTCHA.HandleClose', 'CAPTCHA.VerifyResponse')
        UIInterface.dispossessUI(self)
        self.__clearData()

    def __setCaptchaImageSource(self):
        width, height = self._api._IMAGE_SIZE
        self.uiHolder.call('CAPTCHA.SetImageUrl', [CAPTCHA_IMAGE_URL % self.__imageID, width, height])

    def __clearData(self):
        self._challenge = None
        self.__callback = None
        return

    def showCaptcha(self, callback=None):
        if self.getPublicKey() is None:
            SystemMessages.pushI18nMessage('#captcha:error-codes/public-key-empty', type=SystemMessages.SM_TYPE.Error)
            return
        else:
            Waiting.show('requestCaptcha')
            self.__callback = callback
            self.uiHolder.call('common.showCaptcha')
            CaptchaImageWorker(self, '_CaptchaView__afterImageCreate').start()
            return

    def __afterImageCreate(self, challenge):
        if challenge is not None:
            self._challenge = challenge
            self.__tryReset = False
            self.__setCaptchaImageSource()
            if self._captchaTriesLeft <= CAPTCHA_TRIES_LEFT_NOTIFY_THESHOLD:
                errorText = i18n.makeString('#captcha:notification/remains-to-attempt', self._captchaTriesLeft if self._captchaTriesLeft > 0 else 0)
                self.uiHolder.call('CAPTCHA.SetErrorMessage', [errorText])
        else:
            self.closeCaptcha()
            SystemMessages.pushI18nMessage('#captcha:error-codes/image-internal-error', type=SystemMessages.SM_TYPE.Error)
            if not self.__tryReset:
                self.__tryReset = True
                self.tryBattlesTillCaptchaReset()
        Waiting.hide('requestCaptcha')
        return

    def closeCaptcha(self):
        self.uiHolder.call('common.closeCaptcha')
        self.__clearData()

    def reloadCaptcha(self):
        if self.getPublicKey() is None:
            SystemMessages.pushI18nMessage('#captcha:error-codes/public-key-empty', type=SystemMessages.SM_TYPE.Error)
            return
        else:
            Waiting.show('reloadCaptcha')
            CaptchaImageWorker(self, '_CaptchaView__afterImageReload').start()
            return

    def __afterImageReload(self, challenge):
        if challenge is not None:
            self._challenge = challenge
            self.__setCaptchaImageSource()
        else:
            self.closeCaptcha()
            SystemMessages.pushI18nMessage('#captcha:error-codes/image-internal-error', type=SystemMessages.SM_TYPE.Error)
        Waiting.hide('reloadCaptcha')
        return

    def setCaptchaVerified(self):
        Waiting.hide('verifyCaptcha')
        if self.__callback is not None:
            self.__callback()
        self.closeCaptcha()
        return

    def setCaptchaServerError(self, errorCode):
        if Waiting.isVisible():
            Waiting.hide('verifyCaptcha')
        errorText = self._api.getI18nServerErrorText(errorCode)
        if errorCode == self._api._RESPONSE_IS_INCORRECT_CODE:
            triesLeftString = i18n.makeString('#captcha:notification/remains-to-attempt', self._captchaTriesLeft)
            errorText = '{0:>s} {1:>s}'.format(errorText, triesLeftString)
        self.uiHolder.call('CAPTCHA.SetErrorMessage', [errorText])

    def setCaptchaClientError(self, errorText):
        self.uiHolder.call('CAPTCHA.SetErrorMessage', [errorText])

    def onReloadImage(self, responseId):
        self.reloadCaptcha()

    def onHandleClose(self, responseId):
        self.__clearData()
        self.uiHolder.movie.invoke(('loadHangar',))

    def onVerifyResponse(self, responseId, response):
        response = response.strip()
        if self._challenge is None:
            self.setCaptchaClientError(self._CLIENT_ERROR_CODES['challenge-is-empty'])
            return
        elif not len(response):
            self.setCaptchaClientError(self._CLIENT_ERROR_CODES['challenge-is-empty'])
            return
        else:
            Waiting.show('verifyCaptcha')
            self.verify(self._challenge, response)
            return
