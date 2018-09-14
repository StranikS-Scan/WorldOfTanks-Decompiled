# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/CaptchaDialog.py
import threading
import time
import weakref
import BigWorld
from adisp import process
from debug_utils import LOG_DEBUG, LOG_CURRENT_EXCEPTION
from gui import SystemMessages, game_control
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import events, EVENT_BUS_SCOPE
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.meta.CAPTCHAMeta import CAPTCHAMeta

class CaptchaImageWorker(threading.Thread):

    def __init__(self, sharedObj, callbackName):
        super(CaptchaImageWorker, self).__init__()
        self.sharedObj = weakref.ref(sharedObj)
        self.callbackName = callbackName

    def __del__(self):
        LOG_DEBUG('CaptchaImageWorker deleted')

    def run(self):
        obj = self.sharedObj()
        if obj is None:
            return
        else:
            imageName = obj.generateImageName()
            binaryData, challenge = obj.getImageSource()
            if binaryData is None or len(binaryData) == 0 or len(challenge) == 0:
                callback = getattr(self.sharedObj(), self.callbackName, None)
                if callback is not None and callable(callback):
                    callback(None)
                self.sharedObj = None
                return
            try:
                BigWorld.wg_addTempScaleformTexture(imageName, binaryData)
            except AttributeError:
                LOG_CURRENT_EXCEPTION()
                challenge = None

            callback = getattr(self.sharedObj(), self.callbackName, None)
            if callback is not None and callable(callback):
                callback(challenge)
            self.sharedObj = None
            return


class CaptchaDialog(CAPTCHAMeta):
    CAPTCHA_IMAGE_NAME = 'captcha-cache-{0:n}'

    def __init__(self, meta, handler):
        super(CaptchaDialog, self).__init__()
        self.__meta = meta
        self.__handler = handler
        self.__challenge = None
        self.__imageName = ''
        return

    @property
    def controller(self):
        return game_control.g_instance.captcha

    def generateImageName(self):
        self.__imageName = self.CAPTCHA_IMAGE_NAME.format(int(time.time()))
        return self.__imageName

    def getImageSource(self):
        return self.controller.getImageSource()

    @process
    def submit(self, response):
        response = response.strip()
        controller = self.controller
        if self.__challenge is None:
            self.as_setErrorMessageS(controller.getCaptchaClientError('challenge-is-empty'))
            yield lambda callback = None: callback
        if not len(response):
            self.as_setErrorMessageS(controller.getCaptchaClientError('response-is-empty'))
            yield lambda callback = None: callback
        Waiting.show('verifyCaptcha')
        result, errorCode = yield controller.verify(self.__challenge, response)
        Waiting.hide('verifyCaptcha')
        if result:
            self._close(True)
        else:
            if controller.getTriesLeft() > 0:
                self.reload()
            self.as_setErrorMessageS(controller.getCaptchaServerError(errorCode))
        return

    def reload(self):
        Waiting.show('reloadCaptcha')
        CaptchaImageWorker(self, '_CaptchaDialog__afterImageReload').start()

    def onWindowClose(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        self._close(False)

    def _populate(self):
        super(CaptchaDialog, self)._populate()
        Waiting.show('requestCaptcha')
        CaptchaImageWorker(self, '_CaptchaDialog__afterImageCreate').start()

    def _dispose(self):
        self.__meta = None
        self.__handler = None
        self.__challenge = None
        self.__imageName = ''
        super(CaptchaDialog, self)._dispose()
        return

    def _close(self, result):
        if self.__handler is not None:
            self.__handler(result)
        self.destroy()
        return

    def __afterImageCreate(self, challenge):
        Waiting.hide('requestCaptcha')
        Waiting.suspend()
        if challenge is not None:
            self.__challenge = challenge
            self.__setCaptchaImageSource()
            if self.__meta.hasError():
                self.as_setErrorMessageS(self.__meta.getErrorText())
        else:
            SystemMessages.pushI18nMessage('#captcha:error-codes/image-internal-error', type=SystemMessages.SM_TYPE.Error)
            self.controller.tryBattlesTillCaptchaReset()
            self._close(False)
        return

    def __afterImageReload(self, challenge):
        Waiting.hide('reloadCaptcha')
        if challenge is not None:
            self.__challenge = challenge
            self.__setCaptchaImageSource()
        else:
            SystemMessages.pushI18nMessage('#captcha:error-codes/image-internal-error', type=SystemMessages.SM_TYPE.Error)
            self.controller.tryBattlesTillCaptchaReset()
            self._close(False)
        return

    def __setCaptchaImageSource(self):
        width, height = self.controller.getImageSize()
        self.as_setImageS(self.__imageName, width, height)
