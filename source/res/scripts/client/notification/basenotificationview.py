# Embedded file name: scripts/client/notification/BaseNotificationView.py


class BaseNotificationView(object):

    def __init__(self, model = None):
        super(BaseNotificationView, self).__init__()
        self._model = None
        self.setModel(model)
        return

    def setModel(self, value):
        self._model = value

    def cleanUp(self):
        self._model = None
        return
