# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCInterludeVideoPage.py
from gui.Scaleform.daapi.view.bootcamp.BCVideoPage import BCVideoPage
from bootcamp.statistic.decorators import loggerTarget, loggerEntry, simpleLog
from bootcamp.statistic.logging_constants import BC_LOG_ACTIONS, BC_LOG_KEYS

@loggerTarget(logKey=BC_LOG_KEYS.BC_INTERLUDE_VIDEO)
class BCInterludeVideoPage(BCVideoPage):

    def __init__(self, settings):
        super(BCInterludeVideoPage, self).__init__(settings)
        self._content = settings

    @property
    def content(self):
        return self._content

    @loggerEntry
    def _populate(self):
        super(BCInterludeVideoPage, self)._populate()

    @simpleLog(action=BC_LOG_ACTIONS.SKIP_VIDEO)
    def _onFinish(self):
        super(BCInterludeVideoPage, self)._onFinish()
