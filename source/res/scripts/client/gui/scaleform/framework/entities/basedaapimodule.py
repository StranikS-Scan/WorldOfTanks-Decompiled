# Embedded file name: scripts/client/gui/Scaleform/framework/entities/BaseDAAPIModule.py
from debug_utils import LOG_ERROR
from gui.Scaleform.framework.entities.abstract.BaseDAAPIModuleMeta import BaseDAAPIModuleMeta

class BaseDAAPIModule(BaseDAAPIModuleMeta):

    def __init__(self):
        super(BaseDAAPIModule, self).__init__()
        self.__isScriptSet = False
        self.__app = None
        return

    @property
    def app(self):
        return self.__app

    def seEnvironment(self, app):
        self.__app = app

    def _printOverrideError(self, methodName):
        LOG_ERROR('Method must be override!', methodName, self.__class__)

    def setFlashObject(self, movieClip, autoPopulate = True, setScript = True):
        if movieClip is not None:
            self.__isScriptSet = setScript
            try:
                self.turnDAAPIon(setScript, movieClip)
            except:
                raise Exception, 'Can not initialize daapi in ' + str(self)

            if autoPopulate:
                if self._isCreated():
                    LOG_ERROR('object {0} is already created! Please, set flag autoPopulate=False'.format(str(self)))
                else:
                    self.create()
        else:
            LOG_ERROR('flashObject reference can`t be None!')
        return

    def _populate(self):
        super(BaseDAAPIModule, self)._populate()
        self.as_populateS()

    def _dispose(self):
        super(BaseDAAPIModule, self)._dispose()
        if self.flashObject is not None:
            try:
                if self.__isScriptSet:
                    self.as_disposeS()
            except:
                LOG_ERROR('Error during %s flash disposing' % str(self))

            self.turnDAAPIoff(self.__isScriptSet)
        self.__app = None
        return
