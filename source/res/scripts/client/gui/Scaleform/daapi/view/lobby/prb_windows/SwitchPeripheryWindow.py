# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/SwitchPeripheryWindow.py
import constants
from adisp import process
from debug_utils import LOG_DEBUG
from gui import DialogsInterface
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.view.meta.SwitchPeripheryWindowMeta import SwitchPeripheryWindowMeta
from gui.Scaleform.daapi.view.servers_data_provider import ServersDataProvider
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency
from helpers.i18n import makeString as _ms
from predefined_hosts import g_preDefinedHosts, REQUEST_RATE
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IReloginController

class SwitchPeripheryWindow(SwitchPeripheryWindowMeta, Notifiable):
    _BTN_WIDTH = 140
    _CLOSE_BTN_ACTION = 'closeAction'
    _SWITCH_BTN_ACTION = 'switchAction'
    relogin = dependency.descriptor(IReloginController)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, ctx):
        super(SwitchPeripheryWindow, self).__init__()
        self.__ctx = ctx

    def onBtnClick(self, action):
        if action == self._CLOSE_BTN_ACTION:
            self.onWindowClose()

    def requestForChange(self, peripheryId):
        if self.connectionMgr.peripheryID != peripheryId:
            self.__relogin(peripheryId)
        else:
            LOG_DEBUG('Current server for relogin has been chosen: %s' % peripheryId)

    def onWindowClose(self):
        self.destroy()

    def onDropDownOpened(self, opened):
        if GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ON_REQUEST:
            if opened:
                g_preDefinedHosts.startCSISUpdate()
            else:
                g_preDefinedHosts.stopCSISUpdate()
                self._updateServersList()
        if opened:
            g_preDefinedHosts.requestPing(True)

    def _updateServersList(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
        serversList = []
        for hostName, name, csisStatus, peripheryID in hostsList:
            if self.__ctx.isPeripheryAvailable(peripheryID):
                serversList.append({'label': name,
                 'id': peripheryID,
                 'csisStatus': csisStatus,
                 'data': hostName})

        label = _ms(self.__ctx.getSelectServerLabel())
        if not serversList:
            self.onWindowClose()
            return
        if len(serversList) == 1:
            label = _ms(self.__ctx.getApplySwitchLabel(), server=text_styles.stats(serversList[0]['label']))
        self._serversDP.rebuildList(serversList)
        self.as_setServerParamsS(label, len(serversList) > 1)
        self.as_setSelectedIndexS(0)

    def _populate(self):
        super(SwitchPeripheryWindow, self)._populate()
        self._serversDP = ServersDataProvider()
        self._serversDP.setFlashObject(self.as_getServersDPS())
        self.as_setImageS(RES_ICONS.MAPS_ICONS_WINDOWS_SWITCH_PERIPHERY_WINDOW_BG, 0)
        self.as_setWindowTitleS(_ms(DIALOGS.SWITCHPERIPHERYWINDOW_WINDOWTITLE))
        currentServer = self.connectionMgr.serverUserName
        self.as_setTextS(_ms(self.__ctx.getHeader()), _ms(self.__ctx.getDescription(), server=text_styles.error(currentServer)))
        self.addNotificator(SimpleNotifier(self.__ctx.getUpdateTime, self.__onServersUpdate))
        self.startNotification()
        self._updateServersList()
        if not constants.IS_CHINA:
            if GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ALWAYS:
                g_preDefinedHosts.startCSISUpdate()
            g_preDefinedHosts.onCsisQueryStart += self.__onServersUpdate
            g_preDefinedHosts.onCsisQueryComplete += self.__onServersUpdate
            g_preDefinedHosts.onPingPerformed += self.__onServersUpdate
        self.as_setButtonsS([{'label': _ms(DIALOGS.SWITCHPERIPHERYWINDOW_BTNSWITCH),
          'btnLinkage': BUTTON_LINKAGES.BUTTON_NORMAL,
          'action': self._SWITCH_BTN_ACTION,
          'isFocused': True,
          'tooltip': ''}, {'label': _ms(DIALOGS.SWITCHPERIPHERYWINDOW_BTNCANCEL),
          'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK,
          'action': self._CLOSE_BTN_ACTION,
          'isFocused': False,
          'tooltip': ''}], TEXT_ALIGN.RIGHT, self._BTN_WIDTH)

    def _dispose(self):
        self.stopNotification()
        self.clearNotification()
        if not constants.IS_CHINA:
            g_preDefinedHosts.stopCSISUpdate()
            g_preDefinedHosts.onCsisQueryStart -= self.__onServersUpdate
            g_preDefinedHosts.onCsisQueryComplete -= self.__onServersUpdate
            g_preDefinedHosts.onPingPerformed -= self.__onServersUpdate
        self._serversDP.fini()
        self._serversDP = None
        super(SwitchPeripheryWindow, self)._dispose()
        return

    @process
    def __relogin(self, peripheryID):
        if g_preDefinedHosts.isRoamingPeriphery(peripheryID):
            success = yield DialogsInterface.showI18nConfirmDialog('changeRoamingPeriphery')
        else:
            success = yield DialogsInterface.showI18nConfirmDialog('changePeriphery')
        if success:
            self.relogin.doRelogin(peripheryID, extraChainSteps=self.__ctx.getExtraChainSteps())

    def __onServersUpdate(self, *args):
        self._updateServersList()
