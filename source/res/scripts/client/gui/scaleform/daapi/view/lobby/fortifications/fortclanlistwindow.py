# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortClanListWindow.py
import BigWorld
from debug_utils import LOG_DEBUG
from gui import game_control
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortClanListWindowMeta import FortClanListWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.ClanCache import g_clanCache
from helpers import i18n

class FortClanListWindow(AbstractWindowView, View, FortClanListWindowMeta, AppRef, FortViewHelper):

    def __init__(self):
        super(FortClanListWindow, self).__init__()

    def _populate(self):
        super(FortClanListWindow, self)._populate()
        self.startFortListening()
        ctrl = game_control.g_instance
        ctrl.gameSession.onNewDayNotify += self.__gameSession_onNewDayNotify
        self._update()

    def _dispose(self):
        self.stopFortListening()
        ctrl = game_control.g_instance
        ctrl.gameSession.onNewDayNotify -= self.__gameSession_onNewDayNotify
        super(FortClanListWindow, self)._dispose()

    def _update(self):
        initData = {'windowTitle': i18n.makeString(FORTIFICATIONS.FORTCLANLISTWINDOW_TITLE, clanName=g_clanCache.clanTag),
         'members': self._getClanMemebers()}
        self.as_setDataS(initData)

    def _getClanMemebers(self):
        clanMemebrs = []
        for member in g_clanCache.clanMembers:
            intTotalMining, intWeekMining = self.fortCtrl.getFort().getPlayerContributions(member.getID())
            role = self._getClanRole(member)
            vo = vo_converters.makeSimpleClanListRenderVO(member, intTotalMining, intWeekMining, role)
            clanMemebrs.append(vo)

        return clanMemebrs

    def __gameSession_onNewDayNotify(self, nextUpdateTime):
        self._update()

    def _getClanRole(self, member):
        return fort_text.getText(fort_text.STANDARD_TEXT, i18n.makeString(self.UI_ROLES_BIND[member.getClanRole()]))

    def _getWeekMiningStr(self, weekMining):
        randWeek = BigWorld.wg_getIntegralFormat(weekMining)
        return fort_text.getText(fort_text.PURPLE_TEXT, randWeek)

    def _getTotalMiningStr(self, totalMining):
        allTime = BigWorld.wg_getIntegralFormat(totalMining)
        return fort_text.getText(fort_text.PURPLE_TEXT, allTime)

    def onWindowClose(self):
        self.destroy()

    def onUpdated(self):
        self._update()
