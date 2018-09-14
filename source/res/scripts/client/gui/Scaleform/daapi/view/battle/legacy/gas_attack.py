# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/legacy/gas_attack.py
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_constants import VIEW_COMPONENT_RULE
from gui.shared.utils.plugins import IPlugin
from gui import makeHtmlString
from helpers import i18n

class GasAttackPlugin(IPlugin):
    __slots__ = ()

    def start(self):
        super(GasAttackPlugin, self).start()
        self._parentObj.movie.falloutItems.as_loadGasItems(i18n.makeString(FALLOUT.SAFEZONE_MESSAGE), self.__getPanelText())
        g_sessionProvider.addViewComponent('fallout/gasAttack', self._parentObj, rule=VIEW_COMPONENT_RULE.NONE)

    def stop(self):
        g_sessionProvider.removeViewComponent('fallout/gasAttack')
        super(GasAttackPlugin, self).stop()

    @staticmethod
    def __getPanelText():
        infoStr = i18n.makeString(FALLOUT.GASATTACKPANEL_SAFEZONE_MESSAGE)
        return (FALLOUT.GASATTACKPANEL_START_TITLE,
         FALLOUT.GASATTACKPANEL_START_MESSAGE,
         FALLOUT.GASATTACKPANEL_GASATTACK_TITLE,
         FALLOUT.GASATTACKPANEL_GASATTACK_MESSAGE,
         FALLOUT.GASATTACKPANEL_INSIDE_TITLE,
         FALLOUT.GASATTACKPANEL_INSIDE_MESSAGE,
         FALLOUT.GASATTACKPANEL_SAFEZONE_TITLE,
         makeHtmlString('html_templates:battle/gasAtackPanel', 'safeZone', infoStr))
