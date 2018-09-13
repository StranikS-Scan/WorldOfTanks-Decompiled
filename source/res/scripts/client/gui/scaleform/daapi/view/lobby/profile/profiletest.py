# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTest.py
from gui.WindowsManager import g_windowsManager
from gui.shared import events, EVENT_BUS_SCOPE

class _ProfileTest(object):

    def __init__(self):
        pass

    def showProfileWindow(self, userName = 'Happy_3rd_friend'):
        g_windowsManager.window.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_PROFILE_WINDOW, {'userName': userName}), EVENT_BUS_SCOPE.LOBBY)


g_instance = _ProfileTest()
