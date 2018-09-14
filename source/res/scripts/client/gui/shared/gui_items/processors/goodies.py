# Embedded file name: scripts/client/gui/shared/gui_items/processors/goodies.py
import BigWorld
from debug_utils import LOG_DEBUG
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess, plugins

class BoosterActivator(Processor):

    def __init__(self, booster):
        self.__boosterID = booster.boosterID
        self.__boosterName = booster.userName
        self.__effectTime = booster.getEffectTimeStr()
        super(BoosterActivator, self).__init__((plugins.BoosterActivateValidator(booster),))

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('booster/%s' % errStr, boosterName=self.__boosterName)
        return makeI18nError('booster/server_error', boosterName=self.__boosterName)

    def _successHandler(self, code, ctx = None):
        localKey = 'booster/activationSuccess'
        return makeI18nSuccess(localKey, boosterName=self.__boosterName, time=self.__effectTime)

    def _request(self, callback):
        LOG_DEBUG('Make server request to activate booster', self.__boosterID, self.__boosterName)
        BigWorld.player().activateGoodie([self.__boosterID], lambda code, errStr: self._response(code, callback, errStr=errStr))
