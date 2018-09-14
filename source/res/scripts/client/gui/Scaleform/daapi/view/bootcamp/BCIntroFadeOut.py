# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCIntroFadeOut.py
from gui.Scaleform.daapi.view.meta.BCIntroFadeOutMeta import BCIntroFadeOutMeta
from bootcamp.BootCampEvents import g_bootcampEvents

class BCIntroFadeOut(BCIntroFadeOutMeta):

    def __init__(self, settings):
        super(BCIntroFadeOut, self).__init__()
        self.__duration = settings['duration']

    def finished(self):
        self.destroy()

    def handleError(self, data):
        pass

    def _populate(self):
        super(BCIntroFadeOut, self)._populate()
        self.__start()

    def _dispose(self):
        super(BCIntroFadeOut, self)._dispose()

    def __start(self):
        self.as_StartFadeoutS(self.__duration)
        self.app.leaveGuiControlMode(self.alias)

    def __onFinish(self, destroyView):
        g_bootcampEvents.onIntroVideoStop()
        if destroyView:
            self.destroy()
