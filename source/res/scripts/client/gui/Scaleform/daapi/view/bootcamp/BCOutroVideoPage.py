# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCOutroVideoPage.py
from gui.Scaleform.daapi.view.bootcamp.BCVideoPage import BCVideoPage
from tutorial.gui.Scaleform.pop_ups import TutorialDialog
from bootcamp.statistic.decorators import loggerTarget, loggerEntry, simpleLog
from bootcamp.statistic.logging_constants import BC_LOG_ACTIONS, BC_LOG_KEYS

@loggerTarget(logKey=BC_LOG_KEYS.BC_OUTRO_VIDEO)
class BCOutroVideoPage(BCVideoPage, TutorialDialog):
    _DEFAULT_MASTER_VOLUME = 0.5

    def __init__(self, settings):
        BCVideoPage.__init__(self, settings)
        TutorialDialog.__init__(self, settings)

    @loggerEntry
    def _populate(self):
        BCVideoPage._populate(self)

    @simpleLog(action=BC_LOG_ACTIONS.SKIP_VIDEO)
    def _onFinish(self):
        self.soundManager.playInstantSound(self._message['event-stop'])
        self._stop()
