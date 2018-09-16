# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCNationsWindow.py
from gui.Scaleform.daapi.view.meta.BCNationsWindowMeta import BCNationsWindowMeta
from bootcamp.Bootcamp import g_bootcamp
from debug_utils import LOG_DEBUG, LOG_ERROR
from nations import INDICES as NATIONS_INDICES

class BCNationsWindow(BCNationsWindowMeta):

    def onNationShow(self, nationId):
        pass

    def onNationSelected(self, nationId):
        LOG_DEBUG('onNationSelected', nationId)
        varID = self._content.get('resultVarID')
        if varID:
            self._tutorial.getVars().set(varID, nationId)
        else:
            LOG_ERROR('no variable ID provided to save selected nation!')
        self.submit()

    def _populate(self):
        nationsOrder = [NATIONS_INDICES['usa'], NATIONS_INDICES['germany'], NATIONS_INDICES['ussr']]
        self.as_selectNationS(g_bootcamp.nation, nationsOrder)
        super(BCNationsWindow, self)._populate()

    def onTryClosing(self):
        return False
