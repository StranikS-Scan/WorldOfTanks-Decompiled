# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/gas_attack.py
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.battle_control import g_sessionProvider
from gui.shared.utils.plugins import IPlugin
from gui import makeHtmlString
from helpers import i18n

class GasAttackPlugin(IPlugin):

    def start(self):
        super(GasAttackPlugin, self).start()
        self._parentObj.movie.falloutItems.as_loadGasItems(i18n.makeString(FALLOUT.SAFEZONE_MESSAGE), self.__getPanelText())
        g_sessionProvider.getGasAttackCtrl().start(self._parentObj)

    def stop(self):
        g_sessionProvider.getGasAttackCtrl().stop()
        super(GasAttackPlugin, self).stop()

    def __getPanelText(self):
        infoStr = i18n.makeString(FALLOUT.GASATTACKPANEL_SAFEZONE_MESSAGE)
        return (FALLOUT.GASATTACKPANEL_START_TITLE,
         FALLOUT.GASATTACKPANEL_START_MESSAGE,
         FALLOUT.GASATTACKPANEL_GASATTACK_TITLE,
         FALLOUT.GASATTACKPANEL_GASATTACK_MESSAGE,
         FALLOUT.GASATTACKPANEL_INSIDE_TITLE,
         FALLOUT.GASATTACKPANEL_INSIDE_MESSAGE,
         FALLOUT.GASATTACKPANEL_SAFEZONE_TITLE,
         makeHtmlString('html_templates:battle/gasAtackPanel', 'safeZone', infoStr))
