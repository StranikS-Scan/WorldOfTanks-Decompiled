# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/CaptchaUI.py
# Compiled at: 2011-09-24 01:55:22
from abc import ABCMeta, abstractmethod
import AccountCommands
import BigWorld
from account_helpers.captcha import CAPTCHA_API_CLASS
from constants import JOIN_FAILURE
from debug_utils import LOG_ERROR, LOG_WARNING
from helpers import i18n
from PlayerEvents import g_playerEvents

class CaptchaUI(object):
    __metaclass__ = ABCMeta
    _callback = None
    _api = CAPTCHA_API_CLASS()
    _battlesTillCaptcha = 99
    _captchaTriesLeft = 3
    _CLIENT_ERROR_CODES = {'enqueue-failure': i18n.makeString('#captcha:error-codes/enqueue-failure'),
     'response-is-empty': i18n.makeString('#captcha:error-codes/response-is-empty'),
     'challenge-is-empty': i18n.makeString('#captcha:error-codes/challenge-is-empty')}

    @abstractmethod
    def showCaptcha(self, callback=None):
        pass

    @abstractmethod
    def closeCaptcha(self):
        pass

    @abstractmethod
    def reloadCaptcha(self):
        pass

    @abstractmethod
    def setCaptchaVerified(self):
        pass

    @abstractmethod
    def setCaptchaServerError(self, errorCode):
        pass

    @abstractmethod
    def setCaptchaClientError(self, errorTest):
        pass

    def isCaptchaRequired(self):
        return self._battlesTillCaptcha <= 0

    def getPublicKey(self):
        settings = BigWorld.player().serverSettings
        if settings.has_key('captchaKey'):
            return settings['captchaKey']
        else:
            return None

    def getCaptchaRegex(self):
        return BigWorld.player().serverSettings.get('reCaptchaParser', '')

    def verify(self, challenge, response):
        BigWorld.player().challengeCaptcha(challenge, response, self.__pc_onCaptchaChecked)

    def tryBattlesTillCaptchaReset(self):
        if self._captchaTriesLeft > 1:
            LOG_WARNING('Client try battlesTillCaptcha reset')
            BigWorld.player().challengeCaptcha('', '', lambda resultID, errorCode: None)

    def startListening(self):
        BigWorld.player().stats.get('battlesTillCaptcha', self.__pc_onReceiveBattlesTillCaptcha)
        BigWorld.player().stats.get('captchaTriesLeft', self.__pc_onReceiveCaptchaTriesLeft)
        g_playerEvents.onEnqueueFailure += self.__pe_onEnqueueFailure
        g_playerEvents.onClientUpdated += self.__pe_onClientUpdated

    def stopListening(self):
        g_playerEvents.onEnqueueFailure -= self.__pe_onEnqueueFailure
        g_playerEvents.onClientUpdated -= self.__pe_onClientUpdated

    def __pe_onEnqueueFailure(self, errorCode, errorStr):
        if errorCode != JOIN_FAILURE.CAPTCHA:
            return
        self.showCaptcha()
        self.setCaptchaClientError(self._CLIENT_ERROR_CODES['enqueue-failure'])

    def __pe_onClientUpdated(self, diff):
        stats = diff.get('stats', {})
        if 'battlesTillCaptcha' in stats:
            self._battlesTillCaptcha = stats['battlesTillCaptcha']
        if 'captchaTriesLeft' in stats:
            self._captchaTriesLeft = stats['captchaTriesLeft']

    def __pc_onReceiveBattlesTillCaptcha(self, resultID, value):
        if resultID < 0:
            LOG_ERROR('Server return error: ', resultID, value)
            return
        self._battlesTillCaptcha = value

    def __pc_onReceiveCaptchaTriesLeft(self, resultID, value):
        if resultID < 0:
            LOG_ERROR('Server return error: ', resultID, value)
            return
        self._captchaTriesLeft = value

    def __pc_onCaptchaChecked(self, resultID, errorCode):
        if resultID == AccountCommands.RES_SUCCESS:
            self.setCaptchaVerified()
        else:
            if self._captchaTriesLeft > 0:
                self.reloadCaptcha()
            self.setCaptchaServerError(errorCode)
