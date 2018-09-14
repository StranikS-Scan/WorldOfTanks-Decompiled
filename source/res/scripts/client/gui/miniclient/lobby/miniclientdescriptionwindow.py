# Embedded file name: scripts/client/gui/miniclient/lobby/MiniclientDescriptionWindow.py
import os
import ResMgr
from gui.game_control import getBrowserCtrl
from gui.shared import g_eventBus, events
from helpers.i18n import makeString as _ms

class MiniclientDescriptionWindow(object):

    def __init__(self):
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__openDescriptionInBrowser)

    def __openDescriptionInBrowser(self, event):
        current_working_dir = os.getcwd()
        getBrowserCtrl().load(url='file:///{0}'.format(ResMgr.resolveToAbsolutePath('gui/html/miniclient_description/index_{0}.html'.format(_ms('#settings:LANGUAGE_CODE')))), title=_ms('#miniclient:hangar/miniclient_description_window/title'), browserSize=(780, 450), showCloseBtn=True, showActionBtn=False)(lambda success: True)
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__openDescriptionInBrowser)
