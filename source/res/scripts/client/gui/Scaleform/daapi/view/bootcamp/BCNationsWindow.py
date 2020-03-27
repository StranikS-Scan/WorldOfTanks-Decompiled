# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCNationsWindow.py
from gui.Scaleform.daapi.view.meta.BCNationsWindowMeta import BCNationsWindowMeta
from bootcamp.Bootcamp import g_bootcamp
from bootcamp.statistic.decorators import loggerTarget, loggerEntry, simpleLog
from bootcamp.statistic.logging_constants import BC_LOG_KEYS
from debug_utils import LOG_ERROR
from nations import INDICES as NATIONS_INDICES, MAP as NATIONS_MAP
from PlayerEvents import g_playerEvents

@loggerTarget(logKey=BC_LOG_KEYS.BC_NATION_SELECT)
class BCNationsWindow(BCNationsWindowMeta):

    def onNationShow(self, nationId):
        g_bootcamp.previewNation(nationId)

    @simpleLog(argKey='nationId', argMap=NATIONS_MAP)
    def onNationSelected(self, nationId):
        varID = self._content.get('resultVarID')
        if varID:
            self._tutorial.getVars().set(varID, nationId)
        else:
            LOG_ERROR('no variable ID provided to save selected nation!')
        self.submit()

    @loggerEntry
    def _populate(self):
        g_playerEvents.onDisconnected += self._onDisconnected
        nationsOrder = [NATIONS_INDICES['usa'], NATIONS_INDICES['germany'], NATIONS_INDICES['ussr']]
        self.as_selectNationS(g_bootcamp.nation, nationsOrder)
        g_bootcamp.previewNation(g_bootcamp.nation)
        super(BCNationsWindow, self)._populate()

    def _dispose(self):
        g_playerEvents.onDisconnected -= self._onDisconnected
        super(BCNationsWindow, self)._dispose()

    def onTryClosing(self):
        return False

    def _onDisconnected(self):
        self.destroy()
