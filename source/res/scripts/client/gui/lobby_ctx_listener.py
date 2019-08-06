# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lobby_ctx_listener.py
from gui.lobby_ctx_notifiers import FESTIVAL_ENABLED_NOTIFIER

def _getValueFromPath(path, data):
    if not path:
        return data
    else:
        return _getValueFromPath(path[1:], data[path[0]]) if path[0] in data else None


_CHANGE_NOTIFIERS = [FESTIVAL_ENABLED_NOTIFIER]

class LobbyContextChangeListener(object):
    __slots__ = ('__notifiers', '__proxy')

    def __init__(self, proxy):
        self.__notifiers = []
        self.__proxy = proxy
        for notifier in _CHANGE_NOTIFIERS:
            self.addNotifier(notifier)

    def addNotifier(self, notifier):
        self.__notifiers.append(notifier)

    def update(self, data):
        for notifier in self.__notifiers:
            path = notifier.getPath()
            currentValue = _getValueFromPath(path, self.__proxy.getServerSettings().getSettings())
            nextValue = _getValueFromPath(path, data)
            if nextValue is not None:
                notifier(nextValue, currentValue)

        return
