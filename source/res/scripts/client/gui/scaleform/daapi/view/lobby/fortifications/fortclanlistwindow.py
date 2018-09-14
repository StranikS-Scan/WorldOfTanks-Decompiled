# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortClanListWindow.py
import BigWorld
from debug_utils import LOG_DEBUG
from gui import game_control
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortClanListWindowMeta import FortClanListWindowMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.ClanCache import g_clanCache
from gui.shared.utils.functions import getClanRoleString
from helpers import i18n

class FortClanListWindow(AbstractWindowView, View, FortClanListWindowMeta, AppRef, FortViewHelper):

    def __init__(self, ctx = None):
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
         'members': self._getClanMembers()}
        self.as_setDataS(initData)

    def _getClanMembers(self):
        clanMembers = []
        for member in g_clanCache.clanMembers:
            intTotalMining, intWeekMining = self.fortCtrl.getFort().getPlayerContributions(member.getID())
            role = self._getClanRole(member)
            roleID = self.CLAN_MEMBER_ROLES.index(member.getClanRole())
            vo = vo_converters.makeSimpleClanListRenderVO(member, intTotalMining, intWeekMining, role, roleID)
            clanMembers.append(vo)

        return clanMembers

    def __gameSession_onNewDayNotify(self, nextUpdateTime):
        self._update()

    def _getClanRole(self, member):
        return self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(getClanRoleString(member.getClanRole())))

    def _getWeekMiningStr(self, weekMining):
        randWeek = BigWorld.wg_getIntegralFormat(weekMining)
        return self.app.utilsManager.textManager.getText(TextType.DEFRES_TEXT, randWeek)

    def _getTotalMiningStr(self, totalMining):
        allTime = BigWorld.wg_getIntegralFormat(totalMining)
        return self.app.utilsManager.textManager.getText(TextType.DEFRES_TEXT, allTime)

    def onWindowClose(self):
        self.destroy()

    def onClanMembersListChanged(self):
        self._update()

    def onUpdated(self, isFullUpdate):
        self._update()
