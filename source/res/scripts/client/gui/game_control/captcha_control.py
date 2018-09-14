# Embedded file name: scripts/client/gui/game_control/captcha_control.py
from functools import partial
import Event
import AccountCommands
import BigWorld
from account_helpers.captcha import CAPTCHA_API_CLASS
from adisp import async
from constants import JOIN_FAILURE
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.game_control.controllers import Controller
from helpers.aop import Aspect, Weaver, Pointcut
from helpers import i18n
from PlayerEvents import g_playerEvents
CAPTCHA_TRIES_LEFT_NOTIFY_THESHOLD = 1

def _showDialog(text, callback):
    from gui import DialogsInterface
    from gui.Scaleform.daapi.view.dialogs.CaptchaDialogMeta import CaptchaDialogMeta
    return DialogsInterface.showDialog(CaptchaDialogMeta(text), callback)


class CaptchaController(Controller):
    __api = CAPTCHA_API_CLASS()
    __battlesTillCaptcha = 99
    __triesLeft = 3
    _CLIENT_ERROR_CODES = {'enqueue-failure': i18n.makeString('#captcha:error-codes/enqueue-failure'),
     'response-is-empty': i18n.makeString('#captcha:error-codes/response-is-empty'),
     'challenge-is-empty': i18n.makeString('#captcha:error-codes/challenge-is-empty')}

    def __init__(self, proxy):
        super(CaptchaController, self).__init__(proxy)
        self.__tryReset = False
        self.__weaver = None
        self.onCaptchaInputCanceled = Event.Event()
        return

    def fini(self):
        self.onCaptchaInputCanceled.clear()
        self.__stop()
        self.__tryReset = False
        super(CaptchaController, self).fini()

    def onLobbyInited(self, event):
        self.__weaver = Weaver()
        BigWorld.player().stats.get('battlesTillCaptcha', self.__pc_onReceiveBattlesTillCaptcha)
        BigWorld.player().stats.get('captchaTriesLeft', self.__pc_onReceiveCaptchaTriesLeft)
        g_playerEvents.onEnqueueRandomFailure += self.__pe_onEnqueueRandomFailure
        g_playerEvents.onEnqueueEventBattlesFailure += self.__pe_onEnqueueEventBattlesFailure
        g_clientUpdateManager.addCallbacks({'stats.battlesTillCaptcha': self.__onBattlesTillCaptcha,
         'stats.captchaTriesLeft': self.__onCaptchaTriesLeft})

    def onDisconnected(self):
        self.__stop()

    def onAvatarBecomePlayer(self):
        self.__stop()

    def showCaptcha(self, callback):
        if self.__triesLeft <= CAPTCHA_TRIES_LEFT_NOTIFY_THESHOLD:
            errorText = i18n.makeString('#captcha:notification/remains-to-attempt', self.__triesLeft if self.__triesLeft > 0 else 0)
        else:
            errorText = None
        _showDialog(errorText, callback)
        return

    def getCaptchaServerError(self, errorCode):
        errorText = self.__api.getI18nServerErrorText(errorCode)
        if errorCode == self.__api._RESPONSE_IS_INCORRECT_CODE:
            triesLeftString = i18n.makeString('#captcha:notification/remains-to-attempt', self.__triesLeft)
            errorText = '{0:>s} {1:>s}'.format(errorText, triesLeftString)
        return errorText

    def getCaptchaClientError(self, errorCode):
        if errorCode in self._CLIENT_ERROR_CODES:
            errorMsg = i18n.makeString(self._CLIENT_ERROR_CODES[errorCode])
        else:
            errorMsg = errorCode
        return errorMsg

    def isCaptchaRequired(self):
        return False

    def getTriesLeft(self):
        return self.__triesLeft

    def getPublicKey(self):
        settings = BigWorld.player().serverSettings
        if settings.has_key('captchaKey'):
            return settings['captchaKey']
        else:
            return None

    def getCaptchaRegex(self):
        return BigWorld.player().serverSettings.get('reCaptchaParser', '')

    def getImageSource(self):
        return self.__api.getImageSource(self.getPublicKey(), self.getCaptchaRegex())

    def getImageSize(self):
        return self.__api._IMAGE_SIZE

    @async
    def verify(self, challenge, response, callback = None):
        BigWorld.player().challengeCaptcha(challenge, response, partial(self.__pc_onCaptchaChecked, callback))

    def tryBattlesTillCaptchaReset(self):
        if self.__tryReset:
            return
        if self.__triesLeft > 1:
            self.__tryReset = True
            LOG_WARNING('Client try battlesTillCaptcha reset')
            BigWorld.player().challengeCaptcha('', '', lambda resultID, errorCode: None)

    def __stop(self):
        if self.__weaver is not None:
            self.__weaver.clear()
            self.__weaver = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_playerEvents.onEnqueueEventBattlesFailure -= self.__pe_onEnqueueEventBattlesFailure
        g_playerEvents.onEnqueueRandomFailure -= self.__pe_onEnqueueRandomFailure
        return

    def __pe_onEnqueueRandomFailure(self, errorCode, _):
        if errorCode != JOIN_FAILURE.CAPTCHA:
            return

        def callback(result):
            if result:
                from CurrentVehicle import g_currentVehicle
                BigWorld.player().enqueueRandom(g_currentVehicle.invID)
            else:
                from gui.Scaleform.Waiting import Waiting
                Waiting.rollback()
                self.onCaptchaInputCanceled()

        _showDialog(i18n.makeString(self._CLIENT_ERROR_CODES['enqueue-failure']), callback)

    def __pe_onEnqueueEventBattlesFailure(self, errorCode, _):
        if errorCode != JOIN_FAILURE.CAPTCHA:
            return

        def callback(result):
            if result:
                from CurrentVehicle import g_currentVehicle
                BigWorld.player().enqueueEventBattles(g_currentVehicle.invID)
            else:
                from gui.Scaleform.Waiting import Waiting
                Waiting.rollback()
                self.onCaptchaInputCanceled()

        _showDialog(i18n.makeString(self._CLIENT_ERROR_CODES['enqueue-failure']), callback)

    def __onBattlesTillCaptcha(self, value):
        self.__battlesTillCaptcha = value
        if self.isCaptchaRequired():
            if self.__weaver.findPointcut(ShowCaptchaPointcut) is -1:
                self.__weaver.weave(pointcut=ShowCaptchaPointcut, aspects=[ShowCaptchaAspect(self)])

    def __onCaptchaTriesLeft(self, value):
        self.__triesLeft = value

    def __pc_onReceiveBattlesTillCaptcha(self, resultID, value):
        if resultID < 0:
            LOG_ERROR('Server return error: ', resultID, value)
            return
        self.__battlesTillCaptcha = value
        if self.isCaptchaRequired():
            if self.__weaver.findPointcut(ShowCaptchaPointcut) is -1:
                self.__weaver.weave(pointcut=ShowCaptchaPointcut, aspects=[ShowCaptchaAspect(self)])

    def __pc_onReceiveCaptchaTriesLeft(self, resultID, value):
        if resultID < 0:
            LOG_ERROR('Server return error: ', resultID, value)
            return
        self.__triesLeft = value

    def __pc_onCaptchaChecked(self, callback, resultID, responseCode):
        isVerified = resultID == AccountCommands.RES_SUCCESS
        if isVerified:
            self.__weaver.clear(idx=self.__weaver.findPointcut(ShowCaptchaPointcut))
        callback((isVerified, responseCode))


class ShowCaptchaAspect(Aspect):

    def __init__(self, controller):
        super(ShowCaptchaAspect, self).__init__()
        self.__controller = controller

    def atCall(self, cd):

        def callback(result):
            if result:
                cd.function(*cd._packArgs(), **cd._kwargs)
            else:
                from gui.Scaleform.Waiting import Waiting
                Waiting.rollback()
                self.__controller.onCaptchaInputCanceled()

        self.__controller.showCaptcha(callback)
        cd.avoid()

    def clear(self):
        self.__controller = None
        return


class ShowCaptchaPointcut(Pointcut):

    def __init__(self):
        super(ShowCaptchaPointcut, self).__init__('Account', 'PlayerAccount', '^(enqueueRandom|enqueueTutorial|prb_createTraining|prb_createSquad|enqueueHistorical|enqueueEventBattles|prb_createCompany|prb_join|prb_ready|prb_teamReady|prb_acceptInvite)$')
