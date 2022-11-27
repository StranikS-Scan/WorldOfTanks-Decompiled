# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCNationsWindow.py
from constants import CURRENT_REALM
from gui.Scaleform.daapi.view.meta.BCNationsWindowMeta import BCNationsWindowMeta
from bootcamp.Bootcamp import g_bootcamp, BOOTCAMP_SOUND
from uilogging.deprecated.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.deprecated.bootcamp.constants import BC_LOG_KEYS
from uilogging.deprecated.bootcamp.loggers import BootcampUILogger
from debug_utils import LOG_ERROR
from gui.impl import backport
from gui.impl.gen import R
from nations import INDICES as NATIONS_INDICES, MAP as NATIONS_MAP
from PlayerEvents import g_playerEvents

@loggerTarget(logKey=BC_LOG_KEYS.BC_NATION_SELECT, loggerCls=BootcampUILogger)
class BCNationsWindow(BCNationsWindowMeta):
    nations = {'NA': (['usa', 'ussr', 'germany'], ['uk',
             'france',
             'czech',
             'japan',
             'china',
             'poland',
             'sweden',
             'italy']),
     'RU': (['ussr', 'germany', 'usa'], ['france',
             'uk',
             'czech',
             'china',
             'japan',
             'poland',
             'sweden',
             'italy']),
     'EU': (['germany', 'ussr', 'usa'], ['france',
             'uk',
             'china',
             'japan',
             'czech',
             'poland',
             'sweden',
             'italy']),
     'ASIA': (['germany', 'ussr', 'usa'], ['japan',
               'china',
               'uk',
               'france',
               'czech',
               'poland',
               'italy',
               'sweden']),
     'CN': (['china', 'ussr', 'usa'], ['germany',
             'sweden',
             'france',
             'italy',
             'uk',
             'czech',
             'poland',
             'japan']),
     'DEFAULT': (['germany', 'ussr', 'usa'], ['france',
                  'uk',
                  'czech',
                  'china',
                  'japan',
                  'poland',
                  'sweden',
                  'italy'])}

    def onTryClosing(self):
        return False

    def onNationShow(self, nationId):
        g_bootcamp.previewNation(NATIONS_INDICES[nationId])

    @simpleLog(argsIndex=0)
    def onNationSelected(self, nationId):
        varID = self._content.get('resultVarID')
        if varID:
            self._tutorial.getVars().set(varID, NATIONS_INDICES[nationId])
        else:
            LOG_ERROR('no variable ID provided to save selected nation!')
        self.submit()

    def __getNationsOrder(self, realm):
        return self.nations.get(realm, self.nations['DEFAULT'])

    @loggerEntry
    def _populate(self):
        g_playerEvents.onDisconnected += self._onDisconnected
        nationsOrder, promoNationsOrder = self.__getNationsOrder(CURRENT_REALM)
        voList = self._getVONationsList(nationsOrder)
        voPromoList = self._getVONationsList(promoNationsOrder, True)
        selectedItem = NATIONS_MAP[g_bootcamp.nation]
        index = nationsOrder.index(selectedItem) if selectedItem in nationsOrder else 0
        self.as_selectNationS(index, voList, voPromoList)
        g_bootcamp.previewNation(g_bootcamp.nation)
        self.soundManager.playSound(BOOTCAMP_SOUND.NEW_UI_ELEMENT_SOUND)
        super(BCNationsWindow, self)._populate()

    def onHighlightShow(self):
        self.soundManager.playSound(BOOTCAMP_SOUND.NEW_UI_ELEMENT_SOUND)

    def _dispose(self):
        g_playerEvents.onDisconnected -= self._onDisconnected
        super(BCNationsWindow, self)._dispose()

    def _onDisconnected(self):
        self.destroy()

    def _getVONationsList(self, nationsOrder, promo=False):
        return [ self._getVO(nationId, promo) for nationId in nationsOrder ]

    @staticmethod
    def _getVO(nationId, promo):
        return {'id': nationId,
         'label': backport.text(R.strings.bootcamp.award.options.nation.dyn(nationId)()),
         'icon': backport.image(R.images.gui.maps.icons.bootcamp.rewards.dyn('nationsSelect_{}'.format(nationId))()),
         'name': backport.text(R.strings.bootcamp.award.options.name.dyn(nationId)()),
         'description': backport.text(R.strings.bootcamp.award.options.description.dyn(nationId)()),
         'isPromo': promo}
