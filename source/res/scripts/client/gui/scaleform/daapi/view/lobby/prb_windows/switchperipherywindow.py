# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/SwitchPeripheryWindow.py
from ConnectionManager import connectionManager
import constants
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.view.meta.SwitchPeripheryWindowMeta import SwitchPeripheryWindowMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework import AppRef
from predefined_hosts import g_preDefinedHosts
from gui import makeHtmlString
from gui import DialogsInterface
from gui import game_control
from adisp import process

class SwitchPeripheryWindow(View, SwitchPeripheryWindowMeta, AbstractWindowView, AppRef):
    _BTN_WIDTH = 140
    _CLOSE_BTN_ACTION = 'closeAction'
    _SWITCH_BTN_ACTION = 'switchAction'

    def __init__(self, ctx = None):
        super(SwitchPeripheryWindow, self).__init__()

    def onBtnClick(self, action):
        if action == self._CLOSE_BTN_ACTION:
            self.onWindowClose()

    def requestForChange(self, peripheryId):
        if connectionManager.peripheryID != peripheryId:
            self.__relogin(peripheryId)
        else:
            LOG_DEBUG('Current server for relogin has been chosen: %s' % peripheryId)

    def onWindowClose(self):
        self.destroy()

    def _updateServersList(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
        serversList = []
        selectedIndex = -1
        currIndex = -1
        for key, name, csisStatus, peripheryID in hostsList:
            currIndex = currIndex + 1
            selected = connectionManager.peripheryID == peripheryID
            if selected:
                selectedIndex = currIndex
            serversList.append({'label': name if not constants.IS_CHINA else makeHtmlString('html_templates:lobby/serverStats', 'serverName', {'name': name}),
             'id': peripheryID,
             'csisStatus': csisStatus,
             'selected': selected})

        label = _ms(FORTIFICATIONS.SWITCHPERIPHERYWINDOW_SELECTSERVERLABEL)
        if len(serversList) == 1:
            label = _ms(FORTIFICATIONS.SWITCHPERIPHERYWINDOW_APPLYSWITCHLABEL, server=text_styles.stats(serversList[0]['label']))
        self.as_setDataS({'label': label,
         'peripheries': serversList,
         'isServerDropdownMenuVisibility': len(serversList) > 1,
         'selectedIndex': selectedIndex})

    def _populate(self):
        super(SwitchPeripheryWindow, self)._populate()
        self.as_setImageS(RES_ICONS.MAPS_ICONS_WINDOWS_SWITCH_PERIPHERY_WINDOW_BG, 0)
        self.as_setWindowTitleS(_ms(FORTIFICATIONS.SWITCHPERIPHERYWINDOW_WINDOWTITLE))
        currentServer = connectionManager.serverUserName
        self.as_setTextS(_ms(FORTIFICATIONS.SWITCHPERIPHERYWINDOW_HEADER), _ms(FORTIFICATIONS.SWITCHPERIPHERYWINDOW_DESCRIPTION, server=text_styles.error(currentServer)))
        self._updateServersList()
        self.as_setButtonsS([{'label': _ms(FORTIFICATIONS.SWITCHPERIPHERYWINDOW_BTNSWITCH),
          'btnLinkage': BUTTON_LINKAGES.BUTTON_NORMAL,
          'action': self._SWITCH_BTN_ACTION,
          'isFocused': True,
          'tooltip': ''}, {'label': _ms(FORTIFICATIONS.SWITCHPERIPHERYWINDOW_BTNCANCEL),
          'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK,
          'action': self._CLOSE_BTN_ACTION,
          'isFocused': False,
          'tooltip': ''}], TEXT_ALIGN.RIGHT, self._BTN_WIDTH)

    def _dispose(self):
        super(SwitchPeripheryWindow, self)._dispose()

    @process
    def __relogin(self, peripheryID):
        self.__isGuiUpdateSuppressed = True
        if g_preDefinedHosts.isRoamingPeriphery(peripheryID):
            success = yield DialogsInterface.showI18nConfirmDialog('changeRoamingPeriphery')
        else:
            success = yield DialogsInterface.showI18nConfirmDialog('changePeriphery')
        if success:
            game_control.g_instance.roaming.relogin(peripheryID)
