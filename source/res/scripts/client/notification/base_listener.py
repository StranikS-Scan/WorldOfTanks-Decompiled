# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/base_listener.py
import weakref
import typing
if typing.TYPE_CHECKING:
    from notification.NotificationsModel import NotificationsModel
    from typing import Optional

class NotificationListener(object):

    def __init__(self):
        super(NotificationListener, self).__init__()

        def model():
            pass

        self._model = model

    def start(self, model):
        self._model = weakref.ref(model)
        return True

    def stop(self):
        self._model = lambda : None

    def request(self):
        pass
