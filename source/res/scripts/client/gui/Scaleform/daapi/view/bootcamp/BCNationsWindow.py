# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCNationsWindow.py
from constants import IS_CHINA
from gui.Scaleform.daapi.view.meta.BCNationsWindowMeta import BCNationsWindowMeta
from bootcamp.Bootcamp import g_bootcamp
from uilogging.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.bootcamp.constants import BC_LOG_KEYS
from uilogging.bootcamp.loggers import BootcampUILogger
from debug_utils import LOG_ERROR
from gui.impl import backport
from gui.impl.gen import R
from nations import INDICES as NATIONS_INDICES, MAP as NATIONS_MAP
from PlayerEvents import g_playerEvents

@loggerTarget(logKey=BC_LOG_KEYS.BC_HANGAR_HINTS, loggerCls=BootcampUILogger)
class BCNationsWindow(BCNationsWindowMeta):

    def onTryClosing(self):
        return False

    def onNationShow(self, nationId):
        g_bootcamp.previewNation(NATIONS_INDICES[nationId])

    @simpleLog(argsIndex=0, argMap=NATIONS_MAP)
    def onNationSelected(self, nationId):
        varID = self._content.get('resultVarID')
        if varID:
            self._tutorial.getVars().set(varID, NATIONS_INDICES[nationId])
        else:
            LOG_ERROR('no variable ID provided to save selected nation!')
        self.submit()

    @loggerEntry
    def _populate(self):
        g_playerEvents.onDisconnected += self._onDisconnected
        if IS_CHINA:
            nationsOrder = ['china', 'usa', 'germany']
        else:
            nationsOrder = ['ussr', 'germany', 'usa']
        voList = [ self._getVO(nationId) for nationId in nationsOrder ]
        selectedItem = NATIONS_MAP[g_bootcamp.nation]
        index = nationsOrder.index(selectedItem) if selectedItem in nationsOrder else 0
        self.as_selectNationS(index, voList)
        g_bootcamp.previewNation(g_bootcamp.nation)
        super(BCNationsWindow, self)._populate()

    def _dispose(self):
        g_playerEvents.onDisconnected -= self._onDisconnected
        super(BCNationsWindow, self)._dispose()

    def _onDisconnected(self):
        self.destroy()

    @staticmethod
    def _getVO(nationId):
        return {'id': nationId,
         'label': backport.text(R.strings.bootcamp.award.options.nation.dyn(nationId)()),
         'icon': backport.image(R.images.gui.maps.icons.bootcamp.rewards.dyn('nationsSelect_{}'.format(nationId))()),
         'name': backport.text(R.strings.bootcamp.award.options.name.dyn(nationId)()),
         'description': backport.text(R.strings.bootcamp.award.options.description.dyn(nationId)())}
