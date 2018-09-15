# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCNationsWindow.py
from gui.Scaleform.daapi.view.meta.BCNationsWindowMeta import BCNationsWindowMeta
from bootcamp.Bootcamp import g_bootcamp
from debug_utils import LOG_DEBUG
from nations import INDICES as NATIONS_INDICES

class BCNationsWindow(BCNationsWindowMeta):

    def __init__(self, ctx=None):
        super(BCNationsWindow, self).__init__()
        self.__removedCallback = ctx['callback']

    def onNationShow(self, nationId):
        pass

    def onNationSelected(self, nationId):
        LOG_DEBUG('onNationSelected {0}'.format(nationId))
        g_bootcamp.changeNation(nationId, self.__removedCallback)
        self.destroy()

    def _populate(self):
        nationsOrder = [NATIONS_INDICES['usa'], NATIONS_INDICES['germany'], NATIONS_INDICES['ussr']]
        self.as_selectNationS(g_bootcamp.nation, nationsOrder)
        super(BCNationsWindow, self)._populate()
