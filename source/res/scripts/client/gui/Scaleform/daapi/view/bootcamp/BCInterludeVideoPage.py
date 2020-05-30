# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCInterludeVideoPage.py
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.daapi.view.bootcamp.BCVideoPage import BCVideoPage
from bootcamp.statistic.decorators import loggerTarget, loggerEntry, simpleLog
from bootcamp.statistic.logging_constants import BC_LOG_ACTIONS, BC_LOG_KEYS

@loggerTarget(logKey=BC_LOG_KEYS.BC_INTERLUDE_VIDEO)
class BCInterludeVideoPage(BCVideoPage):
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, settings):
        super(BCInterludeVideoPage, self).__init__(settings)
        self._content = settings

    @property
    def content(self):
        return self._content

    @loggerEntry
    def _populate(self):
        super(BCInterludeVideoPage, self)._populate()
        self.appLoader.onGUISpaceLeft += self._onGUISpaceLeft

    def _dispose(self):
        self.appLoader.onGUISpaceLeft -= self._onGUISpaceLeft
        super(BCInterludeVideoPage, self)._dispose()

    @simpleLog(action=BC_LOG_ACTIONS.SKIP_VIDEO)
    def _onDestroy(self):
        super(BCInterludeVideoPage, self)._onDestroy()

    def _onFinish(self):
        if self.content.get('exitEvent', False):
            self.content['exitEvent']()
        super(BCInterludeVideoPage, self)._onFinish()

    def _onGUISpaceLeft(self, _):
        super(BCInterludeVideoPage, self)._onFinish()
