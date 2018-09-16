# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/BaseDAAPIModule.py
from soft_exception import SoftException
from debug_utils import LOG_ERROR
from gui.Scaleform.framework.entities.abstract.BaseDAAPIModuleMeta import BaseDAAPIModuleMeta

class BaseDAAPIModule(BaseDAAPIModuleMeta):

    def __init__(self):
        super(BaseDAAPIModule, self).__init__()
        self.__isScriptSet = False
        self.__isPyReloading = False
        self.__app = None
        return

    @property
    def app(self):
        return self.__app

    def setEnvironment(self, app):
        self.__app = app

    def setPyReloading(self, flag):
        self.__isPyReloading = flag

    def setFlashObject(self, movieClip, autoPopulate=True, setScript=True):
        if movieClip is not None:
            self.__isScriptSet = setScript
            try:
                self.turnDAAPIon(setScript, movieClip)
            except Exception:
                raise SoftException('Can not initialize daapi in ' + str(self))

            if autoPopulate:
                if self.isCreated():
                    LOG_ERROR('object {0} is already created! Please, set flag autoPopulate=False'.format(str(self)))
                else:
                    self.create()
        else:
            LOG_ERROR('flashObject reference can`t be None!')
        return

    def _populate(self):
        super(BaseDAAPIModule, self)._populate()
        self.as_populateS()

    def _destroy(self):
        super(BaseDAAPIModule, self)._destroy()
        if self.flashObject is not None:
            try:
                if self.__isScriptSet and not self.__isPyReloading:
                    self.as_disposeS()
            except Exception:
                LOG_ERROR('Error during %s flash disposing' % str(self))

            self.turnDAAPIoff(self.__isScriptSet)
        self.__app = None
        return

    def _printOverrideError(self, methodName):
        LOG_ERROR('Method must be override!', methodName, self.__class__)
