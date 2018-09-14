# Embedded file name: scripts/client/gui/miniclient/lobby/MiniclientDescriptionWindow.py
import os
from gui import GUI_SETTINGS
from gui.game_control import getBrowserCtrl
from gui.shared import g_eventBus, events
from helpers.i18n import makeString as _ms

class MiniclientDescriptionWindow(object):

    def __init__(self):
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__openDescriptionInBrowser)

    def __openDescriptionInBrowser(self, event):
        current_working_dir = os.getcwd()
        getBrowserCtrl().load(url='{0}/{1}/greeting/mini_wot/'.format(GUI_SETTINGS.miniclient['webBridgeRootURL'], _ms('#settings:LANGUAGE_CODE')), title=_ms('#miniclient:hangar/miniclient_description_window/title'), browserSize=(780, 450), showCloseBtn=True, showActionBtn=False)(lambda success: True)
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__openDescriptionInBrowser)
