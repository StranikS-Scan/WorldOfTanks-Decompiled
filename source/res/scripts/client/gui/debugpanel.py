# Embedded file name: scripts/client/gui/DebugPanel.py
import BigWorld
from gui.DebugView import DebugView
from gui.DebugView import DebugViewItem
from debug_utils import *

class DebugPanel(DebugView):

    def __init__(self, textureName = '', parentGUI = None, updateInterval = 0.1):
        DebugView.__init__(self, textureName, parentGUI)
        self.__cbIDUpdate = None
        self.__cbUpdateInterval = -1.0
        self.setUpdateInterval(updateInterval)
        return

    def destroy(self):
        self.setUpdateInterval(-1.0)
        DebugView.destroy(self)

    def setUpdateInterval(self, interval = 0.1):
        self.__cbUpdateInterval = interval
        if self.__cbIDUpdate is not None:
            BigWorld.cancelCallback(self.__cbIDUpdate)
            self.__cbIDUpdate = None
        if self.__cbUpdateInterval >= 0.0:
            self.__onUpdate()
        return

    def addItem(self, keyname, item):
        if not isinstance(item, DebugPanelItem):
            return
        DebugView.addItem(self, keyname, item)

    def update(self):
        for item in self.iteritems():
            v = item.request()
            if v is not None:
                item.setValue(v)

        DebugView.update(self)
        return

    def __onUpdate(self):
        self.__cbIDUpdate = None
        self.update()
        self.__cbIDUpdate = BigWorld.callback(self.__cbUpdateInterval, lambda : self.__onUpdate())
        return


class DebugPanelItem(DebugViewItem):

    def __init__(self, name = '', updater = None, mapper = None):
        DebugViewItem.__init__(self, name)
        self.__updater = updater
        self.__mapper = mapper

    def destroy(self):
        self.__updater.destroy()
        self.__updater = None
        self.__mapper = None
        DebugViewItem.destroy(self)
        return

    def request(self):
        if self.__updater is None:
            return
        else:
            try:
                v = self.__updater.request()
                if v is None:
                    return
                if self.__mapper is None:
                    return str(v)
                return str(self.__mapper(v))
            except:
                LOG_DEBUG('DebugPanelItem: value request failed. Look exception below')
                LOG_CURRENT_EXCEPTION()
                return

            return

    def setUpdaterMapper(self, updater, mapper):
        self.__updater = updater
        self.__mapper = mapper


class DebugPanelItemUpdater:

    def __init__(self, functor, interval = 0.0):
        self.__value = None
        self.__cbIDValid = None
        self.__cbFunctor = None
        self.__cbInterval = -1.0
        self.setFunctor(functor, interval)
        return

    def destroy(self):
        self.setFunctor(None, -1.0)
        return

    def request(self):
        self.__validate()
        return self.__value

    def setFunctor(self, functor, interval):
        self.__invalidate()
        self.__cbFunctor = functor
        self.__cbInterval = interval

    def getValid(self):
        return self.__cbIDValid is not None

    def __validate(self):
        if self.getValid():
            return
        else:
            self.__value = None
            try:
                self.__value = self.__cbFunctor()
            except:
                LOG_DEBUG('DebugPanelItemUpdater: value validating failed. Look exception below')
                LOG_CURRENT_EXCEPTION()
                return

            self.__cbIDValid = BigWorld.callback(self.__cbInterval, lambda : self.__doInvalidate())
            return

    def __invalidate(self):
        if self.__cbIDValid is not None:
            BigWorld.cancelCallback(self.__cbIDValid)
            self.__doInvalidate()
        return

    def __doInvalidate(self):
        self.__cbIDValid = None
        return
